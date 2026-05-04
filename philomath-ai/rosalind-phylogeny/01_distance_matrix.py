"""
PDST: Creating a Distance Matrix
=================================

Rosalind Problem: https://rosalind.info/problems/pdst/
Session 8 of the Philomath live problem-solving series.

Background
----------
Phylogenetics reconstructs evolutionary history by measuring how similar (or
different) DNA sequences are across species or individuals.  The first step is
always building a **distance matrix**: a table of pairwise distances that
captures how far apart every pair of sequences is.

The simplest distance measure for aligned DNA sequences is the **p-distance**
(also called the Hamming distance fraction):

    p(s, t) = (number of positions where s and t differ) / (length of s)

For four sequences of length 10, this produces a symmetric 4×4 matrix whose
diagonal is all zeros (a sequence has zero distance from itself).

Problem Statement
-----------------
Given:  A collection of DNA strings of equal length in FASTA format
        (at most 10 sequences, each at most 1000 nucleotides).

Return: The p-distance matrix D such that D[i][j] = p_distance(seqᵢ, seqⱼ).
        Report each value to 5 decimal places, space-separated.

Learning Objectives
-------------------
- Understand the p-distance (Hamming fraction) as a baseline sequence metric
- Parse FASTA format and build a distance matrix from aligned sequences
- Recognise the structure of symmetric matrices (D[i][j] = D[j][i])
- Lay the groundwork for UPGMA and Neighbour-Joining phylogenetics
"""


def p_distance(s: str, t: str) -> float:
    """
    Compute the p-distance between two equal-length DNA strings.

    The p-distance is the fraction of positions at which the two strings
    differ.  It ranges from 0.0 (identical) to 1.0 (every position differs).

    Args:
        s: First DNA string.
        t: Second DNA string (must be the same length as s).

    Returns:
        Float in [0.0, 1.0] representing the fraction of mismatching positions.

    Raises:
        ValueError: If the strings have different lengths or are empty.

    Examples:
        >>> p_distance("TTTCCATTTA", "TTTCCATTTA")
        0.0

        >>> p_distance("AAAA", "TTTT")
        1.0

        >>> p_distance("TTTCCATTTA", "GATTCATTTC")
        0.4
    """
    if len(s) != len(t):
        raise ValueError(
            f"Strings must be the same length, got {len(s)} and {len(t)}."
        )
    if len(s) == 0:
        raise ValueError("Strings must not be empty.")
    mismatches = sum(a != b for a, b in zip(s, t))
    return mismatches / len(s)


def distance_matrix(sequences: list) -> list:
    """
    Build the n×n p-distance matrix for a list of equal-length DNA strings.

    Cell [i][j] equals p_distance(sequences[i], sequences[j]).  The matrix
    is symmetric and has zeros on the main diagonal.

    Args:
        sequences: List of equal-length DNA strings.

    Returns:
        n×n list of lists of floats, where n = len(sequences).

    Examples:
        >>> seqs = ["AAAA", "AAAA"]
        >>> distance_matrix(seqs)
        [[0.0, 0.0], [0.0, 0.0]]

        >>> seqs = ["AAAA", "TTTT"]
        >>> distance_matrix(seqs)
        [[0.0, 1.0], [1.0, 0.0]]
    """
    n = len(sequences)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = p_distance(sequences[i], sequences[j])
            matrix[i][j] = d
            matrix[j][i] = d
    return matrix


def parse_fasta(text: str) -> list:
    """
    Parse a FASTA-formatted string and return a list of sequences (no headers).

    Multi-line sequences are joined into a single string.  Header lines
    (starting with '>') are discarded.

    Args:
        text: A string containing one or more FASTA records.

    Returns:
        List of sequence strings in the order they appear in the input.

    Examples:
        >>> fasta = ">seq1\\nACGT\\n>seq2\\nTTTT"
        >>> parse_fasta(fasta)
        ['ACGT', 'TTTT']

        >>> fasta = ">seq1\\nAA\\nCC\\n>seq2\\nGG\\nTT"
        >>> parse_fasta(fasta)
        ['AACC', 'GGTT']
    """
    sequences = []
    current = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line.startswith('>'):
            if current:
                sequences.append(''.join(current))
                current = []
        else:
            current.append(line)
    if current:
        sequences.append(''.join(current))
    return sequences


def format_matrix(matrix: list) -> str:
    """
    Format a distance matrix as a space-separated string with 5 decimal places.

    Each row is on its own line; values are separated by single spaces.

    Args:
        matrix: n×n list of lists of floats.

    Returns:
        Multi-line string with each row formatted to 5 decimal places.

    Examples:
        >>> m = [[0.0, 0.4], [0.4, 0.0]]
        >>> print(format_matrix(m))
        0.00000 0.40000
        0.40000 0.00000
    """
    rows = []
    for row in matrix:
        rows.append(' '.join(f'{v:.5f}' for v in row))
    return '\n'.join(rows)


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("PDST: CREATING A DISTANCE MATRIX")
    print("=" * 70)

    # Rosalind sample dataset
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

    seqs = parse_fasta(sample_fasta)
    print(f"\nParsed {len(seqs)} sequences, each of length {len(seqs[0])}:")
    for i, s in enumerate(seqs):
        print(f"  seq{i+1}: {s}")

    mat = distance_matrix(seqs)

    print("\nDistance matrix (p-distance):")
    print(format_matrix(mat))

    print("\nExpected:")
    print("0.00000 0.40000 0.10000 0.10000")
    print("0.40000 0.00000 0.40000 0.30000")
    print("0.10000 0.40000 0.00000 0.20000")
    print("0.10000 0.30000 0.20000 0.00000")

    # Verify diagonal is all zeros
    print("\nDiagonal check (should all be 0.0):")
    for i in range(len(mat)):
        print(f"  mat[{i}][{i}] = {mat[i][i]}")

    # Verify symmetry
    print("\nSymmetry check mat[0][1] == mat[1][0]:", mat[0][1] == mat[1][0])

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ p-distance = mismatches / length  (Hamming fraction)")
    print("✓ Distance matrix is symmetric: D[i][j] = D[j][i]")
    print("✓ Diagonal is always 0 (a sequence has zero distance from itself)")
    print("✓ p-distance is the basis for UPGMA and Neighbour-Joining trees")
    print("✓ FASTA parser must handle multi-line sequences by joining lines")
