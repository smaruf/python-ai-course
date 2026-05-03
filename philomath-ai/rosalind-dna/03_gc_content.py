"""
GC: Computing GC Content
=========================

Rosalind Problem: https://rosalind.info/problems/gc/
Sessions 1–2 of the Philomath live problem-solving series.

Background
----------
The **GC content** of a DNA sequence is the fraction of bases that are
either Guanine (G) or Cytosine (C).  Because G–C base pairs are held
together by three hydrogen bonds (versus only two for A–T pairs), sequences
with higher GC content are thermodynamically more stable.

GC content varies widely across the tree of life:
  • Human genome:           ~41 %
  • E. coli genome:         ~51 %
  • Thermophilic bacteria:  up to ~75 % (stability at high temperatures)

In the Rosalind problem we are given multiple DNA sequences in FASTA format
and must identify the one with the highest GC content — a common task in
species identification and metagenomic analysis.

FASTA format
------------
Each record starts with a header line beginning with '>':

    >Rosalind_6404
    CCTGCGGAAGATCGGCACTAGAATAGCCAGAACCGTTTCTCTGAGTTTACGCTTT
    >Rosalind_5959
    CCATCGGTAGCGCATCCTTAGTCCAATTAAGTCCCTATCCAGGCGCTCCGCCGAAGGTCTATATCCATTT

A sequence may span multiple lines; only the header line begins with '>'.

Problem Statement
-----------------
Given:  At most 10 DNA strings in FASTA format (each of length at most 1000).

Return: The ID of the string with the highest GC content, followed by the
        GC content expressed as a percentage (to six decimal places).

Learning Objectives
-------------------
- Parse FASTA-formatted text into labelled sequences
- Compute GC content as a fraction and a percentage
- Use Python's max() with a key function
- Understand GC content as a biologically meaningful sequence statistic
"""


def gc_content(dna: str) -> float:
    """
    Compute the GC content of a DNA string as a fraction (0.0 to 1.0).

    GC content = (number of G's + number of C's) / total length

    Args:
        dna: A non-empty string over the alphabet {A, C, G, T}.

    Returns:
        A float in [0.0, 1.0] representing the fraction of G/C bases.

    Raises:
        ValueError: If dna is empty (GC content is undefined for empty string).

    Examples:
        >>> gc_content("GGCC")
        1.0

        >>> gc_content("AATT")
        0.0

        >>> gc_content("ACGT")
        0.5

        >>> round(gc_content("AGCTATAG"), 4)
        0.375
    """
    if not dna:
        raise ValueError("GC content is undefined for an empty sequence.")
    gc = sum(1 for base in dna if base in ('G', 'C'))
    return gc / len(dna)


def parse_fasta(text: str) -> dict:
    """
    Parse a FASTA-formatted string into a mapping of label to sequence.

    Handles multi-line sequences: all non-header lines belonging to a record
    are concatenated.

    Args:
        text: A string in FASTA format. Header lines start with '>'.
              Whitespace-only lines are ignored.

    Returns:
        An ordered dict mapping each sequence label (without the leading '>')
        to its full DNA sequence string (all lines concatenated, no spaces).

    Examples:
        >>> parse_fasta(">seq1\\nACGT\\n>seq2\\nTTTT")
        {'seq1': 'ACGT', 'seq2': 'TTTT'}

        >>> parse_fasta(">seq1\\nAC\\nGT\\nAC")
        {'seq1': 'ACGTAC'}
    """
    sequences = {}
    current_label = None
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            current_label = line[1:].split()[0]
            sequences[current_label] = ''
        elif current_label is not None:
            sequences[current_label] += line
    return sequences


def highest_gc(fasta_text: str) -> tuple:
    """
    Find the FASTA record with the highest GC content.

    Args:
        fasta_text: A string in FASTA format containing one or more records.

    Returns:
        A tuple (label, gc_percentage) where:
          - label is the sequence ID (string)
          - gc_percentage is the GC content expressed as a percentage float
            (i.e., fraction × 100)

    Examples:
        >>> label, pct = highest_gc(">A\\nGGGG\\n>B\\nAAAA")
        >>> label
        'A'
        >>> pct
        100.0

        >>> label, pct = highest_gc(">A\\nAAAA\\n>B\\nGCGC")
        >>> label
        'B'
        >>> pct
        100.0
    """
    sequences = parse_fasta(fasta_text)
    best_label = max(sequences, key=lambda lbl: gc_content(sequences[lbl]))
    best_pct = gc_content(sequences[best_label]) * 100
    return best_label, best_pct


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("GC: COMPUTING GC CONTENT")
    print("=" * 70)

    # Rosalind sample dataset
    sample_fasta = """\
>Rosalind_6404
CCTGCGGAAGATCGGCACTAGAATAGCCAGAACCGTTTCTCTGAGTTTACGCTTT
>Rosalind_5959
CCATCGGTAGCGCATCCTTAGTCCAATTAAGTCCCTATCCAGGCGCTCCGCCGAAGGTCTATATCCATTT
>Rosalind_0808
CCACCCTCGTGGTATGGCTAGGCATTCAGGAACCGGAGAACGCTTCAGACCAGCCCGGACTGGGAACCTGCGGGCAGTAGGTGGAAT
"""

    label, pct = highest_gc(sample_fasta)
    print(f"\nSample dataset result:")
    print(f"  Winner:   {label}")
    print(f"  GC:       {pct:.6f}%")
    print(f"  Expected: Rosalind_0808 with ~60.919540%")

    # Per-record breakdown
    print("\nPer-record GC content:")
    sequences = parse_fasta(sample_fasta)
    for lbl, seq in sequences.items():
        pct_i = gc_content(seq) * 100
        print(f"  {lbl}: {pct_i:.6f}%  (length {len(seq)})")

    # gc_content edge cases
    print("\ngc_content examples:")
    print(f"  GGCC  → {gc_content('GGCC'):.1f}  (all GC)")
    print(f"  AATT  → {gc_content('AATT'):.1f}  (no GC)")
    print(f"  ACGT  → {gc_content('ACGT'):.1f}  (half GC)")

    # FASTA parser multi-line
    multi = ">myseq\nACGT\nACGT\nACGT"
    parsed = parse_fasta(multi)
    print(f"\nMulti-line FASTA: {parsed}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ GC content = (G + C) / length — a fundamental sequence statistic")
    print("✓ Higher GC → more thermodynamic stability (3 H-bonds vs 2 for AT)")
    print("✓ FASTA: header line starts with '>', sequence may span multiple lines")
    print("✓ Use max(dict, key=func) to find the record with the highest value")
