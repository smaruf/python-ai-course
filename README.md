# Python AI Course - Organized Learning Projects

A comprehensive collection of Python learning projects organized into full-featured, phased project folders. Each project is self-contained with its own dependencies, documentation, tests, and examples.

## 🎯 Project Overview

This repository has been reorganized to provide structured learning experiences across different aspects of Python programming, from basic algorithms to advanced web applications and AI implementations.

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

### **Advanced Specialized Projects**

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
1. **Sorting Algorithms** → Learn basic algorithm concepts
2. **Design Patterns** → Understand OOP and software design
3. **Algorithms & Data Structures** → Advanced CS concepts
4. **Web Applications** → Full-stack development
5. **NASDAQ CSE** → Complex system integration
6. **Bayesian Stats** → Advanced data science and AI

## 🤝 Contributing

Each project welcomes contributions:
- Bug fixes and improvements
- New algorithms and patterns
- Enhanced documentation
- Additional test cases

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
