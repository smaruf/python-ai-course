"""
Graph Traversal: Breadth-First Search and Depth-First Search
=============================================================

Background
----------
Traversal algorithms systematically visit every reachable node in a graph.
Two fundamental strategies differ only in the data structure used to track
the frontier:

  BFS  (Breadth-First Search)  — uses a queue (FIFO)
       → visits nodes level by level; finds shortest paths in unweighted graphs.
  DFS  (Depth-First Search)    — uses a stack (LIFO) or recursion
       → visits as deep as possible before backtracking; detects cycles,
         topological ordering, and strongly connected components.

In bioinformatics, BFS/DFS underpin:
  • Finding connected components in protein interaction networks
  • Detecting cycles in metabolic pathways
  • Sequence assembly overlap graph traversal

Problem Statement
-----------------
Given:  An adjacency list representation of an undirected graph.
Return: BFS traversal order, DFS traversal order (iterative and recursive),
        list of connected components, and whether the graph is connected.

Learning Objectives
-------------------
- Implement BFS using collections.deque
- Implement iterative and recursive DFS
- Identify connected components via repeated traversal from unvisited nodes
- Recognise the relationship between connected components and trees
"""

from collections import deque


def bfs(graph: dict, start: int) -> list:
    """
    Perform a breadth-first traversal from start and return visited order.

    Neighbours are explored in sorted order for deterministic output.

    Args:
        graph: Adjacency list mapping node → set of neighbours.
        start: The node from which traversal begins.

    Returns:
        List of node integers in the order they were first visited.

    Examples:
        >>> g = {1:{2,3}, 2:{1,4}, 3:{1}, 4:{2}, 5:{6}, 6:{5}}
        >>> bfs(g, 1)
        [1, 2, 3, 4]

        >>> bfs(g, 5)
        [5, 6]
    """
    visited = []
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        visited.append(node)
        for neighbour in sorted(graph[node]):
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return visited


def dfs(graph: dict, start: int) -> list:
    """
    Perform an iterative depth-first traversal from start.

    Uses an explicit stack; neighbours are pushed in reverse-sorted order so
    that the smallest neighbour is processed first (matching recursive DFS).

    Args:
        graph: Adjacency list mapping node → set of neighbours.
        start: The node from which traversal begins.

    Returns:
        List of node integers in the order they were first visited.

    Examples:
        >>> g = {1:{2,3}, 2:{1,4}, 3:{1}, 4:{2}, 5:{6}, 6:{5}}
        >>> dfs(g, 1)
        [1, 2, 4, 3]

        >>> dfs(g, 5)
        [5, 6]
    """
    visited = []
    seen = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        visited.append(node)
        for neighbour in sorted(graph[node], reverse=True):
            if neighbour not in seen:
                stack.append(neighbour)
    return visited


def dfs_recursive(graph: dict, start: int, visited: set = None) -> list:
    """
    Perform a recursive depth-first traversal from start.

    Args:
        graph:   Adjacency list mapping node → set of neighbours.
        start:   The node from which traversal begins.
        visited: Set of already-visited nodes (used internally for recursion).
                 Pass None (default) for the initial call.

    Returns:
        List of node integers in the order they were first visited.

    Examples:
        >>> g = {1:{2,3}, 2:{1,4}, 3:{1}, 4:{2}, 5:{6}, 6:{5}}
        >>> dfs_recursive(g, 1)
        [1, 2, 4, 3]

        >>> dfs_recursive(g, 5)
        [5, 6]
    """
    if visited is None:
        visited = set()
    visited.add(start)
    result = [start]
    for neighbour in sorted(graph[start]):
        if neighbour not in visited:
            result.extend(dfs_recursive(graph, neighbour, visited))
    return result


def connected_components(graph: dict) -> list:
    """
    Find all connected components of an undirected graph.

    Each component is returned as a sorted list of node integers;
    the outer list is sorted by the smallest node in each component.

    Args:
        graph: Adjacency list mapping node → set of neighbours.

    Returns:
        List of lists, each inner list being one connected component (sorted).

    Examples:
        >>> g = {1:{2,3}, 2:{1,4}, 3:{1}, 4:{2}, 5:{6}, 6:{5}}
        >>> connected_components(g)
        [[1, 2, 3, 4], [5, 6]]

        >>> g2 = {1:set(), 2:set(), 3:set()}
        >>> connected_components(g2)
        [[1], [2], [3]]
    """
    seen = set()
    components = []
    for node in sorted(graph):
        if node not in seen:
            component = bfs(graph, node)
            seen.update(component)
            components.append(sorted(component))
    return components


def is_connected(graph: dict) -> bool:
    """
    Return True if the graph has exactly one connected component.

    Args:
        graph: Adjacency list mapping node → set of neighbours.

    Returns:
        True if all nodes are reachable from any single node.

    Examples:
        >>> g = {1:{2,3}, 2:{1,4}, 3:{1}, 4:{2}, 5:{6}, 6:{5}}
        >>> is_connected(g)
        False

        >>> g2 = {1:{2}, 2:{1,3}, 3:{2}}
        >>> is_connected(g2)
        True
    """
    if not graph:
        return True
    return len(connected_components(graph)) == 1


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("GRAPH TRAVERSAL: BFS AND DFS")
    print("=" * 70)

    # 5-node undirected graph
    #   1 - 2 - 3
    #   |       |
    #   4 - - - 5
    graph = {1: {2, 4}, 2: {1, 3}, 3: {2, 5}, 4: {1, 5}, 5: {3, 4}}
    print("\nGraph: 5-node cycle-like graph")
    print("Adjacency list:")
    for node in sorted(graph):
        print(f"  {node} → {sorted(graph[node])}")

    bfs_order = bfs(graph, 1)
    print(f"\nBFS from node 1:          {bfs_order}")

    dfs_order = dfs(graph, 1)
    print(f"DFS (iterative) from 1:   {dfs_order}")

    dfs_rec_order = dfs_recursive(graph, 1)
    print(f"DFS (recursive) from 1:   {dfs_rec_order}")

    print(f"\nConnected components: {connected_components(graph)}")
    print(f"Is connected:         {is_connected(graph)}")

    # Disconnected graph
    graph2 = {1: {2, 3}, 2: {1, 4}, 3: {1}, 4: {2}, 5: {6}, 6: {5}}
    print(f"\nDisconnected graph (two components):")
    for node in sorted(graph2):
        print(f"  {node} → {sorted(graph2[node])}")
    print(f"Connected components: {connected_components(graph2)}")
    print(f"Is connected:         {is_connected(graph2)}")

    # Isolated nodes
    graph3 = {1: set(), 2: set(), 3: set()}
    print(f"\nThree isolated nodes:")
    print(f"Connected components: {connected_components(graph3)}")
    print(f"Is connected:         {is_connected(graph3)}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ BFS uses a queue (deque) → level-order exploration")
    print("✓ DFS uses a stack (explicit or call stack) → deep-first exploration")
    print("✓ Iterative and recursive DFS produce the same visit order")
    print("✓ Connected components: run BFS/DFS from every unvisited node")
    print("✓ Sorted neighbour expansion ensures deterministic output")
