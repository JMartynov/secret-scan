import io

from detector import SecretDetector


def _build_stripe_secret() -> str:
    codes = [
        115, 107, 95, 116, 101, 115, 116, 95, 70, 65, 75, 69, 75, 69, 89,
        49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 65, 66, 67, 68, 69
    ]
    return "".join(chr(c) for c in codes)


STRIPE_SECRET = _build_stripe_secret()

def test_keyword_filtering_logic():
    detector = SecretDetector(force_scan_all=False)
    text_without_keyword = f"my secret is {STRIPE_SECRET}"
    findings = detector.scan(text_without_keyword)
    assert not any("stripe" in f.secret_type.lower() for f in findings)
    text_with_keyword = f"my stripe key is {STRIPE_SECRET}"
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
    assert detector.engine.calculate_entropy("") == 0.0
    assert detector.engine.calculate_entropy("aaaaa") == 0.0
    entropy_high = detector.engine.calculate_entropy("abcde12345FGHIJ!@#$%")
    entropy_low = detector.engine.calculate_entropy("abcdeabcdeabcdeabcde")
    assert entropy_high > entropy_low

def test_entropy_detection_with_context():
    detector = SecretDetector(entropy_threshold=3.0)
    text_no_context = "Here is a random string: dGhpcyBpcyBhIHJhbmRvbSBzdHJpbmcgd2l0aCBoaWdoIGVudHJvcHk="
    findings_no_context = detector.scan(text_no_context)
    assert any(f.secret_type == "High Entropy String" for f in findings_no_context)
    text_with_context = "My api key is: dGhpcyBpcyBhIHJhbmRvbSBzdHJpbmcgd2l0aCBoaWdoIGVudHJvcHk="
    findings_with_context = detector.scan(text_with_context)
    assert any(f.secret_type == "Potential Secret (High Entropy + Context)" for f in findings_with_context)

def test_scan_stream_basic():
    detector = SecretDetector()
    content = f"Stripe key: {STRIPE_SECRET}"
    stream = io.StringIO(content)
    findings_gen = detector.scan_stream(stream)
    findings = [f for _, findings in findings_gen for f in findings]
    assert any("stripe" in f.secret_type.lower() for f in findings)

def test_scan_stream_line_numbers_new():
    detector = SecretDetector()
    content = f"""Noise
 Noise
Stripe: {STRIPE_SECRET}
Noise"""
    stream = io.StringIO(content)
    findings_gen = detector.scan_stream(stream)
    findings = [f for _, findings in findings_gen for f in findings]
    stripe_finding = next((f for f in findings if "stripe" in f.secret_type.lower()), None)
    assert stripe_finding is not None
    assert stripe_finding.location == 3

def test_binary_data_scan_robustness():
    detector = SecretDetector(force_scan_all=True)
    # Simulate binary data read with surrogateescape
    binary_data_with_secret = b"\x80\x81\x82 " + STRIPE_SECRET.encode("utf-8") + b" \x83\x84\x85"
    text = binary_data_with_secret.decode("utf-8", "surrogateescape")
    
    # This should not raise UnicodeEncodeError even with re2
    findings = detector.scan(text)
    
    # Debug: print findings
    for f in findings:
        print(f"Found: {f.secret_type} with confidence {f.confidence} at {f.location}")

    # Should find the secret despite binary noise
    stripe_finding = next((f for f in findings if "stripe" in f.secret_type.lower()), None)
    assert stripe_finding is not None
    assert STRIPE_SECRET in stripe_finding.content
