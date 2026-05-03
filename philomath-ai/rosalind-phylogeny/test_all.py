#!/usr/bin/env python3
"""
Test suite for the rosalind-phylogeny module.
Run this file to verify all problems are working correctly.

Problems covered:
  01  PDST – Creating a Distance Matrix
  02  INOD – Counting Internal Nodes of a Tree
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
# TEST 1: PDST – Creating a Distance Matrix
# ─────────────────────────────────────────────────────────────────────────────

def test_pdst():
    print("\n" + "=" * 70)
    print("TEST 1: PDST – Creating a Distance Matrix")
    print("=" * 70)

    mod = load_module('01_distance_matrix.py')

    # Identical strings → distance 0.0
    result = mod.p_distance("ACGT", "ACGT")
    assert result == 0.0, f"Expected 0.0, got {result}"
    print(f"✓ Identical strings → p_distance = {result}")

    # Completely different strings → distance 1.0
    result = mod.p_distance("AAAA", "TTTT")
    assert result == 1.0, f"Expected 1.0, got {result}"
    print(f"✓ Completely different strings → p_distance = {result}")

    # Rosalind sample pair: TTTCCATTTA vs GATTCATTTC → 4/10 = 0.4
    result = mod.p_distance("TTTCCATTTA", "GATTCATTTC")
    assert abs(result - 0.4) < 1e-10, f"Expected 0.4, got {result}"
    print(f"✓ Sample pair (4 mismatches in 10): p_distance = {result}")

    # Rosalind sample pair: TTTCCATTTA vs TTTCCATTTT → 1/10 = 0.1
    result = mod.p_distance("TTTCCATTTA", "TTTCCATTTT")
    assert abs(result - 0.1) < 1e-10, f"Expected 0.1, got {result}"
    print(f"✓ Sample pair (1 mismatch in 10): p_distance = {result}")

    # Mismatched lengths raise ValueError
    try:
        mod.p_distance("ACGT", "ACG")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ ValueError raised for mismatched lengths")

    # Full 4×4 distance matrix from Rosalind PDST sample
    sample_fasta = """\
