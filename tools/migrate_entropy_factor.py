import json
import os
from pathlib import Path

def migrate_entropy_factor():
    data_dir = Path('data')
    if not data_dir.exists():
        print("Data directory not found.")
        return

    updated_count = 0
    file_count = 0

    for root, dirs, files in os.walk(data_dir):
        if 'rules.json' in files:
            file_path = Path(root) / 'rules.json'
            file_count += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                
                modified = False
                for rule in rules:
                    # If it has entropy but no entropy_factor, add it explicitly
                    if 'entropy' in rule and 'entropy_factor' not in rule:
                        rule['entropy_factor'] = 0.7
                        modified = True
                        updated_count += 1
                
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(rules, f, indent=2)
                    print(f"Updated {file_path}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print(f"\nMigration complete. Updated {updated_count} rules across {file_count} files.")

if __name__ == '__main__':
    migrate_entropy_factor()
