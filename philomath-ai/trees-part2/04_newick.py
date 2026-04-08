"""
Newick Format: Standard Phylogenetic Tree Representation
=========================================================

Chapter 5 of "Programming for Lovers in Python" — Trees Part 2
by Phillip Compeau (Carnegie Mellon University).

Background
----------
**Newick format** (also called New Hampshire format) is the standard plain-text
representation for phylogenetic trees.  It was adopted at a meeting in Newick's
restaurant in New Hampshire in 1986 and is still ubiquitous in bioinformatics.

Syntax
------
The format is parenthetical:
  - A **leaf** is just its name:                       human
  - An **internal node** wraps its children:           (child1,child2)name
  - Branch lengths follow a colon after the name:      human:0.0120
  - A full tree (rooted binary):
        ((human:0.006,chimp:0.006):0.009,gorilla:0.015);
  - The semicolon terminates the tree string.

Examples:
  Single leaf:              A;
  Two leaves, no lengths:   (A,B);
  With branch lengths:      (A:0.1,B:0.2)root:0.0;
  Four-taxon tree:          ((A:0.1,B:0.1):0.05,(C:0.05,D:0.05):0.05);

Learning Objectives
-------------------
- Convert a TreeNode tree to a Newick string recursively
- Write a basic Newick parser to reconstruct a tree from a string
- Appreciate that Newick is the standard exchange format for trees
"""

from __future__ import annotations
import re
import importlib.util
import os
import sys


