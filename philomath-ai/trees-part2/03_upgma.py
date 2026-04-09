"""
UPGMA: Unweighted Pair Group Method with Arithmetic Mean
=========================================================

Chapter 5 of "Programming for Lovers in Python" — Trees Part 2
by Phillip Compeau (Carnegie Mellon University).

Background
----------
UPGMA is a classic **hierarchical clustering** algorithm used in phylogenetics
to reconstruct evolutionary trees from pairwise distance matrices.

A **distance matrix** D[i][j] gives the observed divergence between taxon i
and taxon j (e.g., fraction of nucleotide positions that differ).

UPGMA Algorithm
---------------
Given n taxa with distances D:

1. Start with n clusters, one per taxon.
2. Find the pair (i, j) with the smallest distance D[i][j].
3. Create a new internal node u joining i and j:
   - Height of u = D[i][j] / 2
   - Branch length to child i = height(u) − height(i)
   - Branch length to child j = height(u) − height(j)
4. Update the distance matrix: replace rows/columns i and j with u.
   New distance to any remaining cluster k:
       D[u][k] = (D[i][k] * size(i) + D[j][k] * size(j)) / (size(i) + size(j))
5. Repeat until only one cluster (the root) remains.

Assumptions & Limitations
--------------------------
UPGMA assumes a **molecular clock** — all lineages evolve at the same rate.
When this assumption is violated, UPGMA can give incorrect topologies.
(Neighbor Joining is a distance method that does not require a molecular clock.)

Learning Objectives
-------------------
- Implement UPGMA from scratch
- Understand how to update a distance matrix during clustering
- Appreciate the connection between hierarchical clustering and phylogenetics
- Recognise the molecular clock assumption and its limitations
"""

from __future__ import annotations
import copy
import sys
import os
from typing import Optional


