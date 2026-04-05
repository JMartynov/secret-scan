# Task: LangChain Integration (Callbacks & Runnables)

## 1. Objective & Context
*   **Goal**: Create a native `SecretScanCallbackHandler` for LangChain to automatically scan all inputs and outputs within a chain or agent.
*   **Rationale**: LangChain is the most popular orchestrator; automated secret detection in chains is critical for security.

## 2. Research & Strategy
*   **Research**: Explore `BaseCallbackHandler` and `AsyncCallbackHandler` for lifecycle hooks like `on_llm_start` and `on_llm_end`.
*   **Approach**: Create a handler that uses the `secret-scan` API to validate `serialized` messages and `outputs`.
*   **Mocking**: Use `FakeListLLM` from `langchain_community` to provide pre-defined responses.

## 3. Implementation Checklist
- [ ] **Research Phase**:
    - [ ] Document the correct handler methods to override (`on_llm_start`, `on_llm_end`, `on_chain_start`).
- [ ] **Integration Component**:
    - [ ] Implement `langchain_secret_scan.SecretScanHandler`.
    - [ ] Add support for redacting secrets before they reach the LLM or final output.
- [ ] **Testing**:
    - [ ] Create `tests/integrations/test_langchain.py`.
    - [ ] Use `FakeListLLM` to simulate a "leaky" model response.
    - [ ] Verify the callback correctly blocks the response and raises a `SecurityException`.

## 4. Engineering Standards
*   **Modularity**: The handler should be usable at the chain level or global level.
*   **Async Support**: Must implement both sync and async versions.
