# Philomath AI - Programming for Lovers Learning Project

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.

Welcome to **Philomath AI**, a comprehensive educational project implementing algorithms and simulations from the "Programming for Lovers in Python" course by Phillip Compeau.

## 📚 Project Overview

This project provides comprehensive learning modules for understanding computer science through hands-on Python implementations:

### Modules Available

1. **Genome Algorithms** - Bioinformatics algorithms for DNA analysis
2. **Monte Carlo Simulation** - Random number generation, probability, and simulation methods
3. **Election Simulation** - Forecasting presidential elections from polling data

Each module includes:

- **Comprehensive documentation** with real-world context
- **Progressive implementations** from basic to advanced
- **Real-world examples** and applications
- **Visual demonstrations** of concepts in action
- **Performance analysis** and statistical validation

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
├── genome_algorithms/                  # Bioinformatics module
│   ├── README.md                       # Detailed module documentation
│   ├── 01_clump_finding.py            # Finding DnaA boxes (clumps)
│   ├── 02_skew_array.py               # GC-skew analysis for ori finding
│   ├── 03_motif_finding.py            # Motif discovery algorithms
│   ├── 04_hamming_distance.py         # String distance and approximate matching
│   ├── 05_optimization_comparison.py   # Performance benchmarking
│   ├── 06_visualization.py             # Genomic data visualization
│   ├── 07_sequence_alignment.py        # Sequence alignment algorithms
│   ├── 08_complete_workflow.py         # End-to-end analysis pipeline
│   └── test_all.py                     # Test suite
├── monte-carlo/                        # Monte Carlo simulation module
│   ├── README.md                       # Detailed module documentation
│   ├── 01_random_numbers.py           # Random number generation and seeding
│   ├── 02_dice_simulation.py          # Dice rolling and law of large numbers
│   ├── 03_craps_simulation.py         # Craps game and house edge
│   └── test_all.py                     # Test suite
└── election-simulation/                # Election forecasting module
    ├── README.md                       # Detailed module documentation
    ├── 01_parsing_data.py             # Parse polling data from files
    ├── 02_single_election.py          # Simulate a single election
    ├── 03_multiple_elections.py       # Monte Carlo election simulations
    ├── 04_electoral_college.py        # Complete Electoral College simulation
    ├── test_all.py                     # Test suite
    └── data/                           # Sample polling data
        ├── sample_polls.csv            # Example swing state data
        └── README.md                   # Data format documentation
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

#### Genome Algorithms

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

#### Monte Carlo Simulation

```bash
cd monte-carlo

# Generate random numbers and explore seeding
python 01_random_numbers.py

# Simulate dice rolls and observe the law of large numbers
python 02_dice_simulation.py

# Simulate craps games and calculate house edge
python 03_craps_simulation.py
```

#### Election Simulation

```bash
cd election-simulation

# Parse polling data from a file
python 01_parsing_data.py

# Simulate a single election based on polls
python 02_single_election.py

# Run multiple simulations to see probability distribution
python 03_multiple_elections.py

# Complete Electoral College simulation
python 04_electoral_college.py
```

### Using in Your Code

```python
import importlib.util
import os

def load_module(module_dir, filename):
    """Helper to load modules with numeric prefixes."""
    path = os.path.join('philomath-ai', module_dir, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load genome algorithms
clump_module = load_module('genome_algorithms', '01_clump_finding.py')
skew_module = load_module('genome_algorithms', '02_skew_array.py')

# Find clumps
genome = "CGGACTCGACAGATGTGAAGAACGACAATGTGAAGACTCGACACGACAGAGTGAAGAGAAGAGGAAACATTGTAA"
clumps = clump_module.find_clumps_optimized(genome, k=5, L=50, t=4)

# Find ori candidates
ori_positions = skew_module.find_min_skew_positions(genome)

# Load Monte Carlo modules
dice_module = load_module('monte-carlo', '02_dice_simulation.py')
craps_module = load_module('monte-carlo', '03_craps_simulation.py')

# Roll dice
result = dice_module.roll_die()

# Play craps
game = craps_module.play_craps_once()

# Load Election Simulation modules
ec_module = load_module('election-simulation', '04_electoral_college.py')

# Run election simulation
state_polls = {
    'Pennsylvania': {'candidate_a': 48.5, 'candidate_b': 47.2, 'electoral_votes': 19},
    'Michigan': {'candidate_a': 49.1, 'candidate_b': 46.8, 'electoral_votes': 15}
}
results = ec_module.simulate_electoral_college(state_polls, num_simulations=10000)
```

## 📖 Course Reference

This project implements concepts from **"Programming for Lovers in Python"** by Phillip Compeau:

### Genome Algorithms Module
Based on the "Genome Algorithms" course, covering:

- **Module 1**: Pattern finding and frequency analysis
- **Module 2**: Clump finding in E. coli genome
- **Module 3**: GC-skew and origin of replication
- **Module 4**: Performance optimization techniques
- **Module 5**: Motif finding and regulatory sequences
- **Module 6**: Sequence alignment and comparison
- **Capstone**: Integrated genomic analysis workflows

### Monte Carlo Simulation Module
Based on "Monte Carlo Simulation and Craps", covering:

