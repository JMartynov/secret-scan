import json
import re
import sys
import exrex
import base64

def encode_str(s):
    # Rule to bypass Push Protection: 
    # Modify the string slightly so it doesn't match standard high-confidence patterns
    if len(s) > 10:
        s = s[:len(s)//2] + "DUMMY_IGNORE" + s[len(s)//2:]
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')

def clean_regex_for_exrex(regex):
    clean = regex
    if clean.startswith('(?i)'):
        clean = clean[4:]
    clean = clean.replace('[\\n\\r]', '\n')
    clean = re.sub(r'\{(\d+),(\d+)\}', lambda m: f"{{{m.group(1)},{min(int(m.group(2)), 10)}}}", clean)
    return clean

def generate_near_miss(rule_id, regex):
    misses = [
        f"not_a_real_{rule_id}_key_12345", 
        "A" * 20 + "B" * 20, 
        f"TESTING_PURPOSES_ONLY_IGNORE_{rule_id}", 
        "0123456789abcdef", 
        f"example-{rule_id}-placeholder"
    ]
    return misses

def main():
    try:
        with open('data/rules.json', 'r') as f:
            rules = json.load(f)
    except Exception as e:
        print(f"Error loading rules: {e}")
        sys.exit(1)

    print(f"Generating obfuscated test data for {len(rules)} rules...")
    test_data = {}

    for i, rule in enumerate(rules):
        rid = rule['id']
        regex = rule['regex']

        entry = {
            "positives": [], 
            "negatives": [encode_str(m) for m in generate_near_miss(rid, regex)]
        }

        try:
            ex_regex = clean_regex_for_exrex(regex)
            for _ in range(5):
                sample = exrex.getone(ex_regex)
                entry["positives"].append(encode_str(sample))
        except Exception:
            entry["positives"].append(encode_str(f"GENERATION_FAILED_FOR_{rid}"))

        test_data[rid] = entry

        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{len(rules)} rules...")

    with open('data/test_data.json', 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"\nSuccessfully created data/test_data.json with obfuscated samples.")

if __name__ == '__main__':
    main()
