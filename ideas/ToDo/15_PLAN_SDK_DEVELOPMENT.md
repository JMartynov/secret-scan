# Task: SDK Development (Python & JS)

## 1. Objective & Context
*   **Goal**: Create developer-friendly SDKs for Python and JavaScript to integrate scanning into any application or AI pipeline.
*   **Rationale**: To increase adoption by making it easy for developers to add security layers to their custom LLM implementations.

## 2. Research & Guardrails Best Practices
Based on industry best practices for security SDKs:
*   **Non-Intrusive Integration**: Provide decorators and context managers so developers can add security with a single line of code.
*   **Local-First Execution**: The Python SDK should default to local execution (direct library calls) to minimize latency and maximize privacy.
*   **Consistent Obfuscation**: Ensure that `redact`, `hash`, and `synthetic` modes are consistent across all SDK methods.
*   **Async/Sync Parity**: Modern AI applications (like those using FastAPI or vLLM) require full `asyncio` support.
*   **Circuit Breakers**: If the scanner encounters an error (e.g., OOM on a massive string), it should fail "open" (allow but log) or "closed" (block) based on user policy, but never crash the process.

## 3. Implementation Examples

Here are 5 examples of using the `py-secret-scan` SDK in common developer workflows.

### Example 1: Basic String Scanning and Redaction
```python
from secret_scan.sdk import Scanner

# Initialize with synthetic obfuscation
scanner = Scanner(obfuscate=True, obfuscate_mode="synthetic")

prompt = "Connect to my db: postgres://admin:password@localhost:5432"
safe_prompt = scanner.redact(prompt)
print(f"Safe: {safe_prompt}") 
# Output: "Connect to my db: postgres://fake_user:fake_pass@localhost:5432"
```

### Example 2: Decorator for Secure Functions
```python
from secret_scan.sdk import secure_prompt

@secure_prompt(obfuscate=True)
def ask_ai(question: str):
    # 'question' is automatically redacted before the function body executes
    return f"AI received safe question: {question}"

print(ask_ai("How do I rotate my AWS key AKIAIOSFODNN7EXAMPLE?"))
```

### Example 3: Context Manager for Batch Processing
```python
from secret_scan.sdk import Scanner

scanner = Scanner()
log_data = ["User logged in", "Key: sk-12345", "User logged out"]

with scanner.session(mode="block") as s:
    for line in log_data:
        # Raises SecurityException on the second line
        s.validate(line)
```

### Example 4: Async Integration for Web Services
```python
import asyncio
from secret_scan.sdk import AsyncScanner

async def handle_request(user_input: str):
    scanner = AsyncScanner(obfuscate=True)
    # Async scanning is ideal for high-throughput API gateways
    safe_input = await scanner.redact(user_input)
    return {"status": "ok", "sanitized": safe_input}
```

### Example 5: Custom Risk Thresholds
```python
from secret_scan.sdk import Scanner

# Only block on Critical risks, allow High/Medium with a warning
scanner = Scanner(min_risk_level="CRITICAL")
result = scanner.scan("Some suspicious but not critical string")
print(f"Is safe: {not result.has_findings}")
```

## 4. Integration Tests

Create `tests/test_sdk_core.py`. We use a mock engine to simulate detection results.

```python
import pytest
from secret_scan.sdk import Scanner
from unittest.mock import MagicMock

class MockDetector:
    """Emulates the core detection engine."""
    def detect(self, text):
        if "ghp_" in text:
            return [{"type": "github_token", "risk": "CRITICAL"}]
        return []

def test_sdk_redaction_with_mock():
    # Setup SDK with a mocked detector engine
    scanner = Scanner(obfuscate=True)
    scanner.engine = MockDetector()
    
    # Test
    input_text = "My token is ghp_12345"
    output = scanner.redact(input_text)
    
    # Assertions
    assert "ghp_12345" not in output
    assert "[REDACTED]" in output

def test_sdk_blocking_mode():
    scanner = Scanner()
    scanner.engine = MockDetector()
    
    with pytest.raises(Exception) as excinfo:
        scanner.validate("Here is a token: ghp_12345")
    
    assert "Security violation" in str(excinfo.value)
```

## 5. Engineering Standards
*   **Performance**: Overhead must be < 2ms for non-matching strings.
*   **Type Safety**: Use Python Type Hints throughout the SDK.
*   **Dependency-Lite**: The SDK should have minimal dependencies to ensure easy installation in varied environments.
