#!/usr/bin/env python3
"""
Test suite for the trees-part2 module.
=======================================

Run this file to verify all components are working correctly:

    python test_all.py

Modules covered:
  01  Recursion      — factorial, fibonacci (naive, memo, iterative)
  02  TreeNode       — is_leaf, count_leaves, build_sample_tree
  03  UPGMA          — upgma algorithm, find_min_distance, update_distances
  04  Newick         — to_newick, parse_newick round-trip
  05  Pipeline       — run_pipeline, load_csv, dataset constants
"""

import os
import sys
import importlib.util


_DIR = os.path.dirname(os.path.abspath(__file__))


def load_module(filename: str):
    """Load a Python module from the trees-part2 directory."""
    path = os.path.join(_DIR, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Recursion
# ─────────────────────────────────────────────────────────────────────────────

def test_recursion():
    print("\n" + "=" * 70)
    print("TEST 1: Recursion")
    print("=" * 70)

    rec = load_module("01_recursion.py")

    # Factorial
    assert rec.factorial(0) == 1,   f"factorial(0) should be 1, got {rec.factorial(0)}"
    assert rec.factorial(1) == 1,   f"factorial(1) should be 1"
    assert rec.factorial(5) == 120, f"factorial(5) should be 120, got {rec.factorial(5)}"
    assert rec.factorial(10) == 3628800
    print("✓ factorial(0) == 1")
    print("✓ factorial(1) == 1")
    print("✓ factorial(5) == 120")
    print("✓ factorial(10) == 3628800")

    # Factorial raises on negative
    try:
        rec.factorial(-1)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ factorial(-1) raises ValueError")

    # fibonacci_naive
    assert rec.fibonacci_naive(0)  == 0
    assert rec.fibonacci_naive(1)  == 1
    assert rec.fibonacci_naive(10) == 55, f"Got {rec.fibonacci_naive(10)}"
    assert rec.fibonacci_naive(15) == 610
    print("✓ fibonacci_naive(0) == 0")
    print("✓ fibonacci_naive(1) == 1")
    print("✓ fibonacci_naive(10) == 55")
    print("✓ fibonacci_naive(15) == 610")

    # fibonacci_memo
    assert rec.fibonacci_memo(0)  == 0
    assert rec.fibonacci_memo(10) == 55
    assert rec.fibonacci_memo(50) == 12586269025
    print("✓ fibonacci_memo(10) == 55")
    print("✓ fibonacci_memo(50) == 12586269025")

    # fibonacci_iterative
    assert rec.fibonacci_iterative(0)  == 0
    assert rec.fibonacci_iterative(1)  == 1
    assert rec.fibonacci_iterative(10) == 55
    assert rec.fibonacci_iterative(50) == 12586269025
    print("✓ fibonacci_iterative(10) == 55")
    print("✓ fibonacci_iterative(50) == 12586269025")

    # All three agree on first 20 values
    for k in range(20):
        naive = rec.fibonacci_naive(k)
        memo  = rec.fibonacci_memo(k)
        itr   = rec.fibonacci_iterative(k)
        assert naive == memo == itr, \
            f"Mismatch at F({k}): naive={naive}, memo={memo}, iter={itr}"
    print("✓ All three Fibonacci variants agree on F(0)..F(19)")

    print("✓ All Recursion tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: TreeNode
# ─────────────────────────────────────────────────────────────────────────────

def test_tree_node():
    print("\n" + "=" * 70)
    print("TEST 2: TreeNode")
    print("=" * 70)

    tn_mod = load_module("02_tree_node.py")
    TN = tn_mod.TreeNode

    # is_leaf
    leaf = TN("A")
    assert leaf.is_leaf() is True
    print("✓ Single node is_leaf() == True")

    internal = TN("root", left=TN("L"), right=TN("R"))
    assert internal.is_leaf() is False
    print("✓ Node with children is_leaf() == False")

    # count_leaves — single node
    assert leaf.count_leaves() == 1
    print("✓ Single leaf count_leaves() == 1")

    # count_leaves — 2-leaf tree
    assert internal.count_leaves() == 2
    print("✓ 2-leaf tree count_leaves() == 2")

    # count_leaves — manual 5-leaf tree
    leaf_a = TN("A")
    leaf_b = TN("B")
    leaf_c = TN("C")
    leaf_d = TN("D")
    leaf_e = TN("E")
    anc_cd  = TN("anc_CD",  left=leaf_c,  right=leaf_d)
    anc_ab  = TN("anc_AB",  left=leaf_a,  right=leaf_b)
    anc_cde = TN("anc_CDE", left=anc_cd,  right=leaf_e)
    root    = TN("root",    left=anc_ab,  right=anc_cde)

    assert root.count_leaves()    == 5, f"Got {root.count_leaves()}"
    assert anc_ab.count_leaves()  == 2
    assert anc_cde.count_leaves() == 3
    assert anc_cd.count_leaves()  == 2
    print("✓ 5-leaf tree: root.count_leaves() == 5")
    print("✓ Subtree leaf counts correct")

    # build_sample_tree helper
    sample = tn_mod.build_sample_tree()
    assert sample.count_leaves() == 5
    print("✓ build_sample_tree().count_leaves() == 5")

    # __repr__ and __str__ don't crash
    r = repr(leaf)
    assert "TreeNode" in r and "leaf=True" in r
    s = str(root)
    assert "root" in s
    print("✓ __repr__ and __str__ work correctly")

    print("✓ All TreeNode tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: UPGMA
# ─────────────────────────────────────────────────────────────────────────────

def test_upgma():
    print("\n" + "=" * 70)
    print("TEST 3: UPGMA")
    print("=" * 70)

    upgma_mod = load_module("03_upgma.py")

    # find_min_distance
    dm = [[0, 5, 9], [5, 0, 3], [9, 3, 0]]
    i, j = upgma_mod.find_min_distance(dm, 3)
    assert (i, j) == (1, 2), f"Expected (1,2), got ({i},{j})"
    print("✓ find_min_distance: correct minimum pair")

    # Small 4-taxon known example
    # A and B at distance 1; C and D at distance 2; AB vs CD at distance 5
    dm4 = [
        [0, 1, 5, 5],
        [1, 0, 5, 5],
        [5, 5, 0, 2],
        [5, 5, 2, 0],
    ]
    labels4 = ["A", "B", "C", "D"]
    root4 = upgma_mod.upgma(dm4, labels4)

    assert root4.count_leaves() == 4, f"Expected 4 leaves, got {root4.count_leaves()}"
    print("✓ 4-taxon UPGMA: 4 leaves")

    # Root should not be a leaf
    assert not root4.is_leaf()
    print("✓ Root is not a leaf")

    # Branch lengths must be non-negative
    def check_branch_lengths(node):
        assert node.distance >= 0, f"Negative distance on node '{node.name}': {node.distance}"
        if node.left:
            check_branch_lengths(node.left)
        if node.right:
            check_branch_lengths(node.right)

    check_branch_lengths(root4)
    print("✓ All branch lengths are non-negative")

    # Great apes — 5-taxon
    apes_dm = [
        [0.000, 0.012, 0.013, 0.030, 0.080],
        [0.012, 0.000, 0.009, 0.031, 0.079],
        [0.013, 0.009, 0.000, 0.032, 0.081],
        [0.030, 0.031, 0.032, 0.000, 0.078],
        [0.080, 0.079, 0.081, 0.078, 0.000],
    ]
    apes_labels = ["human", "chimp", "bonobo", "gorilla", "orangutan"]
    apes_root = upgma_mod.upgma(apes_dm, apes_labels)
    assert apes_root.count_leaves() == 5
    check_branch_lengths(apes_root)
    print("✓ Great apes UPGMA: 5 leaves, valid branch lengths")

    # Raises on mismatched sizes
    try:
        upgma_mod.upgma([[0, 1], [1, 0]], ["A", "B", "C"])
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Mismatched matrix/labels raises ValueError")

    print("✓ All UPGMA tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Newick
# ─────────────────────────────────────────────────────────────────────────────

def test_newick():
    print("\n" + "=" * 70)
    print("TEST 4: Newick")
    print("=" * 70)

    newick_mod = load_module("04_newick.py")
    tn_mod     = load_module("02_tree_node.py")
    TN = tn_mod.TreeNode

    # Single leaf
    leaf = TN("human", distance=0.0)
    nwk  = newick_mod.to_newick(leaf)
    assert nwk.endswith(";"), f"Newick must end with ';': {nwk}"
    assert "human" in nwk
    print(f"✓ Single leaf Newick: {nwk}")

    # 3-node tree
    root = TN("anc", left=TN("A", distance=0.1), right=TN("B", distance=0.2))
    nwk3 = newick_mod.to_newick(root)
    assert nwk3.endswith(";")
    assert "A" in nwk3 and "B" in nwk3
    print(f"✓ 3-node Newick: {nwk3}")

    # Round-trip: to_newick → parse_newick → to_newick
    root2 = newick_mod.parse_newick(nwk3)
    nwk3b = newick_mod.to_newick(root2)
    assert nwk3 == nwk3b, f"Round-trip mismatch:\n  {nwk3}\n  {nwk3b}"
    print("✓ Round-trip (to_newick → parse_newick → to_newick) matches")

    # parse_newick gives correct leaf count
    assert root2.count_leaves() == 2
    print("✓ Parsed tree has correct leaf count")

    # Newick from UPGMA
    upgma_mod = load_module("03_upgma.py")
    dm4 = [[0,1,5,5],[1,0,5,5],[5,5,0,2],[5,5,2,0]]
    tree = upgma_mod.upgma(dm4, ["A","B","C","D"])
    nwk4 = newick_mod.to_newick(tree)
    assert "A" in nwk4 and "B" in nwk4 and "C" in nwk4 and "D" in nwk4
    assert nwk4.endswith(";")
    print(f"✓ UPGMA 4-taxon Newick valid: {nwk4[:60]}...")

    # parse_newick with semicolon
    root_parsed = newick_mod.parse_newick("(A:0.1,B:0.2)root;")
    assert root_parsed.name == "root"
    assert root_parsed.count_leaves() == 2
    print("✓ parse_newick('(A:0.1,B:0.2)root;') — name='root', 2 leaves")

    print("✓ All Newick tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def test_pipeline():
    print("\n" + "=" * 70)
    print("TEST 5: Pipeline")
    print("=" * 70)

    pipeline = load_module("05_pipeline.py")

    # All datasets are present
    expected_keys = {"great_apes", "hemoglobin", "hiv_subtypes",
                     "sars_cov2", "mtdna_haplogroups"}
    assert set(pipeline.ALL_DATASETS.keys()) == expected_keys
    print("✓ All 5 datasets present in ALL_DATASETS")

    # Each dataset has 'labels' and 'matrix' with consistent sizes
    for name, ds in pipeline.ALL_DATASETS.items():
        n = len(ds["labels"])
        assert n > 0, f"{name}: labels is empty"
        assert len(ds["matrix"]) == n, \
            f"{name}: matrix rows ({len(ds['matrix'])}) != labels ({n})"
        for row in ds["matrix"]:
            assert len(row) == n, \
                f"{name}: matrix row length mismatch"
        # Diagonal should be 0
        for i in range(n):
            assert ds["matrix"][i][i] == 0.0, \
                f"{name}: diagonal[{i}] is not 0"
        # Symmetric
        for i in range(n):
            for j in range(n):
                assert abs(ds["matrix"][i][j] - ds["matrix"][j][i]) < 1e-10, \
                    f"{name}: matrix not symmetric at ({i},{j})"
        print(f"✓ Dataset '{name}': {n} taxa, square, symmetric, zero diagonal")

    # run_pipeline returns correct dict
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()  # suppress output
    try:
        result = pipeline.run_pipeline(
            pipeline.GREAT_APES["matrix"],
            pipeline.GREAT_APES["labels"],
            "great_apes_test",
        )
    finally:
        sys.stdout = old_stdout

    assert "root"   in result
    assert "newick" in result
    assert "leaves" in result
    assert result["leaves"] == 5
    assert result["newick"].endswith(";")
    print("✓ run_pipeline returns correct dict with root/newick/leaves")

    # load_csv: write a temp CSV and load it back
    csv_path = os.path.join(_DIR, "_test_matrix_tmp.csv")
    try:
        with open(csv_path, "w") as fh:
            fh.write(",A,B,C\n")
            fh.write("A,0,1,3\n")
            fh.write("B,1,0,3\n")
            fh.write("C,3,3,0\n")
        data = pipeline.load_csv(csv_path)
        assert data["labels"] == ["A", "B", "C"]
        assert data["matrix"][0][1] == 1.0
        assert data["matrix"][2][2] == 0.0
        print("✓ load_csv correctly reads a 3×3 CSV file")
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

    print("✓ All Pipeline tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("TREES PART 2 — TEST SUITE")
    print("=" * 70)

    tests = [
        ("Recursion", test_recursion),
        ("TreeNode",  test_tree_node),
        ("UPGMA",     test_upgma),
        ("Newick",    test_newick),
        ("Pipeline",  test_pipeline),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as exc:
            print(f"\n✗ FAILED: {name}")
            print(f"  {exc}")
            failed += 1
        except Exception as exc:
            print(f"\n✗ ERROR in {name}: {type(exc).__name__}: {exc}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{passed + failed} test groups passed")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)
    else:
        print("✓ All tests passed!")


if __name__ == "__main__":
    main()
