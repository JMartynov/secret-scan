# Task: Pydantic & Pydantic AI Integration (Structured Security)

## 1. Objective & Context
*   **Goal**: Integrate `secret-scan` into Pydantic models and Pydantic AI agents to validate and redact secrets in structured LLM outputs.
*   **Rationale**: Pydantic is the standard for structured data validation; secret detection in JSON responses from LLMs is critical for secure software integration.

## 2. Research & Strategy
*   **Research**: Explore Pydantic `field_validator` and custom types; for Pydantic AI, investigate custom agent tools and response validation.
*   **Approach**: Create a `SecretStr` custom Pydantic type or a global `SecretScanValidator`.
*   **Mocking**: Use `MockLLM` with Pydantic AI's `capture_run` to simulate an agent's response.

## 3. Implementation Checklist
- [ ] **Research Phase**:
    - [ ] Document the correct way to add a global `field_validator` to Pydantic models for secret detection.
- [ ] **Integration Component**:
    - [ ] Implement `SecretSafeModel` subclass for Pydantic.
    - [ ] Create a Pydantic AI `AgentResult` post-processor that scans for secrets before finalizing the response.
- [ ] **Testing**:
    - [ ] Create `tests/integrations/test_pydantic_ai.py`.
    - [ ] Simulate a Pydantic AI agent returning a valid JSON object containing a secret.
    - [ ] Verify that the validator triggers and returns a validation error or redacted field.

## 4. Engineering Standards
*   **Type Safety**: Ensure the validation logic integrates with Pydantic's type system correctly.
*   **Error Reporting**: Provide clear, non-leaky validation error messages.
