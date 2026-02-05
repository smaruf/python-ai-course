"""
Motif Finding Algorithms - Discovering Regulatory Sequences
===========================================================

Motifs are short DNA sequences that appear repeatedly across different regions of DNA,
often with small variations. They typically represent binding sites for regulatory proteins
like transcription factors.

Biological Background:
---------------------
- Transcription factors (proteins) bind to specific DNA sequences to regulate gene expression
- These binding sites (motifs) are usually 8-20 base pairs long
- Motifs aren't exact matches - mutations create variations
- Finding conserved motifs helps identify regulatory elements

Problem:
--------
Given:
- A collection of DNA sequences (where we suspect motifs exist)
- Length k (motif length)
- Maximum distance d (allowed mismatches)

Find:
- Patterns that appear in all or most sequences
- The most likely regulatory motif

Learning Objectives:
-------------------
- Implement motif finding algorithms
- Understand profile matrices and scoring
- Work with probabilistic models
- Apply greedy algorithms to biological problems
- Handle approximate string matching
"""

from typing import List, Dict, Tuple, Set
from collections import defaultdict
import itertools


def hamming_distance(str1: str, str2: str) -> int:
    """
    Calculate Hamming distance between two strings.
    
    Hamming distance is the number of positions at which symbols differ.
    
    Time Complexity: O(n) where n is string length
    Space Complexity: O(1)
    
    Args:
        str1: First string
        str2: Second string
    
    Returns:
        Number of mismatches
    
    Example:
        >>> hamming_distance("GATTACA", "GCATGCU")
        4
    """
    if len(str1) != len(str2):
        raise ValueError("Strings must be same length")
    
    return sum(c1 != c2 for c1, c2 in zip(str1, str2))


def count_with_mismatches(text: str, pattern: str, d: int) -> int:
    """
    Count occurrences of pattern in text allowing up to d mismatches.
    
    Args:
        text: DNA sequence to search
        pattern: Pattern to find
        d: Maximum allowed mismatches
    
    Returns:
        Number of approximate matches
    
    Example:
        >>> count_with_mismatches("AACAAGCTGATAAACATTTAAAGAG", "AAAAA", 2)
        11
    """
    count = 0
    k = len(pattern)
    
    for i in range(len(text) - k + 1):
        kmer = text[i:i + k]
        if hamming_distance(kmer, pattern) <= d:
            count += 1
    
    return count


def find_motifs(dna_list: List[str], k: int, d: int) -> Set[str]:
    """
    Find all (k,d)-motifs: k-mers appearing in every sequence with at most d mismatches.
    
    A (k,d)-motif is a k-mer that appears in every DNA string with at most d mismatches.
    This is useful for finding regulatory elements that are conserved but not identical.
    
    Time Complexity: O(4^k * n * m * k) where n = number of sequences, m = sequence length
    Space Complexity: O(4^k)
    
    Args:
        dna_list: List of DNA sequences to search
        k: Length of motif
        d: Maximum allowed mismatches
    
    Returns:
        Set of all (k,d)-motifs
    
    Example:
        >>> dna = ["ATTTGGC", "TGCCTTA", "CGGTATC", "GAAAATT"]
        >>> motifs = find_motifs(dna, 3, 1)
        >>> "ATA" in motifs
        True
    """
    # Get all possible k-mers from first sequence
    first_seq = dna_list[0]
    candidate_motifs = set()
    
    # Generate all k-mers from first sequence and their d-neighbors
    for i in range(len(first_seq) - k + 1):
        kmer = first_seq[i:i + k]
        # Add the k-mer and all its neighbors within distance d
        neighbors = generate_neighbors(kmer, d)
        candidate_motifs.update(neighbors)
    
    # Check which candidates appear in all sequences
    motifs = set()
    for candidate in candidate_motifs:
        # Check if candidate appears in every sequence with at most d mismatches
        appears_in_all = all(
            count_with_mismatches(seq, candidate, d) > 0 
            for seq in dna_list
        )
        if appears_in_all:
            motifs.add(candidate)
    
    return motifs


