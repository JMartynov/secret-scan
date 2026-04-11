from typing import Any, Optional
from src.sdk import Scanner

class SecurePipeline:
    """Wraps a HuggingFace pipeline with input/output scanning."""
    def __init__(self, pipeline: Any, scanner: Optional[Scanner] = None):
        self.pipeline = pipeline
        self.scanner = scanner or Scanner(obfuscate=True, obfuscate_mode="redact")

    def __call__(self, *args, **kwargs) -> Any:
        # Scan inputs
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(self.scanner.redact(arg))
            elif isinstance(arg, list) and all(isinstance(x, str) for x in arg):
                safe_args.append([self.scanner.redact(x) for x in arg])
            else:
                safe_args.append(arg)

        safe_kwargs = {}
        for k, v in kwargs.items():
            if isinstance(v, str):
                safe_kwargs[k] = self.scanner.redact(v)
            elif isinstance(v, list) and all(isinstance(x, str) for x in v):
                safe_kwargs[k] = [self.scanner.redact(x) for x in v]
            else:
                safe_kwargs[k] = v

        # Run pipeline
        results = self.pipeline(*safe_args, **safe_kwargs)

        # Scan outputs (Assuming standard pipeline outputs: dicts or list of dicts with 'generated_text')
        def sanitize_result(res):
            if isinstance(res, dict):
                for k, v in res.items():
                    if isinstance(v, str):
                        res[k] = self.scanner.redact(v)
            return res

        if isinstance(results, list):
            if results and isinstance(results[0], list): # Batch of batches
                return [[sanitize_result(item) for item in batch] for batch in results]
            return [sanitize_result(res) for res in results]
        return sanitize_result(results)

class SecureGenerationMixin:
    """Mixin for safe generation for HF models."""
    def __init__(self, model: Any, scanner: Optional[Scanner] = None):
        self.model = model
        self.scanner = scanner or Scanner(obfuscate=True, obfuscate_mode="redact")

    def generate(self, *args, **kwargs):
        return self.model.generate(*args, **kwargs)


class SecretScanStoppingCriteria:
    """Stopping criteria for HuggingFace generation that stops if secrets are generated."""
    def __init__(self, tokenizer: Any, scanner: Optional[Scanner] = None, window_size: int = 20):
        self.tokenizer = tokenizer
        self.scanner = scanner or Scanner()
        self.window_size = window_size

    def __call__(self, input_ids: Any, scores: Any, **kwargs) -> bool:
        # Decode the last few tokens to check for secrets
        # Using a slice of the tensor assumes PyTorch-like semantics: input_ids[0, -window_size:]
        try:
            tokens_to_decode = input_ids[0, -self.window_size:]
            text = self.tokenizer.decode(tokens_to_decode, skip_special_tokens=True)
            results = self.scanner.scan(text)

            if any(getattr(r, 'risk', 'LOW') in ["HIGH", "CRITICAL"] for r in results):
                return True
        except Exception:
            pass
        return False
