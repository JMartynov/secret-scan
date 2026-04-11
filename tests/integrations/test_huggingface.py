import pytest
from src.sdk import Scanner
from src.integrations.huggingface import SecurePipeline
from tests.test_sdk_core import MockDetector

class MockHFPipeline:
    def __call__(self, *args, **kwargs):
        # Return what it received as generated text
        if args and isinstance(args[0], list):
             return [{"generated_text": f"Output: {a}"} for a in args[0]]
        return [{"generated_text": f"Output: {args[0]}"}]

@pytest.fixture
def scanner():
    s = Scanner(obfuscate=True)
    s.engine = MockDetector()
    return s

def test_secure_pipeline(scanner):
    pipeline = MockHFPipeline()
    secure_pipeline = SecurePipeline(pipeline, scanner=scanner)

    result = secure_pipeline("Here is my ghp_12345")

    assert "ghp_12345" not in result[0]["generated_text"]
    assert "g...5" in result[0]["generated_text"]

class MockTokenizer:
    def decode(self, tokens, **kwargs):
        if tokens == "bad":
            return "ghp_12345"
        return "safe"

class MockStoppingCriteriaArgs:
    pass

def test_huggingface_stopping_criteria(scanner):
    from src.integrations.huggingface import SecretScanStoppingCriteria
    tokenizer = MockTokenizer()
    criteria = SecretScanStoppingCriteria(tokenizer, scanner=scanner)

    # Test safe
    input_ids_safe = {0: "safe"}
    # mock tensor indexing
    class MockTensorSafe:
        def __getitem__(self, item):
            return "safe"
    assert not criteria(MockTensorSafe(), None)

    # Test bad
    class MockTensorBad:
        def __getitem__(self, item):
            return "bad"
    assert criteria(MockTensorBad(), None)
