from typing import Any, List, Dict, Optional
from src.sdk import Scanner

class SecureOllamaClient:
    """Wraps an Ollama client to sanitize chat interactions."""
    def __init__(self, client: Any, scanner: Optional[Scanner] = None):
        self.client = client
        self.scanner = scanner or Scanner(obfuscate=True, obfuscate_mode="redact")

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Any:
        # Sanitize inputs
        safe_messages = []
        for msg in messages:
            safe_msg = msg.copy()
            if "content" in safe_msg:
                safe_msg["content"] = self.scanner.redact(safe_msg["content"])
            safe_messages.append(safe_msg)

        # Call Ollama
        response = self.client.chat(model=model, messages=safe_messages, **kwargs)

        # Sanitize output (assuming dictionary response like ollama-python)
        if isinstance(response, dict) and "message" in response and "content" in response["message"]:
            response["message"]["content"] = self.scanner.redact(response["message"]["content"])
        elif hasattr(response, "message") and hasattr(response.message, "content"):
             response.message.content = self.scanner.redact(response.message.content)

        return response
