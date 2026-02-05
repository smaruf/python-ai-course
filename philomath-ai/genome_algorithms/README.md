# Genome Algorithms - Programming for Lovers in Python

This directory contains comprehensive Python implementations of genome algorithms from the "Programming for Lovers in Python: Genome Algorithms" course by Phillip Compeau. These implementations are educational, focusing on clarity and understanding while also demonstrating optimization techniques.

## 📚 Overview

In molecular biology, understanding where DNA replication begins (the origin of replication, or "ori") is fundamental. These algorithms help identify the ori by:

1. **Finding frequent patterns (clumps)** - Identifying DnaA boxes where replication proteins bind
2. **Computing GC-skew** - Detecting asymmetries in DNA composition caused by replication
3. **Optimizing performance** - Making algorithms fast enough for real genomes (millions of base pairs)
4. **Visualizing results** - Creating clear plots to understand and communicate findings

## 🧬 Biological Background

### DNA Replication

- DNA replication starts at the **origin of replication (ori)**
- In bacteria like *E. coli*, proteins called **DnaA** bind to specific DNA sequences called **DnaA boxes**
- These DnaA boxes form **clumps** - regions where a particular pattern appears frequently
- Replication creates an **asymmetry** in DNA composition (GC-skew) that points to the ori

### The Problem

Given a bacterial genome (millions of base pairs), find where replication begins.

### The Computational Approach

1. Search for clumps of k-mers (DnaA box candidates)
2. Compute the GC-skew array to find asymmetry
3. Look for correlation: clumps near skew minimum → likely ori location

## 📁 Files and Modules

### 01_clump_finding.py
**Finding DnaA Boxes - Pattern Frequency Analysis**

- `find_clumps_naive(text, k, L, t)` - Naive O(n·L·k) implementation
- `find_clumps_optimized(text, k, L, t)` - Optimized O(n·k) sliding window
- `pattern_count(text, pattern)` - Count pattern occurrences

**Concepts**: Sliding window, hash tables, frequency counting

**Example**:
```python
import importlib.util
import os

# Helper to import modules with numeric prefixes
def load_module(filename):
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load and use the module
clump_module = load_module('01_clump_finding.py')
find_clumps_optimized = clump_module.find_clumps_optimized

genome = "CGGACTCGACAGATGTGAAGAA..." # E. coli fragment
clumps = find_clumps_optimized(genome, k=9, L=500, t=3)
# Returns: {'CGACAGAGT', 'GAAGAACGA', ...}
```

### 02_skew_array.py
**Finding the Origin of Replication - GC-Skew Analysis**

- `compute_skew(genome)` - Calculate skew at each position
- `find_min_skew_positions(genome)` - Find candidate ori locations
- `analyze_skew(genome)` - Comprehensive skew statistics
- `print_skew_diagram(genome)` - Text-based visualization

**Concepts**: Cumulative sums, array algorithms, asymmetry detection

**Example**:
```python
import importlib.util
import os

# Helper to import modules with numeric prefixes
def load_module(filename):
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

skew_module = load_module('02_skew_array.py')
find_min_skew_positions = skew_module.find_min_skew_positions

genome = "TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT"
min_positions = find_min_skew_positions(genome)
# Returns: [11, 24] - candidate ori locations
```

**Key Insight**: The skew value is `#G - #C` from start to position i. DNA replication asymmetry causes skew to reach minimum near ori.

### 03_motif_finding.py
**Motif Finding - Discovering Regulatory Sequences**

- `find_motifs(dna_list, k, d)` - Find (k,d)-motifs in DNA sequences
- `median_string(dna_list, k)` - Find median string (consensus motif)
- `profile_most_probable(text, k, profile)` - Profile-based k-mer search
- `greedy_motif_search(dna_list, k, t)` - Greedy motif discovery
- `create_profile_matrix(motifs)` - Build profile from aligned motifs

**Concepts**: Transcription factor binding sites, profile matrices, greedy algorithms

