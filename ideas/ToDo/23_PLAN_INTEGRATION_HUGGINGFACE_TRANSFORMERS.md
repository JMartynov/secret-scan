# Task: Hugging Face Transformers Integration

## 1. Objective & Context
*   **Goal**: Integrate `py-secret-scan` into the Hugging Face `transformers` pipeline to detect secrets in prompts and generated outputs.
*   **Rationale**: Hugging Face is the industry standard for LLM models; a native integration allows researchers and developers to prevent leaks during inference.

## 2. Research & Guardrails Best Practices
Based on industry best practices for LLM input/output guardrails:
*   **Defense in Depth**: Use deterministic rule-based checks (like `py-secret-scan`) before relying on LLM-as-a-judge models. It's faster, cheaper, and more reliable for PII and secrets.
*   **Input Validation**: Scan and redact prompts *before* they are tokenized and sent to the model to prevent data leaks to external inference endpoints or logging systems.
*   **Output Validation**: Scan the generated output *before* returning it to the user.
*   **Fail Gracefully**: If a secret is detected, redact it (e.g., using `obfuscate_mode="synthetic"`) or block the response entirely, rather than crashing the pipeline.
*   **Hugging Face specific**: Use custom `StoppingCriteria` or wrap the `Pipeline` class to intercept strings before they hit the model.

## 3. Implementation Examples

Here are 3 examples of integrating `py-secret-scan` into a Hugging Face workflow using the SDK.

### Example 1: Wrapping the Pipeline for Input/Output Scanning
```python
from transformers import pipeline
from secret_scan.sdk import Scanner

scanner = Scanner(obfuscate=True, obfuscate_mode="redact")
generator = pipeline("text-generation", model="gpt2")

def safe_generate(prompt: str, **kwargs):
    # 1. Scan and redact input
    safe_prompt = scanner.redact(prompt)
    
    # 2. Generate output
    output = generator(safe_prompt, **kwargs)
    generated_text = output[0]['generated_text']
    
    # 3. Scan and redact output
    safe_output = scanner.redact(generated_text)
    return safe_output

# Usage
prompt = "My AWS key is AKIAIOSFODNN7EXAMPLE. Generate a script to use it."
print(safe_generate(prompt, max_length=50))
```

### Example 2: Custom Stopping Criteria for Streaming
```python
from transformers import StoppingCriteria, StoppingCriteriaList, AutoModelForCausalLM, AutoTokenizer
from secret_scan.sdk import Scanner
import torch

class SecretScanStoppingCriteria(StoppingCriteria):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.scanner = Scanner()

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        # Decode the last few tokens to check for secrets
        text = self.tokenizer.decode(input_ids[0, -20:], skip_special_tokens=True)
        results = self.scanner.scan(text)
        
        # Stop generation if a high-risk secret is detected
        if any(r.risk in ["HIGH", "CRITICAL"] for r in results):
            print("\n[WARNING] Secret detected during generation. Stopping.")
            return True
        return False

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
stopping_criteria = StoppingCriteriaList([SecretScanStoppingCriteria(tokenizer)])

input_ids = tokenizer("Here is a random key: ", return_tensors="pt").input_ids
outputs = model.generate(input_ids, max_length=50, stopping_criteria=stopping_criteria)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Example 3: Dataset Sanitization before Fine-tuning
```python
from datasets import load_dataset
from secret_scan.sdk import Scanner

scanner = Scanner(obfuscate=True, obfuscate_mode="synthetic")
dataset = load_dataset("imdb", split="train[:100]")

def sanitize_example(example):
    # Replace real secrets with synthetic ones in the training data
    example['text'] = scanner.redact(example['text'])
    return example

safe_dataset = dataset.map(sanitize_example)
print("Dataset sanitized and ready for training.")
```

## 4. Integration Tests

Create `tests/integrations/test_huggingface.py`. We use an LLM emulator/mock to ensure tests run quickly and deterministically.

```python
import pytest
from secret_scan.sdk import Scanner

class MockHuggingFacePipeline:
    """Emulates a Hugging Face pipeline response."""
    def __call__(self, prompt, **kwargs):
        # Simulate generating a secret
        if "generate key" in prompt.lower():
            return [{"generated_text": prompt + " Here is your token: ghp_1234567890abcdefghijklmnopqrstuvwx"}]
        return [{"generated_text": prompt + " Normal response."}]

class SafePipeline:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def __call__(self, prompt, **kwargs):
        safe_prompt = self.scanner.redact(prompt)
        output = self.pipeline(safe_prompt, **kwargs)[0]['generated_text']
        return self.scanner.redact(output)

def test_huggingface_pipeline_redaction():
    # Setup
    mock_pipeline = MockHuggingFacePipeline()
    safe_pipe = SafePipeline(mock_pipeline)
    
    # Test Input Leak
    prompt = "My db is postgres://user:password@localhost. generate key"
    output = safe_pipe(prompt)
    
    # Assertions
    assert "postgres://user:password@localhost" not in output
    assert "ghp_1234567890abcdefghijklmnopqrstuvwx" not in output
```
