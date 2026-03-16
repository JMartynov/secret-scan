import json
import re
import sys

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

    # Rule 1(c): Overlapping patterns (a|aa)+
    if '|' in pattern and re.search(r'\(.*\|.*\)\+', pattern):
         issues.append(f"ADVICE: Check for overlapping alternatives in repeating group: {pattern}")

    return issues

def main():
    try:
        with open('data/rules.json', 'r') as f:
            rules = json.load(f)
    except Exception as e:
        print(f"Error loading rules: {e}")
        sys.exit(1)

    print(f"Linting {len(rules)} rules against Safe Regex Style Guide...\n")
    
    found_any = False
    for rule in rules:
        issues = check_regex_safety(rule['id'], rule['regex'])
        if issues:
            found_any = True
            print(f"Rule: {rule['id']}")
            for issue in issues:
                print(f"  [!] {issue}")
            print()

    if not found_any:
        print("All regex patterns passed basic safety checks!")

if __name__ == '__main__':
    main()
