# Task: Ollama Integration (Local Security Proxy)

## 1. Objective & Context
*   **Goal**: Integrate `secret-scan` into Ollama workflows to detect secrets when running LLMs locally.
*   **Rationale**: Ollama is the top tool for local model usage; ensuring local privacy by scanning prompts before they hit the model is essential.

## 2. Research & Strategy
*   **Research**: Explore Ollama's local API (`11434`) and its `generate` / `chat` endpoints.
*   **Approach**: Create an `OllamaSecretScanProxy` or a CLI wrapper that scans inputs before calling the Ollama binary.
*   **Mocking**: Use a mock server that mimics the Ollama API.

## 3. Implementation Checklist
- [ ] **Research Phase**:
    - [ ] Document the Ollama API schema and the best point to intercept local calls.
- [ ] **Integration Component**:
    - [ ] Implement `ollama_secret_scan.Proxy` for intercepting local API requests.
    - [ ] Add a `secret-scan ollama run` CLI wrapper.
- [ ] **Testing**:
    - [ ] Create `tests/integrations/test_ollama.py`.
    - [ ] Send prompts to the proxy and verify it filters secrets before forwarding to a mock Ollama server.

## 4. Engineering Standards
*   **Local-First**: Ensure the scan logic remains local and doesn't leak data.
*   **Simplicity**: Provide a one-command setup for users.
