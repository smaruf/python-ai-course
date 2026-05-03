"""
REVC: Complementing a Strand of DNA
=====================================

Rosalind Problem: https://rosalind.info/problems/revc/
Sessions 1–2 of the Philomath live problem-solving series.

Background
----------
DNA exists as a double helix: two complementary strands wound around each
other.  The strands are antiparallel — they run in opposite directions
(5' → 3' and 3' → 5').

Watson-Crick base pairing rules dictate which bases pair with which:

  A  ↔  T   (Adenine pairs with Thymine)
  C  ↔  G   (Cytosine pairs with Guanine)

The **complement** of a strand replaces each base with its Watson-Crick
partner.  Because the complementary strand runs in the opposite direction,
we also **reverse** it to describe it in the conventional 5' → 3' direction.
The result is the **reverse complement**.

Example (5'→3'):
  Original:          5'-AAAACCCGGT-3'
  Complement:        3'-TTTTGGGCCA-5'
  Reverse complement:5'-ACCGGGTTTT-3'

Reverse complements appear throughout bioinformatics:
  • Both strands of a chromosome are searched for genes
  • Restriction sites are often palindromes (equal to their reverse complement)
  • PCR primer design requires computing reverse complements

Problem Statement
-----------------
Given:  A DNA string s of length at most 1000 nucleotides.

Return: The reverse complement of s.

Learning Objectives
-------------------
- Understand antiparallel DNA strand structure
- Apply Watson-Crick base pairing rules
- Implement string reversal and per-character mapping in Python
- Recognise reverse complement palindromes in biology
"""


def complement(base: str) -> str:
    """
    Return the Watson-Crick complement of a single DNA nucleotide.

    Pairing rules:
      A ↔ T,  C ↔ G

    Args:
        base: A single uppercase character — one of 'A', 'C', 'G', 'T'.

    Returns:
        The complementary nucleotide as an uppercase character.

    Raises:
        ValueError: If base is not one of the four standard DNA nucleotides.

    Examples:
        >>> complement('A')
        'T'

        >>> complement('T')
        'A'

        >>> complement('C')
        'G'

        >>> complement('G')
        'C'
    """
    pairs = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    if base not in pairs:
        raise ValueError(f"Invalid nucleotide: '{base}'. Expected one of A, C, G, T.")
    return pairs[base]


def reverse_complement(dna: str) -> str:
    """
    Compute the reverse complement of a DNA string.

    Steps:
      1. Complement each nucleotide (A↔T, C↔G).
      2. Reverse the resulting string (to account for antiparallel orientation).

    Args:
        dna: A string over the alphabet {A, C, G, T}.
             May be empty.

    Returns:
        The reverse complement of dna as an uppercase string.

    Examples:
        >>> reverse_complement("AAAACCCGGT")
        'ACCGGGTTTT'

        >>> reverse_complement("A")
        'T'

        >>> reverse_complement("ACGT")
        'ACGT'

        >>> reverse_complement("")
        ''
    """
    return ''.join(complement(base) for base in reversed(dna))


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("REVC: REVERSE COMPLEMENT OF A DNA STRAND")
    print("=" * 70)

    # Rosalind sample dataset
    sample = "AAAACCCGGT"
    result = reverse_complement(sample)
    print(f"\nSample dataset:")
    print(f"  Input:    5'-{sample}-3'")
    print(f"  RevComp:  5'-{result}-3'")
    print(f"  Expected: ACCGGGTTTT")

    # Step-by-step illustration
    print("\nStep-by-step:")
    complemented = ''.join(complement(b) for b in sample)
    print(f"  Original:      5'-{sample}-3'")
    print(f"  Complement:    3'-{complemented}-5'")
    print(f"  Rev. comp.:    5'-{complemented[::-1]}-3'")

    # Palindrome example (EcoRI recognition site)
    ecori = "GAATTC"
    print(f"\nPalindrome example (EcoRI site):")
    print(f"  {ecori} → reverse complement: {reverse_complement(ecori)}")
    print(f"  (A palindrome equals its own reverse complement)")

    # Edge cases
    print("\nEdge cases:")
    print(f"  Single A:      {reverse_complement('A')!r}  (expect 'T')")
    print(f"  Empty string:  {reverse_complement('')!r}   (expect '')")
    print(f"  ACGT:          {reverse_complement('ACGT')!r}  (expect 'ACGT' — palindrome)")

    # Individual complements
    print("\nWatson-Crick pairs:")
    for base in "ACGT":
        print(f"  {base} ↔ {complement(base)}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Complement rules: A↔T and C↔G (Watson-Crick base pairing)")
    print("✓ Reverse complement = complement then reverse (antiparallel strands)")
    print("✓ Palindromes: sequences equal to their own reverse complement")
    print("✓ Both DNA strands are biologically active — search both for features")
