import json
import os
from pathlib import Path
from typing import Dict, List, Any

def test_no_duplicate_regex_patterns():
    """
    Validates that no rules across the entire taxonomy share the same regex pattern.
    Shared patterns should be merged using tools/deduplicate_rules.py.
    """
    data_dir = Path('data')
    if not data_dir.exists():
        return

    all_rules_by_regex: Dict[str, List[Dict[str, Any]]] = {}
    
    # 1. Collect all rules
    for root, dirs, files in os.walk(data_dir):
        if 'rules.json' in files:
            file_path = Path(root) / 'rules.json'
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                    category = os.path.basename(root)
                    for rule in rules:
                        regex = rule.get('regex') or rule.get('pattern')
                        if regex:
                            if regex not in all_rules_by_regex:
                                all_rules_by_regex[regex] = []
                            all_rules_by_regex[regex].append({
                                'id': rule.get('id'),
                                'file': str(file_path),
                                'category': category
                            })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # 2. Check for duplicates
    duplicates = []
    for regex, occurrences in all_rules_by_regex.items():
        if len(occurrences) > 1:
            duplicates.append({
                'regex': regex,
                'occurrences': occurrences
            })

    # 3. Assert no duplicates found
    if duplicates:
        error_msg = f"Found {len(duplicates)} duplicate regex patterns in taxonomy:\n"
        for d in duplicates:
            ids = [o['id'] for o in d['occurrences']]
            files = [o['file'] for o in d['occurrences']]
            error_msg += f"\n- Regex: {d['regex'][:100]}...\n"
            error_msg += f"  IDs: {ids}\n"
            error_msg += f"  Files: {files}\n"
        
        assert not duplicates, error_msg
