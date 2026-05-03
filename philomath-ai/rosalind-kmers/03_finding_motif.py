"""
SUBS: Finding a Motif in DNA
=============================

Rosalind Problem: https://rosalind.info/problems/subs/

Background
----------
A **motif** is a short, recurring sequence pattern that often has biological
significance — for example, a transcription factor binding site, a restriction
enzyme recognition site, or a splice site.

Finding all occurrences of a motif in a longer DNA string is one of the most
fundamental operations in bioinformatics.  Because biological motifs can
overlap (e.g. "ATATAT" contains "ATAT" at positions 1 and 3), a naive
substring search must allow overlapping matches.

The Python built-in str.find / str.index only returns the first match;
to find all overlapping occurrences we must advance the search position by 1
after each match rather than by len(motif).

Problem Statement
-----------------
Given:  Two DNA strings s (length ≤ 1 kbp) and t (length ≤ len(s)).

Return: All 1-indexed locations of t as a substring of s.

Learning Objectives
-------------------
- Implement overlapping substring search using a sliding window
- Convert between 0-indexed (Python) and 1-indexed (Rosalind) coordinates
- Understand why overlapping matches require step size 1 in the search loop
- Recognise motif finding as the basis for restriction enzyme mapping and
  transcription factor binding site analysis
"""


def find_motif(dna: str, motif: str) -> list:
    """
    Find all 1-indexed positions where motif occurs in dna (overlapping).

    Rosalind uses 1-based indexing: position 1 is the first character.
    Overlapping occurrences are all reported.

    Args:
        dna:   The haystack DNA string.
        motif: The needle DNA string to search for.

    Returns:
        Sorted list of 1-based positions where motif starts in dna.
        Returns an empty list if motif is not found or is longer than dna.

    Examples:
        >>> find_motif("GATATATGCATATACTT", "ATAT")
        [2, 4, 10]

        >>> find_motif("ACGT", "CG")
        [2]

        >>> find_motif("AAAA", "AA")
        [1, 2, 3]

        >>> find_motif("ACGT", "TTTT")
        []
    """
    positions = []
    start = 0
    while start <= len(dna) - len(motif):
        idx = dna.find(motif, start)
        if idx == -1:
            break
        positions.append(idx + 1)  # convert to 1-indexed
        start = idx + 1             # step by 1 to allow overlaps
    return positions


def find_motif_zero_indexed(dna: str, motif: str) -> list:
    """
    Find all 0-indexed positions where motif occurs in dna (overlapping).

    This is the Python-native 0-based variant of find_motif.  It is useful
    for downstream processing where 0-based slicing is needed.

    Args:
        dna:   The haystack DNA string.
        motif: The needle DNA string to search for.

    Returns:
        Sorted list of 0-based positions where motif starts in dna.
        Returns an empty list if motif is not found or is longer than dna.

    Examples:
        >>> find_motif_zero_indexed("GATATATGCATATACTT", "ATAT")
        [1, 3, 9]

        >>> find_motif_zero_indexed("ACGT", "CG")
        [1]

        >>> find_motif_zero_indexed("AAAA", "AA")
        [0, 1, 2]

        >>> find_motif_zero_indexed("ACGT", "TTTT")
        []
    """
    positions = []
    start = 0
    while start <= len(dna) - len(motif):
        idx = dna.find(motif, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + 1
    return positions


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("SUBS: FINDING A MOTIF IN DNA")
    print("=" * 70)

    # Rosalind sample dataset
    dna = "GATATATGCATATACTT"
    motif = "ATAT"
    positions = find_motif(dna, motif)
    print(f"\nSample dataset:")
    print(f"  DNA   = {dna}  (length {len(dna)})")
    print(f"  Motif = {motif}  (length {len(motif)})")
    print(f"  Positions (1-indexed): {' '.join(map(str, positions))}")
    print(f"  Expected:              2 4 10")

    # Visual alignment of all matches
    print(f"\nVisual alignment:")
    print(f"  {dna}")
    for pos in positions:
        padding = " " * (pos - 1)
        print(f"  {padding}{motif}  ← position {pos}")

    # 0-indexed version
    zero_pos = find_motif_zero_indexed(dna, motif)
    print(f"\n  Positions (0-indexed): {zero_pos}")

    # Overlapping example — all 'AA' in 'AAAA'
    print(f"\nOverlapping example:")
    dna2 = "AAAA"
    motif2 = "AA"
    pos2 = find_motif(dna2, motif2)
    print(f"  DNA   = {dna2}")
    print(f"  Motif = {motif2}")
    print(f"  Positions (1-indexed): {pos2}  (overlapping matches included)")

    # Motif not found
    missing = find_motif("ACGT", "TTTT")
    print(f"\nMotif 'TTTT' in 'ACGT': {missing}  (empty list when absent)")

    # Motif equals the full string
    exact = find_motif("ACGT", "ACGT")
    print(f"Motif 'ACGT' in 'ACGT': {exact}  (single match at position 1)")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Rosalind uses 1-based coordinates; Python uses 0-based — always convert")
    print("✓ Overlapping matches require advancing by 1 after each hit, not len(motif)")
    print("✓ str.find(motif, start) returns -1 when not found — use as loop sentinel")
    print("✓ Motif finding underlies restriction site mapping and TFBS prediction")
    print("✓ For very large genomes, specialised algorithms (KMP, BM) run in O(n+m)")
