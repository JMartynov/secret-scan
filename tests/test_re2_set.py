import pytest
from detector import SecretDetector, DetectionEngine
import re2

def test_re2_set_consistency():
    engine = DetectionEngine(data_dir="data")
    assert getattr(engine, "re2_set_compiled", False) == True, "re2_set should be compiled"

    # Text that triggers one specific rule (e.g. AWS access key)
    test_text = "Here is my key: AKIAIOSFODNN7EXAMPLE"

    # 1. Run full regex matching (ignoring keywords to be sure)
    traditional_matches = set()
    for rule in engine.re2_rules:
        if list(rule['regex'].finditer(test_text)):
            traditional_matches.add(rule['set_idx'])

    # 2. Run re2.Set match
    set_matches = set(engine.re2_set.Match(test_text))

    # 3. Assert they are consistent
    assert traditional_matches.issubset(set_matches)

def test_re2_set_integration_no_misses():
    # Make sure we don't miss secrets with the re2.Set logic
    detector = SecretDetector(data_dir="data", force_scan_all=True)
    findings = detector.scan("Here is an AWS key AKIAIOSFODNN7EXAMPLE inside some text.")
    assert len(findings) > 0, "Should find the AWS key"

if __name__ == "__main__":
    test_re2_set_consistency()
    test_re2_set_integration_no_misses()
    print("re2_set integration tests passed.")
