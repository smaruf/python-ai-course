"""
Minimal adapter implementations for LangChain and LangGraph behaviors.
These are intentionally simple and easily replaceable with real provider SDK calls.
"""
from typing import List, Dict, Any

class LangChainIntegration:
    def __init__(self, config: Dict[str,Any]):
        self.config = config

    def embed_documents(self, docs: List[Dict[str,str]], model: str):
        # Placeholder embeddings: fixed-size vectors; replace with real embeddings call.
        dim = 768
        embeddings = []
        for d in docs:
            embeddings.append({"id": d.get("id", ""), "text": d.get("text", ""), "embedding": [0.0] * dim})
        return embeddings

    def build_vector_index(self, embeddings: List[Dict[str,Any]], store: str):
        # Simple in-memory index for tests/demos. Replace with FAISS / Pinecone / Weaviate integration.
        index = {"store": store, "items": embeddings}
        return index

class LangGraphIntegration:
    def __init__(self, config: Dict[str,Any]):
        self.config = config

    def build_chain(self, index: Dict[str,Any], llm_provider: str, pattern: str):
        # Returns an object with a run(query) method. Replace with actual LangGraph graph builder.
        class SimpleChain:
            def __init__(self, index, provider, pattern):
                self.index = index
                self.provider = provider
                self.pattern = pattern

            def run(self, query: str):
                texts = " ".join([item.get("text","")[:50] for item in self.index.get("items", [])])
                # Mocked response structure
                return {
                    "query": query,
                    "provider": self.provider,
                    "pattern": self.pattern,
                    "answer": f"Mocked result for query '{query}'. Indexed docs: {texts}"
                }

        return SimpleChain(index, llm_provider, pattern)
