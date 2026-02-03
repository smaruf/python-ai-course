"""
Skew Array Algorithm - Finding the Origin of Replication
==========================================================

The skew array is a fundamental tool for identifying the origin of replication (ori)
in bacterial genomes. It exploits the asymmetric behavior of DNA strands during replication.

Biological Background:
----------------------
During DNA replication:
- The leading strand is synthesized continuously (5' → 3')
- The lagging strand is synthesized in fragments (Okazaki fragments)
- On the leading strand, cytosine (C) tends to mutate to thymine (T)
- This creates an imbalance: more guanine (G) on leading strand, more cytosine (C) on lagging

The skew at position i is defined as:
    Skew(i) = #G(0,i) - #C(0,i)
    
Where #G(0,i) is the number of G's and #C(0,i) is the number of C's 
from position 0 to position i.

Key Insight:
-----------
The origin of replication is often located where the skew reaches its minimum value,
marking the transition point where the DNA strands switch roles (leading ↔ lagging).

Learning Objectives:
- Understand biological significance of GC-skew
- Implement efficient array-based algorithms
- Apply cumulative sum techniques
- Identify patterns in genomic data
"""

from typing import List, Tuple


def compute_skew(genome: str) -> List[int]:
    """
    Calculate the skew array for a genome sequence.
    
    The skew starts at 0 and increases by 1 for each G encountered,
    decreases by 1 for each C encountered, and stays the same for A and T.
    
    Time Complexity: O(n) where n is genome length
    Space Complexity: O(n) to store the skew array
    
    Args:
        genome: DNA string containing only A, C, G, T characters
    
    Returns:
        List of skew values at each position (length = len(genome) + 1)
        
    Example:
        >>> compute_skew("CATGGGCATCGGCCATACGCC")
        [0, -1, -1, -1, 0, 1, 2, 1, 1, 1, 0, 1, 2, 1, 0, 0, 0, 0, -1, 0, -1, -2]
        
    Explanation:
        Position 0: skew = 0 (starting point)
        Position 1: C encountered, skew = 0 - 1 = -1
        Position 2: A encountered, skew = -1 (no change)
        Position 3: T encountered, skew = -1 (no change)
        Position 4: G encountered, skew = -1 + 1 = 0
        ... and so on
    """
    skew = [0]  # Start with skew of 0
    current_skew = 0
    
    for nucleotide in genome:
        if nucleotide == 'G':
            current_skew += 1
        elif nucleotide == 'C':
            current_skew -= 1
        # A and T don't change the skew
        
        skew.append(current_skew)
    
    return skew


def find_min_skew_positions(genome: str) -> List[int]:
    """
    Find all positions where the skew is at its minimum value.
    
    These positions are candidate locations for the origin of replication.
    In circular bacterial genomes, the ori is often located near the minimum skew.
    
    Time Complexity: O(n) where n is genome length
    Space Complexity: O(n) for the skew array
    
    Args:
        genome: DNA string
    
    Returns:
        List of positions (0-indexed) where skew is minimum
        
    Example:
        >>> find_min_skew_positions("TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT")
        [11, 24]
        
    Biological Interpretation:
        The positions 11 and 24 are candidate ori locations where we should
        look for DnaA boxes (clumps of specific k-mers).
    """
    skew = compute_skew(genome)
    min_value = min(skew)
    
    # Find all positions with minimum skew value
    min_positions = [i for i, value in enumerate(skew) if value == min_value]
    
    return min_positions


def analyze_skew(genome: str) -> dict:
    """
    Perform comprehensive skew analysis on a genome.
    
    Returns detailed statistics about the skew array useful for 
    understanding the genome's composition and structure.
    
    Args:
        genome: DNA string
        
    Returns:
        Dictionary containing:
            - skew_array: complete skew values
            - min_value: minimum skew value
            - max_value: maximum skew value
            - min_positions: positions where skew is minimum
            - max_positions: positions where skew is maximum
            - range: skew range (max - min)
            - final_skew: skew at end (should be 0 for circular genomes)
            
    Example:
        >>> result = analyze_skew("GAGCCACCGCGATA")
        >>> result['min_value']
        -2
        >>> result['max_value']
        2
    """
    skew = compute_skew(genome)
    min_val = min(skew)
    max_val = max(skew)
    
    return {
        'skew_array': skew,
        'min_value': min_val,
        'max_value': max_val,
        'min_positions': [i for i, v in enumerate(skew) if v == min_val],
        'max_positions': [i for i, v in enumerate(skew) if v == max_val],
        'range': max_val - min_val,
        'final_skew': skew[-1],
        'genome_length': len(genome)
    }


