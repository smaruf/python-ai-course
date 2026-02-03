"""
Sequence Alignment Algorithms
==============================

Sequence alignment is fundamental to bioinformatics, comparing DNA, RNA, or protein
sequences to identify regions of similarity that may indicate functional, structural,
or evolutionary relationships.

Biological Background:
---------------------
- Similar sequences often share common ancestry (homology)
- Mutations accumulate over evolutionary time (substitutions, insertions, deletions)
- Conserved regions indicate functional importance
- Alignment reveals evolutionary relationships and functional domains

Types of Alignment:
------------------
1. Global alignment (Needleman-Wunsch): Align entire sequences end-to-end
   - Best for sequences of similar length
   - Example: Comparing orthologous genes from different species

2. Local alignment (Smith-Waterman): Find best matching subsequences
   - Best for finding conserved domains in divergent sequences
   - Example: Finding conserved protein motifs

3. Longest Common Subsequence (LCS): Find longest shared subsequence
   - Characters must appear in same order but not necessarily consecutive
   - Example: Finding conserved gene order

Learning Objectives:
-------------------
- Implement dynamic programming algorithms
- Understand scoring matrices and gap penalties
- Apply alignment to biological problems
- Visualize alignment results
- Interpret biological significance of alignments
"""

from typing import List, Tuple, Optional, Dict
import sys


def global_alignment(seq1: str, seq2: str, match: int = 1, mismatch: int = -1, gap: int = -2) -> Tuple[int, str, str]:
    """
    Perform global sequence alignment using Needleman-Wunsch algorithm.
    
    Global alignment aligns two sequences from end to end, finding the best
    overall alignment even if parts align poorly. Uses dynamic programming.
    
    Algorithm:
    1. Create scoring matrix (m+1 x n+1)
    2. Initialize first row/column with gap penalties
    3. Fill matrix using recurrence relation
    4. Traceback to reconstruct alignment
    
    Time Complexity: O(m * n) where m, n are sequence lengths
    Space Complexity: O(m * n)
    
    Args:
        seq1: First sequence
        seq2: Second sequence
        match: Score for matching characters (default: 1)
        mismatch: Penalty for mismatched characters (default: -1)
        gap: Penalty for gaps (default: -2)
    
    Returns:
        Tuple of (score, aligned_seq1, aligned_seq2)
    
    Example:
        >>> score, align1, align2 = global_alignment("GATTACA", "GCATGCU")
        >>> score
        0
        >>> align1
        'G-ATTACA'
        >>> align2
        'GCA-TGCU'
    
    Biological Example:
        Aligning orthologous genes from human and mouse:
        
        Human: ATCGATCG
        Mouse: ATCGATCG
        
        If highly conserved (score >> 0), likely functionally important.
        If poorly aligned (score << 0), may have diverged or are unrelated.
    """
    m, n = len(seq1), len(seq2)
    
    # Create scoring matrix
    # dp[i][j] = best score for aligning seq1[0:i] with seq2[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize first row and column (gaps)
    for i in range(m + 1):
        dp[i][0] = i * gap
    for j in range(n + 1):
        dp[0][j] = j * gap
    
    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # Match or mismatch
            if seq1[i-1] == seq2[j-1]:
                diag = dp[i-1][j-1] + match
            else:
                diag = dp[i-1][j-1] + mismatch
            
            # Gap in seq2
            from_top = dp[i-1][j] + gap
            
            # Gap in seq1
            from_left = dp[i][j-1] + gap
            
            # Take maximum
            dp[i][j] = max(diag, from_top, from_left)
    
    # Traceback to construct alignment
    aligned1, aligned2 = "", ""
    i, j = m, n
    
    while i > 0 or j > 0:
        current_score = dp[i][j] if i > 0 and j > 0 else float('-inf')
        
        # Check where we came from
        if i > 0 and j > 0:
            score_from_diag = dp[i-1][j-1]
            if seq1[i-1] == seq2[j-1]:
                score_from_diag += match
            else:
                score_from_diag += mismatch
            
            if dp[i][j] == score_from_diag:
                # Came from diagonal (match/mismatch)
                aligned1 = seq1[i-1] + aligned1
                aligned2 = seq2[j-1] + aligned2
                i -= 1
                j -= 1
                continue
        
        if i > 0 and dp[i][j] == dp[i-1][j] + gap:
            # Came from top (gap in seq2)
            aligned1 = seq1[i-1] + aligned1
            aligned2 = "-" + aligned2
            i -= 1
        elif j > 0:
            # Came from left (gap in seq1)
            aligned1 = "-" + aligned1
            aligned2 = seq2[j-1] + aligned2
            j -= 1
        else:
            break
    
    score = dp[m][n]
    return score, aligned1, aligned2


