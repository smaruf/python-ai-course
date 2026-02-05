# Philomath AI - Bioinformatics Learning Project

Welcome to **Philomath AI**, a comprehensive educational project implementing bioinformatics algorithms from the "Programming for Lovers in Python: Genome Algorithms" course by Phillip Compeau.

## 📚 Project Overview

This project provides a complete learning module for understanding genome algorithms through hands-on Python implementations. Each module includes:

- **Comprehensive documentation** with biological context
- **Progressive implementations** from naive to optimized
- **Real-world examples** using bacterial genome data
- **Visual demonstrations** of algorithms in action
- **Performance comparisons** showing optimization impact

## 🎯 Learning Objectives

By working through this project, you will master:

### Programming Skills
- **Python fundamentals**: Functions, data structures, loops, comprehensions
- **Algorithm design**: Pattern matching, sliding windows, dynamic programming
- **Performance optimization**: Big-O analysis, hash tables, incremental updates
- **Data visualization**: Scientific plotting with matplotlib
- **Software engineering**: Modular design, documentation, testing

### Bioinformatics Concepts
- **DNA structure and replication**: Understanding molecular biology fundamentals
- **Origin of replication (ori)**: Finding where DNA replication begins
- **DnaA boxes**: Identifying protein binding sites in genomes
- **GC-skew analysis**: Detecting strand asymmetries
- **Motif finding**: Discovering regulatory sequences
- **Sequence alignment**: Comparing DNA sequences
- **Pattern matching**: Finding approximate and exact matches

### Computational Biology
- Working with real genomic data (E. coli, Salmonella)
- Analyzing millions of base pairs efficiently
- Interpreting biological significance of computational results
- Bridging computer science and molecular biology

## 📁 Directory Structure

```
philomath-ai/
├── README.md                           # This file - project overview
├── requirements.txt                    # Python dependencies
└── genome_algorithms/                  # Main module directory
    ├── README.md                       # Detailed module documentation
    ├── 01_clump_finding.py            # Finding DnaA boxes (clumps)
    ├── 02_skew_array.py               # GC-skew analysis for ori finding
    ├── 03_motif_finding.py            # Motif discovery algorithms
    ├── 04_hamming_distance.py         # String distance and approximate matching
    ├── 05_optimization_comparison.py   # Performance benchmarking
    ├── 06_visualization.py             # Genomic data visualization
    ├── 07_sequence_alignment.py        # Sequence alignment algorithms
    ├── 08_complete_workflow.py         # End-to-end analysis pipeline
    └── test_all.py                     # Test suite
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/smaruf/python-ai-course.git
cd python-ai-course/philomath-ai
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Running Examples

Each module can be run standalone to see demonstrations:

```bash
cd genome_algorithms

# Find DnaA boxes in E. coli fragments
python 01_clump_finding.py

# Analyze GC-skew to find ori
python 02_skew_array.py

# Discover motifs in DNA sequences
python 03_motif_finding.py

# Calculate Hamming distance and find approximate matches
python 04_hamming_distance.py

# Compare algorithm performance
python 05_optimization_comparison.py

# Visualize genomic data
python 06_visualization.py

# Align DNA sequences
python 07_sequence_alignment.py

# Run complete ori-finding pipeline
python 08_complete_workflow.py
```

### Using in Your Code

```python
import importlib.util
import os

def load_genome_module(filename):
    """Helper to load modules with numeric prefixes."""
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load and use
clump_module = load_genome_module('01_clump_finding.py')
skew_module = load_genome_module('02_skew_array.py')

# Find clumps
genome = "CGGACTCGACAGATGTGAAGAACGACAATGTGAAGACTCGACACGACAGAGTGAAGAGAAGAGGAAACATTGTAA"
clumps = clump_module.find_clumps_optimized(genome, k=5, L=50, t=4)

# Find ori candidates
ori_positions = skew_module.find_min_skew_positions(genome)
```

## 📖 Course Reference

This project implements algorithms from **"Programming for Lovers in Python: Genome Algorithms"** by Phillip Compeau, covering:

- **Module 1**: Pattern finding and frequency analysis
- **Module 2**: Clump finding in E. coli genome
- **Module 3**: GC-skew and origin of replication
- **Module 4**: Performance optimization techniques
- **Module 5**: Motif finding and regulatory sequences
- **Module 6**: Sequence alignment and comparison
- **Capstone**: Integrated genomic analysis workflows

## 🧬 Real-World Applications

These algorithms are used in:

- **Genome sequencing projects**: Finding ori in newly sequenced bacteria
- **Synthetic biology**: Designing artificial chromosomes
- **Drug discovery**: Identifying antibiotic resistance mechanisms
- **Evolutionary biology**: Studying genome evolution
- **Biotechnology**: Engineering bacteria for industrial applications

## 📚 Additional Resources

### Bioinformatics Learning
- [Rosalind](http://rosalind.info/) - Bioinformatics programming challenges
- [NCBI GenBank](https://www.ncbi.nlm.nih.gov/genbank/) - Real genome database
- [Bioinformatics Algorithms Book](http://bioinformaticsalgorithms.com/) - Comprehensive textbook

### Python & Algorithms
- [Python Official Documentation](https://docs.python.org/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/)

### Online Courses
- Coursera: Bioinformatics Specialization (UCSD)
- EdX: Introduction to Computational Thinking and Data Science (MIT)

## 🤝 Contributing

This is an educational project. Contributions welcome:

- Add new algorithms (protein analysis, RNA folding, etc.)
- Improve visualizations
- Add more test cases
- Enhance documentation
- Create Jupyter notebooks
- Add real genome analysis examples

## 📄 License

See the main repository [LICENSE](../LICENSE) file.

## 🙏 Acknowledgments

- **Phillip Compeau** - Course creator and bioinformatics educator
- **Pavel Pevzner** - Co-author of bioinformatics algorithms
- **The bioinformatics community** - For algorithm development and validation
- **E. coli researchers** - For experimental data and validation

## 💡 Learning Path

**Recommended progression**:

1. **Start with basics**: 01_clump_finding.py
2. **Understand skew**: 02_skew_array.py  
3. **Learn motif finding**: 03_motif_finding.py
4. **Master string matching**: 04_hamming_distance.py
5. **Compare performance**: 05_optimization_comparison.py
6. **Visualize results**: 06_visualization.py
7. **Align sequences**: 07_sequence_alignment.py
8. **Complete pipeline**: 08_complete_workflow.py

Each module builds on previous concepts, so following this order is recommended for maximum learning benefit.

---

**Ready to explore the fascinating world where biology meets computation? Let's dive in! 🧬💻**
