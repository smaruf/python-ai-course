import yaml
from langchain_langgraph.pipeline import Pipeline, PipelineConfig
from langchain_langgraph.integrations import LangChainIntegration, LangGraphIntegration

def test_pipeline_runs():
    cfg = {
        "name": "test",
        "ingest_source": "projects/langchain-langgraph-standalone/examples/sample.txt",
        "embedding_model": "dummy",
        "vector_store": "in-memory",
        "llm_provider": "dummy",
        "chain_pattern": "qa",
        "params": {"example_query": "What is this?"}
    }
    pc = PipelineConfig(**cfg)
    p = Pipeline(pc, LangChainIntegration({}), LangGraphIntegration({}))
    out = p.run_full()
    assert "result" in out
    assert isinstance(out["metrics"], dict)
    assert "answer" in out["result"]
