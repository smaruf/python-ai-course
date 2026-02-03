"""
Algorithm Optimization Comparison
==================================

This module demonstrates the dramatic performance differences between naive
and optimized implementations of the clump finding algorithm.

Key Optimization Strategies:
1. Sliding Window: Reuse computation from previous window instead of recalculating
2. Hash Tables: Use dictionaries for O(1) lookups instead of O(n) searches
3. Avoid Recomputation: Calculate once, update incrementally
4. Memory Trade-offs: Sometimes using more memory improves speed

Learning Objectives:
- Understand Big O notation in practice
- Measure and compare algorithm performance
- Apply sliding window optimization technique
- Use profiling to identify bottlenecks
- Make informed trade-offs between time and space complexity
"""

import time
import random
from typing import Callable, Dict, List, Tuple
import sys
import os
import importlib.util

# Import clump finding functions from module 01
# Note: Using importlib since filename starts with number
import importlib.util

def import_module_from_file(module_name, file_path):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import the clump finding module
_clump_module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '01_clump_finding.py')
_clump_module = import_module_from_file('clump_finding', _clump_module_path)
find_clumps_naive = _clump_module.find_clumps_naive
find_clumps_optimized = _clump_module.find_clumps_optimized


def generate_random_genome(length: int, seed: int = None) -> str:
    """
    Generate a random DNA sequence for testing.
    
    Args:
        length: Number of base pairs to generate
        seed: Random seed for reproducibility
        
    Returns:
        Random DNA string of specified length
        
    Example:
        >>> genome = generate_random_genome(100, seed=42)
        >>> len(genome)
        100
        >>> all(c in 'ACGT' for c in genome)
        True
    """
    if seed is not None:
        random.seed(seed)
    
    nucleotides = ['A', 'C', 'G', 'T']
    return ''.join(random.choice(nucleotides) for _ in range(length))


def generate_genome_with_clumps(length: int, k: int, num_clumps: int = 5,
                                clump_region_length: int = 500) -> str:
    """
    Generate a genome with intentionally planted clumps for testing.
    
    This creates a more realistic test case where we know clumps exist.
    
    Args:
        length: Total genome length
        k: k-mer length
        num_clumps: Number of clumped k-mers to plant
        clump_region_length: Length of region where clumps appear frequently
        
    Returns:
        DNA string with planted clumps
    """
    genome = list(generate_random_genome(length))
    
    for _ in range(num_clumps):
        # Create a random k-mer to be a clump
        kmer = generate_random_genome(k)
        
        # Choose a random region to plant the clump
        region_start = random.randint(0, length - clump_region_length)
        
        # Plant this k-mer multiple times in the region
        for _ in range(5):  # Appear at least 5 times
            pos = random.randint(region_start, region_start + clump_region_length - k)
            genome[pos:pos + k] = list(kmer)
    
    return ''.join(genome)


def time_function(func: Callable, *args, **kwargs) -> Tuple[float, any]:
    """
    Time the execution of a function.
    
    Args:
        func: Function to time
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Tuple of (execution_time_seconds, function_result)
        
    Example:
        >>> duration, result = time_function(find_clumps_naive, "ACGT"*100, 3, 50, 2)
        >>> duration > 0
        True
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    return end_time - start_time, result


def format_time(seconds: float) -> str:
    """
    Format time duration for human-readable output.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (ms, seconds, or minutes)
    """
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} seconds"
    else:
        return f"{seconds / 60:.2f} minutes"


def compare_algorithms(genome: str, k: int, L: int, t: int, 
                       verbose: bool = True) -> Dict[str, any]:
    """
    Compare naive vs optimized clump finding algorithms.
    
    Args:
        genome: DNA string to analyze
        k: k-mer length
        L: window length
        t: frequency threshold
        verbose: Whether to print detailed results
        
    Returns:
        Dictionary with timing and speedup information
        
    Example:
        >>> genome = generate_random_genome(10000, seed=42)
        >>> results = compare_algorithms(genome, 9, 500, 3, verbose=False)
        >>> results['speedup'] > 1.0  # Optimized should be faster
        True
    """
    if verbose:
        print(f"\nComparing algorithms on genome of length {len(genome)}")
        print(f"Parameters: k={k}, L={L}, t={t}")
        print("-" * 60)
    
    # Time naive implementation
    if verbose:
        print("Running naive implementation...")
    naive_time, naive_result = time_function(find_clumps_naive, genome, k, L, t)
    
    # Time optimized implementation
    if verbose:
        print("Running optimized implementation...")
    opt_time, opt_result = time_function(find_clumps_optimized, genome, k, L, t)
    
    # Calculate speedup
    speedup = naive_time / opt_time if opt_time > 0 else float('inf')
    
    # Verify results match
    results_match = naive_result == opt_result
    
    if verbose:
        print(f"\nResults:")
        print(f"  Naive algorithm:     {format_time(naive_time)}")
        print(f"  Optimized algorithm: {format_time(opt_time)}")
        print(f"  Speedup:             {speedup:.2f}x faster")
        print(f"  Results match:       {results_match}")
        print(f"  Clumps found:        {len(naive_result)}")
    
    return {
        'naive_time': naive_time,
        'optimized_time': opt_time,
        'speedup': speedup,
        'results_match': results_match,
        'num_clumps': len(naive_result),
        'genome_length': len(genome)
    }


def benchmark_scaling(sizes: List[int], k: int = 9, L: int = 500, 
                     t: int = 3) -> None:
    """
    Benchmark both algorithms across different genome sizes.
    
    This demonstrates how algorithm complexity affects real performance.
    
    Args:
        sizes: List of genome sizes to test
        k: k-mer length
        L: window length  
        t: frequency threshold
    """
    print("\n" + "=" * 70)
    print("SCALING BENCHMARK - How algorithms perform as input size grows")
    print("=" * 70)
    print(f"Parameters: k={k}, L={L}, t={t}\n")
    print(f"{'Size':>10} {'Naive':>15} {'Optimized':>15} {'Speedup':>10}")
    print("-" * 70)
    
    for size in sizes:
        genome = generate_random_genome(size, seed=42)
        
        # Skip naive for very large sizes (would take too long)
        if size > 50000:
            print(f"{size:>10,} {'(skipped)':>15} ", end='')
            opt_time, _ = time_function(find_clumps_optimized, genome, k, L, t)
            print(f"{format_time(opt_time):>15} {'N/A':>10}")
        else:
            results = compare_algorithms(genome, k, L, t, verbose=False)
            print(f"{size:>10,} {format_time(results['naive_time']):>15} "
                  f"{format_time(results['optimized_time']):>15} "
                  f"{results['speedup']:>9.1f}x")


def analyze_complexity() -> None:
    """
    Explain the theoretical complexity of both algorithms.
    """
    print("\n" + "=" * 70)
    print("COMPLEXITY ANALYSIS")
    print("=" * 70)
    print("""
