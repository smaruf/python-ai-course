# Python AI Course - Organized Learning Projects

A comprehensive collection of Python learning projects organized into full-featured, phased project folders. Each project is self-contained with its own dependencies, documentation, tests, and examples.

## 🎯 Project Overview

This repository has been reorganized to provide structured learning experiences across different aspects of Python programming, from basic algorithms to advanced web applications and AI implementations.

## 🚀 Quick Start

### Start with AI Development (Recommended) 🤖
```bash
cd ai-development-project
pip install -r requirements.txt

# Option 1: Local AI (Recommended for learning)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3.1:8b

# Option 2: API-based AI
export OPENAI_API_KEY="your-key-here"

# Run first example
python examples/01_simple_llm/basic_chat.py
```

### Or Choose Any Project
```bash
# Navigate to any project
cd [project-name]
pip install -r requirements.txt

# Run examples or tests
python main.py          # If available
python -m pytest tests/ # Run tests
```

## 📁 Project Structure

### **Core Learning Projects**

#### 🔄 [Sorting Algorithms Project](./sorting-algorithms-project/)
Complete implementations of fundamental sorting algorithms with visualizations.
- **Algorithms**: Bubble, Selection, Insertion, Merge, Quick, Radix Sort
- **Features**: Interactive animations, comprehensive tests, performance comparisons
- **Tech Stack**: Python, Matplotlib, NumPy

#### 🌐 [Web Applications Project](./web-applications-project/)
Full-stack web applications demonstrating Flask and FastAPI frameworks.
- **Flask Apps**: Keyword processing, Elasticsearch integration
- **FastAPI**: Complete blog API with SQLAlchemy ORM
- **Features**: RESTful APIs, database integration, interactive documentation

#### 📊 [Algorithms and Data Structures](./algorithms-and-data-structures/)
Classic computer science algorithms with academic-level documentation.
- **Algorithms**: Dijkstra's shortest path algorithm
- **Features**: Graph implementations, LaTeX documentation, comprehensive testing
- **Educational**: Perfect for CS education and interview preparation

#### 🏭 [Design Patterns Project](./design-patterns-project/)
Object-oriented design pattern implementations with real-world examples.
- **Patterns**: Factory pattern (with more planned)
- **Features**: Employee management system, comprehensive examples
- **Educational**: SOLID principles, OOP best practices

#### 🏦 [Fintech Tools Project](./fintech-tools/) ⭐ **NEW**
Comprehensive fintech toolkit for banking, payments, and financial protocols.
- **Features**: Banking operations, payment processing, FIX/FAST/ITCH protocols
- **Modules**: Account management (BO & Client), back-office operations
- **Security**: JWT authentication, RBAC, password hashing
- **Tech Stack**: FastAPI, Pydantic, SQLAlchemy, industry-standard protocols

#### ✈️ [Drone 3D Printing Design Project](./drone-3d-printing-design/) ⭐ **NEW**
Learn to design parametric drone/RC aircraft parts for 3D printing using Python.
- **Features**: Parametric CAD with CadQuery, STL export, engineering validation
- **Phases**: 7 progressive phases from Python basics to flight-ready parts
- **Parts**: Motor mounts, arms, frames, camera mounts, battery trays, landing gear
- **Learning Path**: 12-week structured course from beginner to advanced
- **Tech Stack**: CadQuery, NumPy, SciPy, 3D printing optimization

### **Advanced Specialized Projects**

#### 💼 [Oracle Job Preparation Project](./oracle-job-prep/) ⭐ **NEW**
Comprehensive preparation guide for Oracle technical interviews and careers.
- **Features**: Database (SQL, PL/SQL), Algorithms, System Design, Cloud Computing
- **Coverage**: Software Engineer, DBA, Cloud Engineer role preparation
- **Content**: 100+ coding problems, SQL queries, system design patterns
- **Learning Path**: 10-week structured study plan with mock interviews
- **Tech Stack**: Python, Oracle DB, SQL, System Design patterns

#### 🤖 [AI Development Project](./ai-development-project/) ⭐ **NEW**
Comprehensive AI development learning project with practical examples.
- **Features**: LLMs, Prompt Engineering, RAG, Vector Databases, AI Agents
- **Complexity Levels**: 🟢 Beginner → 🔴 Expert (4 progressive levels)
- **Learning Path**: Structured 12-week progression from basics to autonomous agents
- **Tech Stack**: OpenAI/Ollama, ChromaDB, FastAPI, Vector embeddings
- **Examples**: 35,000+ word guide with working code for all major AI concepts

#### 💰 [NASDAQ CSE Trading Simulator](./nasdaq-cse/) (Python)
Professional-grade trading simulator with AI assistance.
- **Features**: Real-time trading, AI bot, risk management, FIX/FAST protocols
- **Tech Stack**: FastAPI, SQLAlchemy, WebSocket, Scikit-learn

