# Task: LlamaIndex Integration (RAG Security)

## 1. Objective & Context
*   **Goal**: Integrate `py-secret-scan` into the LlamaIndex query engine to prevent RAG leakage from custom datasets.
*   **Rationale**: LlamaIndex is the top library for RAG; secret detection ensures that retrieved context doesn't contain accidentally indexed credentials.

## 2. Research & Guardrails Best Practices
Based on industry best practices for LLM RAG guardrails:
*   **Defense in Depth**: In a RAG pipeline, the highest risk comes from the context window (documents retrieved from a vector database).
*   **Ingestion Guardrails**: Scan documents *during the ingestion phase* using a `TransformComponent`. If a document contains a secret, redact it before it gets embedded and stored.
*   **Post-Retrieval Guardrails**: Scan retrieved nodes *before* they are injected into the prompt using a `BaseNodePostprocessor`. This catches secrets that might have slipped through or were added dynamically.
*   **Output Guardrails**: Scan the final generated response just in case the LLM hallucinates a secret.

## 3. Implementation Examples

Here are 3 examples of integrating `py-secret-scan` into LlamaIndex using the SDK.

### Example 1: Ingestion Pipeline Redaction
```python
from llama_index.core.schema import TransformComponent, BaseNode
from secret_scan.sdk import Scanner

class SecretRedactTransform(TransformComponent):
    def __init__(self):
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def __call__(self, nodes: list[BaseNode], **kwargs) -> list[BaseNode]:
        for node in nodes:
            node.text = self.scanner.redact(node.text)
        return nodes

# Usage
from llama_index.core.ingestion import IngestionPipeline
pipeline = IngestionPipeline(transformations=[SecretRedactTransform()])
# nodes = pipeline.run(documents=docs)
```

### Example 2: Post-Retrieval Node Filtering
```python
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore
from llama_index.core.bridge.pydantic import Field
from secret_scan.sdk import Scanner

class SecretNodePostprocessor(BaseNodePostprocessor):
    def _postprocess_nodes(self, nodes: list[NodeWithScore], query_bundle=None) -> list[NodeWithScore]:
        scanner = Scanner()
        safe_nodes = []
        for node in nodes:
            results = scanner.scan(node.node.text)
            if not any(r.risk in ["HIGH", "CRITICAL"] for r in results):
                safe_nodes.append(node)
            else:
                print(f"Dropped node {node.node.node_id} due to secret detection.")
        return safe_nodes

# Usage
from llama_index.core import VectorStoreIndex
# index = VectorStoreIndex.from_documents(docs)
# query_engine = index.as_query_engine(node_postprocessors=[SecretNodePostprocessor()])
```

### Example 3: Global Output Redaction (Custom Synthesizer)
```python
from llama_index.core.response_synthesizers import BaseSynthesizer
from secret_scan.sdk import Scanner

class SafeResponseSynthesizer:
    def __init__(self, base_synthesizer: BaseSynthesizer):
        self.base_synthesizer = base_synthesizer
        self.scanner = Scanner(obfuscate=True, obfuscate_mode="redact")

    def synthesize(self, query, nodes, **kwargs):
        response = self.base_synthesizer.synthesize(query, nodes, **kwargs)
        response.response = self.scanner.redact(response.response)
        return response

# Usage
# query_engine = index.as_query_engine(response_synthesizer=SafeResponseSynthesizer(base_synth))
```

## 4. Integration Tests

Create `tests/integrations/test_llamaindex.py`. We use `MockLLM` and mock nodes to verify redaction logic.

```python
import pytest
from llama_index.core.llms import MockLLM
from llama_index.core.schema import TextNode, NodeWithScore
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from secret_scan.sdk import Scanner

class SecretNodeRedactor(BaseNodePostprocessor):
    def _postprocess_nodes(self, nodes: list[NodeWithScore], query_bundle=None) -> list[NodeWithScore]:
        scanner = Scanner(obfuscate=True, obfuscate_mode="redact")
        for node in nodes:
            node.node.text = scanner.redact(node.node.text)
        return nodes

def test_llamaindex_postprocessor_redaction():
    # Setup leaky node
    leaky_text = "Here is the internal database string: postgres://admin:pass@localhost:5432/db"
    node = NodeWithScore(node=TextNode(text=leaky_text), score=1.0)
    
    # Run postprocessor
    postprocessor = SecretNodeRedactor()
    safe_nodes = postprocessor._postprocess_nodes([node])
    
    # Assertions
    safe_text = safe_nodes[0].node.text
    assert "postgres://admin:pass@localhost:5432/db" not in safe_text
    assert "admin:pass" not in safe_text
```