Naive Algorithm:
----------------
Time Complexity: O((n - L + 1) × L × k)
  - For each window position: O(n - L)
  - For each k-mer in window: O(L - k)  
  - For each character in k-mer: O(k)
  
With typical values (n=100,000, L=500, k=9):
  ≈ 100,000 × 500 × 9 = 450,000,000 operations!

Space Complexity: O(L)
  - Store frequency map for current window
  - Plus set of clumps found

Optimized Algorithm (Sliding Window):
-------------------------------------
Time Complexity: O(n × k)
  - Process each position once: O(n)
  - String slicing for k-mer: O(k)
  
With typical values (n=100,000, k=9):
  ≈ 100,000 × 9 = 900,000 operations
  
This is ~500x fewer operations!

Space Complexity: O(4^k) in worst case
  - Frequency map could store all possible k-mers
  - For k=9: 4^9 = 262,144 possible k-mers
  - In practice, much smaller due to genome composition

Key Optimization Insight:
-------------------------
Instead of recalculating k-mer frequencies for each window,
we REUSE the previous window's frequencies:
  - Remove one k-mer (from left)
  - Add one k-mer (from right)
  - Update frequencies incrementally
  
This transforms O(L) work per window to O(1) work per window!
    """)


# Example Usage and Testing
if __name__ == "__main__":
    print("=" * 70)
    print("ALGORITHM OPTIMIZATION COMPARISON")
    print("=" * 70)
    
    # Test 1: Small genome - both algorithms
    print("\nTest 1: Small genome (can run both algorithms)")
    small_genome = generate_random_genome(5000, seed=42)
    compare_algorithms(small_genome, k=9, L=500, t=3)
    
    # Test 2: Medium genome
    print("\n\nTest 2: Medium genome")
    medium_genome = generate_random_genome(20000, seed=42)
    compare_algorithms(medium_genome, k=9, L=500, t=3)
    
    # Test 3: Large genome (only optimized)
    print("\n\nTest 3: Large genome (optimized only - naive would be too slow)")
    large_genome = generate_random_genome(100000, seed=42)
    print(f"Genome length: {len(large_genome)}")
    print("Running optimized algorithm only...")
    opt_time, result = time_function(find_clumps_optimized, large_genome, 9, 500, 3)
    print(f"Time: {format_time(opt_time)}")
    print(f"Clumps found: {len(result)}")
    
    # Test 4: Scaling benchmark
    print("\n\nTest 4: Scaling across different sizes")
    benchmark_scaling([1000, 5000, 10000, 20000, 50000, 100000])
    
    # Show complexity analysis
    analyze_complexity()
    
    # Summary
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("""
1. Algorithm choice matters enormously!
   - Optimized version can be 100x-1000x faster
   
2. Understanding complexity helps predict performance
   - O(n²) vs O(n) makes huge difference at scale
   
3. Optimization strategies:
   - Avoid redundant computation (sliding window)
   - Use efficient data structures (hash tables)
   - Trade space for time when beneficial
   
4. Real-world impact:
   - E. coli genome: ~4.6 million bp
   - Naive: Would take hours or days
   - Optimized: Takes seconds
   
5. Always measure performance!
   - Don't guess which code is faster
   - Use profiling and benchmarks
   - Optimize bottlenecks, not everything
    """)