def local_alignment(seq1: str, seq2: str, match: int = 2, mismatch: int = -1, gap: int = -1) -> Tuple[int, str, str]:
    """
    Perform local sequence alignment using Smith-Waterman algorithm.
    
    Local alignment finds the best matching subsequences, ignoring poorly
    matching regions. Useful for finding conserved domains in divergent sequences.
    
    Key difference from global: negative scores are set to 0 (can start fresh).
    
    Time Complexity: O(m * n)
    Space Complexity: O(m * n)
    
    Args:
        seq1: First sequence
        seq2: Second sequence
        match: Score for matches (default: 2)
        mismatch: Penalty for mismatches (default: -1)
        gap: Penalty for gaps (default: -1)
    
    Returns:
        Tuple of (score, aligned_seq1, aligned_seq2)
    
    Example:
        >>> score, align1, align2 = local_alignment("ATCGATCG", "TCGAT")
        >>> "TCGAT" in align1 or "TCGAT" in align2
        True
    
    Biological Example:
        Finding conserved domain in proteins:
        
        Protein 1: MKATGEFSLKDWVPQRSTGAECL  (with signal peptide)
        Protein 2:     TGEFSLKDWVPQRS         (just the domain)
        
        Local alignment finds: TGEFSLKDWVPQRS (the conserved domain)
        Ignoring non-homologous regions on either end.
    """
    m, n = len(seq1), len(seq2)
    
    # Create scoring matrix
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # No initialization needed (first row/column stay 0)
    # Track maximum score position
    max_score = 0
    max_i, max_j = 0, 0
    
    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # Match or mismatch
            if seq1[i-1] == seq2[j-1]:
                diag = dp[i-1][j-1] + match
            else:
                diag = dp[i-1][j-1] + mismatch
            
            # Gap in seq2
            from_top = dp[i-1][j] + gap
            
            # Gap in seq1
            from_left = dp[i][j-1] + gap
            
            # Take maximum, but at least 0
            dp[i][j] = max(0, diag, from_top, from_left)
            
            # Track maximum
            if dp[i][j] > max_score:
                max_score = dp[i][j]
                max_i, max_j = i, j
    
    # Traceback from maximum score position
    aligned1, aligned2 = "", ""
    i, j = max_i, max_j
    
    while i > 0 and j > 0 and dp[i][j] > 0:
        # Check where we came from
        score_from_diag = dp[i-1][j-1]
        if seq1[i-1] == seq2[j-1]:
            score_from_diag += match
        else:
            score_from_diag += mismatch
        
        if dp[i][j] == score_from_diag:
            # Diagonal
            aligned1 = seq1[i-1] + aligned1
            aligned2 = seq2[j-1] + aligned2
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + gap:
            # Top
            aligned1 = seq1[i-1] + aligned1
            aligned2 = "-" + aligned2
            i -= 1
        elif j > 0:
            # Left
            aligned1 = "-" + aligned1
            aligned2 = seq2[j-1] + aligned2
            j -= 1
        else:
            break
    
    return max_score, aligned1, aligned2


