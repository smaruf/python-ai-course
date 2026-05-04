"""
CORR: Error Correction in Reads
================================

Rosalind Problem: https://rosalind.info/problems/corr/

Background
----------
High-throughput sequencers produce millions of short reads but with a
non-trivial per-base error rate (~0.1–1 %).  Before assembly, erroneous
reads must be identified and corrected — otherwise assemblers produce
fragmented or incorrect contigs.

A simple statistical approach exploits coverage:

  • In a deep sequencing experiment, the true sequence appears many times.
  • A read containing a sequencing error typically appears only ONCE,
    because the exact error is unlikely to recur.

So reads that appear (or whose reverse complement appears) at least twice
are "trusted"; reads appearing only once are candidates for correction.

Correction Strategy
-------------------
For each suspected erroneous read r:
  1. Find a trusted read c (or its reverse complement) that differs from r
     by exactly one substitution (Hamming distance = 1).
  2. Replace r with c (or the appropriate reverse-complement form).

The problem guarantees each erroneous read has a unique correction.

Reverse Complement
------------------
DNA is double-stranded, so a read could be sequenced from either strand.
When checking for duplicates and corrections, we treat a read and its
reverse complement as equivalent representations of the same genomic locus.

Problem Statement
-----------------
Given:  A FASTA collection of DNA reads (all the same length, ≤ 1 Mbp total).

Return: A list of all corrections in the form  [erroneous]->[corrected]
        for each read that is erroneous and correctable.

Learning Objectives
-------------------
- Understand sequencing error models and coverage-based quality assessment
- Implement reverse complement for double-stranded DNA read matching
- Use Hamming distance to identify single-substitution errors
- Build a trusted-read dictionary to correct erroneous sequencing reads
"""

from collections import Counter


def reverse_complement(dna: str) -> str:
    """
    Return the reverse complement of a DNA string.

    Each base is complemented (A↔T, C↔G) and the resulting string is
    reversed, reflecting the antiparallel orientation of the two DNA strands.

    Args:
        dna: A string of uppercase DNA bases (A, T, C, G).

    Returns:
        Reverse complement of *dna*.

    Examples:
        >>> reverse_complement("AAAACCCGGT")
        'ACCGGGTTTT'

        >>> reverse_complement("ATCG")
        'CGAT'

        >>> reverse_complement("AAAA")
        'TTTT'
    """
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    return ''.join(complement[base] for base in reversed(dna))


def hamming_distance(s: str, t: str) -> int:
    """
    Compute the Hamming distance between two equal-length strings.

    The Hamming distance counts the number of positions at which the
    corresponding characters differ.

    Args:
        s: First string.
        t: Second string (must have the same length as *s*).

    Returns:
        Number of positions where s and t differ.

    Examples:
        >>> hamming_distance("ACGT", "ACGT")
        0

        >>> hamming_distance("ACGT", "ACGG")
        1

        >>> hamming_distance("AAAA", "TTTT")
        4
    """
    return sum(a != b for a, b in zip(s, t))


def find_correct_reads(sequences: list) -> set:
    """
    Identify the set of trusted (correct) read sequences.

    A read is considered correct if it OR its reverse complement appears at
    least twice in the collection.  Both the read and its reverse complement
    are added to the trusted set so that downstream correction checks can
    work in a single pass.

    Args:
        sequences: List of DNA read strings (duplicates allowed).

    Returns:
        Set of sequences considered correct (includes reverse complements of
        reads that appear ≥ 2 times).

    Examples:
        >>> seqs = ["GCTA", "GCTA", "TTTT"]
        >>> sorted(find_correct_reads(seqs))
        ['GCTA', 'TAGC']

        >>> seqs = ["ATCG", "CGAT", "GGGG"]
        >>> len(find_correct_reads(seqs))  # each appears once, no duplicates
        0
    """
    counts = Counter(sequences)
    correct = set()

    for seq in counts:
        rc = reverse_complement(seq)
        if counts[seq] >= 2 or counts.get(rc, 0) >= 2:
            correct.add(seq)
            correct.add(rc)

    return correct


