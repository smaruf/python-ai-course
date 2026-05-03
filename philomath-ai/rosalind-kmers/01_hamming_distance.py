"""
HAMM: Counting Point Mutations
===============================

Rosalind Problem: https://rosalind.info/problems/hamm/

Background
----------
When two DNA strings differ at a position due to a point mutation (a single
nucleotide substitution), that position is called a **point mutation** or
**mismatch**.  The Hamming distance is the minimal number of single-character
substitutions needed to transform one string into the other — it is simply the
count of positions where the two strings disagree.

Hamming distance was originally defined for binary strings in coding theory
(Richard Hamming, 1950) and has since become a foundational metric in
bioinformatics for measuring sequence divergence.

Problem Statement
-----------------
Given:  Two DNA strings s and t of equal length (at most 1 kbp each).

Return: The Hamming distance dH(s, t).

Learning Objectives
-------------------
- Understand point mutations and their role in evolutionary sequence divergence
- Implement pairwise string comparison in O(n) time
- Distinguish matching positions from mismatching positions
- Recognise Hamming distance as a special case of edit distance
"""


def hamming_distance(s: str, t: str) -> int:
    """
    Count the number of positions where two DNA strings differ.

    The Hamming distance dH(s, t) is defined as the number of indices i such
    that s[i] != t[i].  Both strings must have the same length.

    Args:
        s: First DNA string.
        t: Second DNA string of equal length to s.

    Returns:
        Integer count of positions where s and t differ.

    Raises:
        ValueError: If len(s) != len(t).

    Examples:
        >>> hamming_distance("GAGCCTACTAACGGGAT", "CATCGTAATGACGGCCT")
        7

        >>> hamming_distance("AAAA", "AAAA")
        0

        >>> hamming_distance("ACGT", "TGCA")
        4

        >>> hamming_distance("A", "T")
        1
    """
    if len(s) != len(t):
        raise ValueError(
            f"Strings must have equal length, got {len(s)} and {len(t)}."
        )
    return sum(a != b for a, b in zip(s, t))


def similar_positions(s: str, t: str) -> list:
    """
    Return 0-indexed positions where two strings agree.

    Args:
        s: First DNA string.
        t: Second DNA string of equal length to s.

    Returns:
        List of 0-based indices i where s[i] == t[i].

    Raises:
        ValueError: If len(s) != len(t).

    Examples:
        >>> similar_positions("GAGCCTACTAACGGGAT", "CATCGTAATGACGGCCT")
        [1, 3, 5, 6, 8, 10, 11, 12, 13, 16]

        >>> similar_positions("AAAA", "AAAA")
        [0, 1, 2, 3]

        >>> similar_positions("ACGT", "TGCA")
        []
    """
    if len(s) != len(t):
        raise ValueError(
            f"Strings must have equal length, got {len(s)} and {len(t)}."
        )
    return [i for i, (a, b) in enumerate(zip(s, t)) if a == b]


def mismatch_positions(s: str, t: str) -> list:
    """
    Return 0-indexed positions where two strings differ.

    Args:
        s: First DNA string.
        t: Second DNA string of equal length to s.

    Returns:
        List of 0-based indices i where s[i] != t[i].

    Raises:
        ValueError: If len(s) != len(t).

    Examples:
        >>> mismatch_positions("GAGCCTACTAACGGGAT", "CATCGTAATGACGGCCT")
        [0, 2, 4, 7, 9, 14, 15]

        >>> mismatch_positions("AAAA", "AAAA")
        []

        >>> mismatch_positions("ACGT", "TGCA")
        [0, 1, 2, 3]
    """
    if len(s) != len(t):
        raise ValueError(
            f"Strings must have equal length, got {len(s)} and {len(t)}."
        )
    return [i for i, (a, b) in enumerate(zip(s, t)) if a != b]


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("HAMM: COUNTING POINT MUTATIONS")
    print("=" * 70)

    # Rosalind sample dataset
    s = "GAGCCTACTAACGGGAT"
    t = "CATCGTAATGACGGCCT"
    dist = hamming_distance(s, t)
    print(f"\nSample dataset:")
    print(f"  s = {s}")
    print(f"  t = {t}")
    print(f"  Hamming distance = {dist}")
    print(f"  Expected:          7")

    # Show mismatching positions
    mismatches = mismatch_positions(s, t)
    print(f"\nMismatch positions (0-indexed): {mismatches}")
    print(f"  Count: {len(mismatches)}")

    matches = similar_positions(s, t)
    print(f"Similar  positions (0-indexed): {matches}")
    print(f"  Count: {len(matches)}")

    # Visual alignment
    print(f"\nAlignment (^ marks mismatches):")
    print(f"  s: {s}")
    print(f"  t: {t}")
    marker = "".join("^" if a != b else " " for a, b in zip(s, t))
    print(f"     {marker}")

    # Edge cases
    print("\nEdge cases:")
    print(f"  Identical strings: {hamming_distance('ACGT', 'ACGT')}  (expect 0)")
    print(f"  All mismatches:    {hamming_distance('ACGT', 'TGCA')}  (expect 4)")
    print(f"  Single char match: {hamming_distance('A', 'A')}  (expect 0)")
    print(f"  Single char diff:  {hamming_distance('A', 'T')}  (expect 1)")

    # ValueError demonstration
    try:
        hamming_distance("ACG", "AC")
    except ValueError as exc:
        print(f"\nValueError raised for unequal lengths: {exc}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Hamming distance counts positions where two equal-length strings differ")
    print("✓ It is computable in O(n) — one pass, no alignment needed")
    print("✓ dH(s,t) = 0 iff s == t; dH(s,t) = len(s) iff every character differs")
    print("✓ Point mutations in DNA are the building blocks of evolutionary change")
    print("✓ Hamming distance is a metric: non-negative, symmetric, triangle inequality")