def generate_neighbors(pattern: str, d: int) -> Set[str]:
    """
    Generate all strings within Hamming distance d from pattern.
    
    This creates all possible mutations of the pattern with up to d changes.
    
    Time Complexity: O(4^d * k) where k is pattern length
    Space Complexity: O(4^d)
    
    Args:
        pattern: DNA string
        d: Maximum Hamming distance
    
    Returns:
        Set of all d-neighbors
    
    Example:
        >>> neighbors = generate_neighbors("ACG", 1)
        >>> len(neighbors)
        10
        >>> "AAG" in neighbors
        True
    """
    if d == 0:
        return {pattern}
    
    if len(pattern) == 1:
        return {'A', 'C', 'G', 'T'}
    
    neighborhood = set()
    suffix_neighbors = generate_neighbors(pattern[1:], d)
    
    for suffix in suffix_neighbors:
        if hamming_distance(pattern[1:], suffix) < d:
            # We can change the first nucleotide
            for nucleotide in ['A', 'C', 'G', 'T']:
                neighborhood.add(nucleotide + suffix)
        else:
            # Must keep the first nucleotide
            neighborhood.add(pattern[0] + suffix)
    
    return neighborhood


def create_profile_matrix(motifs: List[str]) -> Dict[str, List[float]]:
    """
    Create a profile matrix from a list of motifs.
    
    A profile matrix shows the frequency of each nucleotide at each position.
    Uses Laplace's Rule of Succession (pseudocounts) to avoid zero probabilities.
    
    Args:
        motifs: List of aligned DNA sequences (all same length)
    
    Returns:
        Dictionary mapping nucleotides to frequency lists
    
    Example:
        >>> motifs = ["TCGGGG", "CCGGTG", "ACGGGG", "TTGGGG"]
        >>> profile = create_profile_matrix(motifs)
        >>> profile['G'][2]  # Frequency of G at position 2
        1.0
    """
    k = len(motifs[0])
    t = len(motifs)
    
    # Initialize with pseudocounts (Laplace's Rule)
    profile = {
        'A': [1.0] * k,
        'C': [1.0] * k,
        'G': [1.0] * k,
        'T': [1.0] * k
    }
    
    # Count nucleotides at each position
    for motif in motifs:
        for i, nucleotide in enumerate(motif):
            profile[nucleotide][i] += 1
    
    # Convert counts to probabilities
    for nucleotide in profile:
        profile[nucleotide] = [count / (t + 4) for count in profile[nucleotide]]
    
    return profile


def score_motifs(motifs: List[str]) -> int:
    """
    Calculate the score of a set of motifs.
    
    Score is the sum of mismatches at each position compared to consensus.
    Lower score is better (0 = perfect alignment).
    
    Args:
        motifs: List of aligned sequences
    
    Returns:
        Total mismatch count
    
    Example:
        >>> motifs = ["TCGGGG", "CCGGTG", "ACGGGG", "TTGGGG"]
        >>> score_motifs(motifs)
        3
    """
    k = len(motifs[0])
    t = len(motifs)
    score = 0
    
    for i in range(k):
        # Count nucleotides at position i
        counts = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
        for motif in motifs:
            counts[motif[i]] += 1
        
        # Most common nucleotide
        max_count = max(counts.values())
        # Add mismatches
        score += (t - max_count)
    
    return score


