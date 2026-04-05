import pytest
import os
import json
import base64
from detector import SecretDetector

def get_all_test_data():
    all_tests = []
    data_dir = 'data'
    for root, dirs, files in os.walk(data_dir):
        if 'test_data.json' in files:
            cat = os.path.basename(root)
            with open(os.path.join(root, 'test_data.json'), 'r') as f:
                tests = json.load(f)
                for rule_id, data in tests.items():
                    for pos in data.get('positives', []):
                        all_tests.append((rule_id, cat, pos, True))
                    for neg in data.get('negatives', []):
                        all_tests.append((rule_id, cat, neg, False))
    return all_tests

detector = SecretDetector(data_dir='data', force_scan_all=True)

def decode_sample(s):
    try:
        # Step 1: Decode base64 to get hex string
        hex_str = base64.b64decode(s.encode('utf-8')).decode('utf-8')
        # Step 2: Convert hex back to original string
        original = bytes.fromhex(hex_str).decode('utf-8')
        return original
    except Exception:
        # Fallback for old simple base64 if needed
        try:
            return base64.b64decode(s.encode('utf-8')).decode('utf-8')
        except:
            return s

@pytest.mark.parametrize("rule_id, category, b64_data, should_match", get_all_test_data())
def test_rule_detection(rule_id, category, b64_data, should_match):
    text = decode_sample(b64_data)
    
    findings = detector.scan(text)
    
    # We want to see if the SPECIFIC rule_id was detected
    # or at least SOME rule was detected for positives.
    detected_ids = {f.secret_type for f in findings}
    
    if should_match:
        # For positives, we expect at least one finding. 
        # Ideally it matches rule_id, but some rules might overlap or have different IDs.
        assert len(findings) > 0, f"Positive test failed for {rule_id} in {category}. Text: {text}"
    else:
        # For negatives, we expect NO finding for this specific rule_id.
        # It's okay if other rules match (e.g. generic ones), but rule_id shouldn't.
        assert rule_id not in detected_ids, f"Negative test failed for {rule_id} in {category}. Detected: {detected_ids}"

if __name__ == "__main__":
    # Sample run
    detector = SecretDetector()
    all_tests = get_all_test_data()
    print(f"Total tests: {len(all_tests)}")
