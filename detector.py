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
    def __init__(self, entropy_threshold: float = 4.0, data_dir: str = 'data'):
        self.entropy_threshold = entropy_threshold
        self.rules = self._load_all_rules(data_dir)
        self.keyword_map = {}
        self.automaton = ahocorasick.Automaton()
        self.re2_rules = []
        self.legacy_rules = []
        self._initialize_rules()

    def _load_all_rules(self, data_dir: str) -> List[Dict[str, Any]]:
        all_rules = []
        if not os.path.exists(data_dir):
            return []
            
        # Check root rules.json for backward compatibility
        root_rules_path = os.path.join(data_dir, 'rules.json')
        if os.path.exists(root_rules_path):
            try:
                with open(root_rules_path, 'r', encoding='utf-8') as f:
                    all_rules.extend(json.load(f))
            except Exception: pass

        # Load taxonomy rules
        for root, dirs, files in os.walk(data_dir):
            if root == data_dir: continue # Skip root handled above
            for file in files:
                if file == 'rules.json':
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            rules = json.load(f)
                            for r in rules:
                                # Override category based on directory for consistency
                                r['category'] = os.path.basename(root)
                                all_rules.append(r)
                    except Exception: pass
        return all_rules

    def _initialize_rules(self):
        for idx, rule in enumerate(self.rules):
            # Support new schema defaults
            rule.setdefault('engine', 're2')
            rule.setdefault('severity', rule.get('risk', 'medium').lower())
            rule.setdefault('confidence', 'medium')
            
            # If original rules had 'entropy' field, use it as 'min_entropy'
            # but be slightly more lenient (0.7 factor) as it was previously used.
            orig_entropy = rule.get('entropy')
            if orig_entropy:
                rule.setdefault('min_entropy', float(orig_entropy) * 0.7)
                rule.setdefault('entropy_required', True)
            else:
                rule.setdefault('min_entropy', 3.0)
                rule.setdefault('entropy_required', False)

            for kw in (rule.get('keywords') or []):
                kw = kw.lower()
                if kw not in self.keyword_map:
                    self.keyword_map[kw] = []
                    self.automaton.add_word(kw, kw)
                self.keyword_map[kw].append(idx)
            
            # Choose engine based on schema or fallback
            engine_type = rule.get('engine', 're2').lower()
            regex_str = rule.get('regex') or rule.get('pattern')
            if not regex_str: continue

            if engine_type == 're2':
                try:
                    compiled = re2.compile(regex_str)
                    self.re2_rules.append({'id': rule['id'], 'severity': rule['severity'], 'regex': compiled, 'original_idx': idx})
                except Exception:
                    # Fallback to legacy if re2 fails
                    engine_type = 'legacy'
            
            if engine_type == 'legacy':
                try:
                    compiled = standard_re.compile(regex_str, standard_re.DOTALL | standard_re.MULTILINE)
                    self.legacy_rules.append({'id': rule['id'], 'severity': rule['severity'], 'regex': compiled, 'original_idx': idx})
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

    def get_default_threshold(self, data: str) -> float:
        """Determines the entropy threshold based on the character set of the data."""
        if all(c in '0123456789abcdefABCDEF' for c in data):
            return 3.0 # Hex threshold
        if all(c in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/=' for c in data):
            return 4.0 # Base64 threshold
        return 4.0 # Alphanumeric/Generic threshold

    def calculate_confidence(self, base_score: float, line: str, rule: Dict[str, Any]) -> float:
        """Calculates a contextual confidence score based on keywords near the match."""
        score = base_score
        line_lower = line.lower()
        
        # Boost confidence if specific keywords from the rule are present
        for kw in (rule.get('keywords') or []):
            if kw.lower() in line_lower:
                score = min(1.0, score + 0.1)
        
        # Suppress confidence if "false positive" indicators are present
        suppress_keywords = ['example', 'test', 'dummy', 'localhost', 'sample', 'placeholder']
        for skw in suppress_keywords:
            if skw in line_lower:
                score = max(0.1, score - 0.3)
                
        return round(score, 2)

    def run_safe_legacy_match(self, regex, text):
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1)
            try: return list(regex.finditer(text))
            finally: signal.alarm(0)
        except Exception: return []

    def run_entropy_detection(self, line: str, line_num: int, existing_findings: List[Finding], line_offset: int = 0) -> List[Finding]:
        findings = []
        for match in standard_re.finditer(r"\b[a-zA-Z0-9]{20,}\b", line):
            token = match.group(0)
            if any(token in f.content for f in existing_findings): continue
            
            entropy = self.calculate_entropy(token)
            threshold = self.get_default_threshold(token)
            
            if entropy > threshold:
                start = line_offset + match.start()
                end = line_offset + match.end()
                # Use contextual heuristics for boosting
                if standard_re.search(r"(?i)(key|secret|token|password|auth|api|cred|prod)", line):
                    findings.append(Finding("Potential Secret (High Entropy + Context)", line_num, "HIGH", token, 0.7, start, end))
                else:
                    findings.append(Finding("High Entropy String", line_num, "MEDIUM", token, 0.3, start, end))
        return findings

