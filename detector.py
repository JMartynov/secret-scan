import regex as re
import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Finding:
    secret_type: str
    location: int  # Line number (1-indexed)
    risk: str
    content: str
    confidence: float = 0.0

class DetectionEngine:
    # Common patterns for secret detection
    PATTERNS = {
        "OpenAI API Key": {
            "regex": r"sk-[a-zA-Z0-9]{20,}",
            "risk": "HIGH"
        },
        "AWS Access Key ID": {
            "regex": r"AKIA[0-9A-Z]{16}",
            "risk": "HIGH"
        },
        "AWS Secret Access Key": {
            "regex": r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?([a-zA-Z0-9/+=]{40})['\"]?",
            "risk": "CRITICAL"
        },
        "GitHub Personal Access Token": {
            "regex": r"ghp_[a-zA-Z0-9]{36,}",
            "risk": "HIGH"
        },
        "Azure API Key": {
            "regex": r"(?i)azure[a-z0-9_]*key\s*[:=]\s*['\"]?([a-zA-Z0-9]{32,})['\"]?",
            "risk": "HIGH"
        },
        "Google API Key": {
            "regex": r"AIza[0-9A-Za-z-_]{35}",
            "risk": "HIGH"
        },
        "Database Credentials": {
            "regex": r"(postgres|mysql|mongodb|redis)://[a-zA-Z0-9_.-]+:[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+:[0-9]+",
            "risk": "CRITICAL"
        },
        "Generic Private Key": {
            "regex": r"-----BEGIN [A-Z ]+ PRIVATE KEY-----",
            "risk": "CRITICAL"
        },
        "JWT Token": {
            "regex": r"ey[a-zA-Z0-9_-]{10,}\.ey[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}",
            "risk": "MEDIUM"
        }
    }

    def __init__(self, entropy_threshold: float = 3.5):
        self.entropy_threshold = entropy_threshold

    def calculate_entropy(self, data: str) -> float:
        """Calculates Shannon entropy of a string."""
        if not data:
            return 0.0
        entropy = 0
        for x in range(256):
            p_x = data.count(chr(x)) / len(data)
            if p_x > 0:
                entropy += -p_x * math.log(p_x, 2)
        return entropy

    def run_regex_matching(self, line: str, line_num: int) -> List[Finding]:
        findings = []
        for name, pattern_info in self.PATTERNS.items():
            matches = re.finditer(pattern_info["regex"], line)
            for match in matches:
                findings.append(Finding(
                    secret_type=name,
                    location=line_num,
                    risk=pattern_info["risk"],
                    content=match.group(0),
                    confidence=0.9
                ))
        return findings

    def run_entropy_detection(self, line: str, line_num: int, existing_findings: List[Finding]) -> List[Finding]:
        findings = []
        potential_tokens = re.finditer(r"\b[a-zA-Z0-9]{16,}\b", line)
        for match in potential_tokens:
            token = match.group(0)
            # Skip if this token is already part of a regex match
            if any(token in f.content for f in existing_findings):
                continue

            entropy = self.calculate_entropy(token)
            if entropy > self.entropy_threshold:
                findings.append(Finding(
                    secret_type="High Entropy String",
                    location=line_num,
                    risk="MEDIUM",
                    content=token,
                    confidence=0.5
                ))
        return findings

    def apply_context_analysis(self, line: str, finding: Finding) -> Finding:
        # Context check: look for words like 'secret', 'key', 'token' nearby
        if re.search(r"(?i)(key|secret|token|password|cred|auth|api)", line):
            if finding.secret_type == "High Entropy String":
                finding.secret_type = "Potential Secret (Context Match)"
                finding.risk = "HIGH"
                finding.confidence = 0.8
            else:
                # Boost confidence for regex findings if context matches
                finding.confidence = min(finding.confidence + 0.1, 1.0)
        return finding

class PreprocessingLayer:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        # Basic text cleaning: strip trailing whitespace, etc.
        # Could also handle base64 decoding, URL decoding, etc. in future
        return text.strip()

    def identify_format(self, text: str) -> str:
        # Identify if it's JSON, YAML, etc. (for better line number tracking in future)
        if text.startswith("{") and text.endswith("}"):
            return "JSON"
        if "---" in text:
            return "YAML"
        return "TEXT"

class SecurityReport:
    def __init__(self, findings: List[Finding]):
        self.findings = findings

    def generate_summary(self) -> str:
        if not self.findings:
            return "✅ No secrets detected."
        
        counts = {}
        for f in self.findings:
            counts[f.risk] = counts.get(f.risk, 0) + 1
        
        summary = f"⚠ Secrets detected: {len(self.findings)}\n"
        for risk, count in counts.items():
            summary += f"- {risk}: {count}\n"
        return summary

    def format_full_report(self) -> str:
        if not self.findings:
            return "✅ No secrets detected."
        
        report = self.generate_summary() + "\n"
        for f in self.findings:
            report += f"Type: {f.secret_type}\n"
            report += f"Location: line {f.location}\n"
            report += f"Risk: {f.risk}\n"
            report += f"Content: {f.content[:4]}...{f.content[-4:] if len(f.content) > 8 else ''} (redacted)\n"
            report += "\n"
        return report.strip()

class SecretDetector:
    def __init__(self, entropy_threshold: float = 3.5):
        self.preprocessor = PreprocessingLayer()
        self.engine = DetectionEngine(entropy_threshold)

    def classify_finding(self, finding: Finding) -> Finding:
        # Final classification step to adjust risk levels if needed
        # (e.g., tokens found in config files might be higher risk than in random chat messages)
        # For now, it's a simple pass-through but it's part of the architecture
        return finding

    def scan(self, text: str) -> List[Finding]:
        cleaned_text = self.preprocessor.clean_text(text)
        format_type = self.preprocessor.identify_format(cleaned_text)
        # In future, we could use format_type to use specialized parsers
        
        lines = cleaned_text.splitlines()
        all_findings = []

        for i, line in enumerate(lines, 1):
            line_findings = self.engine.run_regex_matching(line, i)
            entropy_findings = self.engine.run_entropy_detection(line, i, line_findings)
            
            for f in line_findings + entropy_findings:
                analyzed_finding = self.engine.apply_context_analysis(line, f)
                classified_finding = self.classify_finding(analyzed_finding)
                all_findings.append(classified_finding)

        return all_findings

    def format_report(self, findings: List[Finding]) -> str:
        report = SecurityReport(findings)
        return report.format_full_report()

if __name__ == "__main__":
    # Quick test
    detector = SecretDetector()
    test_text = """
    Here is my config:
    OPENAI_API_KEY=sk-abc1234567890abcdef123456
    DATABASE_URL=postgres://admin:password123@localhost:5432
    DEBUG=True
    MY_SECRET_TOKEN=xyz789randomStringWithHighEntropy123!
    """
    findings = detector.scan(test_text)
    print(detector.format_report(findings))