**Example**:
```python
import importlib.util
import os

def load_module(filename):
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

motif_module = load_module('03_motif_finding.py')
find_motifs = motif_module.find_motifs

dna_sequences = ["ATTTGGC", "TGCCTTA", "CGGTATC", "GAAAATT"]
motifs = find_motifs(dna_sequences, k=3, d=1)
# Returns: {'ATA', 'ATT', 'GTT', 'TTT'} - motifs with at most 1 mismatch
```

### 04_hamming_distance.py
**String Distance and Approximate Matching**

- `hamming_distance(str1, str2)` - Calculate Hamming distance
- `approximate_pattern_match(pattern, text, d)` - Find approximate occurrences
- `neighbors(pattern, d)` - Generate all d-neighbors
- `frequent_words_with_mismatches(text, k, d)` - Most frequent approximate k-mers
- `reverse_complement(dna)` - Compute reverse complement

**Concepts**: Point mutations, approximate string matching, evolutionary distance

**Example**:
```python
import importlib.util
import os

def load_module(filename):
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

hamming_module = load_module('04_hamming_distance.py')
approximate_pattern_match = hamming_module.approximate_pattern_match

text = "CGCCCGAATCCAGAACGCATTCCCATATTTCGGGACCACTGGCCTCCACGGTACGGACGTCAATCAAAT"
pattern = "ATTCTGGA"
matches = approximate_pattern_match(pattern, text, d=3)
# Returns: [6, 7, 26, 27] - positions with at most 3 mismatches
```

### 05_optimization_comparison.py
**Algorithm Optimization - Performance Analysis**

- `generate_random_genome(length)` - Create test data
- `time_function(func, *args)` - Benchmark execution time
- `compare_algorithms(genome, k, L, t)` - Side-by-side comparison
- `benchmark_scaling(sizes)` - Performance vs input size

**Concepts**: Big-O analysis, profiling, sliding window optimization

**Example**:
```python
import importlib.util
import os

def load_module(filename):
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

opt_module = load_module('05_optimization_comparison.py')
compare_algorithms = opt_module.compare_algorithms
generate_random_genome = opt_module.generate_random_genome

genome = generate_random_genome(50000)
results = compare_algorithms(genome, k=9, L=500, t=3)
# Output:
#   Naive algorithm:     45.32 seconds
#   Optimized algorithm: 0.18 seconds
#   Speedup:             251.78x faster
```

**Performance Comparison**:
- Naive: O((n-L)·L·k) → 450 million operations for n=100k, L=500, k=9
- Optimized: O(n·k) → 900k operations (500x faster!)

### 06_visualization.py
**Genomic Data Visualization - Making Sense of Results**

- `plot_skew(genome, title)` - Line plot of skew array with minimum highlighted
- `visualize_clump_locations(genome, clumps, k)` - Heatmap showing where clumps appear
- `plot_combined_analysis(genome, k, L, t)` - Multi-panel comprehensive view

**Concepts**: Matplotlib, scientific visualization, data communication

**Example**:
```python
import importlib.util
import os

def load_module(filename):
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

viz_module = load_module('06_visualization.py')
plot_skew = viz_module.plot_skew

genome = "GAGCCACCGCGATA..."
plot_skew(genome, "E. coli Fragment - GC Skew")
# Creates plot showing skew values and minimum positions
```

**Requires**: matplotlib, numpy (install via `pip install matplotlib numpy`)

### 07_sequence_alignment.py
**Sequence Alignment - Comparing DNA Sequences**

- `global_alignment(seq1, seq2)` - Needleman-Wunsch algorithm
- `local_alignment(seq1, seq2)` - Smith-Waterman algorithm
- `longest_common_subsequence(seq1, seq2)` - LCS implementation
- `edit_distance(seq1, seq2)` - Levenshtein distance
- `alignment_statistics(aligned1, aligned2)` - Calculate alignment metrics

**Concepts**: Dynamic programming, sequence homology, evolutionary relationships

**Example**:
```python
import importlib.util
import os

def load_module(filename):
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

align_module = load_module('07_sequence_alignment.py')
global_alignment = align_module.global_alignment

score, aligned1, aligned2 = global_alignment("GATTACA", "GCATGCU")
# Returns alignment score and aligned sequences with gaps
```

