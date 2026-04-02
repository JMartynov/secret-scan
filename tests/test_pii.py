import pytest
from src.validators import luhn_check, validate_finding
from detector import DetectionEngine, SecretDetector
from report import Finding

def test_luhn_check_valid():
    # Example valid CC
    assert luhn_check("49927398716") is True
    # Visa test card
    assert luhn_check("4111111111111111") is True

def test_luhn_check_invalid():
    # Same prefix, bad check digit
    assert luhn_check("4111111111111112") is False

def test_rule_tier_loading():
    import os
    # Ensure correct data path is used in tests
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

    # Instantiate with include_pii=True
    engine = DetectionEngine(include_pii=True, data_dir=data_dir)
    pii_rules = [r for r in engine.rules if r.get('category') == 'pii']
    assert len(pii_rules) > 0
    # SSN should be tier 1
    ssn_rule = next((r for r in pii_rules if r['id'] == 'ssn_us'), None)
    assert ssn_rule is not None
    assert ssn_rule.get('tier') == 1
    # Email should be tier 2
    email_rule = next((r for r in pii_rules if r['id'] == 'email_address'), None)
    assert email_rule is not None
    assert email_rule.get('tier') == 2

def test_tier_shadowing():
    # If a string matches both a Tier 1 rule and a Tier 4 (Entropy) rule,
    # Tier 1 should shadow Tier 4.
    detector = SecretDetector(entropy_threshold=1.0) # lower entropy to ensure it flags

    # We construct findings to test the internal _resolve_overlaps method
    # 1. High confidence Tier 1 finding
    f1 = Finding("aws_access_key", 1, "HIGH", "AKIAIOSFODNN7EXAMPLE", 0.9, 0, 20)
    f1.tier = 1

    # 2. Lower confidence Tier 4 (Entropy) finding overlapping the same region
    f2 = Finding("High Entropy String", 1, "MEDIUM", "AKIAIOSFODNN7EXAMPLE", 0.3, 0, 20)
    f2.tier = 4

    resolved = detector._resolve_overlaps([f1, f2])
    assert len(resolved) == 1
    assert resolved[0].secret_type == "aws_access_key"

def test_pii_regex_boundaries():
    import os
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    detector = SecretDetector(include_pii=True, data_dir=data_dir)
    # Valid email
    findings = detector.scan("Contact us at test.user+tag@example.co.uk please.")
    assert any(f.secret_type == "email_address" for f in findings)

    # Valid UK phone
    findings = detector.scan("Call me on cell +447911 123456.")
    assert any(f.secret_type == "phone_number_uk" for f in findings)

def test_regional_filtering():
    import os
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    # Only US
    detector_us = SecretDetector(include_pii=True, pii_regions=["US"], data_dir=data_dir)
    # Should flag US SSN
    findings_us = detector_us.scan("My SSN is 123-45-6789.")
    assert any(f.secret_type == "ssn_us" for f in findings_us)

    # Should NOT flag UK phone since only US requested
    findings_uk_phone = detector_us.scan("Call me on +447911 123456.")
    assert not any(f.secret_type == "phone_number_uk" for f in findings_uk_phone)
