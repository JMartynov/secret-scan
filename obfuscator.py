import base64
import hashlib
import urllib.parse
from typing import List

from faker import Faker

from report import Finding

"""
This module provides the Obfuscator class, which is used to redact, hash, or
replace secrets in a given text.
"""

class Obfuscator:
    """
    Obfuscates secrets in a line of text, based on a list of findings.
    Provides multiple modes: redact, hash, and synthetic.
    """
    def __init__(self, mode: str = "redact"):
        self.mode = mode
        self.secret_map = {}  # Cache for consistent hashing of the same secret
        self.fake = Faker()
        self._registry = self._initialize_registry()

    def _initialize_registry(self):
        """Initializes the dynamic registry for synthetic data generation."""
        # Dispatcher map: regex pattern -> generator function
        # Order matters: more specific patterns first
        return [
            (r"slack", lambda length: "xoxb-" + self.fake.bothify(text="############-############-????????????????", letters="abcdefghijklmnopqrstuvwxyz0123456789")),
            (r"github", lambda length: "ght_" + self.fake.password(length=36, special_chars=False)),
            (r"stripe.*publishable", lambda length: "pk_test_" + self.fake.bothify(text="????????????????????????", letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")),
            (r"stripe", lambda length: "sk_test_" + self.fake.bothify(text="????????????????????????", letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")),
            (r"aws.*id", lambda length: "AKIA" + self.fake.bothify(text="????????????????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")),
            (r"aws", lambda length: self.fake.password(length=length, special_chars=True)),
            (r"cloud", lambda length: self.fake.password(length=length, special_chars=True)),
            (r"mongo", lambda length: self.fake.password(length=length, special_chars=True)),
            (r"database|db", lambda length: self.fake.password(length=length, special_chars=True)),
            (r"sendgrid", lambda length: "SG." + self.fake.bothify(text="??????????????????????", letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") + "." + self.fake.bothify(text="???????????????????????????????????????????", letters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")),
            (r"twilio.*sid", lambda length: "AC" + self.fake.hexify(text="^" * 32)),
            (r"twilio", lambda length: self.fake.hexify(text="^" * 32)),
            (r"private.*key|ssh", lambda length: "-----BEGIN PRIVATE KEY-----\n" + self.fake.text(max_nb_chars=length) + "\n-----END PRIVATE KEY-----"),
            (r"email", lambda length: self.fake.email()),
            (r"password", lambda length: self.fake.password(length=length)),
            (r"secret", lambda length: self.fake.password(length=length)),
            (r"auth", lambda length: self.fake.password(length=length)),
            (r"bearer", lambda length: self.fake.password(length=length, special_chars=False, digits=True, upper_case=True, lower_case=True)),
            (r"token", lambda length: self.fake.password(length=length, special_chars=False)),
            (r"api.*key", lambda length: self.fake.password(length=length, special_chars=False)),
        ]

    def decode_if_encoded(self, content: str) -> str:
        """
        Attempts to decode base64, hex, or url-encoded content to reveal the underlying secret.
        """
        # 1. URL Decoding
        decoded = urllib.parse.unquote(content)
        if decoded != content:
            return decoded

        # 2. Base64 Decoding
        try:
            return base64.b64decode(content).decode('utf-8')
        except Exception:
            # Not valid base64 or not UTF-8 content
            pass

        # 3. Hex Decoding
        try:
            return bytes.fromhex(content).decode('utf-8')
        except Exception:
            # Not valid hex
            pass

        return content

    def _generate_synthetic(self, category: str, secret_type: str, original_length: int) -> str:
        """Generates realistic-looking fake data based on category and secret type."""
        # Normalize for matching: replace separators with spaces
        combined = f"{category} {secret_type}".lower().replace("-", " ").replace("_", " ")

        import re
        for pattern, generator in self._registry:
            if re.search(pattern, combined):
                return generator(original_length)

        return self.fake.hexify(text="^" * original_length)

    def obfuscate_content(self, content: str, secret_type: str, category: str = "generic") -> str:
        """
        Applies the configured obfuscation mode to a single secret's content.
        """
        # Optionally decode before obfuscating if needed,
        # but usually we obfuscate the literal match.

        if self.mode == "redact":
            if len(content) > 12:
                return f"{content[:4]}...{content[-4:]}"
            elif len(content) > 4:
                return f"{content[0]}...{content[-1]}"
            else:
                return "****"
        elif self.mode == "hash":
            if content not in self.secret_map:
                self.secret_map[content] = hashlib.sha256(content.encode()).hexdigest()[:12]
            return f"[HASHED_{self.secret_map[content]}]"
        elif self.mode == "synthetic":
            if content.upper().startswith("AKIA") and len(content) > 4:
                suffix_length = len(content) - 4
                suffix = self.fake.bothify(text="?" * suffix_length, letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                return "AKIA" + suffix
            return self._generate_synthetic(category, secret_type, len(content))
        else:
            return f"[REDACTED_{secret_type.replace(' ', '_').upper()}]"

    def obfuscate(self, text: str, findings: List[Finding]) -> str:
        """
        Obfuscates a single line of text based on the provided findings.

        It sorts findings to handle overlaps, prioritizing longer matches.
        It then iterates through the findings in reverse and replaces the
        secrets in the text without corrupting character offsets.

        :param text: The line of text to obfuscate.
        :param findings: A list of Finding objects for the given line.
        :return: The obfuscated line.
        """
        # Deduplicate and sort findings by start offset in reverse
        # If findings overlap, we should take the union or just the first/longest one.
        # For simplicity, let's sort by start (desc) then by end (desc for longest first)
        sorted_findings = sorted(findings, key=lambda f: (f.start, f.end), reverse=True)

        result = text
        last_start = len(text) + 1

        for f in sorted_findings:
            if f.start < 0 or f.end < 0:
                continue

            # Skip overlapping findings (since we are going backwards)
            if f.end > last_start:
                continue

            obfuscated = self.obfuscate_content(f.content, f.secret_type, f.category)
            result = result[:f.start] + obfuscated + result[f.end:]
            last_start = f.start

        return result

# I need to update Finding to include offsets (start, end) within the block/file.
