"""
Hamming Distance and Approximate Pattern Matching
=================================================

Hamming distance is a fundamental concept in string comparison, measuring how
many positions differ between two strings of equal length. In genomics, this
is crucial for finding patterns that may have mutations.

Biological Background:
---------------------
- DNA sequences mutate over evolutionary time
- Point mutations change single nucleotides (A→G, C→T, etc.)
- Regulatory sequences can tolerate some mutations while maintaining function
- Finding approximate matches reveals evolutionary relationships

Applications:
------------
- Finding mutated binding sites for transcription factors
- Identifying conserved but not identical sequences
- Detecting sequencing errors
- Studying molecular evolution
- SNP (Single Nucleotide Polymorphism) analysis

Learning Objectives:
-------------------
- Understand string distance metrics
- Implement approximate pattern matching
- Generate sequence neighborhoods
- Apply recursive algorithms
- Count pattern frequencies with mismatches
"""

from typing import List, Set, Tuple, Dict


def hamming_distance(str1: str, str2: str) -> int:
    """
    Calculate Hamming distance between two equal-length strings.
    
    The Hamming distance is the number of positions where the symbols differ.
    Named after Richard Hamming, used extensively in error detection/correction.
    
    Time Complexity: O(n) where n is string length
    Space Complexity: O(1)
    
    Args:
        str1: First string
        str2: Second string (must be same length as str1)
    
    Returns:
        Number of positions where strings differ
    
    Raises:
        ValueError: If strings have different lengths
    
    Examples:
        >>> hamming_distance("GATTACA", "GATTACA")
        0
        >>> hamming_distance("GATTACA", "GCATGCU")
        4
        >>> hamming_distance("TTATCCACA", "TTATGCACA")
        1
    
    Biological Example:
        Wild-type DnaA box:   TTATCCACA
        Mutated DnaA box:     TTATGCACA
        Hamming distance = 1 (single point mutation: C→G)
    """
    if len(str1) != len(str2):
        raise ValueError(f"Strings must have equal length: {len(str1)} != {len(str2)}")
    
    return sum(c1 != c2 for c1, c2 in zip(str1, str2))


def approximate_pattern_match(pattern: str, text: str, d: int) -> List[int]:
    """
    Find all approximate occurrences of pattern in text.
    
    An approximate match allows up to d mismatches (Hamming distance ≤ d).
    Returns starting positions of all matches.
    
    Time Complexity: O((n-m+1) * m) where n = len(text), m = len(pattern)
    Space Complexity: O(k) where k = number of matches
    
    Args:
        pattern: Pattern to search for
        text: Text to search in
        d: Maximum allowed mismatches
    
    Returns:
        List of starting positions where pattern matches with ≤ d mismatches
    
    Example:
        >>> text = "CGCCCGAATCCAGAACGCATTCCCATATTTCGGGACCACTGGCCTCCACGGTACGGACGTCAATCAAAT"
        >>> pattern = "ATTCTGGA"
        >>> approximate_pattern_match(pattern, text, 3)
        [6, 7, 26, 27]
    
    Biological Example:
        Finding mutated transcription factor binding sites:
        
        Consensus site:   TGACGTCA
        
        In genome:        TGACGTCA  (exact match, d=0)
                          TGACTTCA  (1 mismatch, d=1)
                          TGATGTAA  (2 mismatches, d=2)
    """
    positions = []
    k = len(pattern)
    
    # Check each position in text
    for i in range(len(text) - k + 1):
        # Extract k-mer at position i
        kmer = text[i:i + k]
        
        # Check if Hamming distance is within threshold
        if hamming_distance(pattern, kmer) <= d:
            positions.append(i)
    
    return positions


