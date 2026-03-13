import regex as standard_re
import re2
import ahocorasick
import math
import json
import os
import signal
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set

# Design rule #4: Limit input size
MAX_TEXT_SIZE = 100_000

@dataclass
class Finding:
    secret_type: str
    location: int
    risk: str
    content: str
    confidence: float = 0.0

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
            re2.compile(r"(?i)(?:my|here is|prod|our).*?(?:api|token|secret|password|key)\s*[:=]\s*(\S+)"),
            re2.compile(r"(?i)(?:api|access|auth).*?(?:key|token|secret)\s*[:=]\s*(\S+)")
        ]

    def scan(self, text: str, force_scan_all: Optional[bool] = None) -> List[Finding]:
        do_force = force_scan_all if force_scan_all is not None else self.force_scan_all
        cleaned_text = text[:MAX_TEXT_SIZE]
        if not cleaned_text: return []
        
        # Line number tracking
        line_offsets = [0]
        for match in standard_re.finditer(r"\n", cleaned_text):
            line_offsets.append(match.end())
        
        def get_line_num(pos):
            # Binary search for efficiency on large files
            import bisect
            idx = bisect.bisect_right(line_offsets, pos)
            return max(1, idx)

        all_findings = []
        triggered_indices = set()
        if not do_force:
            found_keywords = {original_value for _, original_value in self.engine.automaton.iter(cleaned_text.lower())}
            for kw in found_keywords: triggered_indices.update(self.engine.keyword_map.get(kw, []))
            
        # 1. Regex Matching
        for rule in self.engine.re2_rules:
            if do_force or not self.engine.rules[rule['original_idx']].get('keywords') or rule['original_idx'] in triggered_indices:
                for m in rule['regex'].finditer(cleaned_text):
                    content = m.group(1) if m.groups() else m.group(0)
                    all_findings.append(Finding(rule['id'], get_line_num(m.start()), rule['risk'].upper(), content, 0.9))
        
        for rule in self.engine.legacy_rules:
            if do_force or not self.engine.rules[rule['original_idx']].get('keywords') or rule['original_idx'] in triggered_indices:
                for m in self.engine.run_safe_legacy_match(rule['regex'], cleaned_text):
                    content = m.group(1) if m.groups() else m.group(0)
                    all_findings.append(Finding(rule['id'], get_line_num(m.start()), rule['risk'].upper(), content, 0.8))

        # 2. Contextual rules
        for regex in self.context_rules:
            for m in regex.finditer(cleaned_text):
                all_findings.append(Finding("Contextual Secret (LLM Prompt)", get_line_num(m.start()), "MEDIUM", m.group(1), 0.6))

        # 3. Entropy Detection
        lines = cleaned_text.splitlines()
        for i, line in enumerate(lines, 1):
            line_findings = self.engine.run_entropy_detection(line, i, all_findings)
            all_findings.extend(line_findings)

        return all_findings

    def format_report(self, findings: List[Finding]) -> str:
        if not findings: return "✅ No secrets detected."
        
        # Sort and deduplicate findings
        # If multiple rules hit exactly same location/content, take highest confidence
        unique = {}
        for f in findings:
            key = (f.location, f.content)
            if key not in unique or f.confidence > unique[key].confidence:
                unique[key] = f
        
        final = sorted(unique.values(), key=lambda x: (x.location, x.secret_type))
        
        counts = {}
        for f in final: counts[f.risk] = counts.get(f.risk, 0) + 1
        
        report = f"⚠ Secrets detected: {len(final)}\n"
        for risk in sorted(counts.keys()):
            report += f"- {risk}: {counts[risk]}\n"
        report += "\n"
        
        for f in final:
            # Better redaction: keep prefix/suffix, hide middle
            c = f.content
            if len(c) > 12:
                redacted = f"{c[:4]}...{c[-4:]}"
            elif len(c) > 4:
                redacted = f"{c[0]}...{c[-1]}"
            else:
                redacted = "****"
            
            report += f"Type: {f.secret_type}\n"
            report += f"Location: line {f.location}\n"
            report += f"Risk: {f.risk}\n"
            report += f"Content: {redacted} (redacted)\n\n"
            
        return report.strip()

if __name__ == "__main__":
    detector = SecretDetector()
    print(detector.format_report(detector.scan("sk-1234567890abcdef1234567890abcdef")))
