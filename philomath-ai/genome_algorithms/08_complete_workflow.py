"""
Complete Workflow - Finding the Origin of Replication
======================================================

This module demonstrates the complete pipeline for identifying the origin of
replication (ori) in a bacterial genome, combining all the algorithms we've learned.

The biological question:
------------------------
Where does DNA replication begin in a bacterial genome?

The computational approach:
---------------------------
1. Find regions with unusual GC-skew (minimum skew)
2. Look for clumps of specific k-mers (DnaA boxes) near those regions
3. Visualize and validate the results
4. Interpret findings in biological context

This end-to-end example shows how bioinformatics combines:
- Algorithm design
- Performance optimization
- Data visualization
- Biological interpretation

Learning Objectives:
- Integrate multiple algorithms into a pipeline
- Handle real-world genomic data
- Make biological predictions from computational results
- Document and communicate scientific findings
"""

import sys
import os
from typing import List, Dict, Tuple, Set, Optional
import random
import importlib.util

# Import all our modules using importlib
def import_module_from_file(module_name, file_path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # Import clump finding module
    _clump_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '01_clump_finding.py')
    _clump_module = import_module_from_file('clump_finding', _clump_path)
    find_clumps_optimized = _clump_module.find_clumps_optimized
    pattern_count = _clump_module.pattern_count
    
    # Import skew module
    _skew_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '02_skew_array.py')
    _skew_module = import_module_from_file('skew_array', _skew_path)
    compute_skew = _skew_module.compute_skew
    find_min_skew_positions = _skew_module.find_min_skew_positions
    analyze_skew = _skew_module.analyze_skew
    
    # Import visualization module
    _viz_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '06_visualization.py')
    _viz_module = import_module_from_file('visualization', _viz_path)
    plot_skew = _viz_module.plot_skew
    visualize_clump_locations = _viz_module.visualize_clump_locations
    plot_combined_analysis = _viz_module.plot_combined_analysis
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Visualization module not available: {e}")
    print("Install matplotlib to enable visualization.")
    VISUALIZATION_AVAILABLE = False
except Exception as e:
    print(f"Warning: Could not import modules: {e}")
    VISUALIZATION_AVAILABLE = False


def load_genome_from_file(filepath: str) -> str:
    """
    Load a genome sequence from a FASTA file.
    
    FASTA format:
    >Header line with description
    ACGTACGTACGT...
    ACGTACGTACGT...
    
    Args:
        filepath: Path to FASTA file
        
    Returns:
        Genome sequence as a single string
    """
    genome = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('>'):  # Skip header lines
                genome.append(line.upper())
    
    return ''.join(genome)


def simulate_genome(length: int, gc_content: float = 0.5, 
                   ori_position: int = None, seed: int = None) -> str:
    """
    Simulate a bacterial genome with a realistic GC-skew pattern.
    
    This creates a synthetic genome useful for testing and teaching.
    The genome will have:
    - Specified GC content
    - Asymmetric GC distribution mimicking real genomes
    - Optional planted origin of replication
    
    Args:
        length: Genome length in base pairs
        gc_content: Proportion of G+C (0.0 to 1.0)
        ori_position: Position to place the ori (adds GC-skew minimum)
        seed: Random seed for reproducibility
        
    Returns:
        Simulated genome string
        
    Example:
        >>> genome = simulate_genome(10000, gc_content=0.5, ori_position=5000, seed=42)
        >>> len(genome)
        10000
    """
    if seed is not None:
        random.seed(seed)
    
    genome = []
    
    # Simple simulation: create genome with specified GC content
    for i in range(length):
        if random.random() < gc_content:
            # GC nucleotide
            # Create skew pattern: more G before ori, more C after
            if ori_position and i < ori_position:
                # Before ori: favor G
                genome.append('G' if random.random() < 0.6 else 'C')
            elif ori_position and i >= ori_position:
                # After ori: favor C
                genome.append('C' if random.random() < 0.6 else 'G')
            else:
                # No ori specified: random GC
                genome.append(random.choice(['G', 'C']))
        else:
            # AT nucleotide
            genome.append(random.choice(['A', 'T']))
    
    # Plant some DnaA boxes near ori
    if ori_position:
        dnaa_box = "TTATCCACA"  # Common DnaA box motif
        # Plant several copies around ori
        for offset in range(-200, 200, 50):
            pos = ori_position + offset
            if 0 <= pos < length - len(dnaa_box):
                genome[pos:pos+len(dnaa_box)] = list(dnaa_box)
    
    return ''.join(genome)


