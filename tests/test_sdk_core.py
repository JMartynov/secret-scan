import pytest
import asyncio
from src.sdk import Scanner, SecurityException, secure_prompt, AsyncScanner
from src.report import Finding

class MockDetectorEngine:
    def detect(self, text):
        if "ghp_" in text:
            f = Finding(secret_type="github_token", location=0, risk="CRITICAL", content="ghp_12345")
            f.start = text.find("ghp_12345")
            f.end = text.find("ghp_12345")+9
            return [f]
        return []

class MockDetector:
    def __init__(self, data_dir='data'):
        self.engine = MockDetectorEngine()

@pytest.fixture
def scanner():
    s = Scanner(obfuscate=True)
    s.engine = MockDetector()
    return s

def test_sdk_redaction_with_mock(scanner):
    input_text = "My token is ghp_12345"
    output = scanner.redact(input_text)

    assert "ghp_12345" not in output
    assert "g...5" in output

def test_sdk_blocking_mode(scanner):
    with pytest.raises(SecurityException) as excinfo:
        scanner.validate("Here is a token: ghp_12345")

    assert "Security violation" in str(excinfo.value)

def test_secure_prompt_decorator(monkeypatch):
    # Patch Scanner to use our mock
    def mock_init(self, *args, **kwargs):
        self.engine = MockDetector()
        self.obfuscate = kwargs.get('obfuscate', False)
        from src.obfuscator import Obfuscator
        self.obfuscator = Obfuscator(mode=kwargs.get('obfuscate_mode', 'redact')) if self.obfuscate else None
        self.min_risk_level = kwargs.get('min_risk_level', 'LOW')
        self._risk_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    monkeypatch.setattr(Scanner, '__init__', mock_init)

    @secure_prompt(obfuscate=True)
    def ask_ai(question: str):
        return f"AI received safe question: {question}"

    result = ask_ai("How do I use ghp_12345?")
    assert "ghp_12345" not in result
    assert "g...5" in result

@pytest.mark.asyncio
async def test_async_scanner():
    s = AsyncScanner(obfuscate=True)
    s.engine = MockDetector()

    input_text = "My async token is ghp_12345"
    output = await s.redact(input_text)

    assert "ghp_12345" not in output
    assert "g...5" in output
