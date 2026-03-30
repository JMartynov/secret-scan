import json
import os
import sys
from typing import Any, Dict, List, Optional

from redoctor import check
from ruamel.yaml import YAML


def _load_all_rules(data_dir: str) -> List[Dict[str, Any]]:
    """
    Loads all scanning rules from the data directory, including categorized subdirectories.
    Supports both JSON (.json) and YAML (.yml, .yaml) rule files.
    """
    all_rules = []
    if not os.path.exists(data_dir):
        return []

    yaml = YAML(typ='safe')

    def load_rules_from_file(path: str, category: Optional[str] = None):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.json'):
                    rules = json.load(f)
                else:
                    rules = yaml.load(f)
                
                if isinstance(rules, list):
                    for r in rules:
                        if category:
                            r['category'] = category
                    all_rules.extend(rules)
        except Exception:
            pass  # Ignore malformed rule files

    # Handle root files for backward compatibility
    for ext in ['rules.json', 'rules.yml', 'rules.yaml']:
        root_rules_path = os.path.join(data_dir, ext)
        if os.path.exists(root_rules_path):
            load_rules_from_file(root_rules_path)

    # Load rules from subdirectories
    for root, dirs, files in os.walk(data_dir):
        if root == data_dir:
            continue
        
        category = os.path.basename(root)
        for file in files:
            if file in ['rules.json', 'rules.yml', 'rules.yaml']:
                load_rules_from_file(os.path.join(root, file), category)
    
    return all_rules


def main():
    rules = _load_all_rules('data')
    if not rules:
        print("No rules found.")
        sys.exit(0)

    print(f"Scanning {len(rules)} rules for ReDoS using redoctor library...
")

    vulnerable_rules = []

    for rule in rules:
        try:
            pattern = rule['regex']
            # Clean (?i) prefix as redoctor might not support it in static check
            clean_pattern = pattern
            if pattern.startswith('(?i)'):
                clean_pattern = pattern[4:]

            result = check(clean_pattern)
            if result.is_vulnerable:
                vulnerable_rules.append((rule['id'], pattern, result.complexity, result.attack))
        except Exception:
            pass

    if vulnerable_rules:
        print("--- Vulnerable Rules Found by Redoctor ---")
        for rid, pattern, complexity, attack in vulnerable_rules:
            print(f"Rule: {rid}")
            print(f"  [!] Pattern: {pattern}")
            print(f"  [!] Complexity: {complexity}")
            print(f"  [!] Attack string: {attack}")
            print()
        print(f"Found {len(vulnerable_rules)} vulnerable rules.")
    else:
        print("No ReDoS issues found by redoctor!")

if __name__ == '__main__':
    main()
