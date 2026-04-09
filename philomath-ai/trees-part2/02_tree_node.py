"""
TreeNode: A Recursive Tree Data Structure
==========================================

Chapter 5 of "Programming for Lovers in Python" — Trees Part 2
by Phillip Compeau (Carnegie Mellon University).

Background
----------
A **rooted binary tree** is a data structure where:
  - Each node has at most two children (left and right)
  - Every node except the root has exactly one parent
  - **Leaf nodes** have no children (they represent the tips)
  - **Internal nodes** have one or two children

In phylogenetics, rooted binary trees represent evolutionary relationships:
  - Leaf nodes → modern species (or sequences)
  - Internal nodes → common ancestors
  - Branch lengths → evolutionary distance

TreeNode Design
---------------
Each node stores:
  name      — label for the node (species name or cluster label)
  left      — left child TreeNode (or None)
  right     — right child TreeNode (or None)
  distance  — branch length from this node to its parent

Recursive count_leaves()
------------------------
    if is_leaf(node):
        return 1
    else:
        return count_leaves(node.left) + count_leaves(node.right)

This elegantly exploits the recursive structure of the tree itself.

Learning Objectives
-------------------
- Implement a tree node class with recursive methods
- Distinguish leaf nodes from internal nodes using is_leaf()
- Recursively count leaves without any loops
- Build sample trees and verify counts manually
"""

from __future__ import annotations
from typing import Optional


class TreeNode:
    """
    A node in a rooted binary phylogenetic tree.

    Attributes:
        name (str):           Label for this node.  Leaf nodes are typically
                              named after species; internal nodes may be labeled
                              with cluster indices or ancestor names.
        left (TreeNode|None): Left child, or None if absent.
        right (TreeNode|None):Right child, or None if absent.
        distance (float):     Branch length from this node UP to its parent.
                              The root's distance is typically 0.0.
    """

    def __init__(
        self,
        name: str = "",
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
        distance: float = 0.0,
    ) -> None:
        """
        Create a new TreeNode.

        Args:
            name:     Label string for this node.
            left:     Left child TreeNode, or None.
            right:    Right child TreeNode, or None.
            distance: Branch length to parent (default 0.0).

        Examples:
            >>> leaf = TreeNode("human")
            >>> leaf.is_leaf()
            True
            >>> root = TreeNode("ancestor", left=TreeNode("A"), right=TreeNode("B"))
            >>> root.is_leaf()
            False
        """
        self.name = name
        self.left = left
        self.right = right
        self.distance = distance

    # ── Leaf detection ────────────────────────────────────────────────────────

    def is_leaf(self) -> bool:
        """
        Return True if this node is a leaf (has no children).

        A leaf node has both left and right set to None.  In UPGMA, leaf
        nodes correspond to individual species in the input dataset.

        Returns:
            True  — this node has no children
            False — this node has at least one child

        Examples:
            >>> TreeNode("A").is_leaf()
            True
            >>> TreeNode("root", left=TreeNode("A")).is_leaf()
            False
        """
        return self.left is None and self.right is None

    # ── Recursive leaf count ──────────────────────────────────────────────────

    def count_leaves(self) -> int:
        """
        Count the number of leaf descendants of this node (including self if
        this node is a leaf).

        Algorithm (recursive):
            if this node is a leaf:
                return 1
            total = 0
            if left child exists:  total += left.count_leaves()
            if right child exists: total += right.count_leaves()
            return total

        This is O(n) where n is the total number of nodes in the subtree.

        Returns:
            Integer count of leaf nodes in this subtree.

        Examples:
            >>> TreeNode("solo").count_leaves()
            1
            >>> root = TreeNode("r", left=TreeNode("A"), right=TreeNode("B"))
            >>> root.count_leaves()
            2
        """
        if self.is_leaf():
            return 1
        total = 0
        if self.left is not None:
            total += self.left.count_leaves()
        if self.right is not None:
            total += self.right.count_leaves()
        return total

    # ── Height helper ─────────────────────────────────────────────────────────

    def height(self) -> float:
        """
        Return the maximum root-to-leaf distance (sum of branch lengths).

        Useful for UPGMA to compute branch lengths of new internal nodes.

        Returns:
            The longest cumulative branch-length path from this node to any leaf.
        """
        if self.is_leaf():
            return 0.0
        left_h = self.left.height() if self.left else 0.0
        right_h = self.right.height() if self.right else 0.0
        return max(
            (self.left.distance if self.left else 0.0) + left_h,
            (self.right.distance if self.right else 0.0) + right_h,
        )

    # ── String representations ─────────────────────────────────────────────────

    def __repr__(self) -> str:
        """
        Developer representation: TreeNode(name='X', dist=0.5, leaf=True).

        Examples:
            >>> repr(TreeNode("human", distance=0.01))
            "TreeNode(name='human', dist=0.010, leaf=True)"
        """
        return (
            f"TreeNode(name={self.name!r}, dist={self.distance:.3f}, "
            f"leaf={self.is_leaf()})"
        )

    def __str__(self) -> str:
        """
        Human-friendly ASCII tree representation.

        Uses a recursive helper to draw the tree with indentation showing depth.

        Examples:
            >>> print(TreeNode("solo"))
            solo (dist=0.000)
        """
        lines = []
        self._str_helper(lines, prefix="", is_last=True)
        return "\n".join(lines)

    def _str_helper(self, lines: list, prefix: str, is_last: bool) -> None:
        """Recursive helper for __str__ ASCII drawing."""
        connector = "└── " if is_last else "├── "
        dist_tag = f" (dist={self.distance:.4f})"
        lines.append(prefix + connector + self.name + dist_tag)
        child_prefix = prefix + ("    " if is_last else "│   ")
        children = [c for c in (self.left, self.right) if c is not None]
        for i, child in enumerate(children):
            child._str_helper(lines, child_prefix, is_last=(i == len(children) - 1))


