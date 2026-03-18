import regex as standard_re
import re2
import ahocorasick
import math
import json
import os
import signal
import bisect
from typing import List, Dict, Any, Optional, Set, Iterator
from report import Finding, format_report

# Design rule #4: Limit input size for single-block scanning
MAX_BLOCK_SIZE = 100_000

class TimeoutError(Exception): pass
def timeout_handler(signum, frame): raise TimeoutError()

class DetectionEngine:
    def __init__(self, entropy_threshold: float = 4.0, rules_path: str = 'data/rules.json'):
        self.entropy_threshold = entropy_threshold
        self.rules = self._load_rules(rules_path)
        self.keyword_map = {}
        self.automaton = ahocorasick.Automaton()
        self.re2_rules = []
        self.legacy_rules = []
        self._initialize_rules()

    def _load_rules(self, rules_path: str) -> List[Dict[str, Any]]:
        if os.path.exists(rules_path):
            try:
                with open(rules_path, 'r', encoding='utf-8') as f: return json.load(f)
            except Exception: pass
        return []

    def _initialize_rules(self):
        for idx, rule in enumerate(self.rules):
            for kw in rule.get('keywords', []):
                kw = kw.lower()
                if kw not in self.keyword_map:
                    self.keyword_map[kw] = []
                    self.automaton.add_word(kw, kw)
                self.keyword_map[kw].append(idx)
            try:
                compiled = re2.compile(rule['regex'])
                self.re2_rules.append({'id': rule['id'], 'risk': rule['risk'], 'regex': compiled, 'original_idx': idx})
            except Exception:
                try:
                    compiled = standard_re.compile(rule['regex'], standard_re.DOTALL | standard_re.MULTILINE)
                    self.legacy_rules.append({'id': rule['id'], 'risk': rule['risk'], 'regex': compiled, 'original_idx': idx})
                except Exception: continue
        self.automaton.make_automaton()

    def calculate_entropy(self, data: str) -> float:
        if not data: return 0.0
        counts = {}
        for char in data: counts[char] = counts.get(char, 0) + 1
        entropy = 0
        for count in counts.values():
            p_x = count / len(data)
            entropy += -p_x * math.log(p_x, 2)
        return entropy

    def run_safe_legacy_match(self, regex, text):
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1)
            try: return list(regex.finditer(text))
            finally: signal.alarm(0)
        except Exception: return []

    def run_entropy_detection(self, line: str, line_num: int, existing_findings: List[Finding]) -> List[Finding]:
        findings = []
        for match in standard_re.finditer(r"\b[a-zA-Z0-9]{20,}\b", line):
            token = match.group(0)
            if any(token in f.content for f in existing_findings): continue
            if self.calculate_entropy(token) > self.entropy_threshold:
                if standard_re.search(r"(?i)(key|secret|token|password|auth|api|cred|prod)", line):
                    findings.append(Finding("Potential Secret (High Entropy + Context)", line_num, "HIGH", token, 0.7))
                else:
                    findings.append(Finding("High Entropy String", line_num, "MEDIUM", token, 0.3))
        return findings

