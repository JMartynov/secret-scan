import pytest
from pydantic import BaseModel, field_validator, ValidationError
from src.integrations.pydantic_ai import secret_validator, secret_redactor
from src.sdk import Scanner, SecurityException
from tests.test_sdk_core import MockDetector

# Patch the global scanner used in the pydantic integration module for testing
import src.integrations.pydantic_ai as p_ai
def mock_scanner_factory(*args, **kwargs):
    s = Scanner(*args, **kwargs)
    s.engine = MockDetector()
    return s
p_ai.Scanner = mock_scanner_factory

class MockModelBlock(BaseModel):
    query: str

    @field_validator('query')
    @classmethod
    def block_secrets(cls, v: str) -> str:
        return secret_validator(v)

class MockModelRedact(BaseModel):
    query: str

    @field_validator('query')
    @classmethod
    def redact_secrets(cls, v: str) -> str:
        return secret_redactor(v)

def test_pydantic_validator_block():
    with pytest.raises(SecurityException):
        MockModelBlock(query="ghp_12345")

def test_pydantic_validator_redact():
    model = MockModelRedact(query="My token is ghp_12345")
    assert "ghp_12345" not in model.query
    assert "g...5" in model.query
