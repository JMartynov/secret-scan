# Task: vLLM Integration (High-Throughput Security)

## 1. Objective & Context
*   **Goal**: Integrate `secret-scan` into the vLLM API server to provide a secure gateway for high-throughput LLM serving.
*   **Rationale**: vLLM is the leading library for high-performance serving; adding secret scanning at the server level ensures all requests and responses are checked for leaks.

## 2. Research & Strategy
*   **Research**: Explore vLLM's `FastAPI`-based API server and its support for custom middleware or generation hooks.
*   **Approach**: Create a `SecretScanMiddleware` that intercepts `/v1/chat/completions` requests and responses.
*   **Mocking**: Use `vllm.entrypoints.api_server` with a mock engine or a local endpoint test.

## 3. Implementation Checklist
- [ ] **Research Phase**:
    - [ ] Document the correct way to add middleware to the vLLM FastAPI server.
- [ ] **Integration Component**:
    - [ ] Implement `vllm_secret_scan.Middleware` to scan input prompts and streaming chunks.
    - [ ] Add support for canceling a generation if a secret is detected in the stream.
- [ ] **Testing**:
    - [ ] Create `tests/integrations/test_vllm.py`.
    - [ ] Use `httpx` to send requests to a mock vLLM server.
    - [ ] Verify that prompts containing secrets are blocked with a 400 error.

## 4. Engineering Standards
*   **Streaming Support**: Must support real-time scanning of token streams without breaking the connection.
*   **Throughput**: Minimize impact on tokens-per-second (TPS).
