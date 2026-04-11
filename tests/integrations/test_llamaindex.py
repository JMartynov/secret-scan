import pytest
from src.sdk import Scanner
from src.integrations.llamaindex import SecretScannerNodeParser, SecureLLM
from tests.test_sdk_core import MockDetector

class MockNode:
    def __init__(self, text):
        self.text = text

class MockLLM:
    def complete(self, prompt, **kwargs):
        return f"Completed: {prompt}"

@pytest.fixture
def scanner():
    s = Scanner(obfuscate=True)
    s.engine = MockDetector()
    return s

def test_llamaindex_node_parser(scanner):
    parser = SecretScannerNodeParser(scanner=scanner)
    nodes = [MockNode("Safe text"), MockNode("Leaky ghp_12345 text")]

    parsed_nodes = parser(nodes)

    assert parsed_nodes[0].text == "Safe text"
    assert "ghp_12345" not in parsed_nodes[1].text
    assert "g...5" in parsed_nodes[1].text

def test_llamaindex_secure_llm(scanner):
    llm = MockLLM()
    secure_llm = SecureLLM(llm, scanner=scanner)

    result = secure_llm.complete("Use ghp_12345")
    assert "ghp_12345" not in result
    assert "g...5" in result
