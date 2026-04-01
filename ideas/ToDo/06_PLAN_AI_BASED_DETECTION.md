# Task: AI-Based Secret Detection (ML Layer)

## 1. Objective & Context
*   **Goal**: Integrate a lightweight Machine Learning model to detect unconventional secrets that lack structured patterns.
*   **Rationale**: Traditional regex fails to detect "novel" secrets or those embedded in complex natural language without fixed prefixes.
*   **Files Affected**:
    *   `detector.py`: Integrate the ML model into the `SecretDetector` pipeline.
    *   `app/services/ml_engine.py`: Logic for model loading and inference.
    *   `requirements.txt`: Add `onnxruntime` or similar lightweight inference library.

## 2. Research & Strategy
*   **Model**: Use a quantized Transformer-based model (e.g., BERT-tiny) trained on large datasets of leaked vs. synthetic secrets.
*   **Mechanism**: Sliding window classification of text segments.
*   **Engine Choice**: ONNX Runtime for high-performance, CPU-bound inference.

## 3. Implementation Checklist
- [ ] **Model Selection**: Identify or train a lightweight binary classifier for "Secret vs. Non-Secret".
- [ ] **ONNX Integration**: Implement the inference engine in `ml_engine.py` using ONNX for zero-dependency execution.
- [ ] **Feature Extraction**: Implement tokenization and normalization for the input text segments.
- [ ] **Pipeline Hook**: Add the ML scan as a "Deep" mode feature that runs after regex rules have finished.
- [ ] **Confidence Merging**: Implement logic to combine ML confidence with entropy and context scores.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_model_inference`: Verify that the model identifies known unstructured secrets (e.g., unusual password strings).
- [ ] `test_inference_latency`: Assert that ML scanning doesn't increase processing time by more than 100ms per 100KB.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Novel Secret Detection (Model catches a new type of token that wasn't in the regex database).
- [ ] **Scenario**: False Positive Reduction (Model correctly identifies a high-entropy but harmless string as "Non-Secret").
- [ ] **Scenario**: Mode Toggle (ML detection only runs when `--mode deep` is enabled).

### 4.3 Test Data Obfuscation
- [ ] Use standard synthetic datasets to verify model performance.

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Show the ML engine catching an "obscure" secret that traditional tools miss.
- [ ] **README.md**: Document the new AI-powered detection layer.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, innovation-focused.
*   **Perf**: ML is expensive; it must only be used in "Deep" mode and on high-priority segments.
*   **Security**: Ensure the model itself doesn't contain sensitive data from its training set.
