"""
DNA: Counting DNA Nucleotides
=============================

Rosalind Problem: https://rosalind.info/problems/dna/
Sessions 1–2 of the Philomath live problem-solving series.

Background
----------
DNA (deoxyribonucleic acid) is the molecule that carries genetic information
in all living organisms.  It is composed of four types of nucleotide bases:

  • Adenine  (A)
  • Cytosine (C)
  • Guanine  (G)
  • Thymine  (T)

Each single strand of DNA can be represented as a string over the alphabet
{A, C, G, T}.  Counting the frequency of each nucleotide is often the very
first step in any bioinformatics pipeline — it gives us a coarse fingerprint
of a sequence and is the basis of GC-content analysis, quality control, and
more.

Problem Statement
-----------------
Given:  A DNA string s of length at most 1000 nucleotides.

Return: Four integers (separated by spaces) counting the number of times
        that the symbols A, C, G, and T each occur in s.

Learning Objectives
-------------------
- Represent a DNA sequence as a Python string
- Use a dictionary to accumulate per-character counts
- Understand nucleotide composition as a simple sequence statistic
- Produce formatted output matching the Rosalind expected answer format
"""


def count_nucleotides(dna: str) -> dict:
    """
    Count occurrences of each DNA nucleotide in the given string.

    Args:
        dna: A string consisting of characters from the alphabet {A, C, G, T}.
             May be empty.

    Returns:
        A dict with keys 'A', 'C', 'G', 'T' mapping to their integer counts.

    Examples:
        >>> count_nucleotides("AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC")
        {'A': 20, 'C': 12, 'G': 17, 'T': 21}

        >>> count_nucleotides("AAAA")
        {'A': 4, 'C': 0, 'G': 0, 'T': 0}

        >>> count_nucleotides("")
        {'A': 0, 'C': 0, 'G': 0, 'T': 0}
    """
    counts = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
    for base in dna:
        if base in counts:
            counts[base] += 1
    return counts


def format_counts(counts: dict) -> str:
    """
    Format nucleotide counts as a space-separated string in A C G T order.

    This matches the output format expected by the Rosalind grader.

    Args:
        counts: A dict with keys 'A', 'C', 'G', 'T' and integer values,
                as returned by count_nucleotides().

    Returns:
        A string of four integers separated by single spaces, ordered A C G T.

    Examples:
        >>> format_counts({'A': 20, 'C': 12, 'G': 17, 'T': 21})
        '20 12 17 21'

        >>> format_counts({'A': 0, 'C': 0, 'G': 0, 'T': 0})
        '0 0 0 0'
    """
    return f"{counts['A']} {counts['C']} {counts['G']} {counts['T']}"


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("DNA: COUNTING DNA NUCLEOTIDES")
    print("=" * 70)

    # Rosalind sample dataset
    sample = "AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC"
    counts = count_nucleotides(sample)
    result = format_counts(counts)
    print(f"\nSample dataset:")
    print(f"  Input:    {sample}")
    print(f"  Output:   {result}")
    print(f"  Expected: 20 12 17 21")

    # Individual counts
    print("\nBreakdown:")
    for base in "ACGT":
        print(f"  {base}: {counts[base]}")

    # Edge cases
    print("\nEdge cases:")
    print(f"  Empty string:      '{format_counts(count_nucleotides(''))}'  (expect '0 0 0 0')")
    print(f"  All A's (AAAA):    '{format_counts(count_nucleotides('AAAA'))}'  (expect '4 0 0 0')")
    print(f"  Single G:          '{format_counts(count_nucleotides('G'))}'  (expect '0 0 1 0')")
    print(f"  ACGT:              '{format_counts(count_nucleotides('ACGT'))}'  (expect '1 1 1 1')")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ DNA uses four bases: A (Adenine), C (Cytosine), G (Guanine), T (Thymine)")
    print("✓ A dict with fixed keys is the natural Python structure for base counts")
    print("✓ Output order is always A C G T (alphabetical)")
    print("✓ Base counting is O(n) — one pass through the string")
