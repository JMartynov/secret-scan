import json
import os
import re
import sys
from pathlib import Path

def check_regex_safety(rule_id, pattern):
    issues = []

    # Rule 1(a): Nested repetition like (a+)+, (a*)*, (.+)+, (.*)*
    if re.search(r'\([^\)]+[\*\+]\)[\*\+]', pattern):
        issues.append(f"CRITICAL: Potential nested repetition (e.g., (a+)+) in: {pattern}")

    # Rule 1(b): Greedy wildcards .* should be restricted
    if re.search(r'\.[\*\+](?!\?)', pattern):
        if re.search(r'\.[\*\+].*\.[\*\+]', pattern):
             issues.append(f"WARNING: Multiple greedy wildcards may scan entire document: {pattern}")
        else:
             issues.append(f"ADVICE: Replace greedy wildcards with range-restricted search like '[^\\n]{{0,200}}': {pattern}")

    return issues

def check_schema_and_quality(rule):
    issues = []
    
    # Mandatory fields
    for field in ['id', 'regex', 'severity', 'category']:
        if field not in rule:
            issues.append(f"CRITICAL: Missing mandatory field '{field}'")
            
    # Keywords for performance
    if not rule.get('keywords'):
        issues.append("WARNING: No keywords defined. This rule will be slow as it runs on every block.")
        
    # Entropy factor validation
    ef = rule.get('entropy_factor')
    if ef is not None:
        try:
            val = float(ef)
            if val < 0.2:
                 issues.append(f"WARNING: Very low entropy_factor {val}. May cause many false positives if entropy is required.")
            if val > 1.5:
                 issues.append(f"WARNING: Very high entropy_factor {val}. May cause many false negatives.")
        except ValueError:
            issues.append(f"CRITICAL: entropy_factor '{ef}' is not a number")

    return issues

def main():
    data_dir = Path('data')
    all_rules = []
    
    # 1. Load all rules from taxonomy
    if not data_dir.exists():
        print("Data directory not found.")
        sys.exit(1)
        
    for root, dirs, files in os.walk(data_dir):
        if 'rules.json' in files:
            file_path = Path(root) / 'rules.json'
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                    for r in rules:
                        r['_file'] = str(file_path)
                        all_rules.append(r)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    if not all_rules:
        print("No rules found to lint.")
        sys.exit(0)

    print(f"Linting {len(all_rules)} rules across taxonomy...\n")

    critical_count = 0
    warning_count = 0
    
    for rule in all_rules:
        rule_id = rule.get('id', 'UNKNOWN')
        issues = check_regex_safety(rule_id, rule.get('regex', ''))
        issues.extend(check_schema_and_quality(rule))
        
        if issues:
            print(f"Rule: {rule_id} (in {rule['_file']})")
            for issue in issues:
                prefix = "[!]"
                if "CRITICAL" in issue:
                    critical_count += 1
                    prefix = "[CRITICAL]"
                else:
                    warning_count += 1
                    prefix = "[WARNING]"
                print(f"  {prefix} {issue}")
            print()

    print(f"Linting complete: {critical_count} critical issues, {warning_count} warnings.")
    
    if critical_count > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
