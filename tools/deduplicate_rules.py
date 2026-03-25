import json
import os
from pathlib import Path
from typing import Dict, List, Any

def deduplicate():
    data_dir = Path('data')
    if not data_dir.exists():
        print("Data directory not found.")
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
                        rule['category'] = category # Track origin
                        regex = rule.get('regex') or rule.get('pattern')
                        if regex:
                            if regex not in all_rules_by_regex:
                                all_rules_by_regex[regex] = []
                            all_rules_by_regex[regex].append(rule)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # 2. Merge duplicates
    new_taxonomy: Dict[str, List[Dict[str, Any]]] = {}
    duplicates_found = 0

    for regex, rules in all_rules_by_regex.items():
        if len(rules) > 1:
            duplicates_found += 1
            # Merge logic: pick the first one but combine keywords and use best metadata
            merged_rule = rules[0].copy()
            all_keywords = set()
            for r in rules:
                if r.get('keywords'):
                    all_keywords.update(r['keywords'])
            
            if all_keywords:
                merged_rule['keywords'] = sorted(list(all_keywords))
            
            # Prefer non-'generic' categories if available
            categories = [r['category'] for r in rules if r['category'] != 'generic']
            if categories:
                merged_rule['category'] = categories[0]
            
            # Print info about merge
            ids = [r['id'] for r in rules]
            print(f"Merging duplicates for regex: {regex[:50]}...")
            print(f"  IDs: {ids}")
            print(f"  Resulting Category: {merged_rule['category']}")
            
            final_rule = merged_rule
        else:
            final_rule = rules[0]

        cat = final_rule.get('category', 'api_keys')
        if cat not in new_taxonomy:
            new_taxonomy[cat] = []
        
        # Clean up internal tracking field before saving
        save_rule = final_rule.copy()
        if 'category' in save_rule and os.path.basename(data_dir / cat) == save_rule['category']:
             # It's in its correct folder, we can remove the explicit category if we want
             # to keep rules.json lean, but actually keeping it is safer.
             pass
        
        new_taxonomy[cat].append(save_rule)

    if duplicates_found == 0:
        print("No duplicate regex patterns found.")
        return

    # 3. Write back to files
    print(f"\nWriting {duplicates_found} merged rules back to taxonomy...")
    for cat, rules in new_taxonomy.items():
        cat_dir = data_dir / cat
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        rules_path = cat_dir / 'rules.json'
        with open(rules_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, indent=2)
        
        # Also update regex.list
        list_path = cat_dir / 'regex.list'
        with open(list_path, 'w', encoding='utf-8') as f:
            for r in rules:
                f.write(r['regex'] + '\n')

    print("Deduplication completed.")

if __name__ == "__main__":
    deduplicate()
