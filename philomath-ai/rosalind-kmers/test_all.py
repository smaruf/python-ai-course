#!/usr/bin/env python3
"""
Test suite for the rosalind-kmers module.
Run this file to verify all three Rosalind problems are working correctly.

Problems covered:
  01  HAMM – Counting Point Mutations
  02  KMER – k-mer Composition
  03  SUBS – Finding a Motif in DNA
"""

import sys
import os
import importlib.util


def load_module(filename: str):
    """Load a Python module from a file path relative to this directory."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: HAMM – Counting Point Mutations
# ─────────────────────────────────────────────────────────────────────────────

def test_hamm():
    print("\n" + "=" * 70)
    print("TEST 1: HAMM – Counting Point Mutations")
    print("=" * 70)

    mod = load_module('01_hamming_distance.py')

    # Rosalind sample: s="GAGCCTACTAACGGGAT", t="CATCGTAATGACGGCCT" → 7
    result = mod.hamming_distance("GAGCCTACTAACGGGAT", "CATCGTAATGACGGCCT")
    assert result == 7, f"Expected 7, got {result}"
    print(f"✓ Sample dataset: Hamming distance = {result}")

    # Identical strings → 0
    assert mod.hamming_distance("ACGT", "ACGT") == 0
    print("✓ Identical strings → 0")

    # Completely different → length
    assert mod.hamming_distance("ACGT", "TGCA") == 4
    print("✓ All-mismatch strings → 4")

    # Single character
    assert mod.hamming_distance("A", "A") == 0
    assert mod.hamming_distance("A", "T") == 1
    print("✓ Single-character cases pass")

    # ValueError on unequal lengths
    try:
        mod.hamming_distance("ACG", "AC")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ ValueError raised for unequal-length strings")

    # similar_positions
    sim = mod.similar_positions("GAGCCTACTAACGGGAT", "CATCGTAATGACGGCCT")
    assert len(sim) == len("GAGCCTACTAACGGGAT") - 7
    print(f"✓ similar_positions: {len(sim)} matching positions")

    # mismatch_positions
    mis = mod.mismatch_positions("GAGCCTACTAACGGGAT", "CATCGTAATGACGGCCT")
    assert len(mis) == 7
    assert mis == [0, 2, 4, 7, 9, 14, 15]
    print(f"✓ mismatch_positions: {mis}")

    # Consistency: similar + mismatches = full length
    s = "GAGCCTACTAACGGGAT"
    t = "CATCGTAATGACGGCCT"
    assert len(mod.similar_positions(s, t)) + len(mod.mismatch_positions(s, t)) == len(s)
    print("✓ similar + mismatch positions sum to string length")

    print("✓ All HAMM tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: KMER – k-mer Composition
# ─────────────────────────────────────────────────────────────────────────────

def test_kmer():
    print("\n" + "=" * 70)
    print("TEST 2: KMER – k-mer Composition")
    print("=" * 70)

    mod = load_module('02_kmer_composition.py')

    # kmer_count basics
    counts = mod.kmer_count("ACGT", 2)
    assert counts == {'AC': 1, 'CG': 1, 'GT': 1}, f"Got {counts}"
    print(f"✓ kmer_count('ACGT', 2) = {counts}")

    counts_aa = mod.kmer_count("AAAA", 2)
    assert counts_aa == {'AA': 3}, f"Got {counts_aa}"
    print(f"✓ kmer_count('AAAA', 2) = {counts_aa}")

    # Total k-mers in a string of length L with window k = L - k + 1
    dna = "ACGTACGT"
    k = 3
    all_observed = mod.kmer_count(dna, k)
    assert sum(all_observed.values()) == len(dna) - k + 1
    print(f"✓ Total 3-mers in '{dna}' = {sum(all_observed.values())} (= {len(dna)}-{k}+1)")

    # all_kmers: length and first/last
    kmers1 = mod.all_kmers(1)
    assert kmers1 == ['A', 'C', 'G', 'T']
    print(f"✓ all_kmers(1) = {kmers1}")

    kmers4 = mod.all_kmers(4)
    assert len(kmers4) == 256
    assert kmers4[0] == 'AAAA'
    assert kmers4[-1] == 'TTTT'
    print(f"✓ all_kmers(4): length=256, first='AAAA', last='TTTT'")

    kmers2_ac = mod.all_kmers(2, alphabet="AC")
    assert kmers2_ac == ['AA', 'AC', 'CA', 'CC']
    print(f"✓ all_kmers(2, 'AC') = {kmers2_ac}")

    # kmer_composition: length is always 4^k
    comp4 = mod.kmer_composition("ACGT", 4)
    assert len(comp4) == 256
    assert sum(comp4) == 1  # only one 4-mer in a 4-char string
    print(f"✓ kmer_composition('ACGT', 4): length=256, sum=1")

    # Nucleotide composition (k=1) for AAAA
    comp1 = mod.kmer_composition("AAAA", 1)
    assert comp1 == [4, 0, 0, 0], f"Got {comp1}"
    print(f"✓ kmer_composition('AAAA', 1) = {comp1}")

    # Rosalind sample: dna="CTTCGAAAGTTTGGGCCGCTTTGGCCC", k=4
    sample_dna = "CTTCGAAAGTTTGGGCCGCTTTGGCCC"
    sample_comp = mod.kmer_composition(sample_dna, 4)
    assert len(sample_comp) == 256
    # Sum of all counts = len(dna) - k + 1
    assert sum(sample_comp) == len(sample_dna) - 4 + 1
    print(f"✓ Rosalind sample: 256 values, sum={sum(sample_comp)}")

    # Spot-check a specific k-mer: count 'CGCT' in sample_dna
    expected_cgct = sample_dna.count("CGCT")
    # find index of CGCT in all_kmers
    cgct_idx = mod.all_kmers(4).index("CGCT")
    assert sample_comp[cgct_idx] == expected_cgct
    print(f"✓ 'CGCT' count in sample = {expected_cgct} at lex index {cgct_idx}")

    print("✓ All KMER tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: SUBS – Finding a Motif in DNA
# ─────────────────────────────────────────────────────────────────────────────

def test_subs():
    print("\n" + "=" * 70)
    print("TEST 3: SUBS – Finding a Motif in DNA")
    print("=" * 70)

    mod = load_module('03_finding_motif.py')

    # Rosalind sample: dna="GATATATGCATATACTT", motif="ATAT" → [2, 4, 10]
    result = mod.find_motif("GATATATGCATATACTT", "ATAT")
    assert result == [2, 4, 10], f"Expected [2, 4, 10], got {result}"
    print(f"✓ Sample dataset: {result}")

    # Overlapping 'AA' in 'AAAA' → [1, 2, 3] (1-indexed)
    result2 = mod.find_motif("AAAA", "AA")
    assert result2 == [1, 2, 3], f"Expected [1, 2, 3], got {result2}"
    print(f"✓ Overlapping 'AA' in 'AAAA': {result2}")

    # No match → empty list
    result3 = mod.find_motif("ACGT", "TTTT")
    assert result3 == [], f"Expected [], got {result3}"
    print("✓ No match returns []")

    # Single position match
    result4 = mod.find_motif("ACGT", "CG")
    assert result4 == [2], f"Expected [2], got {result4}"
    print(f"✓ 'CG' in 'ACGT': {result4}")

    # Motif equals the full string
    result5 = mod.find_motif("ACGT", "ACGT")
    assert result5 == [1], f"Expected [1], got {result5}"
    print(f"✓ Full-string motif match: {result5}")

    # Motif at the end — overlapping 'TT' in 'ACGTTT'
    result6 = mod.find_motif("ACGTTT", "TT")
    assert result6 == [4, 5], f"Expected [4, 5], got {result6}"
    print(f"✓ End-of-string overlapping 'TT' in 'ACGTTT': {result6}")

    # 0-indexed variant
    zero = mod.find_motif_zero_indexed("GATATATGCATATACTT", "ATAT")
    assert zero == [1, 3, 9], f"Expected [1, 3, 9], got {zero}"
    print(f"✓ find_motif_zero_indexed: {zero}")

    # Relationship: 0-indexed = 1-indexed − 1
    one_based = mod.find_motif("GATATATGCATATACTT", "ATAT")
    zero_based = mod.find_motif_zero_indexed("GATATATGCATATACTT", "ATAT")
    assert all(z == o - 1 for z, o in zip(zero_based, one_based))
    print("✓ 0-indexed positions = 1-indexed − 1 for all matches")

    print("✓ All SUBS tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("ROSALIND k-MERS & DISTANCE – TEST SUITE (Sessions 3–4)")
    print("=" * 70)
    print("Testing HAMM | KMER | SUBS\n")

    tests = [test_hamm, test_kmer, test_subs]
    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as exc:
            import traceback
            print(f"✗ Test failed: {exc}")
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed} / {len(tests)}")
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
