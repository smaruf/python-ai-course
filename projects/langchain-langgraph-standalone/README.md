# LangChain + LangGraph — Standalone Pipeline

> **Part of [Python AI Course](../../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [AI Development Project](../../ai-development-project/) | [Oracle AI Prep](../../oracle-job-prep/)

A standalone project demonstrating a full-phase AI pipeline that integrates LangChain and LangGraph patterns, with configurable AI-field variants (LLM providers, embeddings, vector stores, chain patterns).

Features
- Full-phase implementation: ingestion → preprocessing → embedding/vector store → chain/graph construction → orchestration → evaluation
- Pluggable providers (OpenAI, local LLMs), vector DB presets (FAISS, Pinecone), and chain patterns (QA, summarization)
- Config-driven presets in YAML for quick switching between variants
- Examples and tests included

Quickstart
1. Create a virtual environment and install dependencies:
   - python -m venv .venv
   - source .venv/bin/activate
   - pip install -e .

2. Run tests:
   - python -m pytest projects/langchain-langgraph-standalone/tests

3. Run the example:
   - python -c "from langchain_langgraph.pipeline import Pipeline, PipelineConfig; from langchain_langgraph.integrations import LangChainIntegration, LangGraphIntegration; import yaml; cfg = yaml.safe_load(open('projects/langchain-langgraph-standalone/configs/config_variants.yaml')); v = cfg['variants']['openai-faiss-qa']; pc = PipelineConfig(name='demo', **v); p = Pipeline(pc, LangChainIntegration({}), LangGraphIntegration({})); print(p.run_full())"

Docs
- Usage & architecture: projects/langchain-langgraph-standalone/docs/USAGE.md
- Presets and configuration: projects/langchain-langgraph-standalone/configs/config_variants.yaml

External links
- LangChain: https://github.com/langchain-ai/langchain
- LangGraph: https://github.com/langgraph/langgraph
- FAISS: https://github.com/facebookresearch/faiss
- Pinecone: https://www.pinecone.io/