def profile_most_probable(text: str, k: int, profile: Dict[str, List[float]]) -> str:
    """
    Find the most probable k-mer in text based on profile matrix.
    
    Profile-based search uses probability model to find best matching k-mer.
    Probability of a k-mer = product of probabilities at each position.
    
    Args:
        text: DNA sequence to search
        k: Length of k-mer
        profile: Profile matrix (nucleotide -> probability list)
    
    Returns:
        Most probable k-mer
    
    Example:
        >>> text = "ACCTGTTTATTGCCTAAGTTCCGAACAAACCCAATATAGCCCGAGGGCCT"
        >>> profile = {'A': [0.2, 0.2, 0.0, 0.0, 0.0, 0.0, 0.9, 0.1, 0.1, 0.1, 0.3, 0.0],
        ...            'C': [0.1, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 0.1, 0.2, 0.4, 0.6],
        ...            'G': [0.0, 0.0, 1.0, 1.0, 0.9, 0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0],
        ...            'T': [0.7, 0.2, 0.0, 0.0, 0.1, 0.1, 0.0, 0.5, 0.8, 0.7, 0.3, 0.4]}
        >>> profile_most_probable(text, 12, profile)
        'CCGAACAAACCC'
    """
    max_probability = -1
    most_probable = text[:k]
    
    for i in range(len(text) - k + 1):
        kmer = text[i:i + k]
        probability = 1.0
        
        # Calculate probability of this k-mer
        for j, nucleotide in enumerate(kmer):
            probability *= profile[nucleotide][j]
        
        if probability > max_probability:
            max_probability = probability
            most_probable = kmer
    
    return most_probable


def greedy_motif_search(dna_list: List[str], k: int, t: int) -> List[str]:
    """
    Find motifs using greedy algorithm with profile matrices.
    
    Greedy approach:
    1. Try each k-mer from first sequence as starting point
    2. Build profile from current motifs
    3. Use profile to find best k-mer in next sequence
    4. Repeat for all sequences
    5. Keep best scoring set of motifs
    
    Time Complexity: O(n * m * k * t) where n = #sequences, m = sequence length
    Space Complexity: O(k * t)
    
    Args:
        dna_list: List of DNA sequences
        k: Motif length
        t: Number of sequences (usually len(dna_list))
    
    Returns:
        Best motifs found (one from each sequence)
    
    Example:
        >>> dna = ["GGCGTTCAGGCA", "AAGAATCAGTCA", "CAAGGAGTTCGC", "CACGTCAATCAC", "CAATAATATTCG"]
        >>> motifs = greedy_motif_search(dna, 3, 5)
        >>> score_motifs(motifs) < 10
        True
    """
    best_motifs = [seq[:k] for seq in dna_list]
    best_score = score_motifs(best_motifs)
    
    # Try each k-mer from first sequence
    for i in range(len(dna_list[0]) - k + 1):
        # Start with this k-mer from first sequence
        motifs = [dna_list[0][i:i + k]]
        
        # Build motifs for remaining sequences
        for j in range(1, t):
            # Create profile from current motifs
            profile = create_profile_matrix(motifs)
            # Find most probable k-mer in next sequence
            motif = profile_most_probable(dna_list[j], k, profile)
            motifs.append(motif)
        
        # Check if this is better
        score = score_motifs(motifs)
        if score < best_score:
            best_motifs = motifs
            best_score = score
    
    return best_motifs


def median_string(dna_list: List[str], k: int) -> str:
    """
    Find the k-mer that minimizes distance to all sequences.
    
    The median string is the k-mer with minimum total Hamming distance
    to the closest k-mer in each sequence. This finds a consensus motif.
    
    Time Complexity: O(4^k * n * m * k) where n = #sequences, m = length
    Space Complexity: O(k)
    
    Args:
        dna_list: List of DNA sequences
        k: Length of motif to find
    
    Returns:
        Median k-mer
    
    Example:
        >>> dna = ["AAATTGACGCAT", "GACGACCACGTT", "CGTCAGCGCCTG", "GCTGAGCACCGG", "AGTACGGGACAG"]
        >>> median = median_string(dna, 3)
        >>> median in ["GAC", "ACG"]
        True
    """
    distance = float('inf')
    median = ""
    
    # Try all possible k-mers
    for pattern in all_kmers(k):
        # Calculate distance from pattern to dna_list
        pattern_distance = 0
        
        for seq in dna_list:
            # Find minimum Hamming distance from pattern to any k-mer in seq
            min_dist = float('inf')
            for i in range(len(seq) - k + 1):
                kmer = seq[i:i + k]
                dist = hamming_distance(pattern, kmer)
                min_dist = min(min_dist, dist)
            pattern_distance += min_dist
        
        # Update median if better
        if pattern_distance < distance:
            distance = pattern_distance
            median = pattern
    
    return median


