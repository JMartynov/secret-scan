import json
import os
import tomli

def load_existing_regexes(data_dir):
    existing = set()
    for root, dirs, files in os.walk(data_dir):
        if 'rules.json' in files:
            with open(os.path.join(root, 'rules.json'), 'r') as f:
                try:
                    rules = json.load(f)
                    for r in rules:
                        if 'regex' in r:
                            existing.add(r['regex'])
                        if 'pattern' in r:
                            existing.add(r['pattern'])
                except json.JSONDecodeError:
                    pass
    return existing

def map_gitleaks_tags_to_category(tags):
    tags_lower = [t.lower() for t in tags]
    if 'key' in tags_lower or 'api' in tags_lower:
        return 'api_keys'
    if 'token' in tags_lower or 'auth' in tags_lower:
        return 'tokens'
    if 'cloud' in tags_lower or 'aws' in tags_lower or 'gcp' in tags_lower or 'azure' in tags_lower:
        return 'cloud_credentials'
    return 'api_keys' # default fallback

def ingest_gitleaks(toml_path, data_dir):
    existing_regexes = load_existing_regexes(data_dir)
    
    with open(toml_path, 'rb') as f:
        gitleaks_config = tomli.load(f)
        
    rules = gitleaks_config.get('rules', [])
    new_rules = []
    
    for rule in rules:
        regex = rule.get('regex')
        if not regex or regex in existing_regexes:
            continue
            
        rule_id = rule.get('id', 'gitleaks_imported_rule').lower().replace('-', '_')
        description = rule.get('description', '')
        tags = rule.get('tags', [])
        keywords = rule.get('keywords', [])
        
        # Determine category based on tags
        category = map_gitleaks_tags_to_category(tags)
        
        new_rule = {
            "id": f"gitleaks_{rule_id}",
            "category": category,
            "keywords": keywords,
            "regex": regex,
            "severity": "high",
            "tier": 2,
            "entropy": 3.5,
            "entropy_factor": 0.7
        }
        new_rules.append(new_rule)
        existing_regexes.add(regex)
        
    # Group by category
    categorized_rules = {}
    for r in new_rules:
        cat = r['category']
        if cat not in categorized_rules:
            categorized_rules[cat] = []
        categorized_rules[cat].append(r)
        
    # Append to files
    for cat, rules in categorized_rules.items():
        cat_dir = os.path.join(data_dir, 'Structured', cat)
        if not os.path.exists(cat_dir):
            os.makedirs(cat_dir)
            
        rules_path = os.path.join(cat_dir, 'rules.json')
        current_rules = []
        if os.path.exists(rules_path):
            with open(rules_path, 'r') as f:
                try:
                    current_rules = json.load(f)
                except json.JSONDecodeError:
                    pass
                    
        current_rules.extend(rules)
        
        with open(rules_path, 'w') as f:
            json.dump(current_rules, f, indent=2)
            
    print(f"Ingested {len(new_rules)} new rules.")

if __name__ == '__main__':
    ingest_gitleaks('tools/gitleaks.toml', 'data')