#### 🚀 [NASDAQ CSE Trading Simulator - Go](./nasdaq-cse-go/)
High-performance Go implementation of the trading simulator.
- **Features**: Enhanced performance, concurrent processing, native Go implementation
- **Tech Stack**: Go, Gin, GORM, Gorilla WebSocket

#### 📈 [Bayesian Statistics & AI Tools](./nasdaq-bayesian-math-ai-stats/)
Advanced statistical analysis and AI interview preparation tools.
- **Features**: Bayesian market analysis, AI interview questions trainer
- **Tech Stack**: PyMC3, Tkinter, Statistical analysis

#### ✈️ [AI Flight Tracker](./ai-flight-tracker/)
Flight tracking application with AI capabilities.

#### 🤖 [AI Generation Tools](./ai-gen/)
AI-powered content generation utilities.

## 🚀 Quick Start

Each project is self-contained. Navigate to any project directory and follow its README:

```bash
# Example: Running the sorting algorithms project
cd sorting-algorithms-project
pip install -r requirements.txt
python src/basic_sorting.py

# Example: Running the web applications
cd web-applications-project
pip install -r requirements.txt
cd flask-app && python keyword_processor.py
```

## 🎓 Educational Value

This repository provides:
- **Structured Learning**: Progress from basic algorithms to complex applications
- **Best Practices**: Proper project organization, testing, documentation
- **Real-World Examples**: Practical applications of theoretical concepts
- **Multiple Paradigms**: Procedural, OOP, functional programming patterns
- **Technology Diversity**: Web frameworks, databases, AI/ML, algorithms

## 📋 Project Comparison

| Project | Language | Complexity | Focus Area | Key Technologies |
|---------|----------|------------|------------|------------------|
| **Oracle Job Prep** | **Python** | **🟢→🔴 Progressive** | **Interview Preparation** | **SQL, PL/SQL, Algorithms, System Design** |
| **AI Development** | **Python** | **🟢→🔴 Progressive** | **AI Development** | **LLMs, RAG, Vector DBs, Agents** |
| **Fintech Tools** | **Python** | **Intermediate-Advanced** | **Financial Technology** | **FastAPI, FIX/FAST/ITCH, JWT Auth** |
| **Drone 3D Design** | **Python** | **🟢→🔴 Progressive** | **CAD & 3D Printing** | **CadQuery, NumPy, Parametric Design** |
| Sorting Algorithms | Python | Beginner | Algorithms | Matplotlib, NumPy |
| Web Applications | Python | Intermediate | Web Development | Flask, FastAPI, SQLAlchemy |
| Algorithms & DS | Python | Intermediate | Computer Science | Graph theory, Academic documentation |
| Design Patterns | Python | Intermediate | Software Design | OOP, SOLID principles |
| NASDAQ CSE | Python | Advanced | Financial Technology | Trading, AI, Real-time systems |
| NASDAQ CSE Go | Go | Advanced | System Programming | High performance, Concurrency |
| Bayesian Stats | Python | Advanced | Data Science | Statistical analysis, ML |

## 🔧 Development Setup

### Prerequisites
- Python 3.7+
- Go 1.19+ (for Go projects)
- Git

### Installation
```bash
git clone https://github.com/smaruf/python-ai-course.git
cd python-ai-course

# Navigate to any project and install its dependencies
cd [project-name]
pip install -r requirements.txt
```

## 🧪 Testing

Each project includes comprehensive tests:
```bash
# Run tests for any project
cd [project-name]
python -m pytest tests/ -v
```

## 📚 Learning Path

**Recommended progression:**
1. **AI Development** → Start here! Learn modern AI development from basics to advanced
2. **Sorting Algorithms** → Learn basic algorithm concepts and programming fundamentals  
3. **Design Patterns** → Understand OOP and software design principles
4. **Algorithms & Data Structures** → Advanced CS concepts and graph theory
5. **Web Applications** → Full-stack development with modern frameworks
6. **Fintech Tools** → Financial technology with banking and messaging protocols
7. **Drone 3D Design** → Parametric CAD design for 3D printing and hardware
8. **NASDAQ CSE** → Complex system integration with real-time trading
9. **Bayesian Stats** → Advanced data science and statistical AI

### 🎯 Quick Start Recommendations

**Preparing for Oracle Interview?** → Start with **Oracle Job Preparation Project**
**New to Programming?** → Start with **Sorting Algorithms Project**
**New to AI?** → Start with **AI Development Project** (🟢 Beginner level)
**Experienced Developer?** → Jump to **AI Development Project** (🟡 Intermediate level)
**Interest in Finance/Trading?** → Explore **Fintech Tools Project** or **NASDAQ CSE Project**
**Want Full-Stack Skills?** → Try **Web Applications Project**
**Interest in Hardware/Drones/3D Printing?** → Check out **Drone 3D Printing Design Project**

## 🤝 Contributing

Each project welcomes contributions:
- Bug fixes and improvements
- New algorithms and patterns
- Enhanced documentation
- Additional test cases

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
