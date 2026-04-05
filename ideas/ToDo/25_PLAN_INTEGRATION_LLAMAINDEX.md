# Task: LlamaIndex Integration (RAG Security)

## 1. Objective & Context
*   **Goal**: Integrate `secret-scan` into the LlamaIndex query engine to prevent RAG leakage from custom datasets.
*   **Rationale**: LlamaIndex is the top library for RAG; secret detection ensures that retrieved context doesn't contain accidentally indexed credentials.

## 2. Research & Strategy
*   **Research**: Explore `BaseNodePostprocessor` for filtering retrieved nodes and `TransformComponent` for data ingestion.
*   **Approach**: Create a `SecretFilterPostprocessor` that scans retrieved chunks before they are sent to the LLM.
*   **Mocking**: Use `MockLLM` from `llama_index.core.llms` to simulate a response based on retrieved nodes.

## 3. Implementation Checklist
- [ ] **Research Phase**:
    - [ ] Document the `BaseNodePostprocessor` implementation requirements.
- [ ] **Integration Component**:
    - [ ] Implement `SecretScanPostprocessor` to filter out nodes containing secrets.
    - [ ] Add support for redacting secrets in `IngestionPipeline` (data loading phase).
- [ ] **Testing**:
    - [ ] Create `tests/integrations/test_llamaindex.py`.
    - [ ] Use `MockLLM` and a small index containing "mock secret" nodes.
    - [ ] Verify that the query engine filters or redacts the secret nodes correctly.

## 4. Engineering Standards
*   **Data Integrity**: Ensure the filtering logic doesn't corrupt legitimate data chunks.
*   **Granularity**: Provide options to "Redact" (mask the secret) or "Drop" (exclude the entire node).
