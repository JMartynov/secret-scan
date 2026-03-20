import hashlib
import re
from typing import List, Dict, Any, Optional
from faker import Faker
from report import Finding

"""
This module provides the Obfuscator class, which is used to redact, hash, or
replace secrets in a given text.
"""

class Obfuscator:
    """
    Obfuscates secrets in a line of text, based on a list of findings.
    """
    def __init__(self, mode: str = "redact"):
        self.mode = mode
        self.secret_map = {} # For consistent hashing
        self.fake = Faker()
        # Seed for reproducibility if needed, but for obfuscation randomness is usually fine.
        # self.fake.seed_instance(42)

    def _generate_synthetic(self, secret_type: str, original_length: int) -> str:
        """Generates realistic-looking fake data based on the secret type."""
        st = secret_type.lower()
        
        if "aws_api_id" in st:
            return "AKIA" + self.fake.bothify(text="????????????????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        elif "aws_api_secret" in st:
            return self.fake.password(length=40, special_chars=True, digits=True, upper_case=True, lower_case=True)
        elif "github_token" in st:
            return "ghp_" + self.fake.password(length=36, special_chars=False)
        elif "slack" in st:
            if "token" in st:
                return "xoxb-" + self.fake.bothify(text="############-############-????????????????", letters="abcdefghijklmnopqrstuvwxyz0123456789")
        elif "email" in st:
            return self.fake.email()
        elif "password" in st or "secret" in st:
            return self.fake.password(length=original_length)
        elif "api_key" in st or "token" in st:
            return self.fake.password(length=original_length, special_chars=False)
        
        # Fallback to a generic but realistic-looking hex/alphanumeric string
        return self.fake.hexify(text="^" * original_length)

    def obfuscate_content(self, content: str, secret_type: str) -> str:
        """
        Applies the configured obfuscation mode to a single secret's content.

        :param content: The secret content to obfuscate.
        :param secret_type: The type of secret, used for synthetic data generation.
        :return: The obfuscated string.
        """
        if self.mode == "redact":
            if len(content) > 12:
                return f"{content[:4]}...{content[-4:]}"
            elif len(content) > 4:
                return f"{content[0]}...{content[-1]}"
            else:
                return "****"
        elif self.mode == "hash":
            if content not in self.secret_map:
                # Use a short hash for readability but keep it unique
                self.secret_map[content] = hashlib.sha256(content.encode()).hexdigest()[:12]
            return f"[HASHED_{self.secret_map[content]}]"
        elif self.mode == "synthetic":
            return self._generate_synthetic(secret_type, len(content))
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
            
            obfuscated = self.obfuscate_content(f.content, f.secret_type)
            result = result[:f.start] + obfuscated + result[f.end:]
            last_start = f.start
            
        return result

# I need to update Finding to include offsets (start, end) within the block/file.