class SecretDetector:
    def __init__(self, entropy_threshold: float = 4.0, data_dir: str = 'data', force_scan_all: bool = False):
        self.engine = DetectionEngine(entropy_threshold, data_dir)
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
            
        # 1. Regex Matching (RE2)
        for rule in self.engine.re2_rules:
            rule_def = self.engine.rules[rule['original_idx']]
            if force_scan_all or not rule_def.get('keywords') or rule['original_idx'] in triggered_indices:
                for m in rule['regex'].finditer(text):
                    content = (m.group(1) if m.groups() else m.group(0)) or ""
                    if rule_def.get('entropy_required'):
                        if self.engine.calculate_entropy(content) < rule_def.get('min_entropy', 3.0):
                            continue
                    
                    line_num = get_line_num(m.start())
                    # Extract line content for contextual scoring
                    line_start = line_offsets[max(0, bisect.bisect_right(line_offsets, m.start()) - 1)]
                    line_end = text.find('\n', m.start())
                    if line_end == -1: line_end = len(text)
                    line_content = text[line_start:line_end]
                    
                    confidence = self.engine.calculate_confidence(0.8, line_content, rule_def)
                    all_findings.append(Finding(rule['id'], line_num, rule['severity'].upper(), content, confidence, m.start(), m.end()))
        
        # 2. Regex Matching (Legacy)
        for rule in self.engine.legacy_rules:
            rule_def = self.engine.rules[rule['original_idx']]
            if force_scan_all or not rule_def.get('keywords') or rule['original_idx'] in triggered_indices:
                for m in self.engine.run_safe_legacy_match(rule['regex'], text):
                    content = (m.group(1) if m.groups() else m.group(0)) or ""
                    if rule_def.get('entropy_required'):
                        if self.engine.calculate_entropy(content) < rule_def.get('min_entropy', 3.0):
                            continue
                    
                    line_num = get_line_num(m.start())
                    line_start = line_offsets[max(0, bisect.bisect_right(line_offsets, m.start()) - 1)]
                    line_end = text.find('\n', m.start())
                    if line_end == -1: line_end = len(text)
                    line_content = text[line_start:line_end]

                    confidence = self.engine.calculate_confidence(0.7, line_content, rule_def)
                    all_findings.append(Finding(rule['id'], line_num, rule['severity'].upper(), content, confidence, m.start(), m.end()))

        # 2. Contextual rules
        for regex in self.context_rules:
            for m in regex.finditer(text):
                secret = m.group(1) or ""
                all_findings.append(Finding("Contextual Secret (LLM Prompt)", get_line_num(m.start()), "MEDIUM", secret, 0.6, m.start(), m.end()))

        # 3. Entropy Detection
        for i, start in enumerate(line_offsets):
            end = line_offsets[i+1] if i+1 < len(line_offsets) else len(text)
            line = text[start:end].rstrip('\r\n')
            line_findings = self.engine.run_entropy_detection(line, base_line + i, all_findings, start)
            all_findings.extend(line_findings)

        return all_findings

    def scan(self, text: str, force_scan_all: Optional[bool] = None) -> List[Finding]:
        do_force = force_scan_all if force_scan_all is not None else self.force_scan_all
        cleaned_text = text[:MAX_BLOCK_SIZE]
        return self._scan_block(cleaned_text, 1, do_force)

    def scan_stream(self, stream: Iterator[str], force_scan_all: Optional[bool] = None, yield_non_matches=False) -> Iterator[tuple[str, list[Finding]]]:
        """
        Scans a stream of text for secrets, line by line.

        :param stream: The stream to scan.
        :param force_scan_all: If True, scan all lines, otherwise use keyword search to speed up.
        :param yield_non_matches: If True, yield lines even if they don't have findings.
        """
        do_force = force_scan_all if force_scan_all is not None else self.force_scan_all
        for i, line in enumerate(stream):
            findings = self._scan_block(line, i + 1, do_force)
            if findings:
                yield (line, findings)
            elif yield_non_matches:
                yield (line, [])

    def format_report(self, findings: List[Finding], show_full: bool = False, show_short: bool = False, no_colors: bool = False) -> str:
        return format_report(findings, show_full, show_short, no_colors)

if __name__ == "__main__":
    detector = SecretDetector()
    print(detector.format_report(detector.scan("sk-1234567890abcdef1234567890abcdef")))
