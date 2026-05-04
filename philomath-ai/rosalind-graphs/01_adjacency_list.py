"""
Graph Fundamentals: Adjacency List Representation
==================================================

Background
----------
A graph G = (V, E) consists of a set of vertices (nodes) V and a set of
edges E connecting pairs of vertices.  In bioinformatics, graphs model
many structures: metabolic networks, protein-interaction networks,
phylogenetic trees, and sequence overlap graphs.

Two common representations:
  • Adjacency matrix  — O(V²) space, O(1) edge lookup
  • Adjacency list    — O(V + E) space, efficient for sparse graphs

An adjacency list stores, for every node u, a collection of its
neighbours.  In Python a dict mapping node → set of neighbours is both
memory-efficient and O(1) average-case for membership tests.

Problem Statement
-----------------
Given:  An integer n (number of nodes, labelled 1..n) and a list of
        (u, v) edge pairs.
Build:  An adjacency list representation of the graph.
Return: The degree of each node and the total edge count.

Learning Objectives
-------------------
- Understand adjacency list vs adjacency matrix trade-offs
- Build directed and undirected graphs from an edge list
- Compute node degrees and total edge counts
"""


def build_adjacency_list(
    n: int, edges: list, directed: bool = False
) -> dict:
    """
    Build an adjacency list for a graph with nodes labelled 1..n.

    Args:
        n:        Number of nodes.  Nodes are integers 1 through n.
        edges:    List of (u, v) tuples representing edges.
        directed: If False (default) each edge is added in both directions.

    Returns:
        dict mapping each node (int) to a set of its neighbours (set[int]).

    Examples:
        >>> g = build_adjacency_list(4, [(1,2),(2,3),(3,4)])
        >>> sorted(g[2])
        [1, 3]

        >>> g2 = build_adjacency_list(3, [(1,2),(2,3)], directed=True)
        >>> sorted(g2[2])
        [3]

        >>> g3 = build_adjacency_list(3, [])
        >>> g3[1]
        set()
    """
    graph = {node: set() for node in range(1, n + 1)}
    for u, v in edges:
        graph[u].add(v)
        if not directed:
            graph[v].add(u)
    return graph


def degree(graph: dict, node: int) -> int:
    """
    Return the degree of a node (number of neighbours).

    Args:
        graph: Adjacency list as returned by build_adjacency_list.
        node:  The node whose degree to compute.

    Returns:
        Number of neighbours of node (int).

    Examples:
        >>> g = build_adjacency_list(4, [(1,2),(1,3),(1,4)])
        >>> degree(g, 1)
        3

        >>> degree(g, 4)
        1
    """
    return len(graph[node])


def edge_count(graph: dict, directed: bool = False) -> int:
    """
    Return the total number of edges in the graph.

    For an undirected graph each edge is stored at both endpoints,
    so the sum of all degrees is divided by 2.

    Args:
        graph:    Adjacency list.
        directed: True if the graph is directed (default False).

    Returns:
        Number of edges (int).

    Examples:
        >>> g = build_adjacency_list(4, [(1,2),(2,3),(3,4)])
        >>> edge_count(g)
        3

        >>> g2 = build_adjacency_list(4, [(1,2),(2,3),(3,4)], directed=True)
        >>> edge_count(g2, directed=True)
        3
    """
    total = sum(len(neighbours) for neighbours in graph.values())
    return total if directed else total // 2


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("GRAPH FUNDAMENTALS: ADJACENCY LIST REPRESENTATION")
    print("=" * 70)

    # 5-node undirected graph
    #   1 - 2 - 3
    #   |       |
    #   4 - - - 5
    n = 5
    edges = [(1, 2), (2, 3), (3, 5), (4, 5), (1, 4)]
    g = build_adjacency_list(n, edges)

    print(f"\nUndirected graph: n={n}, edges={edges}")
    print("\nAdjacency list:")
    for node in sorted(g):
        print(f"  {node} → {sorted(g[node])}")

    print("\nDegrees:")
    for node in sorted(g):
        print(f"  deg({node}) = {degree(g, node)}")

    print(f"\nTotal edges: {edge_count(g)}  (expect {len(edges)})")

    # Directed version
    gd = build_adjacency_list(n, edges, directed=True)
    print(f"\nDirected adjacency list:")
    for node in sorted(gd):
        print(f"  {node} → {sorted(gd[node])}")
    print(f"Directed edge count: {edge_count(gd, directed=True)}  (expect {len(edges)})")

    # Empty graph
    g_empty = build_adjacency_list(3, [])
    print(f"\nEmpty graph (n=3, no edges): {edge_count(g_empty)} edges  (expect 0)")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Adjacency list uses O(V + E) space — efficient for sparse graphs")
    print("✓ Undirected: each edge stored at both endpoints → sum(degrees) = 2|E|")
    print("✓ dict[int → set[int]] gives O(1) average neighbour lookup")
    print("✓ Node labels 1..n match Rosalind's convention")
