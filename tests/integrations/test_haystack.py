import pytest
from src.sdk import Scanner, SecurityException
from src.integrations.haystack import SecretDocumentRedactorCore, SecretQueryValidatorCore
from tests.test_sdk_core import MockDetector

class MockDocument:
    def __init__(self, content, meta=None):
        self.content = content
        self.meta = meta or {}

@pytest.fixture
def scanner():
    s = Scanner(obfuscate=True)
    s.engine = MockDetector()
    return s

def test_haystack_document_redactor(scanner):
    redactor = SecretDocumentRedactorCore(scanner=scanner)
    docs = [MockDocument("Safe"), MockDocument("Key ghp_12345")]

    result = redactor.run(docs)
    safe_docs = result["documents"]

    assert safe_docs[0].content == "Safe"
    assert "ghp_12345" not in safe_docs[1].content
    assert "g...5" in safe_docs[1].content

def test_haystack_query_validator(scanner):
    validator = SecretQueryValidatorCore(scanner=scanner)
    # Re-init scanner in block mode for validator to match its default behavior
    validator.scanner.obfuscate = False

    with pytest.raises(SecurityException):
        validator.run("Find ghp_12345")
