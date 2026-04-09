# Trees Part 2 — Programming for Lovers in Python

> **Part of [Philomath AI](../README.md)** — a comprehensive learning project from
> Phillip Compeau's "Programming for Lovers in Python" course.  
> See also: [Rosalind Genetics](../rosalind-genetics/) | [Genome Algorithms](../genome_algorithms/)

This module implements **Chapter 5: Trees Part 2** of *Programming for Lovers
in Python*.  It covers recursion fundamentals, the UPGMA phylogenetic algorithm,
Newick tree format, and running end-to-end analyses on five real biological
datasets.

---

## 📚 Table of Contents

1. [Learning Objectives](#learning-objectives)
2. [Module Files](#module-files)
3. [Datasets](#datasets)
4. [How to Run](#how-to-run)
5. [Background: UPGMA and Phylogenetics](#background-upgma-and-phylogenetics)
6. [Where UPGMA Gets It Wrong](#where-upgma-gets-it-wrong)

---

## 🎯 Learning Objectives

By working through this module you will:

- **Recursion**: Understand base cases, recursive cases, and the call stack
- **Fibonacci blow-up**: See why naive recursion is O(2^n) and fix it with memoization
- **Tree data structures**: Build a `TreeNode` class with recursive `count_leaves()`
- **UPGMA algorithm**: Implement hierarchical clustering for phylogenetics
- **Newick format**: Serialize and parse the standard phylogenetic tree text format
- **Real biological data**: Run UPGMA on great apes, hemoglobin, HIV, SARS-CoV-2, mtDNA
- **Algorithm critique**: Understand when UPGMA fails (molecular clock violations)

---

## 📁 Module Files

| File | Topic | Key Functions |
|------|-------|---------------|
| `01_recursion.py` | Recursion intro, factorial, Fibonacci | `factorial`, `fibonacci_naive`, `fibonacci_memo`, `fibonacci_iterative` |
| `02_tree_node.py` | TreeNode data structure | `TreeNode`, `is_leaf`, `count_leaves`, `build_sample_tree` |
| `03_upgma.py` | UPGMA algorithm | `upgma`, `find_min_distance`, `update_distances` |
| `04_newick.py` | Newick format serialization | `to_newick`, `parse_newick` |
| `05_pipeline.py` | End-to-end pipeline + datasets | `run_pipeline`, `load_csv`, `ALL_DATASETS` |
| `06_cli.py` | Command-line interface | `python 06_cli.py upgma --dataset great_apes` |
| `07_gui.py` | Tkinter GUI | `python 07_gui.py` |
| `test_all.py` | Full test suite | `python test_all.py` |
| `data/` | CSV distance matrices | 5 biological datasets |

---

## 🧬 Datasets

| Dataset | Taxa | Description |
|---------|------|-------------|
| `great_apes` | 5 | Human, chimp, bonobo, gorilla, orangutan cytochrome b |
| `hemoglobin` | 6 | Haemoglobin alpha chain across the animal kingdom |
| `hiv_subtypes` | 6 | HIV-1 group M subtypes A1, B, C, D, AE, G |
| `sars_cov2` | 5 | SARS-CoV-2 variants: Original, Alpha, Delta, Omicron BA.1/BA.2 |
| `mtdna_haplogroups` | 7 | Human mtDNA haplogroups tracing out-of-Africa migration |

See [`data/README.md`](data/README.md) for full dataset documentation.

---

## 🚀 How to Run

### Run the test suite
```bash
cd philomath-ai/trees-part2
python test_all.py
```

### CLI — individual demos
```bash
# Recursion demo (factorial, Fibonacci, timing comparison)
python 06_cli.py recursion

# Build and display a sample tree
python 06_cli.py tree

# Run UPGMA on a built-in dataset
python 06_cli.py upgma --dataset great_apes
python 06_cli.py upgma --dataset hemoglobin
python 06_cli.py upgma --dataset hiv_subtypes
python 06_cli.py upgma --dataset sars_cov2
python 06_cli.py upgma --dataset mtdna_haplogroups

# Output Newick format
python 06_cli.py newick --dataset great_apes

# Run UPGMA from your own CSV file
python 06_cli.py upgma --file data/great_apes.csv

# Run everything
python 06_cli.py all
```

### GUI
```bash
python 07_gui.py
```

The GUI has two tabs:
- **UPGMA Phylogenetics**: Select a dataset, click "Run UPGMA", view the
  distance matrix, ASCII tree, and Newick string.  Load your own CSV with
  "Load CSV…".
- **Recursion Demo**: Enter n, compute factorial or Fibonacci with timing.
  "Compare all" shows a full timing table.

### Run individual modules directly
```bash
python 01_recursion.py      # Fibonacci timing demo
python 02_tree_node.py      # Sample tree construction
python 03_upgma.py          # UPGMA on toy + great apes data
python 04_newick.py         # Newick round-trip demo
python 05_pipeline.py       # All 5 datasets end-to-end
```

---

## 🌳 Background: UPGMA and Phylogenetics

A **phylogenetic tree** represents evolutionary relationships among a set of
species or sequences.  Leaves are modern taxa; internal nodes are common
ancestors; branch lengths reflect evolutionary distance.

**UPGMA** (Unweighted Pair Group Method with Arithmetic Mean) is one of the
oldest and simplest tree-building algorithms:

```
Algorithm UPGMA(D, labels):
    Start with n clusters (one per taxon)
    while more than 1 cluster:
        Find (i, j) = argmin D[i][j]
        Create new node u with:
            height(u) = D[i][j] / 2
            branch_length(i → u) = height(u) − height(i)
            branch_length(j → u) = height(u) − height(j)
        Update D: D[u][k] = (D[i][k]*|i| + D[j][k]*|j|) / (|i|+|j|)
        Replace clusters i and j with u
    return the single remaining node (root)
```

The key idea: the "arithmetic mean" in the name refers to the weighted-average
distance update in step 4, which weights each original taxon equally.

### Newick Format

```
((human:0.006,chimp:0.006):0.009,gorilla:0.015);
```

- Parentheses wrap the children of each internal node
- A colon followed by a number gives the branch length
- A semicolon terminates the entire string
- Internal node labels are optional (placed after the closing parenthesis)

---

## ⚠️ Where UPGMA Gets It Wrong

UPGMA assumes a **molecular clock** — that all lineages evolve at the same
rate.  When this is violated:

- Taxa that evolved faster will appear to be more divergent, getting placed
  farther from the root than they should be.
- The resulting tree topology may be incorrect even if the distance matrix
  is accurate.

**Examples in this module:**
- **HIV subtypes**: extensive recombination between subtypes violates the
  tree model entirely; UPGMA cannot recover the true evolutionary history.
- **Mitochondrial haplogroups**: rate variation between African and
  non-African lineages can cause subtle distortions.

**Next step**: Neighbor Joining (NJ) is a distance method that does *not*
assume a molecular clock and generally outperforms UPGMA on real data.
