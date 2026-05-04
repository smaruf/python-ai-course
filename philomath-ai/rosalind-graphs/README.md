# Rosalind Graph Theory — Sessions 6–7

> **Part of [Philomath AI](../README.md)**

Graph theory is a cornerstone of computational biology.  Protein interaction
networks, metabolic pathways, genome assembly overlap graphs, and phylogenetic
trees are all naturally modelled as graphs.  This module builds the algorithmic
foundation — adjacency lists, BFS/DFS, connected components — and applies it
directly to the Rosalind **TREE** problem.

---

## Problems

| # | File | Topic | Rosalind |
|---|------|--------|---------|
| 01 | `01_adjacency_list.py` | Adjacency list representation | [DEG](https://rosalind.info/problems/deg/) |
| 02 | `02_bfs_dfs.py` | BFS, DFS, connected components | — |
| 03 | `03_tree_completion.py` | Completing a tree (TREE) | [TREE](https://rosalind.info/problems/tree/) |

---

## Problem Explanations

### 01 — Adjacency List Representation

A graph on *n* nodes is stored as a Python `dict` mapping each node (integer
1..n) to a `set` of its neighbours.  Both directed and undirected graphs are
supported.  Key operations:

- **`build_adjacency_list(n, edges, directed=False)`** — constructs the graph
- **`degree(graph, node)`** — returns the number of neighbours
- **`edge_count(graph, directed=False)`** — total edges (for undirected graphs,
  each edge is counted once even though it is stored at both endpoints)

This representation uses O(V + E) space and gives O(1) average-case neighbour
membership tests — ideal for the sparse graphs common in bioinformatics.

---

### 02 — BFS and DFS Traversal

Two fundamental graph traversal strategies:

| Strategy | Data structure | Key property |
|----------|---------------|--------------|
| BFS | Queue (FIFO) | Level-order; finds shortest paths in unweighted graphs |
| DFS | Stack / recursion | Deep-first; detects cycles, topological order |

Both implementations use **sorted neighbours** to produce deterministic output.
`connected_components` runs BFS from every unvisited node to partition the
graph, and `is_connected` checks that exactly one component exists.

---

### 03 — Completing a Tree (Rosalind TREE)

**Core insight:** a forest with *k* connected components on *n* nodes needs
exactly **k − 1** additional edges to become a spanning tree.

**Sample dataset:**

```
n = 10
edges = [(1,2),(2,8),(4,10),(5,3),(5,7),(5,9),(6,7),(7,2)]
```

This forest has **2 components**: `{1,2,3,5,6,7,8,9}` and `{4,10}`.
Answer: **1** (one edge to join the two components).

`is_tree` provides a quick validity check: a graph is a tree iff it has
exactly n − 1 edges **and** is connected.

---

## Directory Structure

```
rosalind-graphs/
├── 01_adjacency_list.py    # Graph representation (build, degree, edge_count)
├── 02_bfs_dfs.py           # BFS, DFS, connected components, is_connected
├── 03_tree_completion.py   # Rosalind TREE: min edges to complete a forest
├── test_all.py             # Full test suite (standard library only)
└── README.md               # This file
```

---

## Quick Start

```bash
# Run any file standalone to see a worked demo
python 01_adjacency_list.py
python 02_bfs_dfs.py
python 03_tree_completion.py

# Run the full test suite
python test_all.py
```

Expected output of `test_all.py`:

```
🎉 All tests passed!
```

---

## Learning Objectives

After working through this module you should be able to:

- **Graphs** — represent a graph as an adjacency list; distinguish directed vs
  undirected, sparse vs dense representations
- **BFS** — implement breadth-first search using `collections.deque`; explain
  why BFS finds shortest paths in unweighted graphs
- **DFS** — implement iterative (stack-based) and recursive DFS; explain the
  role of the visited set
- **Connected components** — partition a graph into components by repeated
  traversal from unvisited nodes
- **Trees** — state the equivalence *tree ⟺ connected + n − 1 edges*; compute
  the minimum edges needed to complete a forest into a tree

---

## Resources

- **Rosalind TREE problem** — https://rosalind.info/problems/tree/
- **Graph theory overview (degree array)** — https://rosalind.info/problems/deg/
