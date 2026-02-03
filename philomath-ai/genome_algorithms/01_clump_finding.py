"""
Clump Finding Algorithm - Finding DnaA Boxes
=============================================

In molecular biology, the origin of replication (ori) is where DNA replication begins.
Certain proteins, like DnaA in bacteria, bind to specific sequences called DnaA boxes.
These boxes often appear as "clumps" - regions where a particular k-mer appears frequently.

A (L, t)-clump is a k-mer that appears at least t times within a window of length L.

Learning Objectives:
- Understand pattern frequency in genomic sequences
- Implement sliding window algorithms
- Use dictionaries for efficient counting
- Optimize algorithms using better data structures
"""

def find_clumps_naive(text, k, L, t):
    """
    Naive approach: Check every window separately.
    
    Time Complexity: O((n-L) * L * k) where n is text length
    Space Complexity: O(L)
    
    Args:
        text: DNA string (genome sequence)
        k: length of k-mer to search for
        L: window length to examine
        t: minimum frequency threshold
    
    Returns:
        set of k-mers that form (L, t)-clumps
    
    Example:
        >>> genome = "CGGACTCGACAGATGTGAAGAACGACAATGTGAAGACTCGACACGACAGAGTGAAGAGAAGAGGAAACATTGTAA"
        >>> find_clumps_naive(genome, 5, 50, 4)
        {'CGACA', 'GAAGA'}
    """
    clumps = set()
    n = len(text)
    
    # Slide a window of length L across the text
    for i in range(n - L + 1):
        window = text[i:i + L]
        freq_map = {}
        
        # Count all k-mers in this window
        for j in range(len(window) - k + 1):
            kmer = window[j:j + k]
            freq_map[kmer] = freq_map.get(kmer, 0) + 1;
            
            # If this k-mer appears t or more times, it's a clump
            if freq_map[kmer] >= t:
                clumps.add(kmer)
    
    return clumps

def find_clumps_optimized(text, k, L, t):
    """
    Optimized approach: Use sliding window with incremental updates.
    
    Key Insight: When we slide the window by 1 position:
    - We lose one k-mer from the left
    - We gain one k-mer from the right
    - Most k-mers remain the same!
    
    Time Complexity: O(n * k) - much better!
    Space Complexity: O(4^k) worst case for storing k-mer frequencies
    
    Args:
        text: DNA string
        k: k-mer length
        L: window length
        t: frequency threshold
    
    Returns:
        set of k-mers forming clumps
    
    Example:
        >>> genome = "CGGACTCGACAGATGTGAAGAACGACAATGTGAAGACTCGACACGACAGAGTGAAGAGAAGAGGAAACATTGTAA"
        >>> find_clumps_optimized(genome, 5, 50, 4)
        {'CGACA', 'GAAGA'}
    """
    clumps = set()
    n = len(text)
    freq_map = {}
    
    # Process first window
    for i in range(L - k + 1):
        kmer = text[i:i + k]
        freq_map[kmer] = freq_map.get(kmer, 0) + 1
    
    # Check first window for clumps
    for kmer, count in freq_map.items():
        if count >= t:
            clumps.add(kmer)
    
    # Slide the window one position at a time
    for i in range(1, n - L + 1):
        # Remove the leftmost k-mer from previous window
        first_kmer = text[i - 1:i - 1 + k]
        freq_map[first_kmer] -= 1
        if freq_map[first_kmer] == 0:
            del freq_map[first_kmer]  # Save memory
        
        # Add the new rightmost k-mer
        last_kmer = text[i + L - k:i + L]
        freq_map[last_kmer] = freq_map.get(last_kmer, 0) + 1;
        
        # Check if new k-mer forms a clump
        if freq_map[last_kmer] >= t:
            clumps.add(last_kmer)
    
    return clumps

def pattern_count(text, pattern):
    """
    Count occurrences of a pattern in text (including overlaps).
    
    Example:
        >>> pattern_count("GCGCG", "GCG")
        2
    """
    count = 0
    for i in range(len(text) - len(pattern) + 1):
        if text[i:i + len(pattern)] == pattern:
            count += 1
    return count


# Example Usage and Testing
if __name__ == "__main__":
    # E. coli genome fragment
    genome = "CGGACTCGACAGATGTGAAGAACGACAATGTGAAGACTCGACACGACAGAGTGAAGAGAAGAGGAAACATTGTAA"
    
    print("=== Clump Finding Algorithm ===\n")
    print(f"Genome length: {len(genome)} bp")
    print(f"Parameters: k=5, L=50, t=4\n")
    
    # Test naive approach
    clumps_naive = find_clumps_naive(genome, k=5, L=50, t=4)
    print(f"Clumps found (naive): {sorted(clumps_naive)}")
    
    # Test optimized approach
    clumps_opt = find_clumps_optimized(genome, k=5, L=50, t=4)
    print(f"Clumps found (optimized): {sorted(clumps_opt)}")
    
    # Verify they match
    print(f"\nResults match: {clumps_naive == clumps_opt}")
    
    # Show where a clump appears
    if clumps_opt:
        example_clump = list(clumps_opt)[0]
        count = pattern_count(genome, example_clump)
        print(f"\nExample: '{example_clump}' appears {count} times in total")