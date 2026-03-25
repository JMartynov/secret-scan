import json
import os
from pathlib import Path

def fix_schema():
    data_dir = Path('data')
    if not data_dir.exists():
        return

    for root, dirs, files in os.walk(data_dir):
        if 'rules.json' in files:
            file_path = Path(root) / 'rules.json'
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                
                modified = False
                for rule in rules:
                    # 1. Map 'risk' to 'severity'
                    if 'risk' in rule and 'severity' not in rule:
                        rule['severity'] = rule.pop('risk').lower()
                        modified = True
                    
                    # 2. Add default severity if missing
                    if 'severity' not in rule:
                        rule['severity'] = 'medium'
                        modified = True
                
                if modified:
                    print(f"Updating schema for {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(rules, f, indent=2)
            except Exception as e:
                print(f"Error fixing {file_path}: {e}")

if __name__ == "__main__":
    fix_schema()