def all_kmers(k: int) -> List[str]:
    """
    Generate all possible k-mers of length k.
    
    Args:
        k: Length of k-mers
    
    Returns:
        List of all 4^k possible k-mers
    
    Example:
        >>> kmers = all_kmers(2)
        >>> len(kmers)
        16
        >>> "AG" in kmers
        True
    """
    nucleotides = ['A', 'C', 'G', 'T']
    return [''.join(p) for p in itertools.product(nucleotides, repeat=k)]


# Example Usage and Testing
if __name__ == "__main__":
    print("=== Motif Finding Algorithms ===\n")
    
    # Example 1: Finding (k,d)-motifs
    print("Example 1: Finding (3,1)-motifs")
    print("-" * 50)
    dna_sequences = [
        "ATTTGGC",
        "TGCCTTA", 
        "CGGTATC",
        "GAAAATT"
    ]
    
    print("DNA sequences:")
    for i, seq in enumerate(dna_sequences, 1):
        print(f"  Seq {i}: {seq}")
    
    motifs = find_motifs(dna_sequences, k=3, d=1)
    print(f"\n(3,1)-motifs found: {sorted(motifs)}")
    print(f"Total: {len(motifs)} motifs\n")
    
    # Example 2: Greedy motif search
    print("\nExample 2: Greedy Motif Search")
    print("-" * 50)
    dna_sequences2 = [
        "GGCGTTCAGGCA",
        "AAGAATCAGTCA",
        "CAAGGAGTTCGC",
        "CACGTCAATCAC",
        "CAATAATATTCG"
    ]
    
    print("DNA sequences:")
    for i, seq in enumerate(dna_sequences2, 1):
        print(f"  Seq {i}: {seq}")
    
    best_motifs = greedy_motif_search(dna_sequences2, k=3, t=5)
    print(f"\nBest motifs (k=3):")
    for i, motif in enumerate(best_motifs, 1):
        print(f"  Seq {i}: {motif}")
    
    print(f"\nScore: {score_motifs(best_motifs)}")
    
    # Example 3: Profile matrix
    print("\n\nExample 3: Profile Matrix Analysis")
    print("-" * 50)
    example_motifs = ["TCGGGG", "CCGGTG", "ACGGGG", "TTGGGG"]
    print("Motifs:")
    for motif in example_motifs:
        print(f"  {motif}")
    
    profile = create_profile_matrix(example_motifs)
    print("\nProfile matrix:")
    print("Pos:  ", "  ".join(str(i) for i in range(len(example_motifs[0]))))
    for nuc in ['A', 'C', 'G', 'T']:
        probs = "  ".join(f"{p:.2f}" for p in profile[nuc])
        print(f"  {nuc}: {probs}")
    
    # Example 4: Median string
    print("\n\nExample 4: Median String")
    print("-" * 50)
    dna_sequences3 = [
        "AAATTGACGCAT",
        "GACGACCACGTT",
        "CGTCAGCGCCTG",
        "GCTGAGCACCGG",
        "AGTACGGGACAG"
    ]
    
    print("DNA sequences:")
    for i, seq in enumerate(dna_sequences3, 1):
        print(f"  Seq {i}: {seq}")
    
    median = median_string(dna_sequences3, k=3)
    print(f"\nMedian 3-mer: {median}")
    
    # Calculate total distance for median
    total_dist = 0
    for seq in dna_sequences3:
        min_dist = min(
            hamming_distance(median, seq[i:i+3])
            for i in range(len(seq) - 2)
        )
        total_dist += min_dist
    print(f"Total distance: {total_dist}")
    
    print("\n" + "=" * 50)
    print("Motif finding complete!")
    print("=" * 50)
