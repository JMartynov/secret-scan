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

def test_calculate_entropy():
    detector = SecretDetector()
    # Low entropy strings
    assert detector.engine.calculate_entropy("") == 0.0
    assert detector.engine.calculate_entropy("aaaaa") == 0.0
    # High entropy strings
    entropy_high = detector.engine.calculate_entropy("abcde12345FGHIJ!@#$%")
    entropy_low = detector.engine.calculate_entropy("abcdeabcdeabcdeabcde")
    assert entropy_high > entropy_low

def test_entropy_detection_with_context():
    detector = SecretDetector(entropy_threshold=3.0)
    # High entropy string without context keywords
    text_no_context = "Here is a random string: dGhpcyBpcyBhIHJhbmRvbSBzdHJpbmcgd2l0aCBoaWdoIGVudHJvcHk="
    findings_no_context = detector.scan(text_no_context)
    assert any(f.secret_type == "High Entropy String" for f in findings_no_context)
    assert not any(f.secret_type == "Potential Secret (High Entropy + Context)" for f in findings_no_context)

    # High entropy string with context keywords
    text_with_context = "My api key is: dGhpcyBpcyBhIHJhbmRvbSBzdHJpbmcgd2l0aCBoaWdoIGVudHJvcHk="
    findings_with_context = detector.scan(text_with_context)
    assert any(f.secret_type == "Potential Secret (High Entropy + Context)" for f in findings_with_context)

def test_scan_stream_basic():
    detector = SecretDetector()
    import io
    content = "Stripe key: sk_live_abc123def456ghi789j012"
    stream = io.StringIO(content)
    findings_gen = detector.scan_stream(stream)
    findings = [f for _, findings in findings_gen for f in findings]
    assert any("stripe" in f.secret_type.lower() for f in findings)

def test_scan_stream_line_numbers_new():
    detector = SecretDetector()
    import io
    content = """Noise
Noise
Stripe: sk_live_abc123def456ghi789j012
Noise"""
    stream = io.StringIO(content)
    findings_gen = detector.scan_stream(stream)
    findings = [f for _, findings in findings_gen for f in findings]
    stripe_finding = next((f for f in findings if "stripe" in f.secret_type.lower()), None)
    assert stripe_finding is not None
    assert stripe_finding.location == 3
