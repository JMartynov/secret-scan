# Task: SDK Development (Python & JS)

## 1. Objective & Context
*   **Goal**: Create developer-friendly SDKs for Python and JavaScript to integrate scanning into any application or AI pipeline.
*   **Rationale**: To increase adoption by making it easy for developers to add security layers to their custom LLM implementations.
*   **Files Affected**:
    *   `sdks/python/`: New package `llm-guard-python`.
    *   `sdks/javascript/`: New package `@llm-guard/sdk`.
    *   `examples/`: Sample integrations with LangChain, OpenAI, and FastAPI.

## 2. Research & Strategy
*   **Design**: Simple, promise-based (JS) and sync/async (Python) interfaces.
*   **Logic**: Primarily a thin wrapper around the Backend API, with an optional "Local Mode" for Python.
*   **Distribution**: Publish to PyPI and NPM.

## 3. Implementation Checklist
- [ ] **Python SDK**: Implement `Scanner` class with `scan(text)` and `redact(text)` methods.
- [ ] **JavaScript SDK**: Implement a lightweight Node.js/Browser compatible client.
- [ ] **LLM Wrappers**: Add helper decorators (Python) or middleware (JS) to automatically scrub inputs to `openai.ChatCompletion`.
- [ ] **Configuration**: Support environment variable based configuration for API keys and endpoints.
- [ ] **Error Handling**: Implement robust retries and graceful degradation if the Backend API is unreachable.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_sdk_api_client`: Verify correct headers and JSON serialization in API requests.
- [ ] `test_redaction_helper`: Assert that the SDK's local redaction logic matches the engine's output.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Python integration in 3 lines (Import -> Initialize -> Scan).
- [ ] **Scenario**: JS middleware in Express (Scrubbing prompts before they hit the controller).
- [ ] **Scenario**: LangChain Wrapper (Automatically redacting secrets in a chain).

### 4.3 Test Data Obfuscation
- [ ] SDK examples must use synthetic secrets and standard `[REDACTED]` placeholders.

## 5. Demo & Documentation
- [ ] **Quickstart Guides**: 2-minute setup guides for both Python and JS.
- [ ] **API Reference**: Auto-generated documentation (Sphinx for Python, TypeDoc for JS).

## 6. Engineering Standards
*   **Tone**: Senior Engineer, developer-focused.
*   **Perf**: Minimal overhead (< 5ms) for the SDK wrapper itself.
*   **Security**: Ensure API keys used by the SDK are never logged or exposed in stack traces.