def find_origin_of_replication(genome: str, k: int = 9, L: int = 500, t: int = 3,
                               window_around_minimum: int = 1000,
                               verbose: bool = True) -> Dict:
    """
    Complete pipeline to identify the origin of replication.
    
    This is the main analysis function that:
    1. Computes the GC-skew array
    2. Finds minimum skew positions (candidate ori)
    3. Searches for DnaA box clumps near minimum
    4. Returns comprehensive results
    
    Args:
        genome: DNA string to analyze
        k: k-mer length for clump finding
        L: window length for clump finding
        t: frequency threshold for clump finding
        window_around_minimum: How far around skew minimum to search (bp)
        verbose: Print progress information
        
    Returns:
        Dictionary containing:
            - skew_analysis: Full skew analysis results
            - candidate_ori_positions: List of minimum skew positions
            - all_clumps: Set of all clumps in genome
            - ori_region_clumps: Clumps found near minimum skew
            - predicted_ori: Best predicted ori position
            
    Example:
        >>> genome = simulate_genome(10000, ori_position=5000, seed=42)
        >>> results = find_origin_of_replication(genome, verbose=False)
        >>> 'predicted_ori' in results
        True
    """
    if verbose:
        print("=" * 70)
        print("ORIGIN OF REPLICATION FINDER")
        print("=" * 70)
        print(f"\nGenome length: {len(genome):,} bp")
        print(f"Parameters: k={k}, L={L}, t={t}\n")
    
    # Step 1: Analyze GC-skew
    if verbose:
        print("Step 1: Computing GC-skew array...")
    
    skew_analysis = analyze_skew(genome)
    candidate_positions = skew_analysis['min_positions']
    
    if verbose:
        print(f"  Minimum skew: {skew_analysis['min_value']}")
        print(f"  Maximum skew: {skew_analysis['max_value']}")
        print(f"  Candidate ori positions: {candidate_positions[:5]}")
        if len(candidate_positions) > 5:
            print(f"  ... and {len(candidate_positions) - 5} more")
    
    # Step 2: Find all DnaA box clumps in genome
    if verbose:
        print("\nStep 2: Finding DnaA box clumps (frequent k-mers)...")
    
    all_clumps = find_clumps_optimized(genome, k, L, t)
    
    if verbose:
        print(f"  Clumps found genome-wide: {len(all_clumps)}")
        if all_clumps:
            print(f"  Examples: {sorted(list(all_clumps))[:5]}")
    
    # Step 3: Find clumps specifically near minimum skew positions
    if verbose:
        print("\nStep 3: Identifying clumps near candidate ori positions...")
    
    ori_region_clumps = set()
    
    for min_pos in candidate_positions:
        # Define region around this minimum
        region_start = max(0, min_pos - window_around_minimum)
        region_end = min(len(genome), min_pos + window_around_minimum)
        region = genome[region_start:region_end]
        
        # Find clumps in this specific region
        region_clumps = find_clumps_optimized(region, k, L, t)
        ori_region_clumps.update(region_clumps)
    
    if verbose:
        print(f"  Clumps near ori candidates: {len(ori_region_clumps)}")
        if ori_region_clumps:
            print(f"  Examples: {sorted(list(ori_region_clumps))[:5]}")
    
    # Step 4: Predict most likely ori position
    # Use the first minimum skew position as primary prediction
    predicted_ori = candidate_positions[0] if candidate_positions else None
    
    if verbose and predicted_ori is not None:
        print(f"\nStep 4: Prediction")
        print(f"  Predicted ori position: {predicted_ori:,} bp")
        print(f"  (Located at {predicted_ori / len(genome) * 100:.1f}% of genome)")
    
    # Compile results
    results = {
        'skew_analysis': skew_analysis,
        'candidate_ori_positions': candidate_positions,
        'all_clumps': all_clumps,
        'ori_region_clumps': ori_region_clumps,
        'predicted_ori': predicted_ori,
        'genome_length': len(genome),
        'parameters': {'k': k, 'L': L, 't': t}
    }
    
    return results


