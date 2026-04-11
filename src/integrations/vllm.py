from typing import Any, Optional
from src.sdk import Scanner

class SecureVLLMGenerator:
    """Wraps a vLLM LLM instance to sanitize inputs and outputs for offline inference."""
    def __init__(self, llm: Any, scanner: Optional[Scanner] = None):
        self.llm = llm
        self.scanner = scanner or Scanner(obfuscate=True, obfuscate_mode="synthetic")

    def generate(self, prompts, sampling_params=None, **kwargs):
        safe_prompts = [self.scanner.redact(p) if isinstance(p, str) else p for p in prompts]

        outputs = self.llm.generate(safe_prompts, sampling_params=sampling_params, **kwargs)

        for output in outputs:
            if hasattr(output, "outputs"):
                for idx, generated_text in enumerate(output.outputs):
                    if hasattr(generated_text, "text"):
                        output.outputs[idx].text = self.scanner.redact(generated_text.text)
        return outputs

# (Middleware is best implemented per FastAPI app as shown in tests/examples,
# because it depends on Starlette classes. We avoid adding FastAPI as a core dependency here.)
