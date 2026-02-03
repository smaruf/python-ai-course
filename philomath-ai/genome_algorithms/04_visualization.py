"""
Genomic Data Visualization
===========================

This module provides visualization tools for understanding genomic algorithms.
Visualizations are crucial for:
- Understanding algorithm behavior
- Identifying patterns in data
- Communicating results
- Debugging and validation

Learning Objectives:
- Create informative scientific plots
- Use matplotlib effectively
- Visualize algorithm results
- Present biological data clearly
"""

import sys
import os
from typing import List, Dict, Optional, Set
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import importlib.util

# Import functions from other modules using importlib
def import_module_from_file(module_name, file_path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

try:
    # Import skew module
    _skew_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '02_skew_array.py')
    _skew_module = import_module_from_file('skew_array', _skew_path)
    compute_skew = _skew_module.compute_skew
    find_min_skew_positions = _skew_module.find_min_skew_positions
    
    # Import clump finding module
    _clump_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '01_clump_finding.py')
    _clump_module = import_module_from_file('clump_finding', _clump_path)
    find_clumps_optimized = _clump_module.find_clumps_optimized
    pattern_count = _clump_module.pattern_count
except Exception as e:
    print(f"Warning: Could not import modules: {e}")
    # Fallback if modules have different naming
    pass


