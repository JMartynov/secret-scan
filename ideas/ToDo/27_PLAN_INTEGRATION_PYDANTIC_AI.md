# Task: Pydantic & Pydantic AI Integration (Structured Security)

## 1. Objective & Context
*   **Goal**: Integrate `py-secret-scan` into Pydantic models and Pydantic AI agents to validate and redact secrets in structured LLM outputs.
*   **Rationale**: Pydantic is the standard for structured data validation; secret detection in JSON responses from LLMs is critical for secure software integration.

## 2. Research & Guardrails Best Practices
Based on industry best practices for structured LLM guardrails:
*   **Output Constraints**: When forcing an LLM to generate structured output (e.g., JSON), the validation layer should verify not only the types but also the semantic safety of the data.
*   **Field-Level Validation**: Use Pydantic's `field_validator` or `model_validator` to intercept strings before the object is fully instantiated.
*   **Secret Masking vs. Error Throwing**: In structured outputs, throwing a `ValidationError` forces the LLM orchestrator (like Pydantic AI or Instructor) to retry generation. If retries are exhausted, you can fallback to redaction.
*   **Custom Types**: Creating a custom Pydantic type (e.g., `SafeString`) allows for reusable security across many models without writing redundant validators.

## 3. Implementation Examples

Here are 3 examples of integrating `py-secret-scan` into Pydantic using the SDK.

### Example 1: Pydantic Custom Validator (Throws Error for Retries)
```python
from pydantic import BaseModel, field_validator
from secret_scan.sdk import Scanner

scanner = Scanner()

class AgentResponse(BaseModel):
    thought: str
    action_input: str

    @field_validator('action_input')
    @classmethod
    def check_for_secrets(cls, v: str) -> str:
        results = scanner.scan(v)
        if any(r.risk in ["HIGH", "CRITICAL"] for r in results):
            raise ValueError("High-risk secret detected in action input. Please regenerate.")
        return v

# Usage
# If the LLM generates a secret, Pydantic will raise a ValidationError, 
# which Pydantic AI can catch and send back to the LLM as a retry prompt.
```

### Example 2: Pydantic Custom Validator (Auto-Redacting)
```python
from pydantic import BaseModel, model_validator
from secret_scan.sdk import Scanner

class RedactedResponse(BaseModel):
    summary: str
    details: str

    @model_validator(mode='after')
    def redact_all_fields(self) -> 'RedactedResponse':
        scanner = Scanner(obfuscate=True, obfuscate_mode="redact")
        self.summary = scanner.redact(self.summary)
        self.details = scanner.redact(self.details)
        return self

# Usage
# response = RedactedResponse(summary="Found key", details="sk-12345")
# print(response.details) # Outputs redacted version
```

### Example 3: Pydantic AI Agent Post-Processor
```python
from pydantic_ai import Agent, RunContext
from secret_scan.sdk import Scanner

agent = Agent('openai:gpt-4o')
scanner = Scanner(obfuscate=True, obfuscate_mode="synthetic")

@agent.result_validator
def sanitize_result(ctx: RunContext[str], result: str) -> str:
    """Scans and redacts the final result string from the agent."""
    return scanner.redact(result)

# Usage
# result = agent.run_sync('Give me a random AWS key for testing.')
# print(result.data) # Contains synthetic key
```

## 4. Integration Tests

Create `tests/integrations/test_pydantic_ai.py`. We use a mock LLM structure.

```python
import pytest
from pydantic import BaseModel, ValidationError, field_validator
from secret_scan.sdk import Scanner

scanner = Scanner()

class LLMOutput(BaseModel):
    query: str
    result: str

    @field_validator('result')
    @classmethod
    def no_secrets_allowed(cls, v: str) -> str:
        if any(r.risk in ["HIGH", "CRITICAL"] for r in scanner.scan(v)):
            raise ValueError("Secret detected")
        return v

def test_pydantic_validation_blocks_secret():
    # Setup leaky LLM response
    leaky_response = {
        "query": "get token",
        "result": "ghp_1234567890abcdefghijklmnopqrstuvwx"
    }
    
    # Assertions
    with pytest.raises(ValidationError) as exc_info:
        LLMOutput(**leaky_response)
        
    assert "Secret detected" in str(exc_info.value)

def test_pydantic_validation_allows_safe_text():
    safe_response = {
        "query": "get token",
        "result": "I cannot provide a token."
    }
    obj = LLMOutput(**safe_response)
    assert obj.result == "I cannot provide a token."
```