def print_analysis_report(results: Dict, genome: str) -> None:
    """
    Print a comprehensive analysis report.
    
    Args:
        results: Results dictionary from find_origin_of_replication()
        genome: Original genome sequence
    """
    print("\n" + "=" * 70)
    print("ANALYSIS REPORT: Origin of Replication")
    print("=" * 70)
    
    print("\n### GENOME STATISTICS ###")
    print(f"Length: {results['genome_length']:,} bp")
    
    # Nucleotide composition
    a_count = genome.count('A')
    c_count = genome.count('C')
    g_count = genome.count('G')
    t_count = genome.count('T')
    total = len(genome)
    
    print(f"Composition:")
    print(f"  A: {a_count:,} ({a_count/total*100:.1f}%)")
    print(f"  C: {c_count:,} ({c_count/total*100:.1f}%)")
    print(f"  G: {g_count:,} ({g_count/total*100:.1f}%)")
    print(f"  T: {t_count:,} ({t_count/total*100:.1f}%)")
    print(f"  GC content: {(g_count + c_count)/total*100:.1f}%")
    
    print("\n### SKEW ANALYSIS ###")
    skew = results['skew_analysis']
    print(f"Minimum skew: {skew['min_value']}")
    print(f"Maximum skew: {skew['max_value']}")
    print(f"Skew range: {skew['range']}")
    print(f"Final skew: {skew['final_skew']} (circular genome should be ~0)")
    
    print("\n### CANDIDATE ORI POSITIONS ###")
    positions = results['candidate_ori_positions']
    print(f"Number of minimum skew positions: {len(positions)}")
    if positions:
        print(f"Positions: {positions[:10]}")
        if len(positions) > 10:
            print(f"... and {len(positions) - 10} more")
    
    print("\n### CLUMP ANALYSIS ###")
    params = results['parameters']
    print(f"Parameters: k={params['k']}, L={params['L']}, t={params['t']}")
    print(f"Total clumps in genome: {len(results['all_clumps'])}")
    print(f"Clumps near ori candidates: {len(results['ori_region_clumps'])}")
    
    if results['ori_region_clumps']:
        print("\nTop DnaA box candidates (clumps near ori):")
        for i, clump in enumerate(sorted(results['ori_region_clumps'])[:10], 1):
            count = pattern_count(genome, clump)
            print(f"  {i}. {clump} (appears {count} times)")
    
    print("\n### PREDICTION ###")
    if results['predicted_ori'] is not None:
        ori = results['predicted_ori']
        print(f"Predicted ori location: {ori:,} bp")
        print(f"Position in genome: {ori / results['genome_length'] * 100:.1f}%")
        
        # Show sequence around predicted ori
        window = 50
        start = max(0, ori - window)
        end = min(len(genome), ori + window)
        print(f"\nSequence near predicted ori ({start}-{end}):")
        print(genome[start:end])
    else:
        print("No clear ori prediction could be made.")
    
    print("\n" + "=" * 70)


