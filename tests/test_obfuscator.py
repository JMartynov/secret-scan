from obfuscator import Obfuscator
from report import Finding

def test_in_place_replacement():
    obfuscator = Obfuscator(mode="redact")
    text = "The AWS key is AKIA0000000000000000 and it is secret."
    findings = [
        Finding("AWS API ID", 1, "HIGH", "AKIA0000000000000000", 0.9, 15, 35)
    ]
    result = obfuscator.obfuscate(text, findings)
    assert result == "The AWS key is AKIA...CDEF and it is secret."

def test_overlapping_matches_handling():
    obfuscator = Obfuscator(mode="redact")
    text = "The key is ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    findings = [
        Finding("Type1", 1, "HIGH", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 0.9, 11, 37),
        Finding("Type2", 1, "HIGH", "ABCDEFGHIJKL", 0.9, 11, 23)
    ]
    result = obfuscator.obfuscate(text, findings)
    assert "..." in result
    assert "ABCDEFGHIJKL" not in result

def test_hashing_consistency():
    obfuscator = Obfuscator(mode="hash")
    text1 = "secret123"
    text2 = "secret123"
    hash1 = obfuscator.obfuscate_content(text1, "type")
    hash2 = obfuscator.obfuscate_content(text2, "type")
    assert hash1 == hash2
    assert "[HASHED_" in hash1

def test_synthetic_data_generation():
    obfuscator = Obfuscator(mode="synthetic")
    
    # Test AWS API ID (should start with AKIA and have 20 chars total)
    result_aws = obfuscator.obfuscate_content("AKIA0000000000000000", "aws_api_id")
    assert result_aws.startswith("AKIA")
    assert len(result_aws) == 20
    assert result_aws != "AKIA0000000000000000"

    # Test GitHub Token (should start with ght_)
    result_github = obfuscator.obfuscate_content("ght_GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", "github_token")
    assert result_github.startswith("ght_")
    assert len(result_github) == 40

    # Test Email
    result_email = obfuscator.obfuscate_content("test@example.com", "email")
    assert "@" in result_email
    assert "." in result_email
    assert result_email != "test@example.com"

    # Test generic fallback (should be hex and match original length)
    original_hex = "abcdef123456"
    result_generic = obfuscator.obfuscate_content(original_hex, "generic_key")
    assert len(result_generic) == len(original_hex)
    assert all(c in "0123456789abcdef" for c in result_generic)

def test_obfuscate_with_overlapping_findings():
    """
    Tests that the longest match wins when findings overlap at the same start position.
    """
    obfuscator = Obfuscator(mode="redact")
    line = "key=ABCDEFGH, otherkey=ABC"
    long_finding = Finding(secret_type="Generic Key", location=1, risk="HIGH", content="ABCDEFGH", confidence=0.9, start=4, end=12)
    short_finding = Finding(secret_type="Generic Key", location=1, risk="HIGH", content="ABC", confidence=0.9, start=4, end=7)
    findings = [long_finding, short_finding]

    result = obfuscator.obfuscate(line, findings)

    redacted_long = obfuscator.obfuscate_content(long_finding.content, long_finding.secret_type)
    assert redacted_long == "A...H"
    assert result == f"key={redacted_long}, otherkey=ABC"
