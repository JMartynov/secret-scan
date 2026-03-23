import json
import os
import re
import exrex
import base64
import random
import string
import sys

def random_string(length, chars=string.ascii_letters + string.digits):
    return ''.join(random.choices(chars, k=length))

def uuid():
    h = "0123456789abcdef"
    return f"{random_string(8, h)}-{random_string(4, h)}-{random_string(4, h)}-{random_string(4, h)}-{random_string(12, h)}"

# Helper generators for complex/strict rules
MANUAL_GENERATORS = {
    'nexmo_api_secret': lambda: "nexmo-" + random_string(16),
    'roaring_api_secret': lambda: "roaring-" + random_string(28, string.ascii_letters + string.digits + "_-"),
    'satismeter_api_password': lambda: "satismeter-" + random_string(10),
    'tru_api_secret': lambda: "tru-" + random_string(26, string.ascii_letters + string.digits + ".-_"),
    'discord_api_token': lambda: "discord " + "M" + random_string(23) + "." + random_string(6) + "." + random_string(27),
    'mrticktock_password': lambda: "mrticktock " + random_string(50, string.ascii_letters + string.digits),
    'github_private_key': lambda: "github\n-----BEGIN RSA PRIVATE KEY-----\n" + "a"*40 + "\n-----END RSA PRIVATE KEY-----",
    'private_key': lambda: "-----BEGIN RSA PRIVATE KEY-----\n" + "b"*40 + "\n-----END RSA PRIVATE KEY-----",
    'ssh_public_key': lambda: "ssh-rsa AAAA" + random_string(40, string.ascii_letters + string.digits + "+/") + " user@host",
    'azure_generic_key': lambda: random_string(52) + "JQQJ99A" + "X" + "AC" + random_string(10) + "AAA" + random_string(9),
    'slack_webhook': lambda: "https://hooks.slack.com/services/" + random_string(9) + "/" + random_string(9) + "/" + random_string(24),
    'google_api_key': lambda: "AIza" + random_string(35, string.ascii_letters + string.digits + "_-"),
    'aws_access_key_id': lambda: "AKIA" + random_string(16, string.ascii_uppercase + string.digits),
    'stripe_api_key': lambda: "sk_live_" + random_string(24, string.ascii_letters + string.digits),
    'sendgrid_api_key': lambda: "sendgrid " + "SG." + random_string(22, string.ascii_letters + string.digits + "-_") + "." + random_string(43, string.ascii_letters + string.digits + "-_"),
    'teams_incoming_webhook': lambda: "https://test.webhook.office.com/webhookb2/" + uuid() + "@" + uuid() + "/IncomingWebhook/" + random_string(32, "0123456789abcdef") + "/" + uuid(),
    'lexigram_api_key': lambda: "lexigram " + random_string(301),
    'nethunt_api_key': lambda: "nethunt " + uuid(),
    'iban_mt': lambda: "MT" + random_string(29, string.digits + string.ascii_uppercase),
    'iban_gi': lambda: "GI" + random_string(21, string.digits + string.ascii_uppercase),
    'iban_rs': lambda: "RS" + random_string(20, string.digits),
    'common_passwords_shortlist': lambda: "password = secret123",
    'yaml_passwords_plain': lambda: "db_password: supersecret123",
    'yaml_passwords_single_quoted': lambda: "db_password: 'supersecret123'",
    'yaml_passwords_multiline': lambda: "db_password: >\n  supersecret123",
    'env_passwords': lambda: "export DB_PASSWORD=supersecret123",
    'django_secret_key': lambda: "SECRET_KEY = 'django-insecure-" + random_string(50) + "'",
    'ssh_private_keys': lambda: "-----BEGIN OPENSSH PRIVATE KEY-----\n" + random_string(100, string.ascii_letters + string.digits + "+/") + "\n-----END OPENSSH PRIVATE KEY-----",
    'generic_rsa_keys': lambda: "-----BEGIN RSA PRIVATE KEY-----\n" + random_string(100, string.ascii_letters + string.digits + "+/") + "\n-----END RSA PRIVATE KEY-----",
    'gpg_private_key': lambda: "-----BEGIN PGP PRIVATE KEY BLOCK-----\n" + random_string(100, string.ascii_letters + string.digits + "+/") + "\n-----END PGP PRIVATE KEY BLOCK-----",
    'credit_cards': lambda: "4" + random_string(15, string.digits),
    'bearer_tokens': lambda: "Authorization: Bearer " + random_string(30, string.ascii_letters + string.digits + "-._~+/:="),
    'razorpay_api_key': lambda: "rzp_" + random_string(4, string.ascii_letters + string.digits) + "_" + random_string(15, string.ascii_letters + string.digits),
    'jdbc_token': lambda: "jdbc:mysql://host:3306/db?user=root&password=" + random_string(10, string.ascii_letters + string.digits) + " ",
    'azure_access_key_legacy': lambda: "AzureKey=" + random_string(80, string.ascii_letters + string.digits + "+/") + "==",
    'sugester_api_domain': lambda: "sugester-token",
    'yaml_static_password_fields': lambda: "db_password: secret_value_123",
    'hardcoded_database_passwords': lambda: "postgres_password = " + random_string(12),
}

