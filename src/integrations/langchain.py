from typing import Any, Optional
from src.sdk import Scanner

class SecretScannerRunnable:
    """Wraps a LangChain runnable (like an LLM) to block/redact secrets."""
    def __init__(self, runnable: Any, scanner: Optional[Scanner] = None, mode="redact"):
        self.runnable = runnable
        self.mode = mode
        if scanner:
            self.scanner = scanner
        else:
            self.scanner = Scanner(obfuscate=(mode=="redact"))

    def invoke(self, input: Any, config: Optional[Any] = None, **kwargs: Any) -> Any:
        # Check input
        text_to_scan = ""
        if isinstance(input, str):
            text_to_scan = input
        elif hasattr(input, "to_string"):
            text_to_scan = input.to_string()
        elif hasattr(input, "content"):
            text_to_scan = input.content

        if self.mode == "block":
            self.scanner.validate(text_to_scan)
        elif self.mode == "redact":
            if isinstance(input, str):
                input = self.scanner.redact(input)
            elif hasattr(input, "content") and isinstance(input.content, str):
                input.content = self.scanner.redact(input.content)

        # Run
        result = self.runnable.invoke(input, config=config, **kwargs)

        # Check output
        if self.mode == "block":
            text_to_scan = ""
            if isinstance(result, str):
                text_to_scan = result
            elif hasattr(result, "content"):
                text_to_scan = result.content
            self.scanner.validate(text_to_scan)
        elif self.mode == "redact":
            if isinstance(result, str):
                result = self.scanner.redact(result)
            elif hasattr(result, "content") and isinstance(result.content, str):
                result.content = self.scanner.redact(result.content)

        return result