def _load_tree_node():
    """Load TreeNode class from 02_tree_node.py."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "02_tree_node.py")
    spec = importlib.util.spec_from_file_location("tree_node", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TreeNode


# ─────────────────────────────────────────────────────────────────────────────
# Newick serialiser
# ─────────────────────────────────────────────────────────────────────────────

def to_newick(node, include_root_distance: bool = False) -> str:
    """
    Convert a TreeNode tree to a Newick format string.

    Recursion:
      - Leaf:     return  "name:distance"
      - Internal: return  "(left_newick,right_newick)name:distance"
    The root gets no trailing distance by default (include_root_distance=False).

    Args:
        node:                    Root of the tree (or any subtree).
        include_root_distance:   If True, append ":distance" for the root node
                                 as well (default False).

    Returns:
        Newick string terminated with ";".

    Examples:
        >>> # build minimal tree inline for doctest
        >>> class N:
        ...     def __init__(self, name, left=None, right=None, distance=0.0):
        ...         self.name=name; self.left=left; self.right=right; self.distance=distance
        ...     def is_leaf(self): return self.left is None and self.right is None
        >>> root = N("r", left=N("A", distance=0.1), right=N("B", distance=0.1))
        >>> to_newick(root)
        '(A:0.10000,B:0.10000)r;'
    """
    body = _newick_subtree(node, is_root=True,
                           include_root_distance=include_root_distance)
    return body + ";"


def _newick_subtree(node, is_root: bool = False,
                    include_root_distance: bool = False) -> str:
    """Recursive helper — returns the Newick string for a subtree (no semicolon)."""
    if node.is_leaf():
        return f"{node.name}:{node.distance:.5f}"

    children = []
    if node.left is not None:
        children.append(_newick_subtree(node.left))
    if node.right is not None:
        children.append(_newick_subtree(node.right))

    inner = f"({','.join(children)}){node.name}"

    if is_root and not include_root_distance:
        return inner
    return f"{inner}:{node.distance:.5f}"


# ─────────────────────────────────────────────────────────────────────────────
# Newick parser (basic)
# ─────────────────────────────────────────────────────────────────────────────

def parse_newick(newick_str: str):
    """
    Parse a Newick format string and return the root TreeNode.

    Supports:
      - Leaf nodes with optional names and distances:  A:0.1  or  A  or  :0.1
      - Internal nodes with optional labels:           (A,B)ancestor:0.5
      - Semicolon terminator (stripped automatically)
      - Nested trees of arbitrary depth

    Limitations:
      - Does not support quoted names with special characters
      - Does not support comments ([ ... ])

    Args:
        newick_str: A valid Newick string, optionally ending with ";".

    Returns:
        Root TreeNode reconstructed from the Newick string.

    Examples:
        >>> root = parse_newick("(A:0.1,B:0.1)root;")
        >>> root.name
        'root'
        >>> root.count_leaves()
        2
    """
    TreeNodeClass = _load_tree_node()

    s = newick_str.strip()
    if s.endswith(";"):
        s = s[:-1]

    node, pos = _parse_node(s, 0, TreeNodeClass)
    return node


def _parse_node(s: str, pos: int, TreeNodeClass):
    """
    Recursively parse one node (subtree) starting at position pos.

    Returns (TreeNode, new_pos).
    """
    if pos < len(s) and s[pos] == "(":
        # Internal node: parse children
        pos += 1  # skip '('
        children = []
        while True:
            child, pos = _parse_node(s, pos, TreeNodeClass)
            children.append(child)
            if pos >= len(s):
                break
            if s[pos] == ",":
                pos += 1  # skip ','
            elif s[pos] == ")":
                pos += 1  # skip ')'
                break
            else:
                break

        # Optional internal-node label and distance
        label, dist, pos = _parse_label_dist(s, pos)
        node = TreeNodeClass(
            name=label,
            left=children[0] if len(children) > 0 else None,
            right=children[1] if len(children) > 1 else None,
            distance=dist,
        )
        return node, pos
    else:
        # Leaf node
        label, dist, pos = _parse_label_dist(s, pos)
        node = TreeNodeClass(name=label, distance=dist)
        return node, pos


def _parse_label_dist(s: str, pos: int) -> tuple[str, float, int]:
    """Parse an optional 'name:distance' fragment starting at pos."""
    # Collect characters until we hit ')', ',', or end of string
    name_chars = []
    while pos < len(s) and s[pos] not in (")", ",", ";"):
        if s[pos] == ":":
            pos += 1
            break
        name_chars.append(s[pos])
        pos += 1

    label = "".join(name_chars).strip()

    # Try to parse a distance after ':'
    dist_chars = []
    while pos < len(s) and s[pos] not in (")", ",", "(", ";"):
        dist_chars.append(s[pos])
        pos += 1

    dist_str = "".join(dist_chars).strip()
    dist = float(dist_str) if dist_str else 0.0

    return label, dist, pos


# ─────────────────────────────────────────────────────────────────────────────
# Pretty-print Newick as an indented outline
# ─────────────────────────────────────────────────────────────────────────────

def newick_to_indented(newick_str: str) -> str:
    """
    Convert a Newick string to a human-readable indented outline.

    Useful for quickly checking tree topology in the terminal.

    Args:
        newick_str: A valid Newick format string.

    Returns:
        Multi-line indented string showing the tree hierarchy.
    """
    root = parse_newick(newick_str)
    return str(root)


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("NEWICK FORMAT: STANDARD TREE REPRESENTATION")
    print("=" * 70)

    TreeNodeClass = _load_tree_node()

    # Build a four-taxon tree manually
    print("\n── Building a four-taxon tree ──")
    leaf_a = TreeNodeClass("human",    distance=0.006)
    leaf_b = TreeNodeClass("chimp",    distance=0.006)
    leaf_c = TreeNodeClass("gorilla",  distance=0.015)
    anc_hc = TreeNodeClass("anc_hc",   left=leaf_a, right=leaf_b, distance=0.009)
    root   = TreeNodeClass("root",     left=anc_hc, right=leaf_c)

    newick = to_newick(root)
    print(f"\nNewick string:\n  {newick}")

    # Parse it back
    print("\n── Round-trip: parse the Newick string back to a tree ──")
    root2 = parse_newick(newick)
    newick2 = to_newick(root2)
    print(f"Re-serialised:\n  {newick2}")
    print(f"Strings match: {newick == newick2}")

    # Five-taxon great-apes tree
    print("\n── Five-taxon tree (great apes) ──")
    import sys
    import importlib.util
    import os
    upgma_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_upgma.py")
    spec = importlib.util.spec_from_file_location("upgma_mod", upgma_path)
    upgma_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upgma_mod)

    apes_dm = [
        [0.000, 0.012, 0.013, 0.030, 0.080],
        [0.012, 0.000, 0.009, 0.031, 0.079],
        [0.013, 0.009, 0.000, 0.032, 0.081],
        [0.030, 0.031, 0.032, 0.000, 0.078],
        [0.080, 0.079, 0.081, 0.078, 0.000],
    ]
    apes_labels = ["human", "chimp", "bonobo", "gorilla", "orangutan"]
    apes_root = upgma_mod.upgma(apes_dm, apes_labels)
    apes_newick = to_newick(apes_root)
    print(f"\nNewick:\n  {apes_newick}")
    print(f"\nIndented tree:")
    print(apes_root)

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Newick uses nested parentheses to encode tree topology")
    print("✓ Branch lengths follow a colon: name:distance")
    print("✓ Semicolon terminates the entire tree string")
    print("✓ Virtually all phylogenetics software supports Newick")