def print_skew_diagram(genome: str, width: int = 80) -> None:
    """
    Print a simple text-based visualization of the skew array.
    
    This is useful for quick inspection without matplotlib.
    
    Args:
        genome: DNA string
        width: maximum width for the diagram
        
    Example:
        >>> print_skew_diagram("GAGCCACCGCGATA")
        Skew Diagram for genome (length: 14)
        =====================================
        Position  0: 0 
        Position  1: 1 *
        Position  2: 0 
        Position  3: 1 *
        ...
    """
    skew = compute_skew(genome)
    min_val = min(skew)
    max_val = max(skew)
    
    print(f"Skew Diagram for genome (length: {len(genome)})")
    print("=" * width)
    
    for i, value in enumerate(skew[:min(len(skew), 50)]):  # Limit output
        # Create visual bar
        if max_val > min_val:
            normalized = int(((value - min_val) / (max_val - min_val)) * 20)
        else:
            normalized = 0
            
        bar = '*' * normalized
        marker = ' MIN' if value == min_val else ''
        print(f"Position {i:3d}: {value:3d} {bar}{marker}")
    
    if len(skew) > 50:
        print(f"... ({len(skew) - 50} more positions)")


# Example Usage and Testing
if __name__ == "__main__":
    print("=== Skew Array Algorithm ===\n")
    
    # Example 1: Simple demonstration
    print("Example 1: Simple sequence")
    print("-" * 50)
    simple_genome = "CATGGGCATCGGCCATACGCC"
    skew = compute_skew(simple_genome)
    print(f"Genome: {simple_genome}")
    print(f"Length: {len(simple_genome)} bp")
    print(f"Skew array: {skew}")
    print(f"Minimum skew: {min(skew)} at positions {find_min_skew_positions(simple_genome)}")
    print()
    
    # Example 2: Finding ori candidates
    print("Example 2: Finding origin of replication candidates")
    print("-" * 50)
    genome = "TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT"
    min_positions = find_min_skew_positions(genome)
    print(f"Genome length: {len(genome)} bp")
    print(f"Minimum skew positions: {min_positions}")
    print(f"\nThese positions are candidates for the origin of replication.")
    print(f"We should search for DnaA box clumps near these positions.")
    print()
    
    # Example 3: Comprehensive analysis
    print("Example 3: Comprehensive skew analysis")
    print("-" * 50)
    test_genome = "GAGCCACCGCGATA"
    analysis = analyze_skew(test_genome)
    print(f"Genome: {test_genome}")
    print(f"Analysis results:")
    print(f"  Min skew: {analysis['min_value']} at positions {analysis['min_positions']}")
    print(f"  Max skew: {analysis['max_value']} at positions {analysis['max_positions']}")
    print(f"  Skew range: {analysis['range']}")
    print(f"  Final skew: {analysis['final_skew']}")
    print(f"  (For circular genomes, final skew should be 0)")
    print()
    
    # Example 4: E. coli-like genome fragment
    print("Example 4: Larger genome fragment analysis")
    print("-" * 50)
    ecoli_fragment = (
        "GCGCGCGCGCGCAAATTTCCCGGGAAATTTCCCGGGCGCGCGAAATTTCCCGGG"
        "AAATTTGCGCGCAAATTTCCCGGGCGCGCGCGCAAATTTCCCGGGCGCGCG"
    )
    print(f"Genome fragment length: {len(ecoli_fragment)} bp")
    min_pos = find_min_skew_positions(ecoli_fragment)
    analysis = analyze_skew(ecoli_fragment)
    print(f"Minimum skew: {analysis['min_value']} at {len(min_pos)} position(s)")
    print(f"First few minimum positions: {min_pos[:5]}")
    print()
    
    # Example 5: Text diagram
    print("Example 5: Text-based visualization")
    print("-" * 50)
    print_skew_diagram("GAGCCACCGCGATA")
    print()
    
    # Educational note
    print("\n" + "=" * 70)
    print("BIOLOGICAL SIGNIFICANCE")
    print("=" * 70)
    print("""
The skew array helps identify the origin of replication because:

1. DNA replication is asymmetric - one strand (leading) is copied continuously,
   while the other (lagging) is copied in fragments.

2. Deamination: Cytosine (C) tends to mutate to Thymine (T) on the leading
   strand more frequently, causing an imbalance.

3. This creates regions with excess Guanine (G) and regions with excess 
   Cytosine (C), separated by the origin of replication.

4. The minimum skew often corresponds to the ori location, where we can
   find frequent DnaA boxes (specific k-mer patterns).

Real-world application:
In E. coli, this method successfully identifies the ori region, which
has been experimentally verified to be near position 3,923,620 in a 
genome of ~4.6 million base pairs.
    """)
