"""
CONS: Consensus and Profile
============================

Rosalind Problem: https://rosalind.info/problems/cons/
Episode 4 of the Philomath live problem-solving series with Phillip Compeau
(Carnegie Mellon), streamed on the Rosalind platform.

Background
----------
A profile matrix summarises a collection of DNA strings (all the same length)
by counting, at each position, how many strings contain each nucleotide.

Given a collection of m strings each of length n, the profile matrix P is:

       position 1   position 2   …   position n
    A [  count     count        …   count      ]
    C [  count     count        …   count      ]
    G [  count     count        …   count      ]
    T [  count     count        …   count      ]

The consensus string is built by selecting, at each position, the nucleotide
with the highest count in the profile column.  When there is a tie the
convention used here (and common in bioinformatics) is to prefer in
alphabetical order: A > C > G > T.

Problem Statement
-----------------
Given:  A collection of at most 10 DNA strings of equal length in FASTA format.

Return:
  1. Consensus string
  2. Profile matrix with rows labelled A, C, G, T

Learning Objectives
-------------------
- Parse FASTA-formatted sequence data
- Build a frequency/profile matrix from aligned sequences
- Derive a consensus sequence from a profile matrix
- Understand conservation and variability in biological sequences
"""


def parse_fasta(fasta_text: str) -> dict:
    """
    Parse a FASTA-formatted string into an ordered dict {label: sequence}.

    Handles multi-line sequences.

    Args:
        fasta_text: FASTA string with one or more records

    Returns:
        dict mapping sequence label → sequence string (uppercase)

    Examples:
        >>> fa = ">seq1\\nACGT\\n>seq2\\nTGCA"
        >>> parse_fasta(fa)
        {'seq1': 'ACGT', 'seq2': 'TGCA'}
    """
    sequences = {}
    current_label = None
    current_seq = []

    for line in fasta_text.strip().splitlines():
        line = line.strip()
        if line.startswith('>'):
            if current_label is not None:
                sequences[current_label] = ''.join(current_seq).upper()
            current_label = line[1:].split()[0]  # take first word after '>'
            current_seq = []
        elif line:
            current_seq.append(line)

    if current_label is not None:
        sequences[current_label] = ''.join(current_seq).upper()

    return sequences


def build_profile(sequences: list) -> dict:
    """
    Build a profile matrix from a list of DNA strings of equal length.

    Args:
        sequences: list of DNA strings (all equal length, ACGT alphabet)

    Returns:
        dict with keys 'A', 'C', 'G', 'T', each mapping to a list of
        integer counts indexed by position.

    Raises:
        ValueError: if sequences are not all the same length

    Examples:
        >>> seqs = ["ATCGAT", "ATCGAT"]
        >>> profile = build_profile(seqs)
        >>> profile['A']
        [2, 0, 0, 0, 2, 0]
    """
    if not sequences:
        raise ValueError("Need at least one sequence to build a profile.")

    length = len(sequences[0])
    if any(len(s) != length for s in sequences):
        raise ValueError("All sequences must have the same length.")

    profile = {nt: [0] * length for nt in 'ACGT'}
    for seq in sequences:
        for i, nt in enumerate(seq.upper()):
            if nt in profile:
                profile[nt][i] += 1

    return profile


def consensus_string(profile: dict) -> str:
    """
    Derive the consensus string from a profile matrix.

    At each position, choose the nucleotide with the highest count.
    Ties are broken alphabetically (A > C > G > T).

    Args:
        profile: dict from build_profile()

    Returns:
        Consensus DNA string

    Examples:
        >>> profile = {'A': [5,1], 'C': [0,3], 'G': [0,2], 'T': [2,1]}
        >>> consensus_string(profile)
        'AC'
    """
    if not profile or not profile.get('A'):
        return ''

    length = len(profile['A'])
    consensus = []
    for i in range(length):
        # Iterate 'ACGT' in alphabetical order; Python's max returns the FIRST
        # maximum encountered, so ties are resolved as A > C > G > T.
        best_nt = 'A'
        best_count = profile['A'][i]
        for nt in 'CGT':
            if profile[nt][i] > best_count:
                best_count = profile[nt][i]
                best_nt = nt
        consensus.append(best_nt)
    return ''.join(consensus)


def format_profile(profile: dict) -> str:
    """
    Format a profile matrix as the Rosalind-style string output.

    Args:
        profile: dict from build_profile()

    Returns:
        Multi-line string, one row per nucleotide

    Examples:
        >>> profile = {'A': [1, 2], 'C': [0, 1], 'G': [2, 0], 'T': [0, 0]}
        >>> print(format_profile(profile))
        A: 1 2
        C: 0 1
        G: 2 0
        T: 0 0
    """
    lines = []
    for nt in 'ACGT':
        counts_str = ' '.join(str(c) for c in profile[nt])
        lines.append(f"{nt}: {counts_str}")
    return '\n'.join(lines)


def consensus_and_profile(fasta_text: str) -> tuple:
    """
    Full pipeline: parse FASTA → profile → consensus.

    Args:
        fasta_text: FASTA-formatted string

    Returns:
        (consensus_str, profile_dict)
    """
    sequences_dict = parse_fasta(fasta_text)
    seqs = list(sequences_dict.values())
    profile = build_profile(seqs)
    consensus = consensus_string(profile)
    return consensus, profile


# ── Demo ──────────────────────────────────────────────────────────────────────

SAMPLE_FASTA = """\
>Rosalind_1
ATCCAGCT
>Rosalind_2
GGGCAACT
>Rosalind_3
ATGGATCT
>Rosalind_4
AAGCAACC
>Rosalind_5
TTGGAACT
>Rosalind_6
ATGCCATT
>Rosalind_7
ATGGCACT
"""

if __name__ == "__main__":
    print("=" * 70)
    print("CONS: CONSENSUS AND PROFILE")
    print("=" * 70)

    consensus, profile = consensus_and_profile(SAMPLE_FASTA)

    print("\nInput sequences:")
    for label, seq in parse_fasta(SAMPLE_FASTA).items():
        print(f"  {label}: {seq}")

    print(f"\nConsensus: {consensus}")
    print("\nProfile matrix:")
    print(format_profile(profile))

    print("\nRosalind expected output:")
    print("ATGCAACT")
    print("A: 5 1 0 0 5 5 0 0")
    print("C: 0 0 1 4 2 0 6 1")
    print("G: 1 1 6 3 0 1 0 0")
    print("T: 1 5 0 0 0 1 1 6")

    # Visualise conservation
    print("\nPosition conservation analysis:")
    seqs_list = list(parse_fasta(SAMPLE_FASTA).values())
    n = len(seqs_list)
    for i in range(len(consensus)):
        col_counts = {nt: profile[nt][i] for nt in 'ACGT'}
        most_common_count = max(col_counts.values())
        conservation = most_common_count / n * 100
        print(
            f"  pos {i+1}: {consensus[i]} "
            f"({conservation:.0f}% conserved)  {col_counts}"
        )

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Profile matrix: rows = A/C/G/T, columns = positions")
    print("✓ Consensus: most frequent nucleotide at each position")
    print("✓ Highly conserved positions → biologically important")
    print("✓ Profile matrices are used in motif finding and multiple alignment")
