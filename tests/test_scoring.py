import pytest
from src.detector import DetectionEngine, SecretDetector

def test_scoring_weights():
    engine = DetectionEngine()
    # Tier 1 vs Tier 2
    # Tier 1 base score 0.8 => 70 points
    # Score = Base_Weight * Confidence
    # base_score 0.8 => weight 70, confidence 0.8 => score 56
    conf1, score1, _ = engine.calculate_confidence(0.8, "Here is a secret: abcd1234efgh5678ijkl9012", {'keywords': []}, "abcd1234efgh5678ijkl9012", 18)
    assert score1 == 56.0
    
    # Tier 2 base score 0.7 => 40 points
    # base_score 0.7 => weight 40, confidence 0.7 => score 28
    conf2, score2, _ = engine.calculate_confidence(0.7, "Here is a secret: abcd1234efgh5678ijkl9012", {'keywords': []}, "abcd1234efgh5678ijkl9012", 18)
    assert score2 == 28.0

def test_context_decay():
    engine = DetectionEngine()
    rule = {'keywords': ['password']}
    
    # Keyword adjacent (distance ~10)
    # line: "password: abcd1234efgh5678ijkl9012"
    # match is at index 10, keyword at index 0. distance = 10
    _, score_adjacent, _ = engine.calculate_confidence(0.8, "password: abcd1234efgh5678ijkl9012", rule, "abcd1234efgh5678ijkl9012", 10)
    
    # Keyword far (distance ~60)
    # line: "password is set in the configuration file far away: abcd1234efgh5678ijkl9012"
    # match is at index 54, keyword at index 0. distance = 54
    _, score_far, _ = engine.calculate_confidence(0.8, "password is set in the configuration file far away: abcd1234efgh5678ijkl9012", rule, "abcd1234efgh5678ijkl9012", 54)
    
    # The adjacent score should have a higher context bonus
    assert score_adjacent > score_far

def test_context_window_and_intent_boost():
    engine = DetectionEngine()
    rule = {'keywords': ['key']}
    
    # Text with an intent marker in the window
    text = "here is my api key: abcd1234efgh5678ijkl9012"
    
    _, score_with_intent, _ = engine.calculate_confidence(
        base_score=0.7, 
        line=text, 
        rule=rule, 
        match_content="abcd1234efgh5678ijkl9012", 
        start_pos=20, 
        context_window=text
    )
    
    # Text without an intent marker
    text_no_intent = "the system uses key: abcd1234efgh5678ijkl9012"
    
    _, score_without_intent, _ = engine.calculate_confidence(
        base_score=0.7, 
        line=text_no_intent, 
        rule=rule, 
        match_content="abcd1234efgh5678ijkl9012", 
        start_pos=20, 
        context_window=text_no_intent
    )
    
    # Score should be higher due to the intent marker boost
    assert score_with_intent > score_without_intent

def test_score_capping():
    engine = DetectionEngine()
    rule = {'keywords': ['secret']}
    # Base 0.8 => 70
    # Context (adjacent) => ~20
    # High entropy (>4.5) => 15
    # Total ~ 105, should cap at 100
    
    high_entropy_secret = "aB3!z9$kPq2@wXy7#vN5^mC8&jL4*hG"
    # To hit 100, we need Confidence to be higher. Let's make it 1.0 (requires another keyword maybe)
    conf, score, _ = engine.calculate_confidence(1.0, f"secret: {high_entropy_secret}", rule, high_entropy_secret, 8)
    
    assert score == 100.0

def test_negative_scoring():
    engine = DetectionEngine()
    rule = {'keywords': ['key']}
    # Base 0.8 => 70
    # penalty => -50
    _, score, _ = engine.calculate_confidence(0.8, "key: EXAMPLE_KEY_12345", rule, "EXAMPLE_KEY_12345", 5)
    
    # Score should be significantly lower
    assert score <= 30
