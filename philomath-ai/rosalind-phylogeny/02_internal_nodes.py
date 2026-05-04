"""
INOD: Counting Internal Nodes of a Tree
========================================

Rosalind Problem: https://rosalind.info/problems/inod/
Session 8 of the Philomath live problem-solving series.

Background
----------
A **phylogenetic tree** represents the evolutionary relationships among a set
of species (or sequences).  In the rooted binary tree model used in
bioinformatics:

  • **Leaf nodes** (external nodes) correspond to the observed taxa (sequences).
  • **Internal nodes** represent hypothetical common ancestors.
  • Every internal node has exactly two children (binary branching).

For a rooted binary tree with n leaves:
  - Number of internal nodes  = n − 1
  - Total nodes               = 2n − 1

This is a foundational identity that comes up whenever analysing the
computational complexity of tree algorithms (e.g., UPGMA is O(n²) because it
merges n−1 times).

Problem Statement
-----------------
Given:  A positive integer n (3 ≤ n ≤ 10000), the number of leaves.

Return: The number of internal nodes of any rooted binary tree with n leaves.

Learning Objectives
-------------------
- Derive the internal-node formula from first principles (induction)
- Implement and traverse a simple binary tree data structure
- Connect the formula to the complexity of tree-building algorithms
- Distinguish leaves (taxa) from internal nodes (ancestors) in phylogenetics
"""


def internal_nodes(n: int) -> int:
    """
    Return the number of internal nodes in a rooted binary tree with n leaves.

    For a rooted binary tree, each internal node has exactly two children.
    By induction:
      - A tree with 1 leaf has 0 internal nodes.
      - Adding a leaf always adds exactly one internal node (the new branch
        point), so internal_nodes(n) = n − 1.

    Args:
        n: Number of leaf nodes (positive integer).

    Returns:
        Number of internal nodes (n − 1).

    Raises:
        ValueError: If n is less than 1.

    Examples:
        >>> internal_nodes(1)
        0

        >>> internal_nodes(4)
        3

        >>> internal_nodes(100)
        99
    """
    if n < 1:
        raise ValueError(f"n must be a positive integer, got {n}.")
    return n - 1


def total_nodes(n: int) -> int:
    """
    Return the total number of nodes (leaves + internal) in a rooted binary
    tree with n leaves.

    total_nodes(n) = n + internal_nodes(n) = n + (n − 1) = 2n − 1.

    Args:
        n: Number of leaf nodes (positive integer).

    Returns:
        Total number of nodes (2n − 1).

    Examples:
        >>> total_nodes(1)
        1

        >>> total_nodes(4)
        7

        >>> total_nodes(100)
        199
    """
    if n < 1:
        raise ValueError(f"n must be a positive integer, got {n}.")
    return 2 * n - 1


def validate_binary_tree_counts(n_leaves: int, n_internal: int, n_total: int) -> bool:
    """
    Validate that three node counts are consistent with a rooted binary tree.

    The relationships that must hold are:
        n_internal = n_leaves − 1
        n_total    = 2 × n_leaves − 1

    Args:
        n_leaves:   Claimed number of leaf nodes.
        n_internal: Claimed number of internal nodes.
        n_total:    Claimed total node count.

    Returns:
        True if all three counts are consistent, False otherwise.

    Examples:
        >>> validate_binary_tree_counts(4, 3, 7)
        True

        >>> validate_binary_tree_counts(4, 4, 8)
        False

        >>> validate_binary_tree_counts(1, 0, 1)
        True
    """
    return (n_internal == n_leaves - 1) and (n_total == 2 * n_leaves - 1)


class TreeNode:
    """
    A node in a rooted binary tree.

    Attributes:
        value: The label or data stored at this node.
        left:  Left child TreeNode, or None if absent.
        right: Right child TreeNode, or None if absent.
    """

    def __init__(self, value, left=None, right=None):
        """
        Initialise a TreeNode.

        Args:
            value: Label or data for the node.
            left:  Left child (TreeNode or None).
            right: Right child (TreeNode or None).

        Examples:
            >>> node = TreeNode("root", TreeNode("A"), TreeNode("B"))
            >>> node.value
            'root'
            >>> node.left.value
            'A'
        """
        self.value = value
        self.left = left
        self.right = right

    def is_leaf(self) -> bool:
        """
        Return True if this node is a leaf (has no children).

        Examples:
            >>> TreeNode("leaf").is_leaf()
            True

            >>> TreeNode("root", TreeNode("child")).is_leaf()
            False
        """
        return self.left is None and self.right is None

    def __repr__(self) -> str:
        return f"TreeNode({self.value!r})"


