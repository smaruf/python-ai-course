"""
TREE: Completing a Tree
=======================

Rosalind Problem: https://rosalind.info/problems/tree/

Background
----------
A tree is a connected, acyclic undirected graph.  A fundamental property:
a tree on n nodes has exactly n − 1 edges.

Equivalently, given any connected graph with n nodes, it is a tree if and
only if it has n − 1 edges (acyclicity follows automatically for simple graphs).

A forest is an acyclic graph that may be disconnected — it is a disjoint
union of trees.  If a forest has n nodes and k connected components
(trees), then it has exactly n − k edges.  To turn it into a single tree
we must add exactly k − 1 edges (one to join each pair of components).

Problem Statement
-----------------
Given:  A positive integer n (≤ 1000) and a list of n − 1 or fewer
        undirected edges describing a forest on n nodes.
Return: The minimum number of edges needed to convert the forest into a
        single tree.

Sample Input:
  10
  1 2
  2 8
  4 10
  5 3
  5 7
  5 9
  6 7
  7 2

Sample Output:
  1

  (Two components: {1,2,3,5,6,7,8,9} and {4,10} → need 1 edge to connect them.)

Learning Objectives
-------------------
- Recognise that min_edges = (connected components) − 1
- Apply BFS/DFS connected-component counting to a real Rosalind problem
- Understand the relationship between trees, forests, and edges
"""

from collections import deque


def _build_graph(n: int, edges: list) -> dict:
    """Build an undirected adjacency list for nodes 1..n."""
    graph = {node: set() for node in range(1, n + 1)}
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)
    return graph


def _connected_components_count(graph: dict) -> int:
    """Count connected components using BFS."""
    seen = set()
    count = 0
    for node in graph:
        if node not in seen:
            count += 1
            queue = deque([node])
            seen.add(node)
            while queue:
                current = queue.popleft()
                for neighbour in graph[current]:
                    if neighbour not in seen:
                        seen.add(neighbour)
                        queue.append(neighbour)
    return count


def min_edges_to_tree(n: int, edges: list) -> int:
    """
    Return the minimum number of edges needed to make a forest a single tree.

    A forest with k connected components requires exactly k − 1 additional
    edges to become a spanning tree on all n nodes.

    Args:
        n:     Number of nodes (labelled 1..n).
        edges: List of (u, v) tuples representing the existing undirected edges.

    Returns:
        Minimum number of edges to add (int), equal to
        (number of connected components) − 1.

    Examples:
        >>> min_edges_to_tree(10, [(1,2),(2,8),(4,10),(5,3),(5,7),(5,9),(6,7),(7,2)])
        1

        >>> min_edges_to_tree(4, [])
        3

        >>> min_edges_to_tree(1, [])
        0
    """
    graph = _build_graph(n, edges)
    k = _connected_components_count(graph)
    return k - 1


def is_tree(n: int, edges: list) -> bool:
    """
    Return True if the graph on n nodes with the given edges is already a tree.

    A graph is a tree if and only if it is:
      1. Connected (one component), AND
      2. Has exactly n − 1 edges.
    Acyclicity follows from conditions 1 and 2 for a simple graph.

    Args:
        n:     Number of nodes.
        edges: List of (u, v) edge tuples.

    Returns:
        True if the graph is a tree, False otherwise.

    Examples:
        >>> is_tree(4, [(1,2),(2,3),(3,4)])
        True

        >>> is_tree(4, [(1,2),(2,3)])
        False

        >>> is_tree(4, [(1,2),(2,3),(3,4),(4,1)])
        False

        >>> is_tree(1, [])
        True
    """
    if len(edges) != n - 1:
        return False
    graph = _build_graph(n, edges)
    return _connected_components_count(graph) == 1


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("TREE: COMPLETING A TREE (Rosalind TREE)")
    print("=" * 70)

    # Rosalind sample dataset
    n = 10
    edges = [(1, 2), (2, 8), (4, 10), (5, 3), (5, 7), (5, 9), (6, 7), (7, 2)]
    result = min_edges_to_tree(n, edges)
    print(f"\nSample dataset: n={n}")
    print(f"Edges: {edges}")
    print(f"Min edges to complete tree: {result}  (expected: 1)")
    print(f"  Components: {{1,2,3,5,6,7,8,9}} and {{4,10}}")
    print(f"Is already a tree?          {is_tree(n, edges)}  (expected: False)")

    # Path graph (already a tree)
    n2 = 5
    edges2 = [(1, 2), (2, 3), (3, 4), (4, 5)]
    print(f"\nPath graph: n={n2}, edges={edges2}")
    print(f"Min edges needed:  {min_edges_to_tree(n2, edges2)}  (expected: 0)")
    print(f"Is already a tree? {is_tree(n2, edges2)}  (expected: True)")

    # Isolated nodes
    n3 = 5
    edges3 = []
    print(f"\nIsolated nodes: n={n3}, no edges")
    print(f"Min edges needed:  {min_edges_to_tree(n3, edges3)}  (expected: 4)")
    print(f"Is already a tree? {is_tree(n3, edges3)}  (expected: False)")

    # Single node
    print(f"\nSingle node: n=1, no edges")
    print(f"Min edges needed:  {min_edges_to_tree(1, [])}  (expected: 0)")
    print(f"Is already a tree? {is_tree(1, [])}  (expected: True)")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ A tree on n nodes has exactly n − 1 edges")
    print("✓ A forest with k components needs k − 1 edges to become a tree")
    print("✓ min_edges = connected_components − 1")
    print("✓ BFS/DFS lets us count components in O(V + E) time")
    print("✓ is_tree: check len(edges) == n-1 AND graph is connected")
