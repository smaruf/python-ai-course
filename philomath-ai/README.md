# Philomath AI - Programming for Lovers Learning Project

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [Algorithms & Data Structures](../algorithms-and-data-structures/) | [Sorting Algorithms](../sorting-algorithms-project/) | [Drone 3D Design](../drone-3d-printing-design/)

Welcome to **Philomath AI**, a comprehensive educational project implementing algorithms and simulations from the "Programming for Lovers in Python" course by Phillip Compeau.

## 📚 Project Overview

This project provides comprehensive learning modules for understanding computer science through hands-on Python implementations:

### Modules Available

1. **Genome Algorithms** - Bioinformatics algorithms for DNA analysis
2. **Monte Carlo Simulation** - Random number generation, probability, and simulation methods
3. **Election Simulation** - Forecasting presidential elections from polling data
4. **2-D Lists** - Multi-dimensional arrays and cellular automata (Conway's Game of Life)
5. **Pygame Graphics** - Intro to 2D graphics: RGB colors, drawing shapes, snowperson, and Game of Life visualization
6. **Gravity Simulator** - OOP-based gravity simulator: two-body orbits, figure-8 three-body solution, Lagrange triangle, chaos, live pygame visualization
7. **Rosalind Genetics** ⭐ - Genetics & probability problems from [Rosalind](https://rosalind.info) (Episode 4: IPRB, IEV, LIA, PROB, CONS)
8. **Trees Part 2** ⭐ - Recursion, UPGMA phylogenetics, Newick format, real biological datasets (Chapter 5)

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
<details>
    <summary>--</summary>

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
├── election-simulation/                # Election forecasting module
│   ├── README.md                       # Detailed module documentation
│   ├── 01_parsing_data.py             # Parse polling data from files
│   ├── 02_single_election.py          # Simulate a single election
│   ├── 03_multiple_elections.py       # Monte Carlo election simulations
│   ├── 04_electoral_college.py        # Complete Electoral College simulation
│   ├── test_all.py                     # Test suite
│   └── data/                           # Sample polling data
│       ├── sample_polls.csv            # Example swing state data
│       └── README.md                   # Data format documentation
├── 2d-lists/                           # 2-D lists and cellular automata
│   ├── README.md                       # Detailed module documentation
│   ├── 01_2d_tuples_and_lists.py      # 2-D data structures and initialization
│   ├── 02_list_comprehensions.py      # List comprehensions for 2-D arrays
│   ├── 03_rows_and_columns.py         # Working with rows and columns
│   ├── 04_pass_by_reference.py        # Understanding mutable objects
│   ├── 05_nested_loops.py             # Iterating through 2-D arrays
│   ├── 06_game_of_life.py             # Conway's Game of Life: flat & toroidal grids, random init
│   └── test_all.py                     # Test suite
└── pygame-graphics/                    # Pygame graphics module
    ├── README.md                       # Detailed module documentation
    ├── 01_pygame_basics.py            # pygame setup, surfaces, coordinate system
    ├── 02_rgb_colors.py               # RGB color model, color mixing utilities
    ├── 03_snowperson.py               # Drawing a snowperson from simple shapes
    ├── 04_game_of_life_visualization.py # Animated Game of Life: age colours, mouse drawing
    ├── 05_krypton_simulation.py       # Multi-faction Game of Life (Krypton theme)
    └── test_all.py                     # Test suite
gravity-simulator/                  # Gravity simulator module (Chapter 4)
    ├── README.md                       # Detailed module documentation
    ├── 01_vector_math.py              # 2D Vector class: arithmetic, magnitude, normalise
    ├── 02_body.py                     # Body class: mass, position, velocity, Euler step
    ├── 03_gravity_simulation.py       # Newton's law, leapfrog integrator, two-body orbit
    ├── 04_three_body_problem.py       # Figure-8, Lagrange, chaotic, Sun-Earth-Moon
    ├── 05_pygame_visualization.py     # Interactive live simulation with 4 scenarios
    └── test_all.py                     # Test suite
└── rosalind-genetics/                  # Rosalind genetics & probability (Episode 4)
    ├── README.md                       # Detailed module documentation
    ├── 01_iprb_mendels_first_law.py   # Mendel's First Law: P(dominant offspring)
    ├── 02_iev_expected_offspring.py    # Expected dominant offspring from 6 cross types
    ├── 03_lia_independent_alleles.py   # Independent assortment, binomial distribution
    ├── 04_prob_random_strings.py       # Log-probability of random DNA strings
    ├── 05_cons_consensus_profile.py    # Profile matrix and consensus sequence
    └── test_all.py                     # Test suite
└── trees-part2/                        # Chapter 5: recursion, UPGMA, phylogenetics
    ├── README.md                       # Module documentation
    ├── 01_recursion.py                 # Factorial, Fibonacci (naive/memo/iterative)
    ├── 02_tree_node.py                 # TreeNode class: is_leaf, count_leaves
    ├── 03_upgma.py                     # UPGMA algorithm
    ├── 04_newick.py                    # Newick format serialization/parsing
    ├── 05_pipeline.py                  # End-to-end pipeline + 5 datasets
    ├── 06_cli.py                       # Command-line interface
    ├── 07_gui.py                       # Tkinter GUI
    ├── test_all.py                     # Test suite
    └── data/                           # CSV distance matrices
        ├── README.md
        ├── great_apes.csv
        ├── hemoglobin.csv
        ├── hiv_subtypes.csv
        ├── sars_cov2.csv
        └── mtdna_haplogroups.csv
```
</details>

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

#### 2-D Lists and Cellular Automata

```bash
cd 2d-lists

# Learn about 2-D tuples and lists
python 01_2d_tuples_and_lists.py

# Master list comprehensions for 2-D arrays
python 02_list_comprehensions.py

# Work with rows and columns
python 03_rows_and_columns.py

# Understand pass by reference behavior
python 04_pass_by_reference.py

# Practice nested loops and printing
python 05_nested_loops.py

# Simulate the Game of Life with R pentomino
python 06_game_of_life.py
```

#### Pygame Graphics

```bash
cd pygame-graphics

# Learn about pygame surfaces and coordinates
python 01_pygame_basics.py

# Explore the RGB color model
python 02_rgb_colors.py

# Draw a snowperson
python 03_snowperson.py

# Visualize the Game of Life with animated circular cells
python 04_game_of_life_visualization.py
```

#### Gravity Simulator

```bash
cd gravity-simulator

# Understand 2-D vector math
python 01_vector_math.py

# Explore the Body class (OOP)
python 02_body.py

# Simulate Earth orbiting the Sun for 1 year
python 03_gravity_simulation.py

# Figure-8, Lagrange, chaos, and Sun-Earth-Moon scenarios
python 04_three_body_problem.py

# Launch the interactive pygame visualization
python 05_pygame_visualization.py
```

#### Rosalind Genetics & Probability (Episode 4)

```bash
cd rosalind-genetics

# IPRB: Mendel's First Law — P(dominant offspring) from mixed population
python 01_iprb_mendels_first_law.py

# IEV: Expected dominant offspring across six Mendelian cross types
python 02_iev_expected_offspring.py

# LIA: Independent alleles — binomial probability after k generations
python 03_lia_independent_alleles.py

# PROB: Log-probability of a random DNA string at varying GC content
python 04_prob_random_strings.py

# CONS: Consensus sequence and profile matrix from FASTA sequences
python 05_cons_consensus_profile.py

# Run the full test suite
python test_all.py
```

### Using in Your Code
<details>
    <summary>Code in Python:</summary>

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
</details>

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

### 2-D Lists Module
Based on "2-D Lists" (streamed Feb 17, 2026), covering:

- **Chapter 3**: Discovering a Self-Replicating Cellular Automaton
- **2-D Tuples and Lists**: Understanding multi-dimensional data structures
- **Proper Initialization**: Avoiding common list creation pitfalls
- **List Comprehensions**: Building 2-D arrays correctly and efficiently
- **Rows and Columns**: Navigating and manipulating 2-D structures
- **Pass by Reference**: Understanding mutable object behavior
- **Nested Loops**: Iterating through multi-dimensional data
- **Game of Life**: Conway's cellular automaton with R pentomino
- **Toroidal Grid**: Wrapping boundary conditions (`apply_rules_toroidal`)
- **Random Initialisation**: Seeded random boards (`create_random_grid`)
- **Self-Replication**: Emergent complexity from simple rules

### Pygame Graphics Module
Based on "An Intro to Graphics in Python" (Chapter 3, Programming for Lovers), covering:

- **Pygame Setup**: Initializing the display and running an event loop
- **RGB Color Model**: Mixing red, green, and blue light to create any color
- **Surfaces and Shapes**: Drawing rectangles and circles with pygame.draw
- **Coordinate System**: Understanding the top-left origin and downward y-axis
- **Snowperson Drawing**: Composing a complex drawing from simple shapes
- **Game of Life Visualization**: Animated grid with circular cells and colour
- **Age-Based Colouring**: Cells fade from green → yellow → white as they age (`draw_board_with_age`)
- **Interactive Drawing**: Mouse click/drag to toggle cells at runtime
- **Speed Control**: Adjustable animation speed with arrow keys
- **Multi-Faction Automaton**: Krypton Chronicles – themed five-state simulation (`05_krypton_simulation.py`)

### Gravity Simulator Module
Based on "Building a Gravity Simulator" (Chapter 4, Programming for Lovers), covering:

- **Chapter 4**: Using Object-Oriented Programming to Solve the Three Body Problem
- **Vector Math**: 2-D vectors for positions, velocities, and forces
- **Body Class**: Encapsulating mass, position, and velocity using OOP
- **Newton's Law**: F = G·m₁·m₂/r² and numerical integration
- **Euler vs Leapfrog**: Simple vs symplectic integrators for energy conservation
- **Two-Body Orbits**: Earth orbiting the Sun for one year with near-zero energy drift
- **Figure-8 Solution**: Chenciner-Montgomery (2000) periodic three-body orbit
- **Lagrange Triangle**: Three equal-mass bodies at corners of an equilateral triangle
- **Chaos Theory**: Demonstrating sensitivity to initial conditions (Poincaré, 1887)
- **Live Visualization**: Interactive pygame window with 4 scenarios, trails, zoom/pan

### Rosalind Genetics & Probability Module (Episode 4)
Based on Philomath Episode 4 live stream with Phillip Compeau (Carnegie Mellon),
solving genetics and probability problems on [Rosalind](https://rosalind.info):

- **IPRB — Mendel's First Law**: Sampling without replacement, complement rule,
  Punnett squares, six genotype cross types
- **IEV — Expected Offspring**: Linearity of expectation applied to Mendelian crosses,
  dominant-phenotype probabilities for each cross type
- **LIA — Independent Alleles**: Mendel's Second Law (independent assortment),
  binomial distribution, CDF tail probability P(X ≥ n)
- **PROB — Random Strings**: GC-content DNA model, log-probability to avoid underflow,
  per-nucleotide probability computation
- **CONS — Consensus and Profile**: FASTA parsing, profile matrix construction,
  consensus string derivation, sequence conservation analysis

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

### 2-D Lists and Cellular Automata
These concepts are used in:

- **Image Processing**: Every pixel in an image is stored in a 2-D array
- **Machine Learning**: Neural networks use multi-dimensional arrays (tensors)
- **Game Development**: Board games, tile-based games, terrain generation
- **Scientific Computing**: Climate models, physics simulations, numerical analysis
- **Biology**: Modeling population dynamics, tumor growth, ecosystem behavior
- **Physics**: Simulating particle systems and fluid dynamics
- **Computer Science**: Procedural content generation, data compression
- **Art and Design**: Creating generative art and music
- **Urban Planning**: Modeling city growth and traffic flow

### Pygame Graphics
These skills are used in:

- **Indie Game Development**: 2D platformers, puzzle games, arcade games
- **Education**: Interactive teaching tools and simulations
- **Data Visualization**: Custom animated charts and scientific plots
- **Generative Art**: Algorithmic artwork and animations
- **Prototyping**: Rapid prototyping of game and UI concepts

### Rosalind Genetics & Probability
These techniques are used in:

- **Population Genetics**: Predicting allele frequencies across generations (Hardy-Weinberg)
- **Breeding Programs**: Estimating expected phenotypic outcomes from controlled crosses
- **Phylogenetics**: Sequence consensus and conservation for evolutionary analysis
- **Genomics**: GC-content analysis for species identification and genome annotation
- **Drug Discovery**: Identifying conserved binding sites in protein-coding sequences
- **Bioinformatics Pipelines**: Profile matrices underpin tools like MEME, JASPAR

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

### For Intermediate - 2-D Lists and Cellular Automata
**Recommended if comfortable with basic Python and want to learn data structures**:

1. **2-D structures**: 2d-lists/01_2d_tuples_and_lists.py
2. **List comprehensions**: 2d-lists/02_list_comprehensions.py
3. **Rows and columns**: 2d-lists/03_rows_and_columns.py
4. **Pass by reference**: 2d-lists/04_pass_by_reference.py
5. **Nested loops**: 2d-lists/05_nested_loops.py
6. **Game of Life**: 2d-lists/06_game_of_life.py

### For Intermediate - Pygame Graphics
**Recommended if comfortable with Python basics and want to learn graphics**:

1. **Pygame setup**: pygame-graphics/01_pygame_basics.py
2. **RGB colors**: pygame-graphics/02_rgb_colors.py
3. **Draw snowperson**: pygame-graphics/03_snowperson.py
4. **Animate Game of Life**: pygame-graphics/04_game_of_life_visualization.py

### For Intermediate - Gravity Simulator (OOP & Physics)
**Recommended after 2-D Lists or Pygame Graphics; introduces OOP through physics**:

1. **Vector math**: gravity-simulator/01_vector_math.py
2. **Body class**: gravity-simulator/02_body.py
3. **Two-body orbit**: gravity-simulator/03_gravity_simulation.py
4. **Three-body problem**: gravity-simulator/04_three_body_problem.py
5. **Live visualization**: gravity-simulator/05_pygame_visualization.py

### For Intermediate - Rosalind Genetics & Probability (Episode 4)
**Recommended after Monte Carlo; combines genetics theory with probability**:

1. **Mendel's First Law**: rosalind-genetics/01_iprb_mendels_first_law.py
2. **Expected offspring**: rosalind-genetics/02_iev_expected_offspring.py
3. **Independent alleles**: rosalind-genetics/03_lia_independent_alleles.py
4. **Random strings**: rosalind-genetics/04_prob_random_strings.py
5. **Consensus & profile**: rosalind-genetics/05_cons_consensus_profile.py

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

**Ready to explore the fascinating world of computer science through real applications? Let's dive in! 🧬🎲🗳️🎮💻**
