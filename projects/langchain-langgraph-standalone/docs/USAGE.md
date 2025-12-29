# Usage Guide

This guide shows how to run the example and switch variants.

1) Install
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .

2) Run a demo using a config variant in Python:
   python -c "import yaml; from langchain_langgraph.pipeline import Pipeline, PipelineConfig; from langchain_langgraph.integrations import LangChainIntegration, LangGraphIntegration; cfg = yaml.safe_load(open('projects/langchain-langgraph-standalone/configs/config_variants.yaml')); v = cfg['variants']['openai-faiss-qa']; pc = PipelineConfig(name='demo', **v); p = Pipeline(pc, LangChainIntegration({}), LangGraphIntegration({})); print(p.run_full())"

3) Add a new variant
   - Add a new YAML entry in configs/config_variants.yaml with keys:
     ingest_source, embedding_model, vector_store, llm_provider, chain_pattern

4) Replace placeholders
   - Replace LangChainIntegration.embed_documents and build_vector_index with real provider calls.
   - Replace LangGraphIntegration.build_chain with actual graph/chain builder from the project you use.
