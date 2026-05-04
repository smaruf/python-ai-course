"""
KMER: k-mer Composition
========================

Rosalind Problem: https://rosalind.info/problems/kmer/

Background
----------
A **k-mer** is a substring of length k extracted from a DNA (or protein)
sequence.  The **k-mer composition** of a string is the ordered list of
counts of all 4^k possible k-mers over the DNA alphabet {A, C, G, T},
arranged in lexicographic order.

k-mer analysis is a fundamental technique in bioinformatics used for:
  • Genome assembly (overlap detection between reads)
  • Sequence alignment seeding
  • Taxonomic classification (e.g. Kraken2)
  • Repeat detection and genome size estimation

For a string of length L, the sliding window yields L − k + 1 k-mers
(with overlap allowed), so every position is covered.

Problem Statement
-----------------
Given:  A DNA string s of length at most 1 kbp.
        An integer k.

Return: The 4^k-length string of integers representing the k-mer composition
        of s, where counts are listed in lexicographic order of k-mers.

Learning Objectives
-------------------
- Enumerate all k-mers of a DNA string with a sliding window
- Generate all possible k-mers in lexicographic order using Cartesian product
- Represent sequences as fixed-length count vectors (k-mer profiles)
- Understand the relationship between k and the sparsity of the composition
"""

import itertools


def kmer_count(dna: str, k: int) -> dict:
    """
    Count every k-mer in a DNA string using a sliding window.

    Only k-mers that actually appear in the string are recorded; absent
    k-mers are not included in the returned dict.

    Args:
        dna: DNA string (characters A, C, G, T).
        k:   Length of each k-mer (positive integer, k <= len(dna)).

    Returns:
        Dictionary mapping each observed k-mer (str) to its count (int).

    Examples:
        >>> kmer_count("ACGT", 2)
        {'AC': 1, 'CG': 1, 'GT': 1}

        >>> kmer_count("AAAA", 2)
        {'AA': 3}

        >>> kmer_count("ACGT", 4)
        {'ACGT': 1}

        >>> kmer_count("AACGT", 2)
        {'AA': 1, 'AC': 1, 'CG': 1, 'GT': 1}
    """
    counts = {}
    for i in range(len(dna) - k + 1):
        kmer = dna[i: i + k]
        counts[kmer] = counts.get(kmer, 0) + 1
    return counts


def all_kmers(k: int, alphabet: str = "ACGT") -> list:
    """
    Generate all possible k-mers over the given alphabet in lexicographic order.

    The number of k-mers is len(alphabet)^k.  For DNA (alphabet = "ACGT")
    and k=4 this is 256 entries.

    Args:
        k:        Length of each k-mer (positive integer).
        alphabet: Ordered string of characters.  Defaults to "ACGT".

    Returns:
        List of all k-mers as strings, sorted lexicographically.

    Examples:
        >>> all_kmers(1)
        ['A', 'C', 'G', 'T']

        >>> all_kmers(2)[:4]
        ['AA', 'AC', 'AG', 'AT']

        >>> len(all_kmers(4))
        256

        >>> all_kmers(2, alphabet="AC")
        ['AA', 'AC', 'CA', 'CC']
    """
    return ["".join(p) for p in itertools.product(alphabet, repeat=k)]


def kmer_composition(dna: str, k: int) -> list:
    """
    Compute the k-mer composition of a DNA string.

    Returns a list of 4^k integers — one per possible k-mer in lexicographic
    order — giving the count of that k-mer in dna.  k-mers absent from dna
    contribute a count of 0.

    Args:
        dna: DNA string (characters A, C, G, T).
        k:   k-mer length (positive integer, k <= len(dna)).

    Returns:
        List of ints of length 4^k, ordered lexicographically over all k-mers.

    Examples:
        >>> kmer_composition("ACGT", 1)
        [1, 1, 1, 1]

        >>> kmer_composition("AAAA", 2)[:4]
        [3, 0, 0, 0]

        >>> len(kmer_composition("ACGT", 4))
        256

        >>> kmer_composition("ACGT", 2)
        [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    """
    observed = kmer_count(dna, k)
    return [observed.get(km, 0) for km in all_kmers(k)]


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("KMER: k-MER COMPOSITION")
    print("=" * 70)

    # Rosalind sample dataset
    dna = "CTTCGAAAGTTTGGGCCGCTTTGGCCC"
    k = 4
    composition = kmer_composition(dna, k)
    output = " ".join(map(str, composition))

    print(f"\nSample dataset:")
    print(f"  DNA = {dna}  (length {len(dna)})")
    print(f"  k   = {k}")
    print(f"\n  Total k-mers in string: {len(dna) - k + 1}")
    print(f"  Distinct k-mers observed: {sum(1 for c in composition if c > 0)}")
    print(f"  Possible 4-mers (4^4):  {len(composition)}")

    print(f"\n  k-mer composition (space-separated, 256 values):")
    # Print in rows of 16 for readability
    for row_start in range(0, len(composition), 16):
        row = composition[row_start: row_start + 16]
        kmers_in_row = all_kmers(k)[row_start: row_start + 16]
        print("  " + " ".join(f"{c:2}" for c in row))

    # Show the top-5 most frequent k-mers
    observed = kmer_count(dna, k)
    top5 = sorted(observed.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n  Top-5 most frequent 4-mers:")
    for km, cnt in top5:
        print(f"    {km}: {cnt}")

    # Demonstrate for k=1 (nucleotide frequencies)
    print(f"\nNucleotide composition (k=1):")
    comp1 = kmer_composition(dna, 1)
    for nt, cnt in zip(all_kmers(1), comp1):
        print(f"  {nt}: {cnt}")

    # all_kmers examples
    print(f"\nFirst 8 of {len(all_kmers(k))} 4-mers in lex order:")
    print("  " + ", ".join(all_kmers(k)[:8]))

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Sliding window over dna yields len(dna) − k + 1 overlapping k-mers")
    print("✓ Total possible k-mers over ACGT = 4^k (exponential in k)")
    print("✓ k-mer composition is a fixed-length vector: easy to compare sequences")
    print("✓ itertools.product generates the Cartesian product for lex enumeration")
    print("✓ Larger k → sparser composition, more discriminative but higher memory")