def count_approximate_matches(text: str, pattern: str, d: int) -> int:
    """
    Count number of approximate pattern occurrences in text.
    
    Args:
        text: DNA sequence to search
        pattern: Pattern to count
        d: Maximum allowed mismatches
    
    Returns:
        Number of approximate matches
    
    Example:
        >>> count_approximate_matches("AACAAGCTGATAAACATTTAAAGAG", "AAAAA", 2)
        11
        >>> count_approximate_matches("TTTAGAGCCTTCAGAGG", "GAGG", 2)
        4
    """
    return len(approximate_pattern_match(pattern, text, d))


def neighbors(pattern: str, d: int) -> Set[str]:
    """
    Generate all strings within Hamming distance d from pattern.
    
    The d-neighborhood of a pattern is the set of all strings that differ
    from the pattern in at most d positions. This creates all possible
    mutational variants.
    
    Uses recursive algorithm:
    - Base case: d=0 returns just the pattern
    - Base case: len=1 returns all 4 nucleotides
    - Recursive: Generate neighbors of suffix, then add prefixes
    
    Time Complexity: O(4^d * k) where k = len(pattern)
    Space Complexity: O(4^d)
    
    Args:
        pattern: DNA string
        d: Maximum Hamming distance
    
    Returns:
        Set of all strings within distance d
    
    Example:
        >>> nbrs = neighbors("ACG", 1)
        >>> len(nbrs)
        10
        >>> "ACG" in nbrs  # Original pattern
        True
        >>> "AAG" in nbrs  # 1 mismatch
        True
        >>> "ATG" in nbrs  # 1 mismatch
        True
        >>> "ACA" in nbrs  # 1 mismatch
        True
    
    Biological Example:
        For DnaA box "TGT" with d=1:
        - Exact match: TGT
        - 1st position variants: AGT, CGT, GGT
        - 2nd position variants: TAT, TCT, TTT
        - 3rd position variants: TGA, TGC, TGG
        Total: 10 neighbors (including original)
    """
    if d == 0:
        return {pattern}
    
    if len(pattern) == 1:
        return {'A', 'C', 'G', 'T'}
    
    neighborhood = set()
    
    # Get neighbors of suffix (all but first character)
    suffix_neighbors = neighbors(pattern[1:], d)
    
    for suffix in suffix_neighbors:
        # Check Hamming distance between original suffix and this neighbor
        if hamming_distance(pattern[1:], suffix) < d:
            # We have room to change the first nucleotide
            for nucleotide in ['A', 'C', 'G', 'T']:
                neighborhood.add(nucleotide + suffix)
        else:
            # Must keep first nucleotide unchanged
            neighborhood.add(pattern[0] + suffix)
    
    return neighborhood


def frequent_words_with_mismatches(text: str, k: int, d: int) -> List[str]:
    """
    Find most frequent k-mers with up to d mismatches.
    
    This finds k-mers that appear most frequently when allowing d mismatches.
    Each approximate occurrence of a k-mer counts toward its frequency.
    
    Time Complexity: O(n * 4^k * k) where n = len(text)
    Space Complexity: O(4^k)
    
    Args:
        text: DNA sequence
        k: Length of k-mers
        d: Maximum allowed mismatches
    
    Returns:
        List of most frequent k-mers (with mismatches)
    
    Example:
        >>> text = "ACGTTGCATGTCGCATGATGCATGAGAGCT"
        >>> frequent_words_with_mismatches(text, 4, 1)
        ['ATGC', 'GATG', 'ATGT']
    
    Biological Application:
        Finding transcription factor binding sites that tolerate mutations.
        Instead of exact TGACGTCA, we find all variants like TGATGTCA, TGACTTCA.
    """
    frequency_map = {}
    
    # Count approximate occurrences for all k-mers in text
    for i in range(len(text) - k + 1):
        kmer = text[i:i + k]
        
        # Generate all neighbors (including kmer itself)
        neighborhood = neighbors(kmer, d)
        
        # Increment count for each neighbor
        for neighbor in neighborhood:
            frequency_map[neighbor] = frequency_map.get(neighbor, 0) + 1
    
    # Find maximum frequency
    max_freq = max(frequency_map.values()) if frequency_map else 0
    
    # Return all k-mers with maximum frequency
    return [kmer for kmer, freq in frequency_map.items() if freq == max_freq]


