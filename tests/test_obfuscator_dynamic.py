from src.obfuscator import Obfuscator
from src.report import Finding

def test_dynamic_synthetic_mapping():
    obf = Obfuscator(mode="synthetic")
    
    # Test AWS ID
    f_aws = Finding("aws-id", 1, "HIGH", "AKIA0000000000000000", 1.0, 0, 20, "cloud_credentials")
    res_aws = obf.obfuscate_content(f_aws.content, f_aws.secret_type, f_aws.category)
    assert res_aws.startswith("AKIA")
    assert res_aws != f_aws.content
    
    # Test Slack
    f_slack = Finding("slack-token", 1, "HIGH", "xoxb-1234-5678-abcdef", 1.0, 0, 20, "api_keys")
    res_slack = obf.obfuscate_content(f_slack.content, f_slack.secret_type, f_slack.category)
    assert res_slack.startswith("xoxb-")
    
    # Test Fallback
    f_unknown = Finding("unknown-type", 1, "LOW", "some-random-string", 0.5, 0, 18, "unknown_cat")
    res_unknown = obf.obfuscate_content(f_unknown.content, f_unknown.secret_type, f_unknown.category)
    assert len(res_unknown) == 18
    assert res_unknown != f_unknown.content

def test_obfuscate_with_categories():
    obf = Obfuscator(mode="synthetic")
    text = "My AWS key is AKIA0000000000000000 and my email is test@example.com"
    
    findings = [
        Finding("aws-id", 1, "HIGH", "AKIA0000000000000000", 1.0, 14, 34, "cloud_credentials"),
        Finding("email", 1, "LOW", "test@example.com", 0.5, 51, 67, "authentication")
    ]
    
    result = obf.obfuscate(text, findings)
    assert "AKIA" in result
    assert "@" in result
    assert "AKIA0000000000000000" not in result
    assert "test@example.com" not in result