def _load_tree_node():
    """Load TreeNode from 02_tree_node.py using importlib."""
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "02_tree_node.py")
    spec = importlib.util.spec_from_file_location("tree_node", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TreeNode


# ─────────────────────────────────────────────────────────────────────────────
# Core UPGMA helpers
# ─────────────────────────────────────────────────────────────────────────────

def find_min_distance(dist: list[list[float]], n: int) -> tuple[int, int]:
    """
    Find the indices (i, j) of the minimum off-diagonal entry in dist.

    Only the upper triangle (j > i) is examined since the matrix is symmetric.

    Args:
        dist: n×n symmetric distance matrix (0 on diagonal)
        n:    Current number of active clusters

    Returns:
        (i, j) with i < j such that dist[i][j] is minimal

    Examples:
        >>> find_min_distance([[0,5,9],[5,0,3],[9,3,0]], 3)
        (1, 2)
    """
    min_val = float("inf")
    min_i, min_j = 0, 1
    for i in range(n):
        for j in range(i + 1, n):
            if dist[i][j] < min_val:
                min_val = dist[i][j]
                min_i, min_j = i, j
    return min_i, min_j


def update_distances(
    dist: list[list[float]],
    sizes: list[int],
    i: int,
    j: int,
    n: int,
) -> tuple[list[list[float]], list[int]]:
    """
    Merge clusters i and j into cluster i using UPGMA distance updating.

    The new distance from the merged cluster (i+j) to any other cluster k is
    the weighted average:
        D[new][k] = (D[i][k]*size(i) + D[j][k]*size(j)) / (size(i)+size(j))

    After merging, row/column j is removed from the matrix.

    Args:
        dist:  Current n×n distance matrix
        sizes: List of cluster sizes (number of original taxa in each cluster)
        i:     Index of first cluster to merge (will become the merged cluster)
        j:     Index of second cluster to merge (will be removed)
        n:     Current number of clusters

    Returns:
        (new_dist, new_sizes): Updated (n-1)×(n-1) matrix and sizes list
    """
    new_size = sizes[i] + sizes[j]

    # Update row/column i with weighted-average distances
    for k in range(n):
        if k == i or k == j:
            continue
        new_d = (dist[i][k] * sizes[i] + dist[j][k] * sizes[j]) / new_size
        dist[i][k] = new_d
        dist[k][i] = new_d

    dist[i][i] = 0.0

    # Remove row and column j
    new_dist = []
    for r in range(n):
        if r == j:
            continue
        new_row = [dist[r][c] for c in range(n) if c != j]
        new_dist.append(new_row)

    new_sizes = [sizes[k] for k in range(n) if k != j]
    new_sizes[i if i < j else i - 1] = new_size

    return new_dist, new_sizes


def upgma(
    distance_matrix: list[list[float]],
    labels: list[str],
) -> "TreeNode":
    """
    Run UPGMA on a distance matrix and return the root of the resulting tree.

    Args:
        distance_matrix: Symmetric n×n matrix of pairwise distances.
                         Diagonal should be 0.  Values are not modified
                         (a deep copy is made internally).
        labels:          List of n taxon names, one per row/column.

    Returns:
        Root TreeNode of the fully resolved binary phylogenetic tree.
        Each leaf node's name matches the corresponding label.
        Branch lengths (node.distance) reflect the UPGMA branch-length
        calculation.

    Raises:
        ValueError: if distance_matrix and labels have inconsistent sizes.

    Examples:
        >>> dm = [[0,1,5,5],[1,0,5,5],[5,5,0,2],[5,5,2,0]]
        >>> labels = ['A','B','C','D']
        >>> root = upgma(dm, labels)
        >>> root.count_leaves()
        4
    """
    n = len(labels)
    if len(distance_matrix) != n:
        raise ValueError(
            f"distance_matrix has {len(distance_matrix)} rows but "
            f"labels has {n} entries"
        )

    TreeNodeClass = _load_tree_node()

    # Working copies
    dist  = copy.deepcopy(distance_matrix)
    names = list(labels)
    sizes = [1] * n
    # nodes[i] is the current tree node for cluster i
    nodes = [TreeNodeClass(name=name) for name in names]
    # heights[i] is the cumulative height (from the original leaves) of cluster i
    heights = [0.0] * n

    while len(nodes) > 1:
        cur_n = len(nodes)
        i, j  = find_min_distance(dist, cur_n)

        # New internal node height
        new_height = dist[i][j] / 2.0

        # Branch lengths for each child = new_height - child's current height
        bl_i = new_height - heights[i]
        bl_j = new_height - heights[j]

        # Assign branch lengths to child nodes
        nodes[i].distance = max(bl_i, 0.0)
        nodes[j].distance = max(bl_j, 0.0)

        # Create new internal node merging i and j
        new_name = f"({names[i]},{names[j]})"
        new_node = TreeNodeClass(
            name=new_name,
            left=nodes[i],
            right=nodes[j],
            distance=0.0,
        )

        # Update distance matrix and bookkeeping
        dist, sizes = update_distances(dist, sizes, i, j, cur_n)

        # Remove j's bookkeeping (j > i guaranteed by find_min_distance)
        nodes.pop(j)
        nodes[i] = new_node
        names.pop(j)
        names[i] = new_name
        heights.pop(j)
        heights[i] = new_height

    return nodes[0]


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("UPGMA: UNWEIGHTED PAIR GROUP METHOD WITH ARITHMETIC MEAN")
    print("=" * 70)

    # Small toy example — textbook distances
    print("\n── Toy example (4 taxa) ──")
    dm = [
        [0,   1,   5,   5],
        [1,   0,   5,   5],
        [5,   5,   0,   2],
        [5,   5,   2,   0],
    ]
    labels = ["A", "B", "C", "D"]
    root = upgma(dm, labels)
    print(root)
    print(f"\nLeaves: {root.count_leaves()}")

    # Great apes example
    print("\n── Great Apes ──")
    apes_dm = [
        #      human  chimp  bonobo gorilla orang
        [0.000, 0.012, 0.013, 0.030, 0.080],  # human
        [0.012, 0.000, 0.009, 0.031, 0.079],  # chimp
        [0.013, 0.009, 0.000, 0.032, 0.081],  # bonobo
        [0.030, 0.031, 0.032, 0.000, 0.078],  # gorilla
        [0.080, 0.079, 0.081, 0.078, 0.000],  # orangutan
    ]
    apes_labels = ["human", "chimp", "bonobo", "gorilla", "orangutan"]
    apes_root = upgma(apes_dm, apes_labels)
    print(apes_root)
    print(f"\nLeaves: {apes_root.count_leaves()}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ UPGMA iteratively merges the closest pair of clusters")
    print("✓ New node height = min_distance / 2")
    print("✓ Branch length = new_height − child_height")
    print("✓ Distance update uses weighted average (UPGMA = 'arithmetic mean')")
    print("✓ Assumes molecular clock — equal rates across all lineages")