def longest_common_subsequence(seq1: str, seq2: str) -> Tuple[int, str]:
    """
    Find the longest common subsequence (LCS) of two sequences.
    
    LCS is the longest sequence that appears in the same relative order
    in both sequences (but not necessarily consecutively).
    
    Unlike alignment, LCS doesn't use gaps - just finds matching characters.
    
    Time Complexity: O(m * n)
    Space Complexity: O(m * n)
    
    Args:
        seq1: First sequence
        seq2: Second sequence
    
    Returns:
        Tuple of (length, lcs_string)
    
    Example:
        >>> length, lcs = longest_common_subsequence("ABCDEFG", "BCDGK")
        >>> lcs
        'BCDG'
        >>> length
        4
    
    Biological Example:
        Finding conserved gene order:
        
        Species 1 genes: A-B-C-D-E-F-G
        Species 2 genes: B-C-D-G-K
        
        LCS: B-C-D-G (conserved synteny)
        
        This suggests these genes maintained their relative order
        despite insertions/deletions of other genes.
    """
    m, n = len(seq1), len(seq2)
    
    # Create DP table
    # dp[i][j] = length of LCS of seq1[0:i] and seq2[0:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill the table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                # Characters match, extend LCS
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                # No match, take best from removing one character
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Reconstruct LCS
    lcs = ""
    i, j = m, n
    
    while i > 0 and j > 0:
        if seq1[i-1] == seq2[j-1]:
            # Part of LCS
            lcs = seq1[i-1] + lcs
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    return dp[m][n], lcs


def edit_distance(seq1: str, seq2: str) -> int:
    """
    Calculate edit distance (Levenshtein distance) between two sequences.
    
    Edit distance is minimum number of operations (insert, delete, substitute)
    to transform one sequence into another.
    
    Time Complexity: O(m * n)
    Space Complexity: O(m * n)
    
    Args:
        seq1: First sequence
        seq2: Second sequence
    
    Returns:
        Minimum number of edits needed
    
    Example:
        >>> edit_distance("GCATGCU", "GATTACA")
        4
        >>> edit_distance("ATCG", "ATCG")
        0
    
    Biological Application:
        Measuring sequence divergence:
        - Low edit distance → closely related sequences
        - High edit distance → distantly related or unrelated
        
        Example: Comparing genes across species
        - Human-Chimp: small edit distance (recent common ancestor)
        - Human-Yeast: large edit distance (distant common ancestor)
    """
    m, n = len(seq1), len(seq2)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize: converting from/to empty string
    for i in range(m + 1):
        dp[i][0] = i  # Delete all characters
    for j in range(n + 1):
        dp[0][j] = j  # Insert all characters
    
    # Fill table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                # No operation needed
                dp[i][j] = dp[i-1][j-1]
            else:
                # Minimum of: insert, delete, substitute
                dp[i][j] = 1 + min(
                    dp[i][j-1],    # Insert
                    dp[i-1][j],    # Delete
                    dp[i-1][j-1]   # Substitute
                )
    
    return dp[m][n]


def print_alignment(seq1: str, seq2: str, aligned1: str, aligned2: str, score: int):
    """
    Pretty-print a sequence alignment.
    
    Args:
        seq1: Original sequence 1
        seq2: Original sequence 2
        aligned1: Aligned sequence 1 (with gaps)
        aligned2: Aligned sequence 2 (with gaps)
        score: Alignment score
    """
    print(f"Original sequences:")
    print(f"  Seq1: {seq1}")
    print(f"  Seq2: {seq2}")
    print(f"\nAlignment (score = {score}):")
    
    # Print in chunks of 60
    chunk_size = 60
    for i in range(0, len(aligned1), chunk_size):
        chunk1 = aligned1[i:i+chunk_size]
        chunk2 = aligned2[i:i+chunk_size]
        
        # Create match line
        match_line = ""
        for c1, c2 in zip(chunk1, chunk2):
            if c1 == c2:
                match_line += "|"  # Match
            elif c1 == "-" or c2 == "-":
                match_line += " "  # Gap
            else:
                match_line += "."  # Mismatch
        
        print(f"  {chunk1}")
        print(f"  {match_line}")
        print(f"  {chunk2}")
        print()


