"""
LONG: Genome Assembly as Shortest Superstring
==============================================

Rosalind Problem: https://rosalind.info/problems/long/

Background
----------
Next-generation sequencers shred a genome into millions of short reads.
Assembling those reads back into the original genome is one of the central
challenges of bioinformatics.  The simplest model treats each read as a
substring of a single linear chromosome and asks:

  Given a collection of reads, find the shortest string that contains
  every read as a substring.

This is the **Shortest Superstring Problem**.

Overlap Graph
-------------
We represent the relationships between reads as a directed weighted graph:
  • Each read is a node.
  • A directed edge (s → t) has weight = length of the longest suffix of s
    that matches a prefix of t (the "overlap length").

A Hamiltonian path through this graph (visiting every node exactly once)
visits the reads in assembly order.  Reading off the path and merging
overlapping ends produces the superstring.

Greedy Algorithm
----------------
Under the assumption that the reads admit a unique superstring (no read is a
substring of another and there is a unique Hamiltonian path):

  1. Compute all pairwise overlap lengths.
  2. Identify the pair (s, t) with maximum overlap.
  3. Merge them: superstring = s + t[overlap:]
  4. Remove s and t from the pool, add the merged string.
  5. Repeat until one string remains.

Problem Statement
-----------------
Given:  A collection of DNA strings in FASTA format (total length ≤ 1 Mbp).

Return: The shortest superstring containing every string as a substring.
        (Assumes a unique Hamiltonian path exists in the overlap graph.)

Learning Objectives
-------------------
- Understand the Shortest Superstring Problem as a model of genome assembly
- Construct an overlap graph from a set of DNA reads
- Apply the greedy Hamiltonian-path heuristic for sequence assembly
- Appreciate why real assemblers use de Bruijn graphs for scalability
"""


def overlap(a: str, b: str) -> int:
    """
    Compute the length of the longest suffix of *a* that is a prefix of *b*.

    Scans from the longest possible overlap down to 1, returning as soon as
    a match is found.  Returns 0 when no suffix of *a* is a prefix of *b*.

    Args:
        a: First DNA string (source in the overlap graph).
        b: Second DNA string (target in the overlap graph).

    Returns:
        Length of the longest suffix of a that equals a prefix of b.

    Examples:
        >>> overlap("ATTAGACCTG", "AGACCTGCCG")
        7

        >>> overlap("ATCGG", "CGGTA")
        3

        >>> overlap("AAAA", "TTTT")
        0

        >>> overlap("ACGT", "CGTA")
        3
    """
    max_k = min(len(a), len(b))
    for k in range(max_k, 0, -1):
        if a[-k:] == b[:k]:
            return k
    return 0


def shortest_superstring(sequences: list) -> str:
    """
    Assemble a collection of DNA reads into the shortest superstring using
    the greedy overlap-graph algorithm.

    At each step the pair of strings with the largest pairwise overlap is
    merged.  The process is repeated until a single string remains.

    Assumption: the input admits a unique Hamiltonian path through its
    overlap graph (no read is a substring of another, and overlaps are
    unambiguous).

    Args:
        sequences: List of DNA strings to assemble.

    Returns:
        The shortest superstring containing every input string as a substring.

    Examples:
        >>> seqs = ["ATTAGACCTG", "CCTGCCGGAA", "AGACCTGCCG", "GCCGGAATAC"]
        >>> shortest_superstring(seqs)
        'ATTAGACCTGCCGGAATAC'

        >>> shortest_superstring(["AACG", "CGTT"])
        'AACGTT'

        >>> shortest_superstring(["HELLO"])
        'HELLO'
    """
    strings = list(sequences)

    while len(strings) > 1:
        best_i, best_j, best_ov = -1, -1, -1

        for i in range(len(strings)):
            for j in range(len(strings)):
                if i == j:
                    continue
                ov = overlap(strings[i], strings[j])
                if ov > best_ov:
                    best_ov = ov
                    best_i, best_j = i, j

        merged = strings[best_i] + strings[best_j][best_ov:]
        strings = [strings[k] for k in range(len(strings))
                   if k != best_i and k != best_j]
        strings.append(merged)

    return strings[0]


def parse_fasta(text: str) -> list:
    """
    Parse a FASTA-formatted string and return an ordered list of sequences.

    Header lines (starting with '>') are discarded; only the sequence data
    is returned.  Multi-line sequences are concatenated into a single string.

    Args:
        text: A string in FASTA format.

    Returns:
        List of sequence strings in the order they appear in the input.

    Examples:
        >>> fasta = ">seq1\\nACGT\\n>seq2\\nTTTT"
        >>> parse_fasta(fasta)
        ['ACGT', 'TTTT']

        >>> fasta = ">id1\\nACG\\nTAC\\n>id2\\nGGGG"
        >>> parse_fasta(fasta)
        ['ACGTAC', 'GGGG']
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


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("LONG: GENOME ASSEMBLY AS SHORTEST SUPERSTRING")
    print("=" * 70)

    # Rosalind sample dataset
    sample_fasta = """\
>Rosalind_56
ATTAGACCTG
>Rosalind_57
CCTGCCGGAA
>Rosalind_58
AGACCTGCCG
>Rosalind_59
GCCGGAATAC
"""
    reads = parse_fasta(sample_fasta)
    print(f"\nInput reads ({len(reads)} sequences):")
    for r in reads:
        print(f"  {r}")

    # Overlap graph — show all pairwise overlaps
    print("\nOverlap graph (edge weight = overlap length):")
    print(f"  {'Source':<14} {'Target':<14} {'Overlap':>7}")
    print("  " + "-" * 37)
    for i, s in enumerate(reads):
        for j, t in enumerate(reads):
            if i != j:
                ov = overlap(s, t)
                if ov > 0:
                    print(f"  {s:<14} {t:<14} {ov:>7}")

    # Greedy assembly
    result = shortest_superstring(reads)
    expected = "ATTAGACCTGCCGGAATAC"
    print(f"\nAssembled superstring : {result}")
    print(f"Expected              : {expected}")
    print(f"Match                 : {result == expected}")

    # Two-read example
    print("\nTwo-read example:")
    two_reads = ["AACGT", "CGTTA"]
    print(f"  Reads   : {two_reads}")
    print(f"  Overlap : {overlap(two_reads[0], two_reads[1])}")
    print(f"  Result  : {shortest_superstring(two_reads)}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Overlap graph: edge (s→t) weighted by len(longest suffix of s = prefix of t)")
    print("✓ Greedy: repeatedly merge the pair with maximum overlap")
    print("✓ Merge formula: superstring = s + t[overlap:]  (no duplication)")
    print("✓ Assumption: unique Hamiltonian path (no read is substring of another)")
    print("✓ Real assemblers use de Bruijn graphs to scale to billions of reads")
