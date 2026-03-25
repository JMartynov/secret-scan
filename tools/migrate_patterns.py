import json
from pathlib import Path


def migrate():
    data_dir = Path('data')
    rules_file = data_dir / 'rules.json'

    if not rules_file.exists():
        print(f"{rules_file} not found.")
        return

    with open(rules_file, 'r', encoding='utf-8') as f:
        rules = json.load(f)

    taxonomy = {
        'api_keys': [],
        'cloud_credentials': [],
        'database_credentials': [],
        'infrastructure': [],
        'authentication': [],
        'private_keys': [],
        'certificates': [],
        'tokens': [],
        'pii': [],
        'generic_secrets': []
    }

    # Basic categorization logic
    for rule in rules:
        rid = rule['id'].lower()
        cat = 'api_keys' # Default

        if any(x in rid for x in ['aws', 'azure', 'google_cloud', 'gcp', 'heroku', 'digitalocean']):
            cat = 'cloud_credentials'
        elif any(x in rid for x in ['mongo', 'mysql', 'postgres', 'redis', 'db', 'database', 'sql']):
            cat = 'database_credentials'
        elif any(x in rid for x in ['ssh', 'private_key', 'pem', 'rsa', 'dsa', 'ecdsa', 'ed25519']):
            cat = 'private_keys'
        elif any(x in rid for x in ['cert', 'certificate', 'p12', 'pfx']):
            cat = 'certificates'
        elif any(x in rid for x in ['kube', 'terraform', 'docker', 'env', 'config']):
            cat = 'infrastructure'
        elif any(x in rid for x in ['token', 'jwt', 'auth']):
            cat = 'tokens'
        elif any(x in rid for x in ['password', 'secret', 'cred']):
            cat = 'authentication'

        taxonomy[cat].append(rule)

    # Create directories and write files
    for cat, cat_rules in taxonomy.items():
        if not cat_rules:
            continue

        cat_dir = data_dir / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        # rules.json
        with open(cat_dir / 'rules.json', 'w', encoding='utf-8') as f:
            json.dump(cat_rules, f, indent=2)

        # regex.list
        with open(cat_dir / 'regex.list', 'w', encoding='utf-8') as f:
            for rule in cat_rules:
                f.write(rule['regex'] + '\n')

        # test_data.json (initial empty or basic)
        test_data_path = cat_dir / 'test_data.json'
        if not test_data_path.exists():
            with open(test_data_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    print("Migration completed.")

if __name__ == "__main__":
    migrate()
