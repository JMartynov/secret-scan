#!/bin/bash

# LLM Secrets Leak Detector Demo (Fixed)
# This script demonstrates the tool's ability to detect various types of secrets.

# 1. Setup temporary directory
DEMO_DIR=$(mktemp -d /tmp/secret-scan-demo.XXXXXX)
echo "--- Initializing Demo Environment in $DEMO_DIR ---"

# 2. Generate Demo Files using Python
# This extracts "safe" samples from the tool's own test data.
python3 <<EOF
import json, base64, os

def decode_sample(s):
    try:
        decoded = base64.b64decode(s.encode('utf-8')).decode('utf-8')
        return decoded.replace("DUMMY_IGNORE", "")
    except: return s

with open('data/test_data.json', 'r') as f:
    data = json.load(f)

# Scenario mapping: Rule ID -> (Filename, Content Prefix)
scenarios = {
    'aws_api_id': ('aws.txt', 'AWS Access Key: '),
    'github_token': ('github.txt', 'Github Token: '),
    'stripe_api_key': ('stripe.txt', 'Stripe secret: '),
    'jdbc_token': ('database.txt', 'DB Connection string: ')
}

for rule_id, (filename, prefix) in scenarios.items():
    with open(os.path.join('$DEMO_DIR', filename), 'w') as f:
        # Include a keyword to trigger the scanner in non-forced mode
        f.write(prefix + decode_sample(data[rule_id]['positives'][0]))

# Manual Contextual Example
# The tool matches patterns like "prod password : <value>"
with open(os.path.join('$DEMO_DIR', 'context_prompt.txt'), 'w') as f:
    f.write("Our prod password is: MySecretPass123! and my api token: ABC-12345-XYZ")

# Manual High Entropy Example
with open(os.path.join('$DEMO_DIR', 'entropy_token.txt'), 'w') as f:
    f.write("config_token = 'jX8zK9m2nP5qR7v4s1t3wB5y7z9A2C4D'")

EOF

# 3. Demonstrate Detection
echo -e "\n--- Demonstrating Rule-based, Contextual, and Entropy Detection ---"

# Order scenarios for better presentation
for file_name in aws.txt github.txt stripe.txt database.txt context_prompt.txt entropy_token.txt; do
    file="$DEMO_DIR/$file_name"
    if [ ! -f "$file" ]; then continue; fi
    
    echo -e "\n>>> Scenario: $file_name"
    echo "Content Preview:"
    head -n 2 "$file" | sed 's/^/  /'
    echo -e "\nDetection Result:"
    ./run.sh "$file"
    echo "----------------------------------------------------"
done

# 4. Cleanup
rm -rf "$DEMO_DIR"
echo -e "\n--- Demo Complete (Temporary files cleaned up) ---"
