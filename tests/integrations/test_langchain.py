import pytest
from src.sdk import Scanner, SecurityException
from src.integrations.langchain import SecretScannerRunnable
from tests.test_sdk_core import MockDetector

class MockRunnable:
    def invoke(self, input, **kwargs):
        if hasattr(input, "content"):
            return type(input)(content=f"Echo: {input.content}")
        return f"Echo: {input}"

class MockMessage:
    def __init__(self, content):
        self.content = content
    def to_string(self):
        return self.content

@pytest.fixture
def scanner():
    s = Scanner(obfuscate=True)
    s.engine = MockDetector()
    return s

def test_langchain_runnable_redact(scanner):
    runnable = MockRunnable()
    secure_runnable = SecretScannerRunnable(runnable, scanner=scanner, mode="redact")

    result = secure_runnable.invoke("Key is ghp_12345")
    assert "ghp_12345" not in result
    assert "g...5" in result

def test_langchain_runnable_block(scanner):
    runnable = MockRunnable()
    secure_runnable = SecretScannerRunnable(runnable, scanner=scanner, mode="block")

    with pytest.raises(SecurityException):
        secure_runnable.invoke("Key is ghp_12345")

def test_langchain_runnable_redact_message(scanner):
    runnable = MockRunnable()
    secure_runnable = SecretScannerRunnable(runnable, scanner=scanner, mode="redact")

    msg = MockMessage("Key is ghp_12345")
    result = secure_runnable.invoke(msg)
    assert "ghp_12345" not in result.content
    assert "g...5" in result.content
