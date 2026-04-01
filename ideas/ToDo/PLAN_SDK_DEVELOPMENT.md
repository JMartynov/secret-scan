# Task: SDK Development (Python & JS)

## 1. Objective & Context
*   **Goal**: Create developer-friendly SDKs for Python and JavaScript to integrate scanning into any application.
*   **Rationale**: To increase adoption by making it easy for developers to add security checks to their own AI workflows.
*   **Files Affected**:
    *   `sdks/python/` (New package)
    *   `sdks/js/` (New package)
    *   `examples/` (Usage examples)

## 2. Research & Strategy
*   **Design**: Simple, promise-based (JS) and sync/async (Python) interfaces.
*   **Features**: Scan text, scan files, and "Wrap" LLM calls.
*   **Distribution**: Publish to PyPI and NPM.

## 3. Implementation Checklist
- [ ] **Python SDK**: Implement `llm-guard-py` with `scan()` and `redact()` functions.
- [ ] **JavaScript SDK**: Implement `@llm-guard/sdk` for Node.js and Browser.
- [ ] **LLM Wrappers**: Add helper decorators/functions to automatically scan LangChain or OpenAI inputs.
- [ ] **Local Mode**: Allow the SDK to run the detection engine locally (RE2) or via the SaaS API.
- [ ] **Documentation**: Generate API reference docs for both languages.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test SDK functions against both local engine and mock API responses.
- [ ] Verify error handling for network timeouts and invalid API keys.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: A Python developer imports the SDK and scans a string in 3 lines of code.
- [ ] **Scenario**: A JS developer uses the SDK to redact a prompt before sending it to a model.
- [ ] **Scenario**: The SDK correctly handles rate limit errors from the SaaS API.

## 5. Demo & Documentation
- [ ] **Getting Started**: Create a "Quickstart" guide for each language.
- [ ] **Examples**: Provide sample code for common frameworks (Django, Express, FastAPI).

## 6. Engineering Standards
*   **Idiomatic Code**: Ensure the SDK follows the conventions of its respective language (e.g., PEP 8 for Python, CamelCase for JS).
*   **Zero Dependencies**: Keep the JS SDK lightweight to avoid bloating client-side bundles.