# ─────────────────────────────────────────────────────────────────────────────
# Tree-building helpers
# ─────────────────────────────────────────────────────────────────────────────

def build_sample_tree() -> TreeNode:
    """
    Build a small five-leaf tree for demonstration purposes.

    Tree topology:

                    root
                   /    \\
              anc_AB   anc_CDE
             /    \\    /     \\
            A     B  anc_CD   E
                    /    \\
                   C      D

    Returns:
        The root TreeNode.
    """
    leaf_a = TreeNode("A",  distance=0.1)
    leaf_b = TreeNode("B",  distance=0.1)
    leaf_c = TreeNode("C",  distance=0.05)
    leaf_d = TreeNode("D",  distance=0.05)
    leaf_e = TreeNode("E",  distance=0.15)

    anc_cd  = TreeNode("anc_CD",  left=leaf_c,   right=leaf_d,  distance=0.1)
    anc_ab  = TreeNode("anc_AB",  left=leaf_a,   right=leaf_b,  distance=0.2)
    anc_cde = TreeNode("anc_CDE", left=anc_cd,   right=leaf_e,  distance=0.2)
    root    = TreeNode("root",    left=anc_ab,   right=anc_cde, distance=0.0)
    return root


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("TREENODE: RECURSIVE TREE DATA STRUCTURE")
    print("=" * 70)

    # Single leaf
    print("\n── Single leaf ──")
    leaf = TreeNode("human", distance=0.0)
    print(f"  {leaf!r}")
    print(f"  is_leaf(): {leaf.is_leaf()}")
    print(f"  count_leaves(): {leaf.count_leaves()}")

    # Simple 3-node tree
    print("\n── 3-node tree ──")
    small = TreeNode(
        "ancestor",
        left=TreeNode("chimp", distance=0.01),
        right=TreeNode("human", distance=0.01),
        distance=0.0,
    )
    print(small)
    print(f"  count_leaves(): {small.count_leaves()}")

    # Five-leaf sample tree
    print("\n── Five-leaf sample tree ──")
    root = build_sample_tree()
    print(root)
    print(f"\n  Total leaves:  {root.count_leaves()}  (expected 5)")
    print(f"  Tree height:   {root.height():.4f}")

    # Verify all subtree counts
    print("\n── Subtree leaf counts ──")
    for node in [root.left, root.right, root.right.left]:
        print(f"  {node.name}: {node.count_leaves()} leaves")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ is_leaf() → True when both left and right are None")
    print("✓ count_leaves() is elegantly recursive — no loops needed")
    print("✓ The tree structure mirrors the recursive function structure")
    print("✓ Each TreeNode carries a distance (branch length) to its parent")
