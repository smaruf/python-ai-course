"""
Pipeline orchestrator implementing:
- ingestion
- preprocessing
- embedding/vectorization (via LangChainIntegration)
- vector store index creation
- chain/graph construction (via LangGraphIntegration)
- orchestration and evaluation
"""
from typing import Any, Dict, List
from dataclasses import dataclass, field

@dataclass
class PipelineConfig:
    name: str
    ingest_source: str
    embedding_model: str
    vector_store: str
    llm_provider: str
    chain_pattern: str
    params: Dict[str, Any] = field(default_factory=dict)

class Pipeline:
    def __init__(self, config: PipelineConfig, langchain_integ, langgraph_integ, evaluator=None):
        self.config = config
        self.langchain = langchain_integ
        self.langgraph = langgraph_integ
        self.evaluator = evaluator

    def run_full(self) -> Dict[str, Any]:
        # Phase 1 — Ingest
        docs = self.ingest(self.config.ingest_source)

        # Phase 2 — Preprocess
        docs = self.preprocess(docs)

        # Phase 3 — Embeddings / Vectorization
        embeddings = self.langchain.embed_documents(docs, model=self.config.embedding_model)

        # Phase 4 — Vector store (index)
        index = self.langchain.build_vector_index(embeddings, store=self.config.vector_store)

        # Phase 5 — Chain / Graph construction
        chain = self.langgraph.build_chain(index=index, llm_provider=self.config.llm_provider, pattern=self.config.chain_pattern)

        # Phase 6 — Orchestration / Execution (example query)
        query = self.config.params.get("example_query", "Explain the main idea of the documents.")
        result = chain.run(query)

        # Phase 7 — Evaluation
        metrics = {}
        if self.evaluator:
            metrics = self.evaluator.evaluate(result)

        return {"result": result, "metrics": metrics}

    def ingest(self, source: str) -> List[Dict[str, str]]:
        # Minimal ingestion implementation supporting plain text files.
        try:
            if source.endswith(".txt"):
                with open(source, "r", encoding="utf-8") as f:
                    return [{"id": "doc1", "text": f.read()}]
        except FileNotFoundError:
            # Fallback: small sample document
            return [{"id": "doc_sample", "text": "Sample document text used by the pipeline."}]
        return [{"id": "doc_sample", "text": "Sample document text used by the pipeline."}]

    def preprocess(self, docs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # Minimal preprocessing — trimming whitespace and simple normalization.
        for d in docs:
            d["text"] = " ".join(d.get("text", "").strip().split())
        return docs
