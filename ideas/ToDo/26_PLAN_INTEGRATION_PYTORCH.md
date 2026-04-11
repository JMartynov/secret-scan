# Task: PyTorch & Lightning Integration (Secure Training)

## 1. Objective & Context
*   **Goal**: Integrate `py-secret-scan` into PyTorch training loops to detect accidental secret leakage in logs, checkpoints, or print statements.
*   **Rationale**: PyTorch is the fundamental deep learning framework; preventing secret leakage in training logs (like TensorBoard or Weights & Biases) is critical for enterprise data security.

## 2. Research & Guardrails Best Practices
Based on industry best practices for training telemetry guardrails:
*   **Telemetry Filtering**: Data leakages often happen through logging frameworks (WandB, TensorBoard, MLflow) when unstructured text data or raw examples are logged for debugging.
*   **Zero-Latency Path**: Scanning large tensors is slow and unnecessary. Guardrails in training should strictly intercept strings and metadata dictionaries right before the logging API call.
*   **Fail Gracefully vs. Hard Stop**: If a training run logs a secret, the standard approach is to redact the log locally to avoid corrupting the remote experiment, but generate a local alert.
*   **Lightning Hooks**: For PyTorch Lightning, the safest interception points are `Callback` hooks or wrapping the `Logger` instance.

## 3. Implementation Examples

Here are 3 examples of integrating `py-secret-scan` into PyTorch workflows using the SDK.

### Example 1: Safe Logger Wrapper for PyTorch
```python
import logging
from secret_scan.sdk import Scanner

class SafeLogger:
    """Wraps the standard python logger to prevent secret leakage in ML scripts."""
    def __init__(self, name="PyTorchTrainer"):
        self.logger = logging.getLogger(name)
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def info(self, msg, *args, **kwargs):
        safe_msg = self.scanner.redact(str(msg))
        self.logger.info(safe_msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        safe_msg = self.scanner.redact(str(msg))
        self.logger.warning(safe_msg, *args, **kwargs)

# Usage
log = SafeLogger()
log.info("Starting training with token ghp_1234567890abcdefghijklmnopqrstuvwx")
```

### Example 2: PyTorch Lightning Callback
```python
import pytorch_lightning as pl
from secret_scan.sdk import Scanner

class SecretScanCallback(pl.Callback):
    """Scans exception messages or custom strings during training."""
    def __init__(self):
        self.scanner = Scanner()

    def on_exception(self, trainer: pl.Trainer, pl_module: pl.LightningModule, exception: BaseException) -> None:
        # Check if the stack trace or exception string contains a secret
        error_msg = str(exception)
        results = self.scanner.scan(error_msg)
        
        if any(r.risk in ["HIGH", "CRITICAL"] for r in results):
            # Print a separate, safe warning
            print("\n[SECURITY WARNING] The exception message contained a secret!")
            print(f"Redacted error: {self.scanner.redact(error_msg)}")

# Usage
# trainer = pl.Trainer(callbacks=[SecretScanCallback()])
```

### Example 3: Wrapping Weights & Biases (WandB) Logger
```python
from pytorch_lightning.loggers import WandbLogger
from secret_scan.sdk import Scanner

class SafeWandbLogger(WandbLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def log_text(self, key: str, columns: list[str], data: list[list[str]], step: int = None) -> None:
        """Sanitize text tables before uploading to WandB."""
        safe_data = []
        for row in data:
            safe_row = [self.scanner.redact(cell) if isinstance(cell, str) else cell for cell in row]
            safe_data.append(safe_row)
            
        super().log_text(key, columns, safe_data, step)

# Usage
# safe_wandb = SafeWandbLogger(project="secure-nlp")
# trainer = pl.Trainer(logger=safe_wandb)
```

## 4. Integration Tests

Create `tests/integrations/test_pytorch.py`. We use mock loggers and simulated training errors.

```python
import pytest
from secret_scan.sdk import Scanner

class MockWandbLogger:
    def __init__(self):
        self.logged_texts = []
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def log_text(self, key, text_data):
        # Apply security wrapper logic
        safe_data = [self.scanner.redact(text) for text in text_data]
        self.logged_texts.append({key: safe_data})

def test_pytorch_safe_logging():
    # Setup
    logger = MockWandbLogger()
    
    # Simulate an NLP task logging a leaky generation
    leaky_generations = [
        "The model generated a valid output.",
        "The model leaked: postgres://user:password@localhost:5432/db"
    ]
    
    # Run
    logger.log_text("sample_generations", leaky_generations)
    
    # Assertions
    logged_output = logger.logged_texts[0]["sample_generations"]
    assert "postgres://user:password@localhost:5432/db" not in logged_output[1]
```
