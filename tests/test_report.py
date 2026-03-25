from report import Finding, format_report

def test_finding_redaction():
    # Long secret
    f1 = Finding("stripe_api_key", 10, "HIGH", "sk_ignore_000000000000000000000000")
    assert f1.redacted_value == "sk_l...j012"
    
    # Medium secret
    f2 = Finding("generic", 1, "LOW", "12345678")
    assert f2.redacted_value == "1...8"
    
    # Short secret
    f3 = Finding("short", 1, "LOW", "abc")
    assert f3.redacted_value == "****"

def test_format_report_no_findings():
    report = format_report([], no_colors=True)
    assert "No secrets detected" in report

def test_format_report_summary_only():
    findings = [
        Finding("AWS", 1, "HIGH", "AKIA..."),
        Finding("Stripe", 5, "HIGH", "sk_ignore_..."),
        Finding("Entropy", 10, "MEDIUM", "abc123xyz")
    ]
    report = format_report(findings, show_full=False, show_short=False, no_colors=True)
    assert "Secrets detected: 3" in report
    assert "[HIGH]: 2" in report
    assert "[MEDIUM]: 1" in report
    assert "AKIA" not in report # Content should be hidden in summary

def test_format_report_short_mode():
    findings = [
        Finding("Stripe", 5, "HIGH", "sk_ignore_000000000000000000000000")
    ]
    report = format_report(findings, show_short=True, no_colors=True)
    assert "Type: Stripe" in report
    assert "Location: line 5" in report
    assert "Content: sk_l...j012 (redacted)" in report

def test_format_report_full_mode():
    secret = "sk_ignore_000000000000000000000000"
    findings = [
        Finding("Stripe", 5, "HIGH", secret)
    ]
    report = format_report(findings, show_full=True, no_colors=True)
    assert f"Content: {secret}" in report

def test_format_report_sorting_and_deduplication():
    findings = [
        Finding("TypeB", 10, "HIGH", "secret1", confidence=0.5),
        Finding("TypeA", 5, "HIGH", "secret2", confidence=0.8),
        Finding("TypeB", 10, "HIGH", "secret1", confidence=0.9), # Duplicate with higher confidence
    ]
    report = format_report(findings, show_short=True, no_colors=True)
    
    # Check deduplication: only 2 unique findings should remain
    assert "Secrets detected: 2" in report
    
    # Check sorting: line 5 should come before line 10
    details_pos = report.find("--- Details ---")
    line5_pos = report.find("line 5")
    line10_pos = report.find("line 10")
    assert details_pos < line5_pos < line10_pos

def test_format_report_colors():
    findings = [Finding("Type", 1, "HIGH", "secret")]
    # By default format_report uses sys.stdout.isatty() if no_colors=False
    # We can't easily mock isatty() here without more effort, 
    # but we can test if it DOES NOT have colors when no_colors=True
    report_no_color = format_report(findings, no_colors=True)
    assert "\033[" not in report_no_color