def encode_str(s):
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')

def sanitize_regex_for_python(regex):
    """
    Cleans regex to be compatible with Python's re module.
    Returns (cleaned_regex, flags_int)
    """
    # Handle JS style /regex/flags
    m = re.match(r'^/(.*)/[a-z]*$', regex, re.DOTALL)
    if m:
        regex = m.group(1)

    flags = re.VERBOSE | re.IGNORECASE # Default to ignorecase as most rules seem to imply it or use (?i)
    
    # Handle \z (Perl end of string) -> \Z (Python end of string)
    clean = regex.replace(r'\z', r'\Z')
    
    # Remove inline flags (?i), (?s), etc. and map to int flags if needed
    clean = re.sub(r'\(\?[imsx]+\)', '', clean)
    
    return clean, flags

def simplify_regex_for_exrex(regex):
    # 1. First, make it Python compatible-ish
    # Handle JS style /regex/flags
    m = re.match(r'^/(.*)/[a-z]*$', regex, re.DOTALL)
    if m:
        regex = m.group(1)
        
    clean = regex.replace(r'\z', r'\Z')
    
    # Strip flags
    clean = re.sub(r'\(\?[imsx]+\)', '', clean)
    
    # Strip anchors - exrex doesn't need them to generate a matching string
    clean = re.sub(r'\\A|\\Z|\^|\$', '', clean)
    clean = re.sub(r'\\b|\\B', '', clean) 
    
    # Limit quantifiers
    clean = re.sub(r'\{(\d+),\}', lambda m: f"{{{m.group(1)},{int(m.group(1))+5}}}", clean)
    def cap_quantifier(m):
        n = int(m.group(1))
        limit = int(m.group(2))
        return f"{{{n},{min(limit, n+5)}}}"
    clean = re.sub(r'\{(\d+),(\d+)\}', cap_quantifier, clean)
    
    return clean

def strip_lookarounds(regex):
    clean = re.sub(r'\(\?\=[^)]+\)', '', regex)
    clean = re.sub(r'\(\?\![^)]+\)', '', regex)
    clean = re.sub(r'\(\?\<\=[^)]+\)', '', regex)
    clean = re.sub(r'\(\?\<\![^)]+\)', '', regex)
    return clean

def main():
    data_dir = 'data'
    total_rules = 0
    generated_count = 0
    failed_rules = []

    for cat in os.listdir(data_dir):
        cat_path = os.path.join(data_dir, cat)
        if not os.path.isdir(cat_path): continue
        rules_path = os.path.join(cat_path, 'rules.json')
        if not os.path.exists(rules_path): continue
        
        with open(rules_path, 'r') as f:
            rules = json.load(f)

        print(f"Processing {len(rules)} rules in {cat}...")
        total_rules += len(rules)
        cat_test_data = {}

        for rule in rules:
            rid = rule['id']
            raw_regex = rule.get('regex') or rule.get('pattern')
            if not raw_regex:
                continue

            # Use a safe negative string that won't trigger keyword-based rules
            entry = {"positives": [], "negatives": [encode_str(f"safe-negative-test-string-{uuid()}")]}
            
            # Prepare validation regex
            try:
                val_regex, val_flags = sanitize_regex_for_python(raw_regex)
            except Exception as e:
                print(f"Skipping rule {rid}, invalid regex for sanitization: {e}", file=sys.stderr)
                continue

            # 1. Try Manual
            sample = None
            if rid in MANUAL_GENERATORS:
                try:
                    s = MANUAL_GENERATORS[rid]()
                    if re.search(val_regex, s, val_flags):
                        sample = s
                    else:
                        print(f"Manual gen failed validation for {rid}. Regex: {val_regex}", file=sys.stderr)
                except Exception as e:
                    print(f"Manual gen failed for {rid}: {e}", file=sys.stderr)

            # 2. Try Exrex (Smart)
            if not sample:
                try:
                    clean = simplify_regex_for_exrex(raw_regex)
                    for _ in range(10): 
                        s = exrex.getone(clean)
                        if re.search(val_regex, s, val_flags):
                            sample = s
                            break
                        if re.search(val_regex, f" {s} ", val_flags):
                            sample = f" {s} "
                            break
                except Exception as e:
                    # 3. Try Exrex (Aggressive Strip)
                    try:
                        clean_stripped = strip_lookarounds(clean)
                        for _ in range(5):
                            s = exrex.getone(clean_stripped)
                            if re.search(val_regex, s, val_flags):
                                sample = s
                                break
                    except Exception as e2:
                        pass # Fail silently, logged below

            if sample:
                entry["positives"].append(encode_str(sample))
                generated_count += 1
            else:
                failed_rules.append(rid)
                print(f"FAILED to generate for {rid}. Val Regex: {val_regex[:50]}...", file=sys.stderr)
            
            cat_test_data[rid] = entry

        with open(os.path.join(cat_path, 'test_data.json'), 'w') as f:
            json.dump(cat_test_data, f, indent=2)

    print(f"Generation complete. Generated: {generated_count}/{total_rules}. Failed: {len(failed_rules)}")
    if failed_rules:
        print(f"Failed IDs: {failed_rules[:20]}...")

if __name__ == '__main__':
    main()