class SecretDetector:
    def __init__(self, entropy_threshold: float = 4.0, rules_path: str = 'data/rules.json', force_scan_all: bool = False):
        self.engine = DetectionEngine(entropy_threshold, rules_path)
        self.force_scan_all = force_scan_all
        self.context_rules = [
            re2.compile(r"(?is)(?:my|here is|prod|our).*?(?:api|token|secret|password|key)\s*[:=]\s*(\S+)"),
            re2.compile(r"(?is)(?:api|access|auth).*?(?:key|token|secret)\s*[:=]\s*(\S+)")
        ]

    def _scan_block(self, text: str, base_line: int, force_scan_all: bool) -> List[Finding]:
        if not text: return []
        
        # Line number tracking within the block
        line_offsets = [0]
        for match in standard_re.finditer(r"\n", text):
            line_offsets.append(match.end())
        
        def get_line_num(pos):
            idx = bisect.bisect_right(line_offsets, pos)
            return base_line + max(0, idx - 1)

        all_findings = []
        triggered_indices = set()
        if not force_scan_all:
            found_keywords = {original_value for _, original_value in self.engine.automaton.iter(text.lower())}
            for kw in found_keywords: triggered_indices.update(self.engine.keyword_map.get(kw, []))
            
        # 1. Regex Matching
        for rule in self.engine.re2_rules:
            rule_def = self.engine.rules[rule['original_idx']]
            if force_scan_all or not rule_def.get('keywords') or rule['original_idx'] in triggered_indices:
                for m in rule['regex'].finditer(text):
                    content = m.group(1) if m.groups() else m.group(0)
                    if 'entropy' in rule_def:
                        if self.engine.calculate_entropy(content) < (rule_def['entropy'] * 0.8):
                            continue
                    all_findings.append(Finding(rule['id'], get_line_num(m.start()), rule['risk'].upper(), content, 0.9))
        
        for rule in self.engine.legacy_rules:
            rule_def = self.engine.rules[rule['original_idx']]
            if force_scan_all or not rule_def.get('keywords') or rule['original_idx'] in triggered_indices:
                for m in self.engine.run_safe_legacy_match(rule['regex'], text):
                    content = m.group(1) if m.groups() else m.group(0)
                    if 'entropy' in rule_def:
                        if self.engine.calculate_entropy(content) < (rule_def['entropy'] * 0.8):
                            continue
                    all_findings.append(Finding(rule['id'], get_line_num(m.start()), rule['risk'].upper(), content, 0.8))

        # 2. Contextual rules
        for regex in self.context_rules:
            for m in regex.finditer(text):
                all_findings.append(Finding("Contextual Secret (LLM Prompt)", get_line_num(m.start()), "MEDIUM", m.group(1), 0.6))

        # 3. Entropy Detection
        lines = text.splitlines()
        for i, line in enumerate(lines):
            line_findings = self.engine.run_entropy_detection(line, base_line + i, all_findings)
            all_findings.extend(line_findings)

        return all_findings

    def scan(self, text: str, force_scan_all: Optional[bool] = None) -> List[Finding]:
        do_force = force_scan_all if force_scan_all is not None else self.force_scan_all
        cleaned_text = text[:MAX_BLOCK_SIZE]
        return self._scan_block(cleaned_text, 1, do_force)

    def scan_stream(self, stream: Iterator[str], force_scan_all: Optional[bool] = None, chunk_size: int = 1024*1024) -> List[Finding]:
        do_force = force_scan_all if force_scan_all is not None else self.force_scan_all
        all_findings = []
        current_line = 1
        overlap = ""
        
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            
            # Combine overlap from previous chunk to ensure no secrets are missed at boundaries
            # We use a simple strategy: process up to the last newline in the chunk
            # The remaining part becomes overlap for the next chunk.
            
            text_to_scan = overlap + chunk
            last_newline = text_to_scan.rfind('\n')
            
            if last_newline == -1:
                # No newline in chunk, keep it all as overlap unless chunk is huge
                if len(text_to_scan) > chunk_size * 5:
                    # Emergency flush if no newline found for a long time
                    # We keep a small overlap (e.g. 1024 or chunk_size) to ensure secrets aren't split
                    keep = min(len(text_to_scan), 4096)
                    block = text_to_scan[:-keep]
                    overlap = text_to_scan[-keep:]
                    
                    if block:
                        findings = self._scan_block(block, current_line, do_force)
                        all_findings.extend(findings)
                        current_line += block.count('\n')
                else:
                    overlap = text_to_scan
                    continue
            else:
                block = text_to_scan[:last_newline + 1]
                overlap = text_to_scan[last_newline + 1:]
                
                findings = self._scan_block(block, current_line, do_force)
                all_findings.extend(findings)
                current_line += block.count('\n')
        
        # Scan final remaining overlap
        if overlap:
            findings = self._scan_block(overlap, current_line, do_force)
            all_findings.extend(findings)
            
        return all_findings

    def format_report(self, findings: List[Finding], show_full: bool = False, show_short: bool = False, no_colors: bool = False) -> str:
        return format_report(findings, show_full, show_short, no_colors)

if __name__ == "__main__":
    detector = SecretDetector()
    print(detector.format_report(detector.scan("sk-1234567890abcdef1234567890abcdef")))
