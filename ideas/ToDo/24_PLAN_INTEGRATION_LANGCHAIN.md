# Task: LangChain Integration (Callbacks & Runnables)

## 1. Objective & Context
*   **Goal**: Create a native `SecretScanCallbackHandler` for LangChain to automatically scan all inputs and outputs within a chain or agent.
*   **Rationale**: LangChain is the most popular orchestrator; automated secret detection in chains is critical for security.

## 2. Research & Guardrails Best Practices
Based on industry best practices for LLM guardrails:
*   **Defense in Depth**: Combine deterministic secret scanning (`py-secret-scan`) before relying on LLM-as-a-judge (like LlamaGuard) to ensure credentials are caught instantly without adding latency or API costs.
*   **Middleware Approach**: LangChain treats guardrails best as middleware (using Runnables or Callbacks). Callbacks provide a non-intrusive way to monitor execution globally.
*   **Input and Output Layers**: Use `on_llm_start` to intercept and redact prompts sent to the LLM. Use `on_llm_end` to scan responses from the LLM.
*   **Fail Gracefully**: Redacting the secret is preferred for smooth conversational flows, but throwing an explicit `SecurityException` is safer for high-risk applications.

## 3. Implementation Examples

Here are 3 examples of integrating `py-secret-scan` into LangChain using the SDK.

### Example 1: Global Callback Handler
```python
from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from secret_scan.sdk import Scanner

class SecretScanCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        # Scan and redact inputs before they hit the LLM
        for i, prompt in enumerate(prompts):
            prompts[i] = self.scanner.redact(prompt)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        # Scan and redact outputs before returning to user
        for generation_list in response.generations:
            for generation in generation_list:
                generation.text = self.scanner.redact(generation.text)

# Usage
from langchain_openai import OpenAI
llm = OpenAI(callbacks=[SecretScanCallbackHandler()])
response = llm.invoke("My API key is sk-12345. How do I use it?")
print(response)
```

### Example 2: Runnable Wrapper (LCEL)
```python
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from secret_scan.sdk import Scanner

scanner = Scanner(obfuscate=True, obfuscate_mode="synthetic")

def scan_input(text: str) -> str:
    return scanner.redact(text)

def scan_output(ai_msg) -> str:
    ai_msg.content = scanner.redact(ai_msg.content)
    return ai_msg

# Create a safe chain
llm = ChatOpenAI()
safe_chain = RunnableLambda(scan_input) | llm | RunnableLambda(scan_output)

# Usage
print(safe_chain.invoke("Translate this: my token is ghp_1234567890abcdefghijklmnopqrstuvwx"))
```

### Example 3: Blocking Execution on High Risk
```python
from langchain_core.callbacks import BaseCallbackHandler
from secret_scan.sdk import Scanner

class SecurityException(Exception):
    pass

class BlockOnSecretCallback(BaseCallbackHandler):
    def __init__(self):
        self.scanner = Scanner()

    def on_llm_start(self, serialized, prompts, **kwargs) -> Any:
        for prompt in prompts:
            results = self.scanner.scan(prompt)
            if any(r.risk in ["HIGH", "CRITICAL"] for r in results):
                raise SecurityException("Blocked: High-risk secret detected in prompt.")

# Usage
# llm = OpenAI(callbacks=[BlockOnSecretCallback()])
# llm.invoke("sk-12345") # Will raise SecurityException
```

## 4. Integration Tests

Create `tests/integrations/test_langchain.py`. We use LangChain's `FakeListLLM` to simulate LLM responses without network calls.

```python
import pytest
from langchain_community.llms.fake import FakeListLLM
from langchain_core.prompts import PromptTemplate
from secret_scan.sdk import Scanner
from langchain_core.callbacks import BaseCallbackHandler

class SecretScanCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def on_llm_start(self, serialized, prompts, **kwargs):
        for i, prompt in enumerate(prompts):
            prompts[i] = self.scanner.redact(prompt)

    def on_llm_end(self, response, **kwargs):
        for gen_list in response.generations:
            for gen in gen_list:
                gen.text = self.scanner.redact(gen.text)

def test_langchain_callback_redaction():
    # Setup Fake LLM that leaks a secret
    leaky_responses = ["Here is the token: ghp_1234567890abcdefghijklmnopqrstuvwx"]
    fake_llm = FakeListLLM(responses=leaky_responses, callbacks=[SecretScanCallbackHandler()])
    
    # Run
    prompt = "What is the token?"
    output = fake_llm.invoke(prompt)
    
    # Assertions
    assert "ghp_1234567890abcdefghijklmnopqrstuvwx" not in output
```
