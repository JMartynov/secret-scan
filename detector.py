import bisect
import json
import math
import os
import signal
from typing import Any, Dict, Iterator, List, Optional

import ahocorasick
import re2
import regex as standard_re

from report import Finding, format_report

# Design rule #4: Limit input size for single-block scanning
MAX_BLOCK_SIZE = 100_000

class TimeoutError(Exception):
    """Exception raised when a regex match exceeds the allowed time limit."""
    pass

def timeout_handler(signum, frame):
    """Signal handler that raises TimeoutError to interrupt slow operations."""
    raise TimeoutError()

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
        """
        Loads all scanning rules from the data directory, including categorized subdirectories.
        Ensures backward compatibility with a root rules.json.
        """
        all_rules = []
        if not os.path.exists(data_dir):
            return []

        # Check root rules.json for backward compatibility
        root_rules_path = os.path.join(data_dir, 'rules.json')
        if os.path.exists(root_rules_path):
            try:
                with open(root_rules_path, 'r', encoding='utf-8') as f:
                    all_rules.extend(json.load(f))
            except Exception:
                # Ignore malformed root rules files
                pass

        # Load taxonomy rules from subdirectories
        for root, dirs, files in os.walk(data_dir):
            if root == data_dir:
                # Skip root as it was handled above for legacy support
                continue
            for file in files:
                if file == 'rules.json':
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            rules = json.load(f)
                            for r in rules:
                                # Standardize category based on directory structure
                                r['category'] = os.path.basename(root)
                                all_rules.append(r)
                    except Exception:
                        # Ignore malformed rule files to prevent engine crash
                        pass
        return all_rules

    def _initialize_rules(self):
        """
        Compiles regex patterns and builds the Aho-Corasick automaton for keyword filtering.
        Prefers RE2 engine for safety against ReDoS.
        """
        for idx, rule in enumerate(self.rules):
            # Support new schema defaults
            rule.setdefault('engine', 're2')
            rule.setdefault('severity', rule.get('risk', 'medium').lower())
            rule.setdefault('confidence', 'medium')

            # If original rules had 'entropy' field, use it as 'min_entropy'
            # but apply a leniency factor (defaults to 0.7 for backward compatibility,
            # but can be tuned per-rule in the schema).
            orig_entropy = rule.get('entropy')
            entropy_factor = rule.get('entropy_factor', 0.7)
            if orig_entropy:
                rule.setdefault('min_entropy', float(orig_entropy) * entropy_factor)
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
            if not regex_str:
                continue

            if engine_type == 're2':
                try:
                    compiled = re2.compile(regex_str)
                    self.re2_rules.append({'id': rule['id'], 'severity': rule['severity'], 'regex': compiled, 'original_idx': idx})
                except Exception:
                    # Fallback to legacy if re2 fails (e.g. unsupported syntax)
                    engine_type = 'legacy'

            if engine_type == 'legacy':
                try:
                    compiled = standard_re.compile(regex_str, standard_re.DOTALL | standard_re.MULTILINE)
                    self.legacy_rules.append({'id': rule['id'], 'severity': rule['severity'], 'regex': compiled, 'original_idx': idx})
                except Exception:
                    continue
        self.automaton.make_automaton()

    def calculate_entropy(self, data: str) -> float:
        """Calculates Shannon entropy to identify high-randomness tokens (likely secrets)."""
        if not data:
            return 0.0
        counts = {}
        for char in data:
            counts[char] = counts.get(char, 0) + 1
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
        """
        Executes a legacy regex match with a strict timeout to prevent ReDoS attacks.
        Legacy patterns may use features not supported by the linear-time RE2 engine.
        """
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1)
            try:
                return list(regex.finditer(text))
            finally:
                # Always clear the alarm to avoid interrupting subsequent operations
                signal.alarm(0)
        except Exception:
            # Fallback for systems without SIGALRM or on timeout/error
            return []

    def run_entropy_detection(self, line: str, line_num: int, existing_findings: List[Finding], line_offset: int = 0) -> List[Finding]:
        """
        Identifies high-entropy strings that may be secrets but aren't caught by regex rules.
        """
        findings = []
        for match in standard_re.finditer(r"\b[a-zA-Z0-9]{20,}\b", line):
            token = match.group(0)
            # Skip tokens already identified by structured rules to avoid duplication
            if any(token in f.content for f in existing_findings):
                continue

            entropy = self.calculate_entropy(token)
            threshold = self.get_default_threshold(token)

            if entropy > threshold:
                start = line_offset + match.start()
                end = line_offset + match.end()
                # Use contextual heuristics to boost confidence for generic entropy hits
                if standard_re.search(r"(?i)(key|secret|token|password|auth|api|cred|prod)", line):
                    findings.append(Finding("Potential Secret (High Entropy + Context)", line_num, "HIGH", token, 0.7, start, end, "entropy"))
                else:
                    findings.append(Finding("High Entropy String", line_num, "MEDIUM", token, 0.3, start, end, "entropy"))
        return findings

