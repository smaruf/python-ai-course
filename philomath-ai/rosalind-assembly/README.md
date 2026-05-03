# Rosalind Genome Assembly — Session 8

> **Part of [Philomath AI](../README.md)** — a comprehensive learning project from
> Phillip Compeau's "Programming for Lovers in Python" course.  
> See also: [Rosalind Genetics](../rosalind-genetics/) | [Genome Algorithms](../genome_algorithms/)

This module implements two genome-assembly problems from the
[Rosalind](https://rosalind.info) bioinformatics learning platform.
Together they introduce the core ideas behind how a genome sequencer's raw
output — millions of short, noisy "reads" — is transformed into a coherent
genomic sequence.

> 🧬 **Session 8** covers the algorithmic foundations of genome assembly:
> building an overlap graph, greedy Hamiltonian-path heuristics, and
> coverage-based error correction.

---

## 📚 Problems Covered

| # | Problem | Rosalind ID | Topic |
|---|---------|-------------|-------|
| 1 | [Shortest Superstring](#1-long--genome-assembly-as-shortest-superstring) | [LONG](https://rosalind.info/problems/long/) | Overlap graph, greedy assembly |
| 2 | [Error Correction in Reads](#2-corr--error-correction-in-reads) | [CORR](https://rosalind.info/problems/corr/) | Hamming distance, trusted reads |

---

## 🧬 Problem Explanations

### 1. LONG — Genome Assembly as Shortest Superstring

**Context:** Next-generation sequencers shred a genome into millions of short
reads.  Reassembling these reads back into the original genome is a central
problem in bioinformatics.  The simplest model asks:

> *Given a collection of reads, find the shortest string that contains every
> read as a substring.*

This is the **Shortest Superstring Problem**.

**Overlap Graph:**

We model the relationships between reads as a directed weighted graph:

```
  Node  → each DNA read
  Edge  → (s → t) with weight = len(longest suffix of s that is a prefix of t)
```

A Hamiltonian path through this graph (each node visited exactly once)
defines the assembly order. Concatenating nodes along the path while
collapsing overlaps gives the shortest superstring.

**Greedy Algorithm:**

```
1. Compute all pairwise overlap lengths.
2. Find the pair (s, t) with maximum overlap.
3. Merge: superstring = s + t[overlap:]
4. Remove s and t, add the merged string.
5. Repeat until one string remains.
```

**Assumption:** The input admits a unique Hamiltonian path — no read is a
substring of another, and the overlap graph has a unique ordering.

**Sample (Rosalind LONG):**

```
>Rosalind_56  ATTAGACCTG
>Rosalind_57  CCTGCCGGAA
>Rosalind_58  AGACCTGCCG
>Rosalind_59  GCCGGAATAC
```

Key overlaps:
| Source | Target | Overlap |
|--------|--------|---------|
| ATTAGACCTG | AGACCTGCCG | 7 |
| AGACCTGCCG | CCTGCCGGAA | 7 |
| CCTGCCGGAA | GCCGGAATAC | 7 |

Assembly path → **ATTAGACCTGCCGGAATAC** (19 bp, saves 21 bp over naive concatenation)

---

### 2. CORR — Error Correction in Reads

**Context:** Sequencers introduce per-base errors (~0.1–1 %).  Erroneous reads
must be corrected before assembly — otherwise assemblers produce fragmented
contigs.

**Key Insight — Coverage:**

In a deeply sequenced sample, the true sequence appears many times.  A read
containing an error appears only once (the exact mistake is unlikely to recur).

```
Correct read  → appears ≥ 2 times (or its reverse complement does)
Erroneous read → appears only once
```

**Double-Stranded DNA:**  Reads can be sequenced from either strand, so a
read and its reverse complement represent the same genomic locus.  Both must
be counted when assessing coverage.

**Correction Algorithm:**

```
For each erroneous read r:
  Find a trusted read c such that Hamming_distance(r, c) = 1.
  Output r → c.
```

The Hamming distance counts positions where two equal-length strings differ.
One substitution is changed to produce the correction.

**Sample (Rosalind CORR):**

```
TCATC ×2  →  correct (and its RC GATGA)
TTTCC ×2  →  correct (and its RC GGAAA)
TGAAA ×1  →  erroneous: HD(TGAAA, GGAAA) = 1 → corrected to GGAAA
```

Correction output:
```
TGAAA->GGAAA
```

---

## 📁 Directory Structure

```
rosalind-assembly/
├── README.md                        # This file
├── 01_shortest_superstring.py       # LONG: Genome Assembly as Shortest Superstring
├── 02_error_correction.py           # CORR: Error Correction in Reads
└── test_all.py                      # Full test suite (both problems)
```

---

## 🚀 Quick Start

```bash
cd philomath-ai/rosalind-assembly

# Run any individual problem (shows demo output with worked examples)
python 01_shortest_superstring.py
python 02_error_correction.py

# Run the full test suite
python test_all.py
```

No additional dependencies are required — all modules use Python's
standard library (`collections` only).

---

## 🎯 Learning Objectives

By working through this module you will understand:

### Genome Assembly
- Why shotgun sequencing produces overlapping reads
- How to construct an overlap graph from a read collection
- The Shortest Superstring Problem as an abstraction of genome assembly
- Why the greedy overlap approach works under the unique-path assumption
- Why real assemblers (SPAdes, Velvet) use de Bruijn graphs for scalability

### Algorithms
- **Greedy algorithms:** repeatedly choose the locally optimal merge step
- **Hamiltonian path:** visit every node in a directed graph exactly once
- **Overlap graphs:** weighted directed graphs encoding read relationships
- **Time complexity:** the greedy superstring algorithm is O(n³) in the
  number of reads (n² overlap computations per merge, n merges)

### Error Correction
- Coverage-based quality assessment: trusted reads appear ≥ 2 times
- Hamming distance as a measure of single-substitution similarity
- Reverse complement and double-stranded DNA read matching
- How error correction improves downstream assembly quality

### Bioinformatics
- FASTA format parsing
- Reverse complement of DNA (antiparallel strand convention)
- Sequencing error models and their impact on assembly
- The relationship between read depth and assembly accuracy

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| Rosalind platform | https://rosalind.info |
| LONG problem | https://rosalind.info/problems/long/ |
| CORR problem | https://rosalind.info/problems/corr/ |
| Overlap-layout-consensus assembly | https://en.wikipedia.org/wiki/Sequence_assembly |
| de Bruijn graph assembly | https://en.wikipedia.org/wiki/De_Bruijn_graph |

---

## 📖 How This Fits Into Philomath AI

This module is **Session 8** of the Philomath live-coding series, covering
genome assembly problems from Rosalind.  It complements the other modules in
`philomath-ai`:

- **[Rosalind Genetics](../rosalind-genetics/)** — Mendelian inheritance,
  expected offspring, independent alleles, random strings, profile matrices
- **[Genome Algorithms](../genome_algorithms/)** — DNA pattern matching,
  clump finding, GC-skew analysis, motif finding
- **[Monte Carlo Simulation](../monte-carlo/)** — random number generation,
  dice simulation, Craps probability
