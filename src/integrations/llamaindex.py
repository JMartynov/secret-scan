from typing import Any, List, Optional
from src.sdk import Scanner

class SecretScannerNodeParser:
    """A naive parser wrapper that redacts secrets from nodes."""
    def __init__(self, scanner: Optional[Scanner] = None):
        self.scanner = scanner or Scanner(obfuscate=True)

    def __call__(self, nodes: List[Any], **kwargs: Any) -> List[Any]:
        for node in nodes:
            if hasattr(node, "text"):
                node.text = self.scanner.redact(node.text)
            elif hasattr(node, "get_content"):
                node.set_content(self.scanner.redact(node.get_content()))
        return nodes

class SecureLLM:
    """Wraps a LlamaIndex LLM instance."""
    def __init__(self, llm: Any, scanner: Optional[Scanner] = None):
        self.llm = llm
        self.scanner = scanner or Scanner(obfuscate=True)

    def complete(self, prompt: str, **kwargs: Any) -> Any:
        safe_prompt = self.scanner.redact(prompt)
        response = self.llm.complete(safe_prompt, **kwargs)
        if hasattr(response, "text"):
            response.text = self.scanner.redact(response.text)
        elif isinstance(response, str):
            response = self.scanner.redact(response)
        return response

    def chat(self, messages: List[Any], **kwargs: Any) -> Any:
        for msg in messages:
            if hasattr(msg, "content"):
                msg.content = self.scanner.redact(msg.content)

        response = self.llm.chat(messages, **kwargs)
        if hasattr(response, "message") and hasattr(response.message, "content"):
            response.message.content = self.scanner.redact(response.message.content)
        return response
