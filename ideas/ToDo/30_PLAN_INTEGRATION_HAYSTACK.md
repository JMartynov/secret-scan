# Task: Haystack Integration (Enterprise Search Security)

## 1. Objective & Context
*   **Goal**: Integrate `secret-scan` into Haystack 2.x pipelines to ensure enterprise-level security for search and RAG workflows.
*   **Rationale**: Haystack is a leading enterprise search framework; its modular pipeline architecture allows for easy integration of custom secret scanning nodes.

## 2. Research & Strategy
*   **Research**: Explore Haystack 2.x `Component` API and how to create a custom node for secret detection.
*   **Approach**: Create a `SecretScanComponent` that can be inserted anywhere in a Haystack pipeline (e.g., after retrieval, before generation).
*   **Mocking**: Use Haystack's `InMemoryDocumentStore` and `MockGenerator` for testing.

## 3. Implementation Checklist
- [ ] **Research Phase**:
    - [ ] Document the Haystack 2.x `component` decorator and I/O typing requirements.
- [ ] **Integration Component**:
    - [ ] Implement `haystack_secret_scan.SecretScanner` component.
    - [ ] Add support for conditional branching in the pipeline if a secret is found.
- [ ] **Testing**:
    - [ ] Create `tests/integrations/test_haystack.py`.
    - [ ] Build a small RAG pipeline with a `SecretScanner` node.
    - [ ] Verify that the scanner correctly blocks results containing "mock secrets."

## 4. Engineering Standards
*   **Reusability**: The component should be usable for both input validation and output filtering.
*   **Type Safety**: Must correctly handle Haystack's `Document` and `GeneratedAnswer` types.