- **Random Numbers**: Generating random integers and understanding seeding
- **Dice Simulation**: Rolling dice and observing statistical properties
- **Law of Large Numbers**: How averages converge with more trials
- **Craps Rules**: Understanding the classic casino dice game
- **House Edge**: Computing the casino's advantage through simulation
- **Simulation Design**: Generalizing simulations for different scenarios

### Election Simulation Module
Based on "Simulating an Election" (streamed Feb 10, 2026), covering:

- **Chapter 2**: Forecasting a Presidential Election from Polling Data
- **Parsing Data**: Reading polling data from files
- **Single Election**: Simulating winner-take-all Electoral College
- **Monte Carlo**: Running thousands of elections with uncertainty
- **Polling Noise**: Adding random variation to model margins of error
- **Model Limitations**: Understanding why polling simulators struggle
- **Prediction Markets**: Alternative approaches like Kalshi

## 🌍 Real-World Applications

### Genome Algorithms
These algorithms are used in:

- **Genome sequencing projects**: Finding ori in newly sequenced bacteria
- **Synthetic biology**: Designing artificial chromosomes
- **Drug discovery**: Identifying antibiotic resistance mechanisms
- **Evolutionary biology**: Studying genome evolution
- **Biotechnology**: Engineering bacteria for industrial applications

### Monte Carlo Methods
These simulations are used in:

- **Finance**: Option pricing, risk analysis, portfolio optimization
- **Physics**: Particle simulations, quantum mechanics
- **Engineering**: Reliability analysis, stress testing
- **Medicine**: Drug discovery, epidemiology modeling
- **Computer Graphics**: Ray tracing, global illumination
- **Operations Research**: Queue simulation, supply chain optimization

### Election Forecasting
These techniques are used in:

- **Political campaigns**: Resource allocation, strategy planning
- **Media organizations**: Election night projections (FiveThirtyEight, The Economist)
- **Prediction markets**: Kalshi, PredictIt for aggregating information
- **Polling organizations**: Understanding uncertainty in survey data
- **Academic research**: Studying electoral systems and voter behavior
- **Policy analysis**: Evaluating effects of voting system changes

## 📚 Additional Resources

### Bioinformatics Learning
- [Rosalind](http://rosalind.info/) - Bioinformatics programming challenges
- [NCBI GenBank](https://www.ncbi.nlm.nih.gov/genbank/) - Real genome database
- [Bioinformatics Algorithms Book](http://bioinformaticsalgorithms.com/) - Comprehensive textbook

### Probability & Statistics
- [Khan Academy - Probability](https://www.khanacademy.org/math/statistics-probability)
- [Seeing Theory - Visual Statistics](https://seeing-theory.brown.edu/)
- [Introduction to Probability (Blitzstein & Hwang)](https://projects.iq.harvard.edu/stat110)

### Python & Algorithms
- [Python Official Documentation](https://docs.python.org/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/)

### Online Courses
- Coursera: Bioinformatics Specialization (UCSD)
- Coursera: Monte Carlo Methods in Finance (Columbia)
- EdX: Introduction to Computational Thinking and Data Science (MIT)

## 🤝 Contributing

This is an educational project. Contributions welcome:

- Add new modules (data science, machine learning, algorithms, etc.)
- Add new algorithms to existing modules
- Improve visualizations
- Add more test cases
- Enhance documentation
- Create Jupyter notebooks
- Add real-world analysis examples

## 📄 License

See the main repository [LICENSE](../LICENSE) file.

## 🙏 Acknowledgments

- **Phillip Compeau** - Course creator and educator at Carnegie Mellon University
- **Pavel Pevzner** - Co-author of bioinformatics algorithms
- **Programming for Lovers** - Open online course for learning programming through science
- **The bioinformatics community** - For algorithm development and validation
- **The statistics community** - For developing Monte Carlo methods

## 💡 Learning Path

### For Beginners - Start with Monte Carlo
**Recommended if new to programming or probability**:

1. **Random numbers**: monte-carlo/01_random_numbers.py
2. **Dice simulation**: monte-carlo/02_dice_simulation.py
3. **Craps game**: monte-carlo/03_craps_simulation.py

### For Intermediate - Election Simulation
**Recommended if comfortable with basic Python and interested in real-world applications**:

1. **Parse data**: election-simulation/01_parsing_data.py
2. **Single election**: election-simulation/02_single_election.py
3. **Multiple elections**: election-simulation/03_multiple_elections.py
4. **Full simulation**: election-simulation/04_electoral_college.py

### For Advanced - Genome Algorithms
**Recommended if comfortable with Python basics**:

1. **Start with basics**: genome_algorithms/01_clump_finding.py
2. **Understand skew**: genome_algorithms/02_skew_array.py  
3. **Learn motif finding**: genome_algorithms/03_motif_finding.py
4. **Master string matching**: genome_algorithms/04_hamming_distance.py
5. **Compare performance**: genome_algorithms/05_optimization_comparison.py
6. **Visualize results**: genome_algorithms/06_visualization.py
7. **Align sequences**: genome_algorithms/07_sequence_alignment.py
8. **Complete pipeline**: genome_algorithms/08_complete_workflow.py

Each module builds on previous concepts, so following these orders is recommended for maximum learning benefit.

---

**Ready to explore the fascinating world of computer science through real applications? Let's dive in! 🧬🎲🗳️💻**
