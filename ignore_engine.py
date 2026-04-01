import os
import re
from typing import List, Set

class IgnoreEngine:
    def __init__(self):
        self.ignored_paths = self._load_secretscanignore()
        self.baseline_hashes: Set[str] = set()

    def _load_secretscanignore(self) -> List[re.Pattern]:
        patterns = []
        ignore_file = '.secretscanignore'
        if os.path.exists(ignore_file):
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    # Simple glob to regex conversion (basic support)
                    regex = line.replace('.', '\\.').replace('*', '.*').replace('?', '.')
                    patterns.append(re.compile(f"^{regex}$"))
        return patterns

    def is_ignored_path(self, filepath: str) -> bool:
        for pattern in self.ignored_paths:
            if pattern.match(filepath):
                return True
        return False

    def is_ignored_line(self, line: str, rule_id: str) -> bool:
        """
        Checks for inline comments like `# secretscan:ignore` or `// secretscan:ignore rule-id`
        """
        if "secretscan:ignore" not in line:
            return False

        # Check if specific rule is ignored
        match = re.search(r'secretscan:ignore\s+([a-zA-Z0-9_-]+)', line)
        if match:
            ignored_rule = match.group(1)
            if ignored_rule == rule_id:
                return True
            return False

        # Generic ignore
        return True

    def load_baseline(self, baseline_file: str):
        import json
        if os.path.exists(baseline_file):
            try:
                with open(baseline_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.baseline_hashes = set(data.get("ignored_hashes", []))
            except Exception:
                pass

    def is_in_baseline(self, content: str) -> bool:
        import hashlib
        hash_val = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return hash_val in self.baseline_hashes
