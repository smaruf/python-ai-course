# Rosalind k-mers & Distance — Sessions 3–4

> **Part of [Philomath AI](../README.md)**

This module implements three string-algorithm problems from the
[Rosalind](https://rosalind.info) bioinformatics learning platform, focused on
**k-mer analysis** and **string distance metrics** — two foundational tools in
computational biology used for everything from genome assembly to phylogenetics.

---

## 📚 Problems Covered

| # | Problem | Rosalind ID | Topic |
|---|---------|-------------|-------|
| 1 | [Counting Point Mutations](#1-hamm--counting-point-mutations) | [HAMM](https://rosalind.info/problems/hamm/) | Hamming distance, string comparison |
| 2 | [k-mer Composition](#2-kmer--k-mer-composition) | [KMER](https://rosalind.info/problems/kmer/) | k-mer profiles, lexicographic enumeration |
| 3 | [Finding a Motif in DNA](#3-subs--finding-a-motif-in-dna) | [SUBS](https://rosalind.info/problems/subs/) | Substring search, overlapping matches |

---

## 🧬 Problem Explanations

### 1. HAMM — Counting Point Mutations

**Concept:** A **point mutation** is a single nucleotide substitution in a DNA
string.  The **Hamming distance** dH(s, t) between two strings of equal length
is the number of positions at which the corresponding characters differ — the
minimum number of point mutations separating the two sequences.

```
s = GAGCCTACTAACGGGAT
t = CATCGTAATGACGGCCT
      ^^^   ^^^  ^        ← 7 mismatches
```

**Problem:** Given two DNA strings s and t of equal length, return dH(s, t).

**Algorithm:**
```python
sum(a != b for a, b in zip(s, t))   # O(n), single pass
```

**Sample:** s=`GAGCCTACTAACGGGAT`, t=`CATCGTAATGACGGCCT` → **7**

| Property | Value |
|----------|-------|
| Time complexity | O(n) |
| Space complexity | O(1) |
| Raises | `ValueError` if lengths differ |

---

### 2. KMER — k-mer Composition

**Concept:** A **k-mer** is a substring of length k.  The **k-mer composition**
of a DNA string is the vector of counts of all 4^k possible k-mers (over
{A, C, G, T}) in lexicographic order.  k-mers absent from the string contribute
a count of 0.

For a string of length L, the sliding window yields L − k + 1 overlapping
k-mers, covering every position:

```
DNA = A C G T A C G T
       ↑
k=3:  ACG, CGT, GTA, TAC, ACG, CGT  →  6 = 8−3+1 k-mers
```

**Problem:** Given a DNA string and integer k, return the 4^k-length composition
vector in lexicographic order.

**Key functions:**
- `all_kmers(k)` — generates all 4^k k-mers using `itertools.product`
- `kmer_count(dna, k)` — sliding window counts (dict, only observed k-mers)
- `kmer_composition(dna, k)` — full length-4^k vector with zeros for absent k-mers

**Why k-mers?**
- Genome assembly: detect overlaps between sequencing reads
- Taxonomic classification: fast fingerprinting (Kraken2, Mash)
- Repeat detection: high-count k-mers reveal repetitive regions

**Sample:** dna=`CTTCGAAAGTTTGGGCCGCTTTGGCCC`, k=4 → 256 integer counts

---

### 3. SUBS — Finding a Motif in DNA

**Concept:** A **motif** is a short, recurring pattern with biological
significance — e.g., a restriction enzyme recognition site (`GAATTC` for
EcoRI) or a transcription factor binding site.  Finding all occurrences
requires handling **overlapping** matches.

```
DNA   = G A T A T A T G C A T A T A C T T
Motif =     A T A T                         ← position 2
Motif =         A T A T                     ← position 4 (overlapping)
Motif =                   A T A T           ← position 10
```

**Problem:** Given DNA string s and motif t, return all 1-indexed start
positions of t in s (overlapping occurrences included).

**Algorithm — why not str.find alone?**
`str.find(motif, start)` skips ahead by `len(motif)` implicitly if you update
`start = idx + len(motif)` — this misses overlapping matches.  Setting
`start = idx + 1` always finds the next occurrence regardless of overlap.

**Sample:** dna=`GATATATGCATATACTT`, motif=`ATAT` → **[2, 4, 10]** (1-indexed)

---

## 📁 Directory Structure

```
rosalind-kmers/
├── README.md                   # This file
├── 01_hamming_distance.py      # HAMM: Counting Point Mutations
├── 02_kmer_composition.py      # KMER: k-mer Composition
├── 03_finding_motif.py         # SUBS: Finding a Motif in DNA
└── test_all.py                 # Full test suite (all 3 problems)
```

---

## 🚀 Quick Start

```bash
cd philomath-ai/rosalind-kmers

# Run any individual problem (shows demo output with worked examples)
python 01_hamming_distance.py
python 02_kmer_composition.py
python 03_finding_motif.py

# Run the full test suite
python test_all.py
```

No additional dependencies are required — all modules use Python's standard
library (`itertools` only).

---

## 🎯 Learning Objectives

By working through this module you will understand:

### String Algorithms
- Hamming distance as a measure of sequence divergence in O(n) time
- Sliding-window k-mer extraction and counting
- Overlapping substring search and why step size matters

### Bioinformatics Concepts
- Point mutations as the elementary units of molecular evolution
- k-mer composition vectors as sequence fingerprints
- Motif finding as the basis for restriction enzyme mapping
- 1-indexed vs 0-indexed coordinate systems in bioinformatics tools

### Python Skills
- `zip` and generator expressions for pairwise comparison
- `itertools.product` for lexicographic enumeration
- `str.find(pattern, start)` for controlled substring search
- Dictionary-based counting with `.get(key, default)`

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| Rosalind platform | https://rosalind.info |
| HAMM problem | https://rosalind.info/problems/hamm/ |
| KMER problem | https://rosalind.info/problems/kmer/ |
| SUBS problem | https://rosalind.info/problems/subs/ |
| Philomath mailing list | http://eepurl.com/iC9DSg |
| Philomath membership | https://philomath.memberful.com |

---

## 📖 How This Fits Into Philomath AI

This module covers **Sessions 3–4** of the Philomath live-coding series,
focusing on k-mer string algorithms and distance metrics.  It complements
the other modules in `philomath-ai`:

- **[Rosalind Genetics](../rosalind-genetics/)** — Mendelian genetics,
  probability, binomial distributions, log-probabilities, profile matrices
- **[Genome Algorithms](../genome_algorithms/)** — DNA pattern matching, clump
  finding, GC-skew analysis, motif finding
- **[Monte Carlo Simulation](../monte-carlo/)** — random number generation,
  dice simulation, Craps probability

Together these modules cover a broad sweep of computational biology and applied
algorithms through hands-on problem solving.
