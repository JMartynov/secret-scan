import pytest
from detector import SecretDetector, Finding, PreprocessingLayer

def test_multi_line_scanning():
    detector = SecretDetector()
    text = "Line 1: No secret\nLine 2: sk-abc1234567890abcdef123456\nLine 3: Still no secret"
    findings = detector.scan(text)
    assert len(findings) == 1
    assert findings[0].location == 2
    assert findings[0].secret_type == "OpenAI API Key"

def test_preprocessing_clean_text():
    pre = PreprocessingLayer()
    text = "   some text   \n"
    assert pre.clean_text(text) == "some text"

def test_preprocessing_format_identification():
    pre = PreprocessingLayer()
    assert pre.identify_format('{"key": "value"}') == "JSON"
    assert pre.identify_format("---\nkey: value") == "YAML"
    assert pre.identify_format("normal text") == "TEXT"

def test_google_api_key_detection():
    detector = SecretDetector()
    text = "AIzaSyB_1234567890abcdefghijklmnopqrstuv"
    findings = detector.scan(text)
    assert len(findings) >= 1
    assert any(f.secret_type == "Google API Key" for f in findings)

def test_openai_key_detection():
    detector = SecretDetector()
    text = "Here is my key: sk-abc1234567890abcdef123456"
    findings = detector.scan(text)
    assert len(findings) >= 1
    assert any(f.secret_type == "OpenAI API Key" for f in findings)
    assert findings[0].location == 1

def test_aws_key_detection():
    detector = SecretDetector()
    text = "AKIA1234567890ABCDEF"
    findings = detector.scan(text)
    assert len(findings) >= 1
    assert any(f.secret_type == "AWS Access Key ID" for f in findings)

def test_database_url_detection():
    detector = SecretDetector()
    text = "postgres://user:pass@localhost:5432/db"
    findings = detector.scan(text)
    assert len(findings) >= 1
    assert any(f.secret_type == "Database Credentials" for f in findings)

def test_entropy_detection():
    detector = SecretDetector(entropy_threshold=3.0)
    # A string with high entropy that looks like a token
    text = "My token is 4f7a9b2c8e1d6f3a5c0b9e8d7f6a5b4c" 
    findings = detector.scan(text)
    assert len(findings) >= 1
    assert any("High Entropy" in f.secret_type or "Potential Secret" in f.secret_type for f in findings)

def test_context_analysis():
    detector = SecretDetector()
    text = "secret_key = 4f7a9b2c8e1d6f3a5c0b9e8d7f6a5b4c"
    findings = detector.scan(text)
    assert len(findings) >= 1
    # Check if context analysis boosted it
    finding = next(f for f in findings if f.content == "4f7a9b2c8e1d6f3a5c0b9e8d7f6a5b4c")
    assert finding.secret_type == "Potential Secret (Context Match)"
    assert finding.risk == "HIGH"

def test_no_secrets():
    detector = SecretDetector()
    text = "This is a normal string with no secrets."
    findings = detector.scan(text)
    assert len(findings) == 0
