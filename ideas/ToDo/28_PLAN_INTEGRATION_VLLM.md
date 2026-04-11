# Task: vLLM Integration (High-Throughput Security)

## 1. Objective & Context
*   **Goal**: Integrate `py-secret-scan` into the vLLM API server to provide a secure gateway for high-throughput LLM serving.
*   **Rationale**: vLLM is the leading library for high-performance serving; adding secret scanning at the server level ensures all requests and responses are checked for leaks.

## 2. Research & Guardrails Best Practices
Based on industry best practices for serving infrastructure guardrails:
*   **Inference-Level Guarding**: vLLM operates at high throughput. The ideal place for guardrails is in the FastAPI middleware (for the API server) or via structured decoding.
*   **Low Latency**: Guardrails must not bottleneck the GPU. A fast, regex-based scanner like `py-secret-scan` is perfectly suited for running on the CPU alongside the vLLM API server without blocking token generation.
*   **Streaming Support**: For streaming endpoints, middleware must intercept chunks as they are yielded. If a secret is detected mid-stream, the connection should be aborted or the chunk redacted before it reaches the client.
*   **Blocking vs Redacting**: At the API level, returning a 400 Bad Request for malicious inputs is standard. For outputs, returning a 500 error or aborting the stream is safer than returning partial redacted data.

## 3. Implementation Examples

Here are 3 examples of integrating `py-secret-scan` into vLLM's FastAPI server using the SDK.

### Example 1: FastAPI Input Middleware (Blocking Secrets)
```python
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from secret_scan.sdk import Scanner

class SecretScanInputMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.scanner = Scanner()

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/v1/chat/completions" and request.method == "POST":
            body = await request.json()
            
            # Scan the messages payload
            messages_text = " ".join([m.get("content", "") for m in body.get("messages", [])])
            results = self.scanner.scan(messages_text)
            
            if any(r.risk in ["HIGH", "CRITICAL"] for r in results):
                return JSONResponse(
                    status_code=400,
                    content={"error": "High-risk secret detected in prompt. Request blocked."}
                )
                
        # Must restore body for the next handlers
        # (Implementation requires Custom Request body caching in FastAPI)
        
        response = await call_next(request)
        return response

# Usage in vLLM API server setup
# app.add_middleware(SecretScanInputMiddleware)
```

### Example 2: Wrapper for Offline Inference (Redaction)
```python
from vllm import LLM, SamplingParams
from secret_scan.sdk import Scanner

llm = LLM(model="facebook/opt-125m")
scanner = Scanner(obfuscate=True, obfuscate_mode="synthetic")
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

def safe_generate(prompts):
    # 1. Redact inputs
    safe_prompts = [scanner.redact(p) for p in prompts]
    
    # 2. Generate
    outputs = llm.generate(safe_prompts, sampling_params)
    
    # 3. Redact outputs
    for output in outputs:
        for idx, generated_text in enumerate(output.outputs):
            output.outputs[idx].text = scanner.redact(generated_text.text)
            
    return outputs

# Usage
# prompts = ["My AWS key is AKIAIOSFODNN7EXAMPLE."]
# print(safe_generate(prompts)[0].outputs[0].text)
```

### Example 3: Output Generator Wrapper for Streaming API
```python
from secret_scan.sdk import Scanner

async def safe_stream_generator(original_generator):
    scanner = Scanner(obfuscate=True, obfuscate_mode="redact")
    
    async for chunk in original_generator:
        # Assuming chunk is a string or a JSON object containing text
        if isinstance(chunk, str):
            yield scanner.redact(chunk)
        else:
            # Modify JSON chunk content
            yield chunk

# Usage
# return StreamingResponse(safe_stream_generator(engine.generate_stream(...)))
```

## 4. Integration Tests

Create `tests/integrations/test_vllm.py`. We use a mock FastAPI server to simulate vLLM's API.

```python
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from secret_scan.sdk import Scanner
import json

class SecretScanInputMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.scanner = Scanner()

    async def dispatch(self, request, call_next):
        body_bytes = await request.body()
        if body_bytes:
            body = json.loads(body_bytes)
            messages_text = " ".join([m.get("content", "") for m in body.get("messages", [])])
            if any(r.risk in ["HIGH", "CRITICAL"] for r in self.scanner.scan(messages_text)):
                return JSONResponse(status_code=400, content={"error": "Secret detected"})
        
        # Restore body for next route
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        request._receive = receive
        return await call_next(request)

app = FastAPI()
app.add_middleware(SecretScanInputMiddleware)

@app.post("/v1/chat/completions")
async def chat_completions(payload: dict):
    return {"choices": [{"message": {"content": "Safe response"}}]}

client = TestClient(app)

def test_vllm_api_blocks_secret_input():
    payload = {
        "model": "opt-125m",
        "messages": [{"role": "user", "content": "My AWS key is AKIAIOSFODNN7EXAMPLE"}]
    }
    
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 400
    assert "Secret detected" in response.json()["error"]

def test_vllm_api_allows_safe_input():
    payload = {
        "model": "opt-125m",
        "messages": [{"role": "user", "content": "Hello world"}]
    }
    
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
```
