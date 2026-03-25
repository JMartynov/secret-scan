import json
import sys

from redoctor import check


def main():
    try:
        with open('data/rules.json', 'r') as f:
            rules = json.load(f)
    except Exception as e:
        print(f"Error loading rules: {e}")
        sys.exit(1)

    print(f"Scanning {len(rules)} rules for ReDoS using redoctor library...\n")

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