def frequent_words_with_mismatches_and_reverse(text: str, k: int, d: int) -> List[str]:
    """
    Find most frequent k-mers considering both strand and reverse complement.
    
    DNA is double-stranded. A protein binding site on one strand corresponds
    to its reverse complement on the other strand. This function counts both.
    
    Reverse complement rules:
    - Reverse the sequence: ATCG → GCTA
    - Complement each base: A↔T, C↔G
    - Final: ATCG → CGAT
    
    Args:
        text: DNA sequence
        k: Length of k-mers
        d: Maximum mismatches
    
    Returns:
        Most frequent k-mers considering both strands
    
    Example:
        >>> text = "AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"
        >>> frequent_words_with_mismatches_and_reverse(text, 2, 1)
        ['AA', 'TT']
    
    Biological Context:
        Transcription factors can bind to either DNA strand.
        TGACGTCA on forward strand = TGACGTCA on forward
        TGACGTCA on reverse strand = reverse_complement(TGACGTCA) = TGACGTCA
        (This particular sequence is a palindrome)
    """
    frequency_map = {}
    
    # Process all k-mers
    for i in range(len(text) - k + 1):
        kmer = text[i:i + k]
        
        # Get neighbors of k-mer and its reverse complement
        neighborhood = neighbors(kmer, d)
        rc_neighborhood = neighbors(reverse_complement(kmer), d)
        
        # Count both
        for neighbor in neighborhood:
            frequency_map[neighbor] = frequency_map.get(neighbor, 0) + 1
        
        for neighbor in rc_neighborhood:
            frequency_map[neighbor] = frequency_map.get(neighbor, 0) + 1
    
    # Find maximum frequency
    max_freq = max(frequency_map.values()) if frequency_map else 0
    
    # Return all k-mers with maximum frequency
    return [kmer for kmer, freq in frequency_map.items() if freq == max_freq]


def reverse_complement(dna: str) -> str:
    """
    Calculate reverse complement of a DNA sequence.
    
    The reverse complement represents the sequence on the opposite DNA strand.
    
    Steps:
    1. Reverse the sequence
    2. Complement each base (A↔T, C↔G)
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    
    Args:
        dna: DNA sequence
    
    Returns:
        Reverse complement
    
    Example:
        >>> reverse_complement("AAAACCCGGT")
        'ACCGGGTTTT'
        >>> reverse_complement("ATCG")
        'CGAT'
    
    Biological Context:
        DNA double helix has two antiparallel strands:
        
        5'-ATCG-3'  (forward strand)
           ||||
        3'-TAGC-5'  (reverse strand)
        
        Reverse complement of ATCG:
        1. Reverse: GCTA
        2. Complement: CGAT
    """
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    return ''.join(complement[base] for base in reversed(dna))


def minimum_skew_positions(genome: str) -> List[int]:
    """
    Find positions where skew (#G - #C) is minimum.
    
    This is useful for finding origin of replication.
    Included here for completeness as it uses similar techniques.
    
    Args:
        genome: DNA sequence
    
    Returns:
        List of positions with minimum skew
    
    Example:
        >>> minimum_skew_positions("TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT")
        [11, 24]
    """
    skew = [0]
    for nucleotide in genome:
        if nucleotide == 'G':
            skew.append(skew[-1] + 1)
        elif nucleotide == 'C':
            skew.append(skew[-1] - 1)
        else:
            skew.append(skew[-1])
    
    min_value = min(skew)
    return [i for i, val in enumerate(skew) if val == min_value]


