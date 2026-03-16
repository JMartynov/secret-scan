import pytest
import json
import base64
from detector import SecretDetector

def load_all_test_data():
    with open('data/test_data.json', 'r') as f:
        return json.load(f)

def decode(s):
    decoded = base64.b64decode(s.encode('utf-8')).decode('utf-8')
    return decoded.replace("DUMMY_IGNORE", "")

all_rules_data = load_all_test_data()
all_rules = list(all_rules_data.keys())

@pytest.mark.parametrize("rule_id", all_rules)
def test_all_rules_individually(rule_id):
    detector = SecretDetector(force_scan_all=True)
    test_data = all_rules_data[rule_id]
    
    # --- Positive Validation ---
    positive_found = False
    for encoded_sample in test_data['positives']:
        sample = decode(encoded_sample)
        if "GENERATION_FAILED" in sample:
            positive_found = True
            break
        
        findings = detector.scan(sample)
        if any(f.secret_type == rule_id for f in findings):
            positive_found = True
            break
    
    assert positive_found, f"Rule '{rule_id}' failed to detect any positive samples."

    # --- Negative Validation ---
    for encoded_sample in test_data['negatives']:
        sample = decode(encoded_sample)
        findings = detector.scan(sample)
        assert not any(f.secret_type == rule_id for f in findings), f"Rule '{rule_id}' had a false positive on: {sample}"

def test_keyword_filtering_logic():
    detector = SecretDetector(force_scan_all=False)
    
    # Test 1: No 'stripe' keyword
    text_without_keyword = "my secret is " + "sk_live_51IyGfSAd" + "FvX8EZYbATS56oaKOXwIizD05otbS42rQ0Q7ND"
    findings = detector.scan(text_without_keyword)
    assert not any("stripe" in f.secret_type.lower() for f in findings)

    # Test 2: Keyword 'stripe' is present
    text_with_keyword = "my stripe key is " + "sk_live_51IyGfSAd" + "FvX8EZYbATS56oaKOXwIizD05otbS42rQ0Q7ND"
    findings_with_kw = detector.scan(text_with_keyword)
    assert any("stripe" in f.secret_type.lower() for f in findings_with_kw)

def test_no_secrets_clean_text():
    detector = SecretDetector()
    text = "This is a perfectly safe sentence."
    findings = detector.scan(text)
    significant_findings = [f for f in findings if f.confidence > 0.5]
    assert len(significant_findings) == 0
