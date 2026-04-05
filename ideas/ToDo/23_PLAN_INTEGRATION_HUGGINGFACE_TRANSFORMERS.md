# Task: Hugging Face Transformers Integration

## 1. Objective & Context
*   **Goal**: Integrate `secret-scan` into the Hugging Face `transformers` pipeline to detect secrets in prompts and generated outputs.
*   **Rationale**: Hugging Face is the industry standard for LLM models; a native integration allows researchers and developers to prevent leaks during inference.

## 2. Research & Strategy
*   **Research**: Identify the best hook points (e.g., custom `Pipeline` subclass, `StoppingCriteria`, or a wrapper around `model.generate`).
*   **Approach**: Create a `SecretScanCallback` or a wrapper that intercepts input/output strings before/after model execution.
*   **Mocking**: Use `transformers.pipelines.Pipeline` with a mock model or a "Dummy" tokenizer to simulate generation without actual weights.

## 3. Implementation Checklist
- [ ] **Research Phase**:
    - [ ] Document the most idiomatic way to intercept text in `transformers` pipelines.
- [ ] **Integration Component**:
    - [ ] Implement `SecretSafePipeline` or a custom `GenerationConfig` hook.
    - [ ] Add logic to redact/block detected secrets based on `secret-scan` findings.
- [ ] **Testing**:
    - [ ] Create `tests/integrations/test_huggingface.py`.
    - [ ] Implement a `MockLLM` that returns hardcoded strings containing secrets.
    - [ ] Verify that `secret-scan` triggers and blocks the output.

## 4. Engineering Standards
*   **Performance**: Ensure the scan overhead is minimal compared to token generation time.
*   **Safety**: Default to "Block" when a high-confidence secret is found.