# Example Usage and Testing
if __name__ == "__main__":
    print("=" * 70)
    print("COMPLETE WORKFLOW: Finding Origin of Replication")
    print("=" * 70)
    print()
    print("This example demonstrates the complete pipeline for identifying")
    print("the origin of replication in a bacterial genome.")
    print()
    
    # Example 1: Simulated genome with known ori
    print("\n### EXAMPLE 1: Simulated Genome with Known Ori ###")
    print("-" * 70)
    
    print("Simulating E. coli-like genome (20,000 bp)...")
    print("True ori position: 10,000 bp (middle of genome)")
    
    genome = simulate_genome(
        length=20000,
        gc_content=0.51,  # E. coli has ~51% GC
        ori_position=10000,
        seed=42
    )
    
    # Run the complete analysis
    results = find_origin_of_replication(
        genome,
        k=9,
        L=500,
        t=3,
        verbose=True
    )
    
    # Print detailed report
    print_analysis_report(results, genome)
    
    # Visualize if available
    if VISUALIZATION_AVAILABLE:
        print("\nGenerating visualizations...")
        
        # Skew plot
        plot_skew(genome, "Simulated Genome - GC Skew Analysis")
        
        # Combined analysis
        plot_combined_analysis(
            genome,
            k=results['parameters']['k'],
            L=results['parameters']['L'],
            t=results['parameters']['t'],
            title="Complete Analysis - Simulated E. coli-like Genome"
        )
    
    # Validation
    print("\n### VALIDATION ###")
    print("-" * 70)
    true_ori = 10000
    predicted_ori = results['predicted_ori']
    if predicted_ori:
        error = abs(predicted_ori - true_ori)
        print(f"True ori position: {true_ori:,} bp")
        print(f"Predicted ori position: {predicted_ori:,} bp")
        print(f"Prediction error: {error:,} bp ({error/len(genome)*100:.2f}% of genome)")
        
        if error < 500:
            print("✓ Excellent prediction! (within 500 bp)")
        elif error < 1000:
            print("✓ Good prediction! (within 1,000 bp)")
        elif error < 5000:
            print("~ Acceptable prediction (within 5,000 bp)")
        else:
            print("✗ Large error - may need parameter tuning")
    
    # Example 2: Realistic parameters for E. coli
    print("\n\n### EXAMPLE 2: E. coli Analysis Parameters ###")
    print("-" * 70)
    print("""
For a real E. coli genome (~4.6 million bp), use these parameters:

  k = 9      # DnaA boxes are typically 9bp
  L = 500    # Search windows of 500bp
  t = 3      # k-mer appears at least 3 times in window
  
Expected results:
  - Ori location: ~3,923,620 bp (experimentally validated)
  - Should find several DnaA box sequences like:
    * TTATNCACA (N = any nucleotide)
    * TTATCCACA (most common)
  
Performance:
  - Analysis time: ~5-30 seconds (optimized algorithm)
  - Memory usage: ~100-500 MB
  
Note: This example uses a simulated genome. To analyze real E. coli,
download the genome from NCBI (GenBank: U00096.3) and use:
  
  genome = load_genome_from_file('ecoli_genome.fasta')
  results = find_origin_of_replication(genome, k=9, L=500, t=3)
    """)
    
    # Summary
    print("\n" + "=" * 70)
    print("KEY INSIGHTS FROM THIS WORKFLOW")
    print("=" * 70)
    print("""
1. Integration is key:
   - Multiple algorithms work together
   - Each provides complementary information
   - Combined results are more reliable than any single method

2. Computational biology workflow:
   - Data preprocessing (loading, cleaning)
   - Algorithm application (skew, clumps)
   - Visualization (understanding results)
   - Interpretation (biological meaning)
   - Validation (compare to known results)

3. Real-world complexity:
   - Genomes are noisy - not perfect patterns
   - Need robust algorithms (optimized, tested)
   - Parameters matter (k, L, t affect results)
   - Biological knowledge guides interpretation

4. From computation to biology:
   - Algorithms find candidate positions
   - Biologists verify experimentally
   - Confirmed origins guide further research
   - Iterative process of discovery

5. Broader applications:
   - This pipeline works for any bacterial genome
   - Can be adapted for other pattern-finding problems
   - Demonstrates power of computational biology
   - Shows why programming is essential for modern biology
    """)
