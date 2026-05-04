#!/usr/bin/env python3
"""
Test suite for the rosalind-graphs module.
Run this file to verify all three graph theory files are working correctly.

Problems covered:
  01  Adjacency List Representation
  02  BFS and DFS Traversal
  03  TREE – Completing a Tree (Rosalind TREE)
"""

import sys
import os
import importlib.util


def load_module(filename: str):
    """Load a Python module from a file path relative to this directory."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Adjacency List
# ─────────────────────────────────────────────────────────────────────────────

def test_adjacency_list():
    print("\n" + "=" * 70)
    print("TEST 1: Adjacency List Representation")
    print("=" * 70)

    mod = load_module('01_adjacency_list.py')

    # Undirected graph: 4 nodes, path 1-2-3-4
    g = mod.build_adjacency_list(4, [(1, 2), (2, 3), (3, 4)])
    assert sorted(g[2]) == [1, 3], f"Expected [1,3], got {sorted(g[2])}"
    assert sorted(g[1]) == [2]
    assert sorted(g[4]) == [3]
    print("✓ Undirected adjacency list built correctly")

    # Isolated nodes are present
    g2 = mod.build_adjacency_list(5, [(1, 2)])
    assert 3 in g2 and g2[3] == set()
    assert 4 in g2 and g2[4] == set()
    assert 5 in g2 and g2[5] == set()
    print("✓ Isolated nodes included for all 1..n")

    # Directed graph: edge 1→2 should not add 2→1
    gd = mod.build_adjacency_list(3, [(1, 2), (2, 3)], directed=True)
    assert sorted(gd[1]) == [2]
    assert sorted(gd[2]) == [3]
    assert gd[3] == set(), f"Node 3 should have no outgoing edges, got {gd[3]}"
    print("✓ Directed graph: edges added in one direction only")

    # Degree
    g3 = mod.build_adjacency_list(4, [(1, 2), (1, 3), (1, 4)])
    assert mod.degree(g3, 1) == 3
    assert mod.degree(g3, 2) == 1
    assert mod.degree(g3, 4) == 1
    print("✓ degree() returns correct values")

    # Edge count – undirected
    g4 = mod.build_adjacency_list(5, [(1, 2), (2, 3), (3, 5), (4, 5), (1, 4)])
    assert mod.edge_count(g4) == 5, f"Expected 5 edges, got {mod.edge_count(g4)}"
    print("✓ edge_count() correct for undirected graph")

    # Edge count – directed
    gd2 = mod.build_adjacency_list(4, [(1, 2), (2, 3), (3, 4)], directed=True)
    assert mod.edge_count(gd2, directed=True) == 3
    print("✓ edge_count() correct for directed graph")

    # Empty graph
    g_empty = mod.build_adjacency_list(3, [])
    assert mod.edge_count(g_empty) == 0
    print("✓ Empty graph has 0 edges")

    print("✓ All Adjacency List tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: BFS and DFS
# ─────────────────────────────────────────────────────────────────────────────

def test_bfs_dfs():
    print("\n" + "=" * 70)
    print("TEST 2: BFS and DFS Traversal")
    print("=" * 70)

    mod = load_module('02_bfs_dfs.py')

    # Graph from module doctests: two components
    g = {1: {2, 3}, 2: {1, 4}, 3: {1}, 4: {2}, 5: {6}, 6: {5}}

    # BFS
    assert mod.bfs(g, 1) == [1, 2, 3, 4], f"BFS got {mod.bfs(g, 1)}"
    assert mod.bfs(g, 5) == [5, 6]
    print("✓ BFS traversal order correct")

    # DFS iterative
    assert mod.dfs(g, 1) == [1, 2, 4, 3], f"DFS got {mod.dfs(g, 1)}"
    assert mod.dfs(g, 5) == [5, 6]
    print("✓ DFS (iterative) traversal order correct")

    # DFS recursive
    assert mod.dfs_recursive(g, 1) == [1, 2, 4, 3], \
        f"DFS recursive got {mod.dfs_recursive(g, 1)}"
    assert mod.dfs_recursive(g, 5) == [5, 6]
    print("✓ DFS (recursive) traversal order correct")

    # Iterative and recursive DFS agree
    g2 = {1: {2, 4}, 2: {1, 3}, 3: {2, 5}, 4: {1, 5}, 5: {3, 4}}
    assert mod.dfs(g2, 1) == mod.dfs_recursive(g2, 1), \
        "Iterative and recursive DFS should agree"
    print("✓ Iterative and recursive DFS produce identical order")

    # Connected components
    comps = mod.connected_components(g)
    assert comps == [[1, 2, 3, 4], [5, 6]], f"Components: {comps}"
    print(f"✓ connected_components: {comps}")

    # is_connected – False
    assert not mod.is_connected(g)
    print("✓ is_connected returns False for disconnected graph")

    # is_connected – True
    g3 = {1: {2}, 2: {1, 3}, 3: {2}}
    assert mod.is_connected(g3)
    print("✓ is_connected returns True for connected graph")

    # Single-node graph is connected
    g4 = {1: set()}
    assert mod.is_connected(g4)
    print("✓ Single-node graph is connected")

    # Three isolated nodes
    g5 = {1: set(), 2: set(), 3: set()}
    assert mod.connected_components(g5) == [[1], [2], [3]]
    assert not mod.is_connected(g5)
    print("✓ Three isolated nodes: 3 components, not connected")

    # BFS visits only reachable nodes from start
    visited_from_1 = mod.bfs(g, 1)
    assert 5 not in visited_from_1 and 6 not in visited_from_1
    print("✓ BFS stays within the reachable component")

    print("✓ All BFS/DFS tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Tree Completion
# ─────────────────────────────────────────────────────────────────────────────

def test_tree_completion():
    print("\n" + "=" * 70)
    print("TEST 3: TREE – Completing a Tree")
    print("=" * 70)

    mod = load_module('03_tree_completion.py')

    # Rosalind sample dataset: n=10, 8 edges → 2 components → answer 1
    rosalind_edges = [
        (1, 2), (2, 8), (4, 10), (5, 3), (5, 7),
        (5, 9), (6, 7), (7, 2),
    ]
    result = mod.min_edges_to_tree(10, rosalind_edges)
    assert result == 1, f"Expected 1, got {result}"
    print(f"✓ Rosalind sample (n=10): min_edges = {result}")

    # All isolated nodes: k components = n, need n-1 edges
    assert mod.min_edges_to_tree(4, []) == 3
    assert mod.min_edges_to_tree(1, []) == 0
    print("✓ Isolated nodes: min_edges = n − 1")

    # Already a tree (path graph): 0 edges needed
    path_edges = [(1, 2), (2, 3), (3, 4), (4, 5)]
    assert mod.min_edges_to_tree(5, path_edges) == 0
    print("✓ Path graph already a tree: min_edges = 0")

    # Two disjoint edges: 3 components (nodes 1,2 / nodes 3,4 / node 5) → need 2
    two_edge_forest = [(1, 2), (3, 4)]
    assert mod.min_edges_to_tree(5, two_edge_forest) == 2
    print("✓ Two disjoint edges + isolated node: min_edges = 2")

    # is_tree – True
    assert mod.is_tree(4, [(1, 2), (2, 3), (3, 4)])
    assert mod.is_tree(1, [])
    print("✓ is_tree returns True for valid trees")

    # is_tree – False: wrong number of edges
    assert not mod.is_tree(4, [(1, 2), (2, 3)])          # too few edges
    assert not mod.is_tree(4, [(1, 2), (2, 3), (3, 4), (4, 1)])  # too many
    print("✓ is_tree returns False when edge count ≠ n − 1")

    # is_tree – False: correct edge count but disconnected (forest)
    assert not mod.is_tree(4, [(1, 2), (3, 4), (2, 1)])  # 3 edges but duplicate + disconnected
    # Use a cleaner forest: n=4, edges=[(1,2),(3,4)] → only 2 edges, caught by first check ✓
    # n=6, star on 1-2-3-4 plus isolated nodes 5,6: 3 edges not 5
    assert not mod.is_tree(5, [(1, 2), (2, 3), (4, 5)])  # disconnected, 3 edges ≠ 4
    print("✓ is_tree returns False for disconnected graph with n-1 edges impossible case")

    # is_tree – False: cycle (same node count, same edge count but cyclic)
    # n=3, edges forming a cycle: 3 edges ≠ 2, caught by edge-count check
    assert not mod.is_tree(3, [(1, 2), (2, 3), (3, 1)])
    print("✓ is_tree returns False for cycle (edge count check catches it)")

    print("✓ All Tree Completion tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("ROSALIND GRAPHS – TEST SUITE (Sessions 6–7)")
    print("=" * 70)
    print("Testing Adjacency List | BFS/DFS | TREE\n")

    tests = [test_adjacency_list, test_bfs_dfs, test_tree_completion]
    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as exc:
            import traceback
            print(f"✗ Test failed: {exc}")
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed} / {len(tests)}")
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
