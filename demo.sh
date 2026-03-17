#!/bin/bash

# LLM Secrets Leak Detector Demo (Advanced)
# This script demonstrates detection in noise, combined cases, and performance.

# 1. Setup temporary directory
DEMO_DIR=$(mktemp -d /tmp/secret-scan-demo.XXXXXX)
echo "--- Initializing Advanced Demo Environment in $DEMO_DIR ---"

# 2. Generate Demo Files using Python
python3 <<EOF
import json, base64, os, random, string

def decode_sample(s):
    try:
        decoded = base64.b64decode(s.encode('utf-8')).decode('utf-8')
        return decoded.replace("DUMMY_IGNORE", "")
    except: return s

def get_noise(length=50):
    words = ["function", "const", "return", "import", "data", "value", "process", "result", "config", "env"]
    return " ".join(random.choices(words, k=length // 8)) + " "

def create_noisy_file(path, secret):
    with open(path, 'w') as f:
        f.write(get_noise(100) + secret + "\n" + get_noise(100))

with open('data/test_data.json', 'r') as f:
    data = json.load(f)

# Secrets to use
samples = {
    'aws': 'AWS Access Key: ' + decode_sample(data['aws_api_id']['positives'][0]),
    'github': 'Github Token: ' + decode_sample(data['github_token']['positives'][0]),
    'stripe': 'Stripe secret: ' + decode_sample(data['stripe_api_key']['positives'][0]),
    'db': 'DB Connection: ' + decode_sample(data['jdbc_token']['positives'][0])
}

# Scenario 1: Individual Noisy Files
for name, secret in samples.items():
    create_noisy_file(os.path.join('$DEMO_DIR', f'noisy_{name}.txt'), secret)

# Scenario 2: Combined Small File
with open(os.path.join('$DEMO_DIR', 'combined_small.txt'), 'w') as f:
    all_secrets = list(samples.values())
    random.shuffle(all_secrets)
    for s in all_secrets:
        f.write(get_noise(50) + s + "\n" + get_noise(50) + "\n")

# Scenario 3: 1MB Performance File
ONE_MB = 1024 * 1024
with open(os.path.join('$DEMO_DIR', 'performance_1mb.txt'), 'w') as f:
    current_size = 0
    # Add secrets at random intervals
    secrets_to_add = list(samples.values())
    random.shuffle(secrets_to_add)
    
    chunk_size = ONE_MB // (len(secrets_to_add) + 1)
    
    for s in secrets_to_add:
        noise = ''.join(random.choices(string.ascii_letters + " \n", k=chunk_size))
        f.write(noise)
        f.write("\n" + s + "\n")
    
    # Final padding
    remaining = ONE_MB - f.tell()
    if remaining > 0:
        f.write(''.join(random.choices(string.ascii_letters + " \n", k=remaining)))

EOF

# 3. Demonstrate Detection
echo -e "\n--- Part 1: Individual Secrets in Noisy Text ---"
for file in "$DEMO_DIR"/noisy_*.txt; do
    echo -e "\n>>> Scanning: $(basename "$file")"
    ./run.sh "$file"
    echo "----------------------------------------------------"
done

echo -e "\n--- Part 2: Combined Small File (All Secrets) ---"
echo ">>> Scanning: combined_small.txt"
./run.sh "$DEMO_DIR/combined_small.txt"
echo "----------------------------------------------------"

echo -e "\n--- Part 3: 1MB Performance Benchmark ---"
echo ">>> Scanning: performance_1mb.txt (1,048,576 bytes)"
# Using time command to measure execution
TIMEFORMAT="Execution Time: %R seconds"
time ./run.sh "$DEMO_DIR/performance_1mb.txt"

# 4. Cleanup
rm -rf "$DEMO_DIR"
echo -e "\n--- Demo Complete ---"