>Rosalind_9499
TTTCCATTTA
>Rosalind_0942
GATTCATTTC
>Rosalind_6568
TTTCCATTTT
>Rosalind_1833
GTTCCATTTA
"""
    seqs = mod.parse_fasta(sample_fasta)
    assert len(seqs) == 4, f"Expected 4 sequences, got {len(seqs)}"
    assert seqs[0] == "TTTCCATTTA", f"Got {seqs[0]}"
    print(f"✓ FASTA parsed: {len(seqs)} sequences of length {len(seqs[0])}")

    mat = mod.distance_matrix(seqs)
    expected = [
        [0.0, 0.4, 0.1, 0.1],
        [0.4, 0.0, 0.4, 0.3],
        [0.1, 0.4, 0.0, 0.2],
        [0.1, 0.3, 0.2, 0.0],
    ]
    for i in range(4):
        for j in range(4):
            assert abs(mat[i][j] - expected[i][j]) < 1e-10, (
                f"mat[{i}][{j}] expected {expected[i][j]}, got {mat[i][j]}"
            )
    print("✓ Full 4×4 distance matrix matches Rosalind sample")

    # Diagonal is all zeros
    for i in range(4):
        assert mat[i][i] == 0.0, f"Diagonal mat[{i}][{i}] = {mat[i][i]}, expected 0"
    print("✓ Matrix diagonal is all zeros")

    # Matrix is symmetric
    for i in range(4):
        for j in range(4):
            assert mat[i][j] == mat[j][i], f"Matrix not symmetric at [{i}][{j}]"
    print("✓ Matrix is symmetric")

    # format_matrix output
    formatted = mod.format_matrix(mat)
    lines = formatted.strip().splitlines()
    assert len(lines) == 4, f"Expected 4 lines, got {len(lines)}"
    assert lines[0] == "0.00000 0.40000 0.10000 0.10000", f"Got: {lines[0]}"
    assert lines[1] == "0.40000 0.00000 0.40000 0.30000", f"Got: {lines[1]}"
    print("✓ format_matrix produces correct 5-decimal output")

    # Multi-line FASTA
    multi_fasta = ">seq1\nAC\nGT\n>seq2\nTT\nTT"
    parsed = mod.parse_fasta(multi_fasta)
    assert parsed == ["ACGT", "TTTT"], f"Got {parsed}"
    print("✓ Multi-line FASTA sequences joined correctly")

    print("✓ All PDST tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: INOD – Counting Internal Nodes of a Tree
# ─────────────────────────────────────────────────────────────────────────────

def test_inod():
    print("\n" + "=" * 70)
    print("TEST 2: INOD – Counting Internal Nodes of a Tree")
    print("=" * 70)

    mod = load_module('02_internal_nodes.py')

    # Edge case: n=1 → 0 internal nodes
    result = mod.internal_nodes(1)
    assert result == 0, f"Expected 0, got {result}"
    print(f"✓ n=1 (edge case): internal_nodes = {result}")

    # Rosalind sample: n=4 → 3
    result = mod.internal_nodes(4)
    assert result == 3, f"Expected 3, got {result}"
    print(f"✓ n=4 (Rosalind sample): internal_nodes = {result}")

    # Large value: n=100 → 99
    result = mod.internal_nodes(100)
    assert result == 99, f"Expected 99, got {result}"
    print(f"✓ n=100: internal_nodes = {result}")

    # total_nodes
    assert mod.total_nodes(1) == 1
    assert mod.total_nodes(4) == 7
    assert mod.total_nodes(100) == 199
    print("✓ total_nodes: 1→1, 4→7, 100→199")

    # validate_binary_tree_counts
    assert mod.validate_binary_tree_counts(4, 3, 7) is True
    assert mod.validate_binary_tree_counts(4, 4, 8) is False
    assert mod.validate_binary_tree_counts(1, 0, 1) is True
    print("✓ validate_binary_tree_counts works correctly")

    # Invalid n raises ValueError
    try:
        mod.internal_nodes(0)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ ValueError raised for n=0")

    # TreeNode basic construction
    node = mod.TreeNode("root", mod.TreeNode("left"), mod.TreeNode("right"))
    assert node.value == "root"
    assert not node.is_leaf()
    assert node.left.is_leaf()
    assert node.right.is_leaf()
    print("✓ TreeNode construction and is_leaf() work correctly")

    # count_leaves on a 4-leaf tree
    tree = mod.build_example_tree(4)
    leaves = mod.count_leaves(tree)
    assert leaves == 4, f"Expected 4 leaves, got {leaves}"
    print(f"✓ count_leaves on 4-leaf tree: {leaves}")

    # count_internal on a 4-leaf tree → should be 3
    internals = mod.count_internal(tree)
    assert internals == 3, f"Expected 3 internal nodes, got {internals}"
    print(f"✓ count_internal on 4-leaf tree: {internals}")

    # count_leaves(None) = 0, count_internal(None) = 0
    assert mod.count_leaves(None) == 0
    assert mod.count_internal(None) == 0
    print("✓ count_leaves(None) and count_internal(None) return 0")

    # Single-node tree is a leaf, not internal
    solo = mod.TreeNode("only")
    assert mod.count_leaves(solo) == 1
    assert mod.count_internal(solo) == 0
    print("✓ Single TreeNode counts as 1 leaf, 0 internal")

    # Formula consistency: count_leaves + count_internal = total_nodes
    for n in [2, 4, 8]:
        t = mod.build_example_tree(n)
        l = mod.count_leaves(t)
        i = mod.count_internal(t)
        assert l + i == mod.total_nodes(n), (
            f"n={n}: leaves={l} + internal={i} != total_nodes={mod.total_nodes(n)}"
        )
    print("✓ count_leaves + count_internal = total_nodes for n=2,4,8")

    print("✓ All INOD tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("ROSALIND PHYLOGENY – TEST SUITE (Session 8)")
    print("=" * 70)
    print("Testing PDST | INOD\n")

    tests = [test_pdst, test_inod]
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
