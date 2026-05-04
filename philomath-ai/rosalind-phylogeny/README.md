# Rosalind Phylogeny — Session 8

> **Part of [Philomath AI](../README.md)**

This module implements two foundational phylogenetics problems from the
[Rosalind](https://rosalind.info) bioinformatics learning platform, solved
in **Session 8** of the Philomath problem-solving series.  Phylogenetics is
the study of evolutionary relationships — these problems introduce the
mathematical building blocks needed to construct and reason about
evolutionary trees.

---

## 📚 Problems Covered

| # | Problem | Rosalind ID | Topic |
|---|---------|-------------|-------|
| 1 | [Creating a Distance Matrix](#1-pdst--creating-a-distance-matrix) | [PDST](https://rosalind.info/problems/pdst/) | p-distance, pairwise sequence comparison |
| 2 | [Counting Internal Nodes](#2-inod--counting-internal-nodes-of-a-tree) | [INOD](https://rosalind.info/problems/inod/) | Rooted binary trees, structural counting |

---

## 🧬 Problem Explanations

### 1. PDST — Creating a Distance Matrix

**Concept:** Before building a phylogenetic tree, we must quantify how
different each pair of sequences is.  The simplest metric for aligned DNA
strings is the **p-distance** (Hamming distance fraction):

```
p(s, t) = (number of positions where s ≠ t) / (length of s)
```

This yields a value in [0, 1]: 0 means the sequences are identical, 1 means
every position differs.

**Distance Matrix:** Given n sequences, we compute all n² pairwise
p-distances and arrange them in an n×n matrix.  The matrix is:
- **Symmetric** — D[i][j] = D[j][i]
- **Zero-diagonal** — D[i][i] = 0 for all i

**Sample (Rosalind PDST):**

```
>Rosalind_9499  TTTCCATTTA
>Rosalind_0942  GATTCATTTC
>Rosalind_6568  TTTCCATTTT
>Rosalind_1833  GTTCCATTTA
```

Expected output:
```
0.00000 0.40000 0.10000 0.10000
0.40000 0.00000 0.40000 0.30000
0.10000 0.40000 0.00000 0.20000
0.10000 0.30000 0.20000 0.00000
```

**Why p-distance?**  It is the starting point for more sophisticated
metrics (Jukes-Cantor, Kimura 2-parameter) that correct for multiple
substitutions at the same site.  The distance matrix feeds directly into
tree-building algorithms such as UPGMA and Neighbour-Joining.

---

### 2. INOD — Counting Internal Nodes of a Tree

**Concept:** In a **rooted binary tree** used for phylogenetics:
- **Leaf nodes** (external) = observed taxa (sequences)
- **Internal nodes** = hypothetical common ancestors
- Each internal node has exactly **two children** (binary branching)

**The key identity:**

| Quantity | Formula |
|----------|---------|
| Internal nodes | n − 1 |
| Total nodes | 2n − 1 |

This identity follows by induction: a single-leaf tree has 0 internal nodes,
and each new leaf added requires exactly one new internal node (the branching
point).

**Why does this matter?**  Tree-building algorithms like UPGMA perform
exactly n−1 merge operations, directly explaining their O(n²) time complexity.

**Sample:** n = 4 leaves → **3 internal nodes**

A simple 4-leaf tree looks like:
```
        root
       /    \
    anc1    anc2
    /  \    /  \
  L1   L2 L3   L4
```
Here root, anc1, anc2 are the 3 internal nodes; L1–L4 are the 4 leaves.

---

## 📁 Directory Structure

```
rosalind-phylogeny/
├── README.md                   # This file
├── 01_distance_matrix.py       # PDST: Creating a Distance Matrix
├── 02_internal_nodes.py        # INOD: Counting Internal Nodes of a Tree
└── test_all.py                 # Full test suite (both problems)
```

---

## 🚀 Quick Start

```bash
cd philomath-ai/rosalind-phylogeny

# Run individual problems (shows demo output with worked examples)
python 01_distance_matrix.py
python 02_internal_nodes.py

# Run the full test suite
python test_all.py
```

No additional dependencies are required — all modules use Python's standard
library only.

---

## 🎯 Learning Objectives

By working through this module you will understand:

### Sequence Distance
- The p-distance (Hamming fraction) as a simple sequence divergence measure
- Why distance matrices must be symmetric with a zero diagonal
- How to parse FASTA format and handle multi-line sequences
- The relationship between p-distance and more advanced substitution models

### Phylogenetic Trees
- The structure of rooted binary trees: leaves vs internal nodes
- The fundamental identity: n leaves → n−1 internal nodes → 2n−1 total
- How to implement and traverse binary trees in Python
- How tree structure relates to the complexity of phylogenetic algorithms

---

## 🔗 Resources

| Resource | Link |
|----------|------|
| Rosalind platform | https://rosalind.info |
| PDST problem | https://rosalind.info/problems/pdst/ |
| INOD problem | https://rosalind.info/problems/inod/ |
| Philomath AI | ../README.md |
| See also: Trees Part 2 | [../trees-part2/](../trees-part2/) for UPGMA phylogenetics |
