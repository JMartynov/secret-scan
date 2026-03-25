from detector import SecretDetector
from report import Finding

def test_overlap_resolution_entropy_vs_structured():
    """
    Ensures that a structured rule (e.g., simulated AWS key) 
    beats a generic high-entropy rule on the same string.
    """
    detector = SecretDetector()
    
    # Simulate findings on the same range [10, 30]
    f1 = Finding("High Entropy String", 1, "MEDIUM", "AKIA1234567890EXAMPLE", 0.4, 10, 30)
    f2 = Finding("aws-access-key", 1, "HIGH", "AKIA1234567890EXAMPLE", 0.8, 10, 30)
    
    resolved = detector._resolve_overlaps([f1, f2])
    assert len(resolved) == 1
    assert resolved[0].secret_type == "aws-access-key"
    assert resolved[0].confidence == 0.8

def test_overlap_resolution_partial():
    """
    Ensures that for partially overlapping findings, the one 
    with higher 'weight' (length * confidence) wins.
    """
    detector = SecretDetector()
    
    # f1: [0, 10], confidence 0.5 -> weight 5.0
    # f2: [5, 15], confidence 0.8 -> weight 8.0
    f1 = Finding("Rule-A", 1, "MEDIUM", "1234567890", 0.5, 0, 10)
    f2 = Finding("Rule-B", 1, "HIGH", "67890ABCDE", 0.8, 5, 15)
    
    resolved = detector._resolve_overlaps([f1, f2])
    assert len(resolved) == 1
    assert resolved[0].secret_type == "Rule-B"

def test_non_overlapping():
    """Ensures that non-overlapping findings are both preserved."""
    detector = SecretDetector()
    
    f1 = Finding("Rule-A", 1, "MEDIUM", "123", 0.8, 0, 3)
    f2 = Finding("Rule-B", 1, "MEDIUM", "456", 0.8, 5, 8)
    
    resolved = detector._resolve_overlaps([f1, f2])
    assert len(resolved) == 2

def test_longest_match_wins():
    """Ensures that the longest match is favored if start/confidence are similar."""
    detector = SecretDetector()
    
    # f1: [0, 5], confidence 0.8 -> weight 4.0
    # f2: [0, 10], confidence 0.8 -> weight 8.0
    f1 = Finding("Short-Rule", 1, "MEDIUM", "12345", 0.8, 0, 5)
    f2 = Finding("Long-Rule", 1, "MEDIUM", "1234567890", 0.8, 0, 10)
    
    resolved = detector._resolve_overlaps([f1, f2])
    assert len(resolved) == 1
    assert resolved[0].secret_type == "Long-Rule"