### 08_complete_workflow.py
**End-to-End Pipeline - Finding Ori in Real Genomes**

- `simulate_genome(length, gc_content, ori_position)` - Generate test genomes
- `find_origin_of_replication(genome, k, L, t)` - Complete analysis pipeline
- `print_analysis_report(results, genome)` - Detailed results summary
- `load_genome_from_file(filepath)` - Load FASTA files

**Concepts**: Pipeline integration, workflow automation, result interpretation

**Example**:
```python
import importlib.util
import os

def load_module(filename):
    path = os.path.join('philomath-ai/genome_algorithms', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

workflow_module = load_module('08_complete_workflow.py')
find_origin_of_replication = workflow_module.find_origin_of_replication
simulate_genome = workflow_module.simulate_genome

# Simulate E. coli-like genome
genome = simulate_genome(20000, gc_content=0.51, ori_position=10000, seed=42)

# Run complete analysis
results = find_origin_of_replication(genome, k=9, L=500, t=3)

# Results include:
# - skew_analysis: Full skew statistics
# - candidate_ori_positions: Minimum skew positions
# - all_clumps: DnaA box candidates
# - predicted_ori: Best ori prediction
```

## 🎓 Learning Objectives

By studying these implementations, you will learn:

### 1. Algorithm Design
- Pattern matching in strings
- Sliding window techniques
- Frequency analysis
- Array-based algorithms

### 2. Performance Optimization
- Identifying bottlenecks (Big-O analysis)
- Incremental updates vs recomputation
- Hash tables for O(1) lookups
- Memory vs speed trade-offs

### 3. Bioinformatics
- DNA structure and replication
- Origin of replication (ori)
- DnaA boxes and protein binding
- GC-skew asymmetry

### 4. Software Engineering
- Modular design
- Code documentation
- Testing and validation
- Scientific computing

### 5. Data Visualization
- Creating informative plots
- Communicating scientific results
- Multi-panel figures
- Annotation and labeling

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/smaruf/python-ai-course.git
cd python-ai-course/philomath-ai/genome_algorithms

# Install dependencies (if needed for visualization)
pip install matplotlib numpy
```

### Quick Start

The easiest way to use these modules is to run them directly or import using importlib:

```python
import importlib.util
import os

