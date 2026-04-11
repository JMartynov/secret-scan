import pytest
from src.sdk import Scanner
from src.integrations.vllm import SecureVLLMGenerator
from tests.test_sdk_core import MockDetector

class MockOutput:
    def __init__(self, text):
        self.text = text

class MockVLLMOutput:
    def __init__(self, text):
        self.outputs = [MockOutput(text)]

class MockVLLM:
    def generate(self, prompts, **kwargs):
        return [MockVLLMOutput(f"Generated from: {p}") for p in prompts]

@pytest.fixture
def scanner():
    s = Scanner(obfuscate=True)
    s.engine = MockDetector()
    return s

def test_vllm_secure_generator(scanner):
    vllm = MockVLLM()
    secure_vllm = SecureVLLMGenerator(vllm, scanner=scanner)

    prompts = ["Hello", "Use key ghp_12345"]
    outputs = secure_vllm.generate(prompts)

    assert outputs[0].outputs[0].text == "Generated from: Hello"
    assert "ghp_12345" not in outputs[1].outputs[0].text
    assert "g...5" in outputs[1].outputs[0].text