def alignment_statistics(aligned1: str, aligned2: str) -> Dict[str, int]:
    """
    Calculate statistics for an alignment.
    
    Args:
        aligned1: Aligned sequence 1
        aligned2: Aligned sequence 2
    
    Returns:
        Dictionary with statistics
    """
    matches = sum(1 for c1, c2 in zip(aligned1, aligned2) if c1 == c2 and c1 != "-")
    mismatches = sum(1 for c1, c2 in zip(aligned1, aligned2) if c1 != c2 and c1 != "-" and c2 != "-")
    gaps1 = aligned1.count("-")
    gaps2 = aligned2.count("-")
    
    total = len(aligned1)
    identity = (matches / total * 100) if total > 0 else 0
    
    return {
        'matches': matches,
        'mismatches': mismatches,
        'gaps1': gaps1,
        'gaps2': gaps2,
        'length': total,
        'identity_percent': identity
    }


# Example Usage and Testing
if __name__ == "__main__":
    print("=== Sequence Alignment Algorithms ===\n")
    
    # Example 1: Global Alignment
    print("Example 1: Global Alignment (Needleman-Wunsch)")
    print("-" * 70)
    seq1 = "GATTACA"
    seq2 = "GCATGCU"
    
    score, aligned1, aligned2 = global_alignment(seq1, seq2)
    print_alignment(seq1, seq2, aligned1, aligned2, score)
    
    stats = alignment_statistics(aligned1, aligned2)
    print(f"Statistics:")
    print(f"  Matches: {stats['matches']}")
    print(f"  Mismatches: {stats['mismatches']}")
    print(f"  Gaps: {stats['gaps1'] + stats['gaps2']}")
    print(f"  Identity: {stats['identity_percent']:.1f}%")
    
    # Example 2: Local Alignment
    print("\n\nExample 2: Local Alignment (Smith-Waterman)")
    print("-" * 70)
    seq1 = "ATCGATCGATCGATCG"
    seq2 = "TCGATCG"
    
    score, aligned1, aligned2 = local_alignment(seq1, seq2)
    print(f"Sequence 1: {seq1}")
    print(f"Sequence 2: {seq2}")
    print(f"\nBest local alignment (score = {score}):")
    print(f"  {aligned1}")
    print(f"  {aligned2}")
    
    # Example 3: Longest Common Subsequence
    print("\n\nExample 3: Longest Common Subsequence")
    print("-" * 70)
    seq1 = "ABCDEFG"
    seq2 = "BCDGK"
    
    length, lcs = longest_common_subsequence(seq1, seq2)
    print(f"Sequence 1: {seq1}")
    print(f"Sequence 2: {seq2}")
    print(f"\nLongest Common Subsequence: {lcs}")
    print(f"Length: {length}")
    
    # Example 4: Edit Distance
    print("\n\nExample 4: Edit Distance (Levenshtein)")
    print("-" * 70)
    pairs = [
        ("GCATGCU", "GATTACA"),
        ("ATCG", "ATCG"),
        ("AAAA", "TTTT"),
    ]
    
    for seq1, seq2 in pairs:
        dist = edit_distance(seq1, seq2)
        print(f"{seq1} → {seq2}: {dist} edits")
    
    # Example 5: Biological Example - Comparing Genes
    print("\n\nExample 5: Biological Example - Gene Comparison")
    print("-" * 70)
    # Simulating comparison of homologous genes
    human_gene = "ATGCGATCGATCGTAGCTAGCTAG"
    mouse_gene = "ATGCGATCGATAGCTAGCTAG"
    
    print("Human gene:", human_gene)
    print("Mouse gene:", mouse_gene)
    
    # Global alignment
    score, aligned1, aligned2 = global_alignment(human_gene, mouse_gene, match=2, mismatch=-1, gap=-2)
    print(f"\nGlobal alignment score: {score}")
    
    stats = alignment_statistics(aligned1, aligned2)
    print(f"Sequence identity: {stats['identity_percent']:.1f}%")
    
    if stats['identity_percent'] > 80:
        print("→ High similarity suggests recent common ancestor")
    elif stats['identity_percent'] > 50:
        print("→ Moderate similarity suggests conserved function")
    else:
        print("→ Low similarity suggests divergence or unrelated")
    
    # Edit distance
    dist = edit_distance(human_gene, mouse_gene)
    print(f"\nEdit distance: {dist}")
    print(f"Divergence rate: {dist/len(human_gene)*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("Sequence alignment complete!")
    print("=" * 70)
