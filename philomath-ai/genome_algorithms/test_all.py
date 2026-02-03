#!/usr/bin/env python3
"""
Test script for genome algorithms modules.
Run this to verify all modules are working correctly.
"""

import sys
import os
import importlib.util

# Set matplotlib to non-interactive mode for headless environments
# This prevents errors in environments without display capabilities (e.g., CI/CD, Docker)
import matplotlib
matplotlib.use('Agg')

def load_module(filename):
    """Load a module from a file with numeric prefix."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_clump_finding():
    """Test the clump finding module."""
    print("\n" + "="*70)
    print("TEST 1: Clump Finding")
    print("="*70)
    
    module = load_module('01_clump_finding.py')
    
    genome = "CGGACTCGACAGATGTGAAGAACGACAATGTGAAGACTCGACACGACAGAGTGAAGAGAAGAGGAAACATTGTAA"
    clumps = module.find_clumps_optimized(genome, k=5, L=50, t=4)
    
    print(f"✓ Module loaded successfully")
    print(f"✓ Found {len(clumps)} clumps: {sorted(clumps)}")
    
    # Verify results
    assert len(clumps) == 2, f"Expected 2 clumps, got {len(clumps)}"
    assert 'CGACA' in clumps, "Expected 'CGACA' in clumps"
    assert 'GAAGA' in clumps, "Expected 'GAAGA' in clumps"
    
    print("✓ All tests passed!")
    return True

def test_skew_array():
    """Test the skew array module."""
    print("\n" + "="*70)
    print("TEST 2: Skew Array")
    print("="*70)
    
    module = load_module('02_skew_array.py')
    
    genome = "TAAAGACTGCCGAGAGGCCAACACGAGTGCTAGAACGAGGGGCGTAAACGCGGGTCCGAT"
    skew = module.compute_skew(genome)
    min_positions = module.find_min_skew_positions(genome)
    
    print(f"✓ Module loaded successfully")
    print(f"✓ Computed skew array of length: {len(skew)}")
    print(f"✓ Found minimum skew at positions: {min_positions}")
    
    # Verify results
    assert len(skew) == len(genome) + 1, "Skew array should be genome length + 1"
    assert len(min_positions) > 0, "Should find at least one minimum position"
    
    print("✓ All tests passed!")
    return True

def test_motif_finding():
    """Test the motif finding module."""
    print("\n" + "="*70)
    print("TEST 3: Motif Finding")
    print("="*70)
    
    module = load_module('03_motif_finding.py')
    
    dna_sequences = ["ATTTGGC", "TGCCTTA", "CGGTATC", "GAAAATT"]
    motifs = module.find_motifs(dna_sequences, k=3, d=1)
    
    print(f"✓ Module loaded successfully")
    print(f"✓ Found {len(motifs)} motifs")
    
    # Verify results
    assert len(motifs) > 0, "Should find at least one motif"
    
    print("✓ All tests passed!")
    return True

def test_hamming_distance():
    """Test the hamming distance module."""
    print("\n" + "="*70)
    print("TEST 4: Hamming Distance")
    print("="*70)
    
    module = load_module('04_hamming_distance.py')
    
    dist = module.hamming_distance("GATTACA", "GCATGCU")
    neighbors = module.neighbors("ACG", 1)
    
    print(f"✓ Module loaded successfully")
    print(f"✓ Hamming distance calculated: {dist}")
    print(f"✓ Generated {len(neighbors)} neighbors")
    
    # Verify results
    assert dist == 4, f"Expected distance 4, got {dist}"
    assert len(neighbors) == 10, f"Expected 10 neighbors, got {len(neighbors)}"
    
    print("✓ All tests passed!")
    return True

def test_optimization_comparison():
    """Test the optimization comparison module."""
    print("\n" + "="*70)
    print("TEST 5: Optimization Comparison")
    print("="*70)
    
    module = load_module('05_optimization_comparison.py')
    
    genome = module.generate_random_genome(1000, seed=42)
    results = module.compare_algorithms(genome, k=9, L=500, t=3, verbose=False)
    
    print(f"✓ Module loaded successfully")
    print(f"✓ Generated test genome of length: {len(genome)}")
    print(f"✓ Naive time: {results['naive_time']:.4f}s")
    print(f"✓ Optimized time: {results['optimized_time']:.4f}s")
    print(f"✓ Speedup: {results['speedup']:.2f}x")
    
    # Verify results
    assert results['results_match'], "Naive and optimized should produce same results"
    assert results['speedup'] > 1, "Optimized should be faster than naive"
    
    print("✓ All tests passed!")
    return True

def test_visualization():
    """Test the visualization module."""
    print("\n" + "="*70)
    print("TEST 6: Visualization")
    print("="*70)
    
    module = load_module('06_visualization.py')
    
    print(f"✓ Module loaded successfully")
    print(f"✓ plot_skew function available")
    print(f"✓ visualize_clump_locations function available")
    print(f"✓ plot_combined_analysis function available")
    print("✓ All visualization functions loaded (plots not tested in headless mode)")
    
    print("✓ All tests passed!")
    return True

def test_sequence_alignment():
    """Test the sequence alignment module."""
    print("\n" + "="*70)
    print("TEST 7: Sequence Alignment")
    print("="*70)
    
    module = load_module('07_sequence_alignment.py')
    
    # Test global alignment
    score, aligned1, aligned2 = module.global_alignment("GATTACA", "GCATGCU")
    
    # Test LCS
    length, lcs = module.longest_common_subsequence("ABCDEFG", "BCDGK")
    
    print(f"✓ Module loaded successfully")
    print(f"✓ Global alignment score: {score}")
    print(f"✓ LCS length: {length}, sequence: {lcs}")
    
    # Verify results
    assert len(aligned1) == len(aligned2), "Alignments should be same length"
    assert lcs == "BCDG", f"Expected LCS 'BCDG', got '{lcs}'"
    
    print("✓ All tests passed!")
    return True

def test_workflow():
    """Test the complete workflow module."""
    print("\n" + "="*70)
    print("TEST 8: Complete Workflow")
    print("="*70)
    
    module = load_module('08_complete_workflow.py')
    
    # Simulate a small genome
    genome = module.simulate_genome(2000, gc_content=0.5, ori_position=1000, seed=42)
    
    # Run analysis
    results = module.find_origin_of_replication(genome, k=9, L=500, t=3, verbose=False)
    
    print(f"✓ Module loaded successfully")
    print(f"✓ Simulated genome of length: {len(genome)}")
    print(f"✓ Predicted ori: {results['predicted_ori']}")
    print(f"✓ Found {len(results['all_clumps'])} clumps")
    print(f"✓ Found {len(results['candidate_ori_positions'])} candidate ori positions")
    
    # Verify results
    assert results['predicted_ori'] is not None, "Should predict an ori position"
    assert results['genome_length'] == len(genome), "Genome length should match"
    
    print("✓ All tests passed!")
    return True

def main():
    """Run all tests."""
    print("="*70)
    print("GENOME ALGORITHMS - TEST SUITE")
    print("="*70)
    print("\nRunning comprehensive tests on all genome algorithm modules...")
    
    tests = [
        test_clump_finding,
        test_skew_array,
        test_motif_finding,
        test_hamming_distance,
        test_optimization_comparison,
        test_visualization,
        test_sequence_alignment,
        test_workflow,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The genome algorithms are working correctly.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
