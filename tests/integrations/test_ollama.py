import pytest
from src.sdk import Scanner
from src.integrations.ollama import SecureOllamaClient
from tests.test_sdk_core import MockDetector

class MockOllamaClientBase:
    def chat(self, model, messages, **kwargs):
        return {"message": {"content": f"Reply to {messages[0]['content']}"}}

@pytest.fixture
def scanner():
    s = Scanner(obfuscate=True)
    s.engine = MockDetector()
    return s

def test_ollama_secure_client(scanner):
    client = MockOllamaClientBase()
    secure_client = SecureOllamaClient(client, scanner=scanner)

    messages = [{"role": "user", "content": "Here is ghp_12345"}]
    response = secure_client.chat(model="llama3", messages=messages)

    assert "ghp_12345" not in response["message"]["content"]
    assert "g...5" in response["message"]["content"]