class SecretDetector:
    """
    Main entry point for secret detection. Manages the detection engine and additional
    contextual/LLM-style heuristic rules.
    """
    def __init__(self, entropy_threshold: float = 4.0, data_dir: str = 'data', force_scan_all: bool = False):
        self.engine = DetectionEngine(entropy_threshold, data_dir)
        self.force_scan_all = force_scan_all
        # Lightweight rules to catch common secret-declaring patterns
        self.context_rules = [
            re2.compile(r"(?is)(?:my|here is|prod|our).*?(?:api|token|secret|password|key)\s*[:=]\s*(\S+)"),
            re2.compile(r"(?is)(?:api|access|auth).*?(?:key|token|secret)\s*[:=]\s*(\S+)")
        ]

    def _scan_block(self, text: str, base_line: int, force_scan_all: bool) -> List[Finding]:
        """
        Analyzes a block of text for potential secrets using regex, context, and entropy.
        """
        if not text:
            return []

        # Sanitize text to handle surrogate escapes (common in binary data or malformed UTF-8)
        # re2 (google-re2) fails if the string contains surrogates that cannot be encoded as UTF-8.
        try:
            # We encode to utf-8 with 'replace' to get rid of surrogates and then decode back.
            # This ensures 'text' is a valid UTF-8 string that re2 can handle.
            text = text.encode('utf-8', errors='replace').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Extremely rare fallback
            pass

        # Line number tracking within the block for efficient mapping
        line_offsets = [0]
        for match in standard_re.finditer(r"\n", text):
            line_offsets.append(match.end())

        def get_line_num(pos):
            """Converts absolute byte position to a 1-based line number."""
            idx = bisect.bisect_right(line_offsets, pos)
            return base_line + max(0, idx - 1)

        all_findings = []
        triggered_indices = set()
        if not force_scan_all:
            # Optimize by only running rules whose keywords are present in the text
            found_keywords = {original_value for _, original_value in self.engine.automaton.iter(text.lower())}
            for kw in found_keywords:
                triggered_indices.update(self.engine.keyword_map.get(kw, []))

        # Helper to extract the best content from a match
        def extract_content(m):
            # If group(1) is available and not empty, use it (standard convention)
            if m.groups() and m.group(1):
                return m.group(1)
            # Otherwise, find the largest non-empty capture group
            best_group = m.group(0)
            if m.groups():
                for i in range(1, len(m.groups()) + 1):
                    g = m.group(i)
                    if g and len(g) > len(best_group) * 0.5: # Heuristic: group must be significant
                        best_group = g
            return best_group or ""

        # 1. Regex Matching (RE2 - Linear Time)
        for rule in self.engine.re2_rules:
            rule_def = self.engine.rules[rule['original_idx']]
            if force_scan_all or not rule_def.get('keywords') or rule['original_idx'] in triggered_indices:
                for m in rule['regex'].finditer(text):
                    content = extract_content(m)
                    # Optional entropy filter to reduce false positives on short/static strings
                    if rule_def.get('entropy_required'):
                        if self.engine.calculate_entropy(content) < rule_def.get('min_entropy', 3.0):
                            continue

                    line_num = get_line_num(m.start())
                    # Extract line content for contextual scoring
                    line_start = line_offsets[max(0, bisect.bisect_right(line_offsets, m.start()) - 1)]
                    line_end = text.find('\n', m.start())
                    if line_end == -1:
                        line_end = len(text)
                    line_content = text[line_start:line_end]

                    confidence = self.engine.calculate_confidence(0.8, line_content, rule_def)
                    all_findings.append(Finding(rule['id'], line_num, rule['severity'].upper(), content, confidence, m.start(), m.end(), rule_def.get('category', 'generic')))

        # 2. Regex Matching (Legacy - Fallback with timeout)
        for rule in self.engine.legacy_rules:
            rule_def = self.engine.rules[rule['original_idx']]
            if force_scan_all or not rule_def.get('keywords') or rule['original_idx'] in triggered_indices:
                for m in self.engine.run_safe_legacy_match(rule['regex'], text):
                    content = extract_content(m)
                    if rule_def.get('entropy_required'):
                        if self.engine.calculate_entropy(content) < rule_def.get('min_entropy', 3.0):
                            continue

                    line_num = get_line_num(m.start())
                    line_start = line_offsets[max(0, bisect.bisect_right(line_offsets, m.start()) - 1)]
                    line_end = text.find('\n', m.start())
                    if line_end == -1:
                        line_end = len(text)
                    line_content = text[line_start:line_end]

                    confidence = self.engine.calculate_confidence(0.7, line_content, rule_def)
                    all_findings.append(Finding(rule['id'], line_num, rule['severity'].upper(), content, confidence, m.start(), m.end(), rule_def.get('category', 'generic')))

        # 2. Contextual rules (Heuristic matches for likely secret declarations)
        for regex in self.context_rules:
            for m in regex.finditer(text):
                secret = m.group(1) or ""
                all_findings.append(Finding("Contextual Secret (LLM Prompt)", get_line_num(m.start()), "MEDIUM", secret, 0.6, m.start(), m.end(), "authentication"))

        # 3. Entropy Detection (Generic catch-all)
        for i, start in enumerate(line_offsets):
            end = line_offsets[i+1] if i+1 < len(line_offsets) else len(text)
            line = text[start:end].rstrip('\r\n')
            line_findings = self.engine.run_entropy_detection(line, base_line + i, all_findings, start)
            all_findings.extend(line_findings)

        return self._resolve_overlaps(all_findings)

    def _resolve_overlaps(self, findings: List[Finding]) -> List[Finding]:
        """
        Resolves overlapping findings by favoring the longest match and highest confidence.
        """
        if not findings:
            return []

        # Sort by start (asc) then length (desc) then confidence (desc)
        sorted_findings = sorted(findings, key=lambda f: (f.start, -(f.end - f.start), -f.confidence))

        resolved = []
        current = sorted_findings[0]

        for i in range(1, len(sorted_findings)):
            next_f = sorted_findings[i]

            # If they overlap
            if next_f.start < current.end:
                # Compare "weight": length * confidence
                current_weight = (current.end - current.start) * current.confidence
                next_weight = (next_f.end - next_f.start) * next_f.confidence

                # Heuristic 1: Boost structured rules over generic entropy hits
                if "Entropy" in current.secret_type and "Entropy" not in next_f.secret_type:
                    next_weight *= 2.0
                elif "Entropy" not in current.secret_type and "Entropy" in next_f.secret_type:
                    current_weight *= 2.0

                # Heuristic 2: Penalize "generic", "common", or "Contextual" rules over specific ones
                is_curr_generic = any(x in current.secret_type.lower() for x in ["generic", "common", "contextual"])
                is_next_generic = any(x in next_f.secret_type.lower() for x in ["generic", "common", "contextual"])

                # Prefer explicit secrets when overlapping with generic heuristics
                if is_curr_generic and not is_next_generic:
                    current = next_f
                    continue

                if is_curr_generic and not is_next_generic:
                    next_weight *= 2.0
                elif not is_curr_generic and is_next_generic:
                    current_weight *= 2.0

                if next_weight > current_weight:
                    current = next_f
            else:
                resolved.append(current)
                current = next_f

        resolved.append(current)
        return resolved

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
