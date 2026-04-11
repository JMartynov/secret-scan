# Task: Ollama Integration (Local Security Proxy)

## 1. Objective & Context
*   **Goal**: Integrate `py-secret-scan` into Ollama workflows to detect secrets when running LLMs locally.
*   **Rationale**: Ollama is the top tool for local model usage; ensuring local privacy by scanning prompts before they hit the model is essential.

## 2. Research & Guardrails Best Practices
Based on industry best practices for local LLM guardrails:
*   **Proxy Pattern**: The most effective way to secure a standalone binary like Ollama is via a reverse proxy (e.g., intercepting `localhost:11434`). This secures both the CLI and any downstream clients using the API.
*   **Local-First Processing**: Ensure the guardrail logic runs entirely locally to maintain Ollama's privacy benefits.
*   **Streaming Interception**: Ollama defaults to streaming responses. The proxy must be able to buffer or stream-scan the chunks as they return from the Ollama server.
*   **CLI Wrappers**: Providing a simple CLI wrapper (e.g., `secret-scan ollama run llama3`) creates a seamless developer experience without needing to manually configure proxies.

## 3. Implementation Examples

Here are 3 examples of integrating `py-secret-scan` with Ollama using the SDK.

### Example 1: Local API Proxy (FastAPI)
```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from secret_scan.sdk import Scanner

app = FastAPI()
scanner = Scanner()
OLLAMA_URL = "http://localhost:11434"

@app.post("/api/generate")
async def generate_proxy(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    
    # 1. Scan Input
    results = scanner.scan(prompt)
    if any(r.risk in ["HIGH", "CRITICAL"] for r in results):
        return JSONResponse(status_code=400, content={"error": "Secret blocked in prompt"})
        
    # 2. Forward to Ollama
    client = httpx.AsyncClient()
    req = client.build_request("POST", f"{OLLAMA_URL}/api/generate", json=body)
    r = await client.send(req, stream=True)
    
    # 3. Stream back (optional output scanning could be added here)
    async def stream_response():
        async for chunk in r.aiter_bytes():
            yield chunk
            
    return StreamingResponse(stream_response(), media_type=r.headers.get("content-type"))

# Run via: uvicorn proxy:app --port 11435
```

### Example 2: Python Client Wrapper
```python
import ollama
from secret_scan.sdk import Scanner

scanner = Scanner(obfuscate=True, obfuscate_mode="synthetic")

def safe_chat(model: str, messages: list):
    # Sanitize inputs
    for msg in messages:
        msg['content'] = scanner.redact(msg['content'])
        
    # Call Ollama
    response = ollama.chat(model=model, messages=messages)
    
    # Sanitize output
    response['message']['content'] = scanner.redact(response['message']['content'])
    return response

# Usage
# messages = [{'role': 'user', 'content': 'Is my key sk-12345 secure?'}]
# print(safe_chat('llama3', messages))
```

### Example 3: Subprocess CLI Wrapper
```python
import subprocess
import sys
from secret_scan.sdk import Scanner

def run_safe_ollama(prompt: str, model="llama3"):
    scanner = Scanner()
    
    if any(r.risk in ["HIGH", "CRITICAL"] for r in scanner.scan(prompt)):
        print("Error: Prompt contains a secret. Aborting.")
        sys.exit(1)
        
    process = subprocess.Popen(
        ['ollama', 'run', model],
        stdin=subprocess.PIPE,
        text=True
    )
    process.communicate(input=prompt)

# Usage
# run_safe_ollama("Write code to use AWS key AKIAIOSFODNN7EXAMPLE")
```

## 4. Integration Tests

Create `tests/integrations/test_ollama.py`. We use a mock HTTP client to simulate the proxy.

```python
import pytest
from secret_scan.sdk import Scanner

class MockOllamaClient:
    def __init__(self):
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def chat(self, model, messages):
        # Apply security wrapper
        safe_messages = []
        for msg in messages:
            safe_messages.append({
                "role": msg["role"],
                "content": self.scanner.redact(msg["content"])
            })
            
        # Mock LLM logic
        user_msg = safe_messages[0]["content"]
        response_text = f"I received: {user_msg}"
        return {"message": {"role": "assistant", "content": response_text}}

def test_ollama_client_wrapper():
    # Setup
    client = MockOllamaClient()
    
    # Run leaky prompt
    messages = [{"role": "user", "content": "My db is postgres://user:password@localhost"}]
    response = client.chat(model="llama3", messages=messages)
    
    # Assertions
    output = response["message"]["content"]
    assert "postgres://user:password@localhost" not in output
    assert "[REDACTED]" in output or "..." in output
```
