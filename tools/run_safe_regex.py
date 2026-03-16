import json
import sys
try:
    from safe_regex import is_safe
except ImportError:
    is_safe = None

def main():
    if is_safe is None:
        print("Error: 'safe-regex' library not found. Install with 'pip install safe-regex'.")
        sys.exit(1)

    try:
        with open('data/rules.json', 'r') as f:
            rules = json.load(f)
    except Exception as e:
        print(f"Error loading rules: {e}")
        sys.exit(1)

    print(f"Scanning {len(rules)} rules for exponential backtracking using safe-regex library...\n")
    
    vulnerable_rules = []
    
    for rule in rules:
        try:
            pattern = rule['regex']
            if not is_safe(pattern):
                vulnerable_rules.append((rule['id'], pattern))
        except Exception:
            pass

    if vulnerable_rules:
        print("--- Vulnerable Rules Found ---")
        for rid, pattern in vulnerable_rules:
            print(f"  [!] {rid}: {pattern}")
        print(f"\nFound {len(vulnerable_rules)} vulnerable rules.")
    else:
        print("No exponential backtracking issues found by safe-regex!")

if __name__ == '__main__':
    main()