def plot_skew(genome: str, title: str = "Genome Skew Analysis", 
              figsize: tuple = (12, 6), save_path: Optional[str] = None) -> None:
    """
    Plot the skew array with minimum positions highlighted.
    
    This visualization helps identify the origin of replication by showing
    where the GC-skew reaches its minimum value.
    
    Args:
        genome: DNA string to analyze
        title: Plot title
        figsize: Figure size (width, height) in inches
        save_path: Optional path to save the figure
        
    Example:
        >>> genome = "TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT"
        >>> plot_skew(genome, "Test Genome Skew")
        # Creates a line plot showing skew values
    """
    # Compute skew array
    skew = compute_skew(genome)
    min_positions = find_min_skew_positions(genome)
    min_value = min(skew)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot skew line
    positions = list(range(len(skew)))
    ax.plot(positions, skew, 'b-', linewidth=2, label='Skew')
    
    # Highlight minimum positions
    if min_positions:
        ax.scatter(min_positions, [min_value] * len(min_positions), 
                  color='red', s=100, zorder=5, label='Minimum Skew (Candidate ori)')
        
        # Add vertical lines at minimum positions
        for pos in min_positions[:5]:  # Limit to first 5 to avoid clutter
            ax.axvline(x=pos, color='red', linestyle='--', alpha=0.3)
    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3, linewidth=1)
    
    # Labels and formatting
    ax.set_xlabel('Position in Genome (bp)', fontsize=12)
    ax.set_ylabel('Skew (#G - #C)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Add annotation with stats
    stats_text = (f"Genome length: {len(genome)} bp\n"
                 f"Min skew: {min_value}\n"
                 f"Max skew: {max(skew)}\n"
                 f"Candidate ori positions: {len(min_positions)}")
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           verticalalignment='top', bbox=dict(boxstyle='round', 
           facecolor='wheat', alpha=0.5), fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.show()


def visualize_clump_locations(genome: str, clumps: Set[str], k: int,
                              title: str = "Clump Distribution Heatmap",
                              figsize: tuple = (14, 8),
                              save_path: Optional[str] = None) -> None:
    """
    Visualize where clumps (frequent k-mers) appear in the genome.
    
    Creates a heatmap showing the density of clump occurrences across
    the genome, helping identify regions of interest.
    
    Args:
        genome: DNA string
        clumps: Set of k-mers identified as clumps
        k: k-mer length
        title: Plot title
        figsize: Figure size
        save_path: Optional path to save figure
        
    Example:
        >>> genome = "ACGT" * 100
        >>> clumps = {'ACG', 'CGT'}
        >>> visualize_clump_locations(genome, clumps, 3)
    """
    if not clumps:
        print("No clumps to visualize!")
        return
    
    # Create a matrix to store clump occurrences
    # Rows = different clumps, Columns = positions in genome
    window_size = 100  # Bin the genome into windows for visualization
    num_windows = (len(genome) - k + 1) // window_size + 1
    clump_list = sorted(list(clumps))
    
    # Initialize matrix
    heatmap_data = np.zeros((len(clump_list), num_windows))
    
    # Count occurrences of each clump in each window
    for clump_idx, clump in enumerate(clump_list):
        for i in range(len(genome) - k + 1):
            if genome[i:i + k] == clump:
                window_idx = i // window_size
                heatmap_data[clump_idx, window_idx] += 1
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, 
                                    gridspec_kw={'height_ratios': [3, 1]})
    
    # Heatmap
    im = ax1.imshow(heatmap_data, aspect='auto', cmap='YlOrRd', 
                   interpolation='nearest')
    
    # Labels
    ax1.set_ylabel('Clump k-mer', fontsize=12)
    ax1.set_yticks(range(len(clump_list)))
    ax1.set_yticklabels(clump_list, fontsize=8)
    ax1.set_title(title, fontsize=14, fontweight='bold')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax1)
    cbar.set_label('Occurrences per window', rotation=270, labelpad=20)
    
    # Total clump density across genome (sum of all clumps)
    total_density = np.sum(heatmap_data, axis=0)
    window_positions = [i * window_size for i in range(num_windows)]
    
    ax2.bar(window_positions, total_density, width=window_size, 
           color='steelblue', alpha=0.7, edgecolor='navy')
    ax2.set_xlabel('Position in Genome (bp)', fontsize=12)
    ax2.set_ylabel('Total Clumps', fontsize=12)
    ax2.set_title('Total Clump Density', fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add stats annotation
    total_occurrences = int(np.sum(heatmap_data))
    stats_text = (f"Genome length: {len(genome)} bp\n"
                 f"Number of clumps: {len(clumps)}\n"
                 f"k-mer length: {k}\n"
                 f"Total clump occurrences: {total_occurrences}\n"
                 f"Window size: {window_size} bp")
    ax2.text(0.98, 0.95, stats_text, transform=ax2.transAxes,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5),
            fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.show()


def plot_combined_analysis(genome: str, k: int, L: int, t: int,
                          title: str = "Combined Genome Analysis",
                          figsize: tuple = (14, 10),
                          save_path: Optional[str] = None) -> None:
    """
    Create a comprehensive multi-panel visualization combining:
    - Skew array plot
    - Clump distribution
    - Statistical summary
    
    Args:
        genome: DNA string
        k: k-mer length for clump finding
        L: window length for clump finding
        t: frequency threshold for clump finding
        title: Overall plot title
        figsize: Figure size
        save_path: Optional path to save figure
    """
    # Compute skew and find clumps
    skew = compute_skew(genome)
    min_positions = find_min_skew_positions(genome)
    clumps = find_clumps_optimized(genome, k, L, t)
    
    # Create figure with 3 subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 2, height_ratios=[2, 2, 1], width_ratios=[3, 1])
    
    # 1. Skew plot (top)
    ax1 = fig.add_subplot(gs[0, :])
    positions = list(range(len(skew)))
    ax1.plot(positions, skew, 'b-', linewidth=2, label='Skew')
    
    if min_positions:
        min_value = min(skew)
        ax1.scatter(min_positions, [min_value] * len(min_positions),
                   color='red', s=100, zorder=5, label='Min Skew')
    
    ax1.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax1.set_ylabel('Skew (#G - #C)', fontsize=11)
    ax1.set_title('GC Skew Analysis', fontsize=12, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # 2. Clump distribution (middle)
    ax2 = fig.add_subplot(gs[1, 0])
    
    if clumps:
        # Create simplified bar chart of clump positions
        clump_counts = {}
        for clump in clumps:
            count = pattern_count(genome, clump)
            clump_counts[clump] = count
        
        sorted_clumps = sorted(clump_counts.items(), key=lambda x: x[1], reverse=True)
        top_clumps = sorted_clumps[:10]  # Show top 10
        
        clump_names = [c[0] for c in top_clumps]
        clump_vals = [c[1] for c in top_clumps]
        
        y_pos = np.arange(len(clump_names))
        ax2.barh(y_pos, clump_vals, color='steelblue', alpha=0.7)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(clump_names, fontsize=9)
        ax2.set_xlabel('Occurrences in Genome', fontsize=11)
        ax2.set_title('Top Clumps (DnaA Box Candidates)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
    
    # 3. Statistics panel (middle right)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis('off')
    
    stats_text = "=== ANALYSIS SUMMARY ===\n\n"
    stats_text += f"Genome Length:\n  {len(genome):,} bp\n\n"
    stats_text += f"Skew Analysis:\n"
    stats_text += f"  Min: {min(skew)}\n"
    stats_text += f"  Max: {max(skew)}\n"
    stats_text += f"  Candidate ori: {len(min_positions)}\n\n"
    stats_text += f"Clump Finding:\n"
    stats_text += f"  Parameters: k={k}, L={L}, t={t}\n"
    stats_text += f"  Clumps found: {len(clumps)}\n\n"
    
    if clumps and min_positions:
        stats_text += f"Correlation:\n"
        stats_text += f"  Clumps near ori: TBD\n"
    
    ax3.text(0.1, 0.95, stats_text, transform=ax3.transAxes,
            verticalalignment='top', fontfamily='monospace',
            fontsize=9, bbox=dict(boxstyle='round', 
            facecolor='lightgray', alpha=0.5))
    
    # 4. Nucleotide composition (bottom)
    ax4 = fig.add_subplot(gs[2, :])
    
    nucleotide_counts = {
        'A': genome.count('A'),
        'C': genome.count('C'),
        'G': genome.count('G'),
        'T': genome.count('T')
    }
    
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    bars = ax4.bar(nucleotide_counts.keys(), nucleotide_counts.values(),
                   color=colors, alpha=0.7, edgecolor='black')
    
    ax4.set_ylabel('Count', fontsize=11)
    ax4.set_title('Nucleotide Composition', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add percentages on bars
    total = sum(nucleotide_counts.values())
    for bar, (nuc, count) in zip(bars, nucleotide_counts.items()):
        height = bar.get_height()
        pct = (count / total) * 100
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Overall title
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.show()


# Example Usage and Testing
if __name__ == "__main__":
    print("=== Genomic Data Visualization ===\n")
    
    # Import with proper error handling
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    def load_module(filename):
        """Load a genome algorithm module by filename."""
        path = os.path.join(base_dir, filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    # Load modules
    skew_module = load_module('02_skew_array.py')
    compute_skew = skew_module.compute_skew
    find_min_skew_positions = skew_module.find_min_skew_positions
    
    clump_module = load_module('01_clump_finding.py')
    find_clumps_optimized = clump_module.find_clumps_optimized
    
    # Example 1: Skew plot
    print("Example 1: Skew Array Visualization")
    print("-" * 50)
    genome1 = "TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT"
    print(f"Plotting skew for genome of length {len(genome1)}")
    plot_skew(genome1, "Example Genome - Skew Analysis")
    
    # Example 2: Clump distribution
    print("\nExample 2: Clump Distribution Visualization")
    print("-" * 50)
    # Create a genome with known clumps
    genome2 = (
        "CGGACTCGACAGATGTGAAGAACGACAATGTGAAGACTCGACACGACAGAGTGAAGAGAAGAGGAAACATTGTAA" * 5
    )
    clumps = find_clumps_optimized(genome2, k=5, L=75, t=4)
    print(f"Found {len(clumps)} clumps: {sorted(clumps)}")
    if clumps:
        visualize_clump_locations(genome2, clumps, k=5,
                                 title="Clump Distribution in Test Genome")
    
    # Example 3: Combined analysis
    print("\nExample 3: Combined Analysis")
    print("-" * 50)
    # Larger, more realistic genome
    import random
    random.seed(42)
    genome3 = ''.join(random.choice('ACGT') for _ in range(5000))
    # Add some intentional patterns
    pattern = "GCGCGCGCGC"
    for i in range(10):
        pos = random.randint(1000, 2000)
        genome3 = genome3[:pos] + pattern + genome3[pos+len(pattern):]
    
    print(f"Analyzing genome of length {len(genome3)}")
    plot_combined_analysis(genome3, k=9, L=500, t=3,
                          title="Comprehensive Genome Analysis Example")
    
    print("\n" + "=" * 70)
    print("VISUALIZATION GUIDELINES")
    print("=" * 70)
    print("""
1. Skew Plot:
   - Shows GC-skew across the genome
   - Minimum points (red) indicate candidate ori locations
   - Look for sharp valleys in the plot
   
2. Clump Distribution:
   - Heatmap shows where each clump appears
   - Bright regions indicate high clump density
   - Use to identify hotspots of biological significance
   
3. Combined Analysis:
   - Integrates multiple views of the same data
   - Helps correlate skew minima with clump locations
   - Provides statistical context
   
4. Best Practices:
   - Always label axes clearly
   - Include scale information (bp = base pairs)
   - Use color meaningfully (not just decoration)
   - Add statistical annotations
   - Save high-resolution versions (300 dpi) for papers
    """)
