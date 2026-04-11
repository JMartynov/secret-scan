from typing import List, Optional, Any
from src.sdk import Scanner

# To avoid requiring Haystack as a core dependency, we build the classes without
# inheriting from Haystack specific component classes, but structured so they can
# easily be decorated with @component by users.

class SecretDocumentRedactorCore:
    """Core logic for a Haystack component that redacts documents."""
    def __init__(self, scanner: Optional[Scanner] = None):
        self.scanner = scanner or Scanner(obfuscate=True, obfuscate_mode="redact")

    def run(self, documents: List[Any]) -> dict:
        safe_docs = []
        for doc in documents:
            if hasattr(doc, "content") and doc.content:
                safe_content = self.scanner.redact(doc.content)
                # Create a new document with redacted content. Requires Document class to be passed or duck-typed.
                # Assuming duck-typing: object with content and meta
                new_doc = type(doc)(content=safe_content, meta=getattr(doc, "meta", {}))
                safe_docs.append(new_doc)
            else:
                safe_docs.append(doc)
        return {"documents": safe_docs}

class SecretQueryValidatorCore:
    """Core logic for a Haystack component that validates queries."""
    def __init__(self, scanner: Optional[Scanner] = None):
        self.scanner = scanner or Scanner(mode="block")

    def run(self, query: str) -> dict:
        self.scanner.validate(query)
        return {"query": query}
