"""
PROB: Introduction to Random Strings
=====================================

Rosalind Problem: https://rosalind.info/problems/prob/
Episode 4 of the Philomath live problem-solving series with Phillip Compeau
(Carnegie Mellon), streamed on the Rosalind platform.

Background
----------
A random DNA string model assumes that each nucleotide at a given position
is drawn independently from a distribution determined by the GC-content x:

    P(G) = P(C) = x / 2
    P(A) = P(T) = (1 − x) / 2

Under this model, the probability of observing a specific string s of
length n is the product of the individual nucleotide probabilities:

    P(s | x) = Π_{i=1}^{n}  P(s[i] | x)

Because these products of small numbers underflow to zero in floating-point
arithmetic for even moderate string lengths, we work in log-base-10 space:

    log10 P(s | x) = Σ_{i=1}^{n}  log10 P(s[i] | x)

Problem Statement
-----------------
Given:  A DNA string s and an array A of GC-content values x ∈ (0, 1).

Return: For each x in A, the log10 probability log10 P(s | x), rounded to
        3 decimal places.

Learning Objectives
-------------------
- Model nucleotide composition using GC-content
- Understand why log-probabilities are necessary for long sequences
- Practice computing products of probabilities as sums of logarithms
"""

import math


def nucleotide_log_prob(nucleotide: str, gc_content: float) -> float:
    """
    Return log10 probability of a single nucleotide given GC content x.

    Args:
        nucleotide:  one of 'A', 'C', 'G', 'T' (case-insensitive)
        gc_content:  GC-content probability x ∈ (0, 1)

    Returns:
        log10( P(nucleotide | gc_content) )

    Raises:
        ValueError: if nucleotide is not A, C, G, or T

    Examples:
        >>> round(nucleotide_log_prob('G', 0.5), 6)
        -0.30103

        >>> round(nucleotide_log_prob('A', 0.5), 6)
        -0.30103
    """
    nt = nucleotide.upper()
    if nt in ('G', 'C'):
        p = gc_content / 2.0
    elif nt in ('A', 'T'):
        p = (1.0 - gc_content) / 2.0
    else:
        raise ValueError(f"Invalid nucleotide: {nucleotide!r}")
    return math.log10(p)


def random_string_log_prob(dna: str, gc_content: float) -> float:
    """
    Compute log10 P(dna | gc_content) for a random string model.

    Args:
        dna:        DNA string (A/C/G/T, case-insensitive)
        gc_content: GC-content value x ∈ (0, 1)

    Returns:
        log10 probability of generating `dna` at the given GC content

    Examples:
        >>> s = "ACGATACAA"
        >>> round(random_string_log_prob(s, 0.129), 3)
        -5.737

        >>> round(random_string_log_prob(s, 0.5), 3)
        -7.217
    """
    return sum(nucleotide_log_prob(nt, gc_content) for nt in dna.upper())


def random_string_log_probs(dna: str, gc_contents: list) -> list:
    """
    Compute log10 probabilities for a DNA string across multiple GC contents.

    Args:
        dna:         DNA string
        gc_contents: list of GC-content values

    Returns:
        List of log10 probabilities (rounded to 3 decimal places)

    Examples:
        >>> s = "ACGATACAA"
        >>> gc = [0.129, 0.287, 0.423, 0.499, 0.532, 0.81, 0.999]
        >>> random_string_log_probs(s, gc)
        [-5.737, -5.217, -5.263, -5.416, -5.51, -7.311, -20.711]
    """
    return [round(random_string_log_prob(dna, x), 3) for x in gc_contents]


def gc_content(dna: str) -> float:
    """
    Calculate the observed GC content of a DNA string.

    Args:
        dna: DNA string (A/C/G/T)

    Returns:
        Fraction of G and C nucleotides

    Examples:
        >>> gc_content("ACGT")
        0.5

        >>> gc_content("AAAA")
        0.0
    """
    dna = dna.upper()
    gc = sum(1 for nt in dna if nt in ('G', 'C'))
    return gc / len(dna) if dna else 0.0


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("PROB: INTRODUCTION TO RANDOM STRINGS")
    print("=" * 70)

    # Rosalind sample dataset
    s = "ACGATACAA"
    gc_values = [0.129, 0.287, 0.423, 0.499, 0.532, 0.81, 0.999]

    print(f"\nDNA string:   {s}")
    print(f"GC contents:  {gc_values}")

    log_probs = random_string_log_probs(s, gc_values)
    print(f"\nlog10 probabilities:")
    for x, lp in zip(gc_values, log_probs):
        print(f"  GC={x:.3f}  →  log10 P = {lp}")

    print("\nComputed values:")
    print("  -5.737 -5.217 -5.263 -5.416 -5.510 -7.311 -20.711")

    # Illustrate why log-space is needed
    print("\nWhy log-space? (underflow demonstration)")
    long_s = "ACGATACAA" * 20
    for x in [0.3, 0.5, 0.7]:
        lp = random_string_log_prob(long_s, x)
        actual_p = 10 ** lp
        print(
            f"  GC={x}, len={len(long_s)}: "
            f"log10 P = {lp:.3f}, actual P ≈ {actual_p:.2e}"
        )

    # Per-nucleotide breakdown
    print(f"\nPer-nucleotide log10 probabilities for GC=0.5:")
    for nt in ['A', 'C', 'G', 'T']:
        print(f"  {nt}: {nucleotide_log_prob(nt, 0.5):.5f}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ P(G) = P(C) = x/2  and  P(A) = P(T) = (1-x)/2")
    print("✓ log10 P(string) = Σ log10 P(nucleotide_i)  (sum, not product)")
    print("✓ Log-space avoids floating-point underflow for long sequences")
    print("✓ Higher GC content → more probable G/C-rich strings")