def count_leaves(node) -> int:
    """
    Recursively count the number of leaf nodes in the subtree rooted at node.

    A leaf is a node with no left or right child.

    Args:
        node: Root TreeNode of the subtree, or None.

    Returns:
        Integer count of leaf nodes.

    Examples:
        >>> count_leaves(None)
        0

        >>> count_leaves(TreeNode("solo"))
        1

        >>> t = TreeNode("r", TreeNode("a"), TreeNode("b", TreeNode("c"), TreeNode("d")))
        >>> count_leaves(t)
        3
    """
    if node is None:
        return 0
    if node.is_leaf():
        return 1
    return count_leaves(node.left) + count_leaves(node.right)


def count_internal(node) -> int:
    """
    Recursively count the number of internal (non-leaf) nodes in the subtree
    rooted at node.

    An internal node has at least one child.

    Args:
        node: Root TreeNode of the subtree, or None.

    Returns:
        Integer count of internal nodes.

    Examples:
        >>> count_internal(None)
        0

        >>> count_internal(TreeNode("solo"))
        0

        >>> t = TreeNode("r", TreeNode("a"), TreeNode("b", TreeNode("c"), TreeNode("d")))
        >>> count_internal(t)
        2
    """
    if node is None:
        return 0
    if node.is_leaf():
        return 0
    return 1 + count_internal(node.left) + count_internal(node.right)


def build_example_tree(n_leaves: int):
    """
    Build a balanced rooted binary tree with exactly n_leaves leaves.

    Constructs a complete binary tree by recursively splitting the leaf
    labels into two halves until single labels remain.

    Args:
        n_leaves: Number of leaves (must be a positive integer).

    Returns:
        Root TreeNode of the constructed tree, or None if n_leaves == 0.

    Examples:
        >>> t = build_example_tree(4)
        >>> count_leaves(t)
        4
        >>> count_internal(t)
        3
    """
    if n_leaves == 0:
        return None
    labels = [f"leaf_{i+1}" for i in range(n_leaves)]
    return _build_subtree(labels)


def _build_subtree(labels: list):
    """Recursively build a balanced binary subtree from a list of leaf labels."""
    if len(labels) == 1:
        return TreeNode(labels[0])
    mid = len(labels) // 2
    left = _build_subtree(labels[:mid])
    right = _build_subtree(labels[mid:])
    return TreeNode(f"anc({labels[0]}..{labels[-1]})", left, right)


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("INOD: COUNTING INTERNAL NODES OF A TREE")
    print("=" * 70)

    # Rosalind sample dataset
    n = 4
    print(f"\nSample dataset: n = {n} leaves")
    print(f"Internal nodes: {internal_nodes(n)}")
    print(f"Expected:        3")

    # Table for small values
    print("\nLeaves → Internal → Total (formula: n-1 and 2n-1):")
    print(f"{'n (leaves)':<14} {'internal (n-1)':<18} {'total (2n-1)':<14}")
    print("-" * 48)
    for n_ex in [1, 2, 3, 4, 5, 10, 100, 1000]:
        print(
            f"{n_ex:<14} {internal_nodes(n_ex):<18} {total_nodes(n_ex):<14}"
        )

    # TreeNode demo — build and traverse a 4-leaf tree
    print("\nBuilding a balanced binary tree with 4 leaves:")
    tree = build_example_tree(4)
    n_leaves_counted = count_leaves(tree)
    n_internal_counted = count_internal(tree)
    print(f"  Counted leaves:   {n_leaves_counted}")
    print(f"  Counted internal: {n_internal_counted}")
    print(f"  Formula check:    {validate_binary_tree_counts(n_leaves_counted, n_internal_counted, n_leaves_counted + n_internal_counted)}")

    # Edge case: single-leaf tree
    print("\nEdge case — single leaf (no internal nodes):")
    solo = build_example_tree(1)
    print(f"  Leaves:   {count_leaves(solo)}")
    print(f"  Internal: {count_internal(solo)}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Rooted binary tree with n leaves has exactly n−1 internal nodes")
    print("✓ Total nodes = 2n−1  (leaves + internal)")
    print("✓ UPGMA performs exactly n−1 merge steps → O(n²) complexity")
    print("✓ Leaves ↔ observed taxa; internal nodes ↔ hypothetical ancestors")
    print("✓ validate_binary_tree_counts confirms structural consistency")
