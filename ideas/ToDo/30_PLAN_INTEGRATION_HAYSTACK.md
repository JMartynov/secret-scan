# Task: Haystack Integration (Enterprise Search Security)

## 1. Objective & Context
*   **Goal**: Integrate `py-secret-scan` into Haystack 2.x pipelines to ensure enterprise-level security for search and RAG workflows.
*   **Rationale**: Haystack is a leading enterprise search framework; its modular pipeline architecture allows for easy integration of custom secret scanning nodes.

## 2. Research & Guardrails Best Practices
Based on industry best practices for enterprise RAG guardrails:
*   **Pipeline Components**: Haystack 2.x relies heavily on custom `@component` classes. Security guardrails should be encapsulated as reusable components that can sit anywhere in the graph.
*   **Routing & Branching**: Instead of throwing errors and crashing the pipeline, use Haystack's branching capabilities (e.g., `LLMMessagesRouter`). If a document contains a secret, route it to a "Redaction" node or a "Security Audit" sink rather than stopping the search.
*   **Pre-indexing vs. Post-retrieval**: Run deep, exhaustive scans (Regex + Entropy) during the indexing phase. Run fast, lightweight scans on the retrieved `Document` objects before sending them to the `PromptBuilder`.
*   **Type Safety**: Ensure components strictly accept and return Haystack's native types (`List[Document]`, `ChatMessage`, `str`).

## 3. Implementation Examples

Here are 3 examples of integrating `py-secret-scan` into Haystack 2.x using the SDK.

### Example 1: Haystack 2.x Component for Document Redaction
```python
from typing import List
from haystack import component, Document
from secret_scan.sdk import Scanner

@component
class SecretDocumentRedactor:
    """Scans and redacts secrets from retrieved Haystack Documents."""
    def __init__(self):
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        safe_docs = []
        for doc in documents:
            if doc.content:
                safe_content = self.scanner.redact(doc.content)
                # Create a new document with redacted content
                safe_docs.append(Document(content=safe_content, meta=doc.meta))
            else:
                safe_docs.append(doc)
        return {"documents": safe_docs}

# Usage
# pipeline.add_component("redactor", SecretDocumentRedactor())
# pipeline.connect("retriever", "redactor")
# pipeline.connect("redactor", "prompt_builder")
```

### Example 2: Prompt / Query Validator
```python
from haystack import component
from secret_scan.sdk import Scanner

@component
class SecretQueryValidator:
    """Blocks execution if the user query contains a secret."""
    def __init__(self):
        self.scanner = Scanner()

    @component.output_types(query=str)
    def run(self, query: str):
        results = self.scanner.scan(query)
        if any(r.risk in ["HIGH", "CRITICAL"] for r in results):
            # For a router, you might return two outputs. Here we raise an exception.
            raise ValueError("Blocked: Query contains sensitive data.")
        return {"query": query}

# Usage
# pipeline.add_component("query_validator", SecretQueryValidator())
```

### Example 3: ChatMessage Sanitizer
```python
from typing import List
from haystack import component
from haystack.dataclasses import ChatMessage
from secret_scan.sdk import Scanner

@component
class ChatMessageSanitizer:
    def __init__(self):
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="synthetic")

    @component.output_types(messages=List[ChatMessage])
    def run(self, messages: List[ChatMessage]):
        safe_msgs = []
        for msg in messages:
            if msg.text:
                safe_text = self.scanner.redact(msg.text)
                safe_msgs.append(ChatMessage.from_user(safe_text) if msg.is_from_user else ChatMessage.from_assistant(safe_text))
            else:
                safe_msgs.append(msg)
        return {"messages": safe_msgs}
```

## 4. Integration Tests

Create `tests/integrations/test_haystack.py`. We use a mock component setup.

```python
import pytest
from haystack import Pipeline, Document
from haystack.components.builders.prompt_builder import PromptBuilder
from secret_scan.sdk import Scanner
from typing import List
from haystack import component

@component
class SecretDocumentRedactor:
    def __init__(self):
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        safe_docs = []
        for doc in documents:
            if doc.content:
                safe_docs.append(Document(content=self.scanner.redact(doc.content)))
        return {"documents": safe_docs}

@component
class MockLLM:
    @component.output_types(replies=List[str])
    def run(self, prompt: str):
        return {"replies": [f"Based on context: {prompt}"]}

def test_haystack_pipeline_redaction():
    # Setup Pipeline
    pipeline = Pipeline()
    pipeline.add_component("redactor", SecretDocumentRedactor())
    pipeline.add_component("prompt_builder", PromptBuilder(template="Context: {{ documents[0].content }}"))
    pipeline.add_component("llm", MockLLM())
    
    pipeline.connect("redactor", "prompt_builder")
    pipeline.connect("prompt_builder", "llm")
    
    # Run with leaky document
    leaky_doc = Document(content="Connect to postgres://admin:pass@localhost")
    results = pipeline.run({"redactor": {"documents": [leaky_doc]}})
    
    # Assertions
    output = results["llm"]["replies"][0]
    assert "postgres://admin:pass@localhost" not in output
    assert "admin:pass" not in output
```