# Example Usage and Testing
if __name__ == "__main__":
    print("=== Hamming Distance and Approximate Matching ===\n")
    
    # Example 1: Basic Hamming distance
    print("Example 1: Hamming Distance")
    print("-" * 60)
    seq1 = "GATTACA"
    seq2 = "GCATGCU"
    dist = hamming_distance(seq1, seq2)
    print(f"Sequence 1: {seq1}")
    print(f"Sequence 2: {seq2}")
    print(f"            ", end="")
    for i, (c1, c2) in enumerate(zip(seq1, seq2)):
        if c1 != c2:
            print("^", end="")
        else:
            print(" ", end="")
    print(f"\nHamming distance: {dist}")
    
    # Example 2: Approximate pattern matching
    print("\n\nExample 2: Approximate Pattern Matching")
    print("-" * 60)
    text = "CGCCCGAATCCAGAACGCATTCCCATATTTCGGGACCACTGGCCTCCACGGTACGGACGTCAATCAAAT"
    pattern = "ATTCTGGA"
    d = 3
    
    print(f"Text: {text}")
    print(f"Pattern: {pattern}")
    print(f"Maximum mismatches (d): {d}")
    
    matches = approximate_pattern_match(pattern, text, d)
    print(f"\nApproximate matches found at positions: {matches}")
    
    if matches:
        print("\nMatching regions:")
        for pos in matches[:3]:  # Show first 3
            matched_seq = text[pos:pos + len(pattern)]
            dist = hamming_distance(pattern, matched_seq)
            print(f"  Position {pos:2d}: {matched_seq} (distance: {dist})")
    
    # Example 3: Generating neighbors
    print("\n\nExample 3: Generating d-Neighbors")
    print("-" * 60)
    pattern = "ACG"
    d = 1
    
    nbrs = neighbors(pattern, d)
    print(f"Pattern: {pattern}")
    print(f"Maximum distance (d): {d}")
    print(f"Number of neighbors: {len(nbrs)}")
    print(f"Neighbors: {sorted(nbrs)}")
    
    # Count by Hamming distance
    dist_counts = {0: 0, 1: 0}
    for nbr in nbrs:
        dist = hamming_distance(pattern, nbr)
        dist_counts[dist] += 1
    
    print(f"\nBreakdown:")
    print(f"  Distance 0 (exact): {dist_counts[0]}")
    print(f"  Distance 1 (1 mismatch): {dist_counts[1]}")
    
    # Example 4: Frequent words with mismatches
    print("\n\nExample 4: Frequent k-mers with Mismatches")
    print("-" * 60)
    text = "ACGTTGCATGTCGCATGATGCATGAGAGCT"
    k = 4
    d = 1
    
    print(f"Text: {text}")
    print(f"k-mer length: {k}")
    print(f"Maximum mismatches: {d}")
    
    frequent = frequent_words_with_mismatches(text, k, d)
    print(f"\nMost frequent {k}-mers (with up to {d} mismatch):")
    print(f"  {frequent}")
    
    # Show counts for top results
    print("\nOccurrence analysis:")
    for kmer in frequent[:3]:  # Show top 3
        count = count_approximate_matches(text, kmer, d)
        print(f"  {kmer}: {count} approximate matches")
    
    # Example 5: Reverse complement
    print("\n\nExample 5: Reverse Complement")
    print("-" * 60)
    sequences = ["ATCG", "AAAACCCGGT", "GCTAGCT"]
    
    for seq in sequences:
        rc = reverse_complement(seq)
        print(f"{seq} → {rc}")
    
    # Example 6: Both strands
    print("\n\nExample 6: Frequent k-mers on Both Strands")
    print("-" * 60)
    text = "AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"
    k = 2
    d = 1
    
    print(f"Text: {text}")
    print(f"k: {k}, d: {d}")
    
    frequent_both = frequent_words_with_mismatches_and_reverse(text, k, d)
    print(f"\nMost frequent {k}-mers (both strands): {sorted(frequent_both)}")
    
    print("\n" + "=" * 60)
    print("Approximate matching analysis complete!")
    print("=" * 60)
