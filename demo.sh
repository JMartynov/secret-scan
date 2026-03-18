#!/bin/bash

# LLM Secrets Leak Detector Demo (Streaming)
# This script demonstrates detection in noise, combined cases, and streaming pipes.

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

with open('data/test_data.json', 'r') as f:
    data = json.load(f)

# Secrets to use
samples = {
    'aws': 'AWS Access Key: ' + decode_sample(data['aws_api_id']['positives'][0]),
    'github': 'Github Token: ' + decode_sample(data['github_token']['positives'][0]),
    'stripe': 'Stripe secret: ' + decode_sample(data['stripe_api_key']['positives'][0]),
    'db': 'DB Connection: ' + decode_sample(data['jdbc_token']['positives'][0])
}

# Scenario 1: Combined Small File
with open(os.path.join('$DEMO_DIR', 'combined_small.txt'), 'w') as f:
    all_secrets = list(samples.values())
    random.shuffle(all_secrets)
    for s in all_secrets:
        f.write(get_noise(50) + s + "\n" + get_noise(50) + "\n")

# Scenario 2: 1MB Performance File
ONE_MB = 1024 * 1024
with open(os.path.join('$DEMO_DIR', 'performance_1mb.txt'), 'w') as f:
    current_size = 0
    secrets_to_add = list(samples.values())
    random.shuffle(secrets_to_add)
    chunk_size = ONE_MB // (len(secrets_to_add) + 1)
    for s in secrets_to_add:
        noise = ''.join(random.choices(string.ascii_letters + " \n", k=chunk_size))
        f.write(noise)
        f.write("\n" + s + "\n")
    remaining = ONE_MB - f.tell()
    if remaining > 0:
        f.write(''.join(random.choices(string.ascii_letters + " \n", k=remaining)))

EOF

COMBINED="$DEMO_DIR/combined_small.txt"
PERF="$DEMO_DIR/performance_1mb.txt"

# 3. Demonstrate Detection Options
echo -e "\n--- Part 1: Default Output (Summary Only) ---"
echo ">>> Scanning: combined_small.txt"
./run.sh "$COMBINED"
echo "----------------------------------------------------"

echo -e "\n--- Part 2: Short Output (Summary + Redacted Details) ---"
echo ">>> Scanning: combined_small.txt --short"
./run.sh "$COMBINED" --short
echo "----------------------------------------------------"

echo -e "\n--- Part 3: Full Output (Summary + Full Details) ---"
echo ">>> Scanning: combined_small.txt --full"
./run.sh "$COMBINED" --full
echo "----------------------------------------------------"

echo -e "\n--- Part 4: No Colors Output ---"
echo ">>> Scanning: combined_small.txt --nocolors"
./run.sh "$COMBINED" --nocolors
echo "----------------------------------------------------"

echo -e "\n--- Part 5: Streaming Output (Piping without -) ---"
echo ">>> cat combined_small.txt | ./run.sh"
cat "$COMBINED" | ./run.sh
echo "----------------------------------------------------"

echo -e "\n--- Part 6: 1MB Performance Benchmark (Summary) ---"
echo ">>> Scanning: performance_1mb.txt (1,048,576 bytes)"
TIMEFORMAT="Execution Time: %R seconds"
time ./run.sh "$PERF"

# 4. Cleanup
rm -rf "$DEMO_DIR"
echo -e "\n--- Demo Complete ---"
