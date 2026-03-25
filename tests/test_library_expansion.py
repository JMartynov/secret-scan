from detector import SecretDetector, DetectionEngine
from obfuscator import Obfuscator

def test_taxonomy_loading():
    # Verify that detector loads rules from multiple subdirectories
    detector = SecretDetector(data_dir='data')
    rules = detector.engine.rules
    categories = {r.get('category') for r in rules}
    
    expected_categories = ['api_keys', 'cloud_credentials', 'database_credentials', 'private_keys']
    for cat in expected_categories:
        assert cat in categories, f"Category {cat} not found in loaded rules"

def test_expanded_rule_schema_defaults():
    engine = DetectionEngine(data_dir='data')
    for rule in engine.rules:
        assert 'engine' in rule
        assert 'severity' in rule
        assert 'confidence' in rule
        assert 'entropy_required' in rule
        assert 'min_entropy' in rule

def test_entropy_thresholds():
    engine = DetectionEngine()
    
    # Hex data
    hex_data = "abc123def456"
    assert engine.get_default_threshold(hex_data) == 3.0
    
    # Base64 data
    b64_data = "YmFzZTY0LWVuY29kZWQtc3RyaW5nLXdpdGgtZW5vdWdoLWVudHJvcHk="
    assert engine.get_default_threshold(b64_data) == 4.0

def test_contextual_confidence_boost():
    engine = DetectionEngine()
    rule = {
        'id': 'test_rule',
        'keywords': ['secret', 'api'],
        'entropy': 3.5
    }
    
    # Normal score
    base_confidence = 0.5
    line_normal = "here is a value: abc123def456"
    score_normal = engine.calculate_confidence(base_confidence, line_normal, rule)
    
    # Boosted score
    line_boosted = "here is the secret api key: abc123def456"
    score_boosted = engine.calculate_confidence(base_confidence, line_boosted, rule)
    
    assert score_boosted > score_normal

def test_contextual_confidence_suppression():
    engine = DetectionEngine()
    rule = {'id': 'test_rule', 'keywords': []}
    
    base_confidence = 0.8
    line_normal = "my_key = 'abc123def456'"
    score_normal = engine.calculate_confidence(base_confidence, line_normal, rule)
    
    line_suppressed = "my_test_key = 'abc123def456' # This is a test"
    score_suppressed = engine.calculate_confidence(base_confidence, line_suppressed, rule)
    
    assert score_suppressed < score_normal

def test_obfuscator_decoding():
    obfuscator = Obfuscator()
    
    # URL Encoded
    encoded = "p%40ssword"
    assert obfuscator.decode_if_encoded(encoded) == "p@ssword"
    
    # Base64 (using a clear string)
    b64 = "SGVsbG8gV29ybGQ=" # Hello World
    assert obfuscator.decode_if_encoded(b64) == "Hello World"

def test_synthetic_generation_taxonomy():
    obfuscator = Obfuscator(mode="synthetic")
    
    # Passing category, secret_type, length
    aws_id = obfuscator._generate_synthetic("cloud_credentials", "aws_api_id", 20)
    assert aws_id.startswith("AKIA")
    
    github_token = obfuscator._generate_synthetic("api_keys", "github_token", 40)
    assert github_token.startswith("ghp_")
    
    slack_token = obfuscator._generate_synthetic("api_keys", "slack_token", 50)
    assert slack_token.startswith("xoxb-")
