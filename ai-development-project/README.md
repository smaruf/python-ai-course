# AI Development Project

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [AI Gateway](../ai-gateway/) | [Oracle AI Prep](../oracle-job-prep/) | [LangChain + LangGraph](../projects/langchain-langgraph-standalone/) | [AI Sync-Async Guide](../ai-sync-async-fix-itch/) | [Yelp-Style AI Assistant](../yelp-ai-assistant/)

A comprehensive, full-phased project for learning AI development concepts and implementations.

## 🎯 Project Overview

This project provides a structured approach to learning and implementing AI features in software development. It covers everything from basic LLM integration to building autonomous AI agents.

## 📁 Project Structure

```
ai-development-project/
├── README.md                    # This file
├── ai_feature_guidelines.md     # Main guidelines document (35,000+ words)
├── requirements.txt             # Python dependencies
├── docs/                        # Additional documentation
│   ├── concepts.md             # Core AI concepts explained
│   ├── best-practices.md       # Production best practices
│   ├── learning-path.md        # Structured learning progression
│   └── physics-applications.md # Physics + Deep Learning guide
├── examples/                   # Working code examples
│   ├── 01_simple_llm/         # Basic LLM integration
│   ├── 02_contextual_ai/      # Context-aware AI assistant
│   ├── 03_physics_deep_learning/ # Physics AI (Aero/Hydro/Thermo)
│   ├── 04_rag_system/         # RAG implementation
│   ├── 05_vector_db/          # Vector database examples
│   └── 06_ai_agents/          # AI agent framework
├── src/                       # Reusable AI components
│   ├── llm_client.py          # LLM client wrapper
│   ├── rag_engine.py          # RAG implementation
│   ├── vector_store.py        # Vector database wrapper
│   └── agent_framework.py     # AI agent base classes
└── tests/                     # Test suite
    ├── test_examples.py       # Test all examples
    ├── test_components.py     # Test reusable components
    └── fixtures/              # Test data and fixtures
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 8GB+ RAM (for local models)
- Git

### Installation

1. **Clone and navigate to the project**:
```bash
cd ai-development-project
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Choose your AI provider**:

**Option A: Local AI (Ollama - Recommended for learning)**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download a model (in another terminal)
ollama pull llama3.1:8b
```

**Option B: API-based AI**
```bash
# Set up your API key (choose one)
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

4. **Run your first example**:
```bash
python examples/01_simple_llm/basic_chat.py
```

## 🎓 Learning Progression

### 🟢 Beginner (Week 1-2)
- **Goal**: Understand LLM basics and prompt engineering
- **Start with**: `examples/01_simple_llm/`
- **Read**: Sections 1-3 of `ai_feature_guidelines.md`

### 🟡 Intermediate (Week 3-4)
- **Goal**: Build context-aware AI systems
- **Work on**: `examples/02_contextual_ai/`
- **Read**: Sections 4-5 of the guidelines

### 🟠 Advanced (Week 5-8)
- **Goal**: Implement RAG and vector search
- **Build**: `examples/03_rag_system/` and `examples/04_vector_db/`
- **Study**: Advanced examples and best practices

### 🔴 Expert (Week 9-12)
- **Goal**: Create autonomous AI agents
- **Master**: `examples/05_ai_agents/`
- **Focus**: Production deployment and optimization

## 💻 Example Applications

Each example is a complete, runnable application:

### 1. Simple LLM Chat (`examples/01_simple_llm/`)
A basic chatbot that demonstrates:
- LLM API integration
- Prompt engineering
- Error handling
- Response streaming

### 2. Contextual AI Assistant (`examples/02_contextual_ai/`)
An AI that understands application context:
- Session management
- Context-aware responses
- Smart routing
- Memory management

### 3. Physics Deep Learning (`examples/03_physics_deep_learning/`)
AI-powered physics analysis for engineering:
- **Aerodynamics**: Airfoil analysis, lift/drag prediction, CFD with AI
- **Hydrodynamics**: Ship resistance, wave patterns, marine engineering
- **Thermodynamics**: Heat exchangers, thermal engines, efficiency optimization
- **Unified Physics AI**: Interactive multi-domain consultant

### 4. RAG Knowledge System (`examples/04_rag_system/`)
Retrieval-augmented generation implementation:
- Document processing
- Semantic search
- Context retrieval
- Answer generation

### 5. Vector Database (`examples/05_vector_db/`)
Semantic search and similarity matching:
- Text embeddings
- Vector storage
- Similarity search
- Knowledge base management

### 6. AI Agent Framework (`examples/06_ai_agents/`)
Autonomous AI agents that can:
- Plan multi-step tasks
- Use tools and APIs
- Learn from results
- Execute complex workflows

## 🧪 Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Test specific examples:
```bash
python -m pytest tests/test_examples.py::test_simple_llm -v
```

## 📚 Documentation

- **[Main Guidelines](ai_feature_guidelines.md)**: Complete 35,000+ word guide
- **[Core Concepts](docs/concepts.md)**: Deep dive into AI concepts
- **[Best Practices](docs/best-practices.md)**: Production-ready patterns
- **[Learning Path](docs/learning-path.md)**: Week-by-week progression
- **[Physics Applications](docs/physics-applications.md)**: Deep learning for physics

## 🛠️ Features

### ✅ Comprehensive Coverage
- Large Language Models (LLMs)
- Prompt Engineering
- RAG (Retrieval Augmented Generation)
- Vector Databases
- AI Agents

### ✅ Practical Focus
- Working code examples
- Real-world applications
- Production best practices
- Error handling and monitoring

### ✅ Progressive Learning
- 4 complexity levels (🟢🟡🟠🔴)
- Clear learning progression
- Hands-on exercises
- 12-week structured path

### ✅ Production Ready
- Security best practices
- Performance optimization
- Monitoring and logging
- Cost management strategies

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](docs/contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs or request features via GitHub issues
- **Discussions**: Join our community discussions
- **Documentation**: Comprehensive guides in the `docs/` folder
- **Examples**: All examples include detailed comments and explanations

---

**Ready to start your AI development journey?** 🚀

Begin with the **[AI Feature Guidelines](ai_feature_guidelines.md)** and choose your starting point based on your experience level!