def correct_errors(sequences: list) -> list:
    """
    Find and correct all erroneous reads in a sequencing dataset.

    A read is erroneous if it is not in the trusted set (see
    ``find_correct_reads``).  Each erroneous read is corrected by finding the
    unique trusted read within Hamming distance 1.

    The search checks both direct matches (HD(r, c) = 1) and reverse-
    complement matches (HD(RC(r), c) = 1, yielding correction r → RC(c)).
    Because ``find_correct_reads`` includes reverse complements in the
    trusted set, both cases are resolved in a single pass over that set.

    Reads with no correction within Hamming distance 1 are silently skipped
    (the problem guarantees this does not occur for valid inputs).

    Args:
        sequences: List of DNA read strings (duplicates allowed).

    Returns:
        List of (erroneous_read, corrected_read) tuples, one entry per
        unique erroneous read that can be corrected, in order of first
        appearance.

    Examples:
        >>> reads = ["ACGT", "ACGT", "ACGG"]
        >>> correct_errors(reads)
        [('ACGG', 'ACGT')]

        >>> reads = ["TGCCA", "TGCCA", "TGCCT"]
        >>> correct_errors(reads)
        [('TGCCT', 'TGCCA')]
    """
    correct = find_correct_reads(sequences)
    corrections = []
    processed = set()

    for read in sequences:
        if read in correct or read in processed:
            continue
        processed.add(read)

        corrected = None

        # Direct check: find a trusted read within Hamming distance 1
        # (this also covers RC-based corrections because find_correct_reads
        #  adds both a read and its RC to the trusted set)
        for c in correct:
            if hamming_distance(read, c) == 1:
                corrected = c
                break

        if corrected is not None:
            corrections.append((read, corrected))

    return corrections


def parse_fasta(text: str) -> list:
    """
    Parse a FASTA-formatted string and return an ordered list of sequences.

    Preserves duplicates so that read counts can be computed downstream.
    Multi-line sequences are concatenated.

    Args:
        text: A string in FASTA format.

    Returns:
        List of sequence strings (preserving duplicates and order).

    Examples:
        >>> fasta = ">r1\\nTCATC\\n>r2\\nTTCAT\\n>r3\\nTCATC"
        >>> parse_fasta(fasta)
        ['TCATC', 'TTCAT', 'TCATC']

        >>> fasta = ">id1\\nACG\\nTAC"
        >>> parse_fasta(fasta)
        ['ACGTAC']
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
    print("CORR: ERROR CORRECTION IN READS")
    print("=" * 70)

    # Rosalind sample dataset
    sample_fasta = """\
>Rosalind_52
TCATC
>Rosalind_44
TTCAT
>Rosalind_68
TCATC
>Rosalind_28
TGAAA
>Rosalind_95
GAGGT
>Rosalind_75
TTTCC
>Rosalind_21
ATCAA
>Rosalind_54
TTGAT
>Rosalind_34
TTTCC
"""
    reads = parse_fasta(sample_fasta)
    print(f"\nInput reads ({len(reads)} total):")
    from collections import Counter
    for seq, cnt in sorted(Counter(reads).items()):
        print(f"  {seq}  ×{cnt}")

    # Identify trusted reads
    correct = find_correct_reads(reads)
    print(f"\nTrusted reads (appear ≥2 times, or RC does): {sorted(correct)}")

    # Show erroneous reads
    erroneous = [r for r in reads if r not in correct]
    print(f"\nErroneous reads (appear once, RC also once): {sorted(set(erroneous))}")

    # Apply corrections
    corrections = correct_errors(reads)
    print(f"\nCorrections found:")
    if corrections:
        for orig, fixed in corrections:
            diff_pos = [i for i, (a, b) in enumerate(zip(orig, fixed)) if a != b]
            print(f"  {orig} -> {fixed}  (position {diff_pos[0]}: {orig[diff_pos[0]]}→{fixed[diff_pos[0]]})")
    else:
        print("  (none in this sample)")

    # Demonstrate reverse complement
    print("\nReverse complement examples:")
    for seq in ["TCATC", "TTTCC", "ATCG"]:
        print(f"  RC({seq}) = {reverse_complement(seq)}")

    # Hamming distance demo
    print("\nHamming distance examples:")
    pairs = [("TGAAA", "GGAAA"), ("ACGT", "ACGG"), ("TTCAT", "TCATC")]
    for s, t in pairs:
        print(f"  HD({s}, {t}) = {hamming_distance(s, t)}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Trusted reads: appear ≥2 times OR their reverse complement does")
    print("✓ Erroneous reads: appear once and have no such duplicate")
    print("✓ Correction: change the one wrong base (Hamming distance = 1)")
    print("✓ Double-stranded DNA: always check both read AND its reverse complement")
    print("✓ Coverage depth is the foundation of statistical error correction")
