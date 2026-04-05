# Task: PyTorch & Lightning Integration (Secure Training)

## 1. Objective & Context
*   **Goal**: Integrate `secret-scan` into PyTorch training loops to detect accidental secret leakage in logs, checkpoints, or print statements.
*   **Rationale**: PyTorch is the fundamental deep learning framework; preventing secret leakage in training logs (like TensorBoard or Weights & Biases) is critical for enterprise data security.

## 2. Research & Strategy
*   **Research**: Explore PyTorch Lightning `Callback` hooks (e.g., `on_train_batch_end`, `on_validation_batch_end`) and PyTorch's native `forward`/`backward` hooks.
*   **Approach**: Create a `SecretSafeLogger` or a Lightning `Callback` that scans metrics and strings before logging.
*   **Mocking**: Use `MockLightningModule` and `FakeDataset` to simulate a training run.

## 3. Implementation Checklist
- [ ] **Research Phase**:
    - [ ] Document the lifecycle methods in Lightning Callbacks that handle string-based logging (`on_log`, `on_exception`).
- [ ] **Integration Component**:
    - [ ] Implement `LightningSecretScanCallback` to scan logged metadata.
    - [ ] Create a `SecretSafeWandbLogger` or similar wrapper to scan metrics before pushing to cloud dashboards.
- [ ] **Testing**:
    - [ ] Create `tests/integrations/test_pytorch.py`.
    - [ ] Run a minimal Lightning training loop with "leaky" logging.
    - [ ] Verify the callback correctly intercepts and redacts the logs.

## 4. Engineering Standards
*   **Zero-Latency**: Ensure the scan doesn't block the training process.
*   **Privacy**: Avoid scanning raw tensors unless they are being converted to strings for logging.