# Helper function to load modules with numeric prefixes
def load_genome_module(filename):
    """Load a genome algorithm module by filename."""
    base_path = 'philomath-ai/genome_algorithms'
    path = os.path.join(base_path, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules
clump_module = load_genome_module('01_clump_finding.py')
skew_module = load_genome_module('02_skew_array.py')
workflow_module = load_genome_module('05_complete_workflow.py')

# Use the functions
find_clumps_optimized = clump_module.find_clumps_optimized
find_min_skew_positions = skew_module.find_min_skew_positions
find_origin_of_replication = workflow_module.find_origin_of_replication

# Example genome (E. coli fragment)
genome = "CGGACTCGACAGATGTGAAGAACGACAATGTGAAGACTCGACACGACAGAGTGAAGAGAAGAGGAAACATTGTAA"

# Find clumps
clumps = find_clumps_optimized(genome, k=5, L=50, t=4)
print(f"Found {len(clumps)} clumps: {clumps}")

# Find ori candidates
min_positions = find_min_skew_positions(genome)
print(f"Minimum skew at positions: {min_positions}")

# Complete analysis (with larger genome)
results = find_origin_of_replication(genome, k=9, L=500, t=3)
print(f"Predicted ori: {results['predicted_ori']}")
```

### Running Examples

Each module can be run standalone:

```bash
# Run individual modules
python 01_clump_finding.py
python 02_skew_array.py
python 03_motif_finding.py
python 04_hamming_distance.py
python 05_optimization_comparison.py
python 06_visualization.py  # Requires matplotlib
python 07_sequence_alignment.py
python 08_complete_workflow.py
```

## 📊 Real-World Example: *E. coli*

For the *E. coli* K-12 genome (~4.6 million base pairs):

**Parameters**:
- k = 9 (DnaA boxes are 9bp)
- L = 500 (window size)
- t = 3 (minimum frequency)

**Expected Results**:
- Ori location: ~3,923,620 bp (experimentally validated)
- Common DnaA boxes: TTATCCACA, TTATNCACA
- Analysis time: 5-30 seconds (optimized algorithm)

**To analyze real *E. coli* genome**:
1. Download from NCBI: GenBank accession U00096.3
2. Save as FASTA file
3. Run: `python 08_complete_workflow.py` (modify to load your file)

## 📖 Course Connection

These implementations correspond to topics from "Programming for Lovers in Python: Genome Algorithms":

- **Lecture 1-2**: Pattern finding, frequency analysis (01_clump_finding.py)
- **Lecture 3**: GC-skew and ori finding (02_skew_array.py)
- **Lecture 4**: Motif finding algorithms (03_motif_finding.py)
- **Lecture 5**: Approximate pattern matching (04_hamming_distance.py)
- **Lecture 6**: Algorithm optimization (05_optimization_comparison.py)
- **Lecture 7**: Data visualization (06_visualization.py)
- **Lecture 8**: Sequence alignment (07_sequence_alignment.py)
- **Capstone**: Integrated workflow (08_complete_workflow.py)

## 🔧 Technical Details

### Time Complexity Summary

| Algorithm | Naive | Optimized |
|-----------|-------|-----------|
| Clump Finding | O((n-L)·L·k) | O(n·k) |
| Skew Array | - | O(n) |
| Min Skew Positions | - | O(n) |

### Space Complexity

| Algorithm | Space |
|-----------|-------|
| Clump Finding | O(4^k) worst case, typically much less |
| Skew Array | O(n) |
| Visualization | O(n) |

### Typical Parameters

| Genome Type | k | L | t |
|-------------|---|---|---|
| Bacteria (small) | 9 | 500 | 3 |
| Bacteria (large) | 9 | 500-1000 | 3-4 |
| Testing/Demo | 5 | 50-100 | 3-4 |

## 🧪 Testing

Each module includes built-in examples and tests:

```python
# Each file has a main block with tests
if __name__ == "__main__":
    # Example usage and test cases
    ...
```

To run tests:
```bash
python -m doctest 01_clump_finding.py -v
python -m doctest 02_skew_array.py -v
```

## 📚 Additional Resources

### Bioinformatics
- [Rosalind](http://rosalind.info/) - Bioinformatics problems
- [NCBI GenBank](https://www.ncbi.nlm.nih.gov/genbank/) - Real genome data
- "*Bioinformatics Algorithms*" by Compeau & Pevzner

### Python & Algorithms
- [Python documentation](https://docs.python.org/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Matplotlib tutorials](https://matplotlib.org/stable/tutorials/)

### Course Materials
- "Programming for Lovers in Python: Genome Algorithms" by Phillip Compeau
- Coursera: Bioinformatics Specialization

## 🤝 Contributing

This is an educational project. Improvements welcome:
- Add more visualization options
- Implement additional genome algorithms
- Improve documentation
- Add more test cases
- Optimize further

## 📄 License

See the main repository LICENSE file.

## 🙏 Acknowledgments

- Phillip Compeau for the "Programming for Lovers" course
- The bioinformatics community for algorithm development
- *E. coli* researchers for experimental validation

## 💡 Tips for Learning

1. **Start with 01_clump_finding.py** - Understand the basic problem
2. **Run 02_skew_array.py** - Learn about GC-skew biology
3. **Explore 03_motif_finding.py** - Discover regulatory sequences
4. **Practice with 04_hamming_distance.py** - Master approximate matching
5. **Compare with 05_optimization_comparison.py** - Measure performance
6. **Visualize with 06_visualization.py** - Make results clear
7. **Align sequences with 07_sequence_alignment.py** - Compare DNA sequences
8. **Try 08_complete_workflow.py** - See it all work together
9. **Modify parameters** - Understand their effects
10. **Generate test data** - Create your own genomes
11. **Read the comments** - They explain biological context
12. **Ask questions** - Bioinformatics is complex but learnable!

---

**Happy Genome Hunting! 🧬🔬**
