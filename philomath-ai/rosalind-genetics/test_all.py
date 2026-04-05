#!/usr/bin/env python3
"""
Test suite for the rosalind-genetics module.
Run this file to verify all five Rosalind problems are working correctly.

Problems covered:
  01  IPRB – Mendel's First Law
  02  IEV  – Calculating Expected Offspring
  03  LIA  – Independent Alleles
  04  PROB – Introduction to Random Strings
  05  CONS – Consensus and Profile
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
# TEST 1: IPRB – Mendel's First Law
# ─────────────────────────────────────────────────────────────────────────────

def test_iprb():
    print("\n" + "=" * 70)
    print("TEST 1: IPRB – Mendel's First Law")
    print("=" * 70)

    mod = load_module('01_iprb_mendels_first_law.py')

    # Rosalind sample: k=2, m=2, n=2 → 0.78333
    result = mod.mendels_first_law(2, 2, 2)
    assert abs(result - 0.78333) < 1e-4, f"Expected ~0.78333, got {result}"
    print(f"✓ Sample dataset (2,2,2): {result:.5f}")

    # Edge cases
    assert mod.mendels_first_law(5, 0, 0) == 1.0
    print("✓ All AA → 1.0")

    assert mod.mendels_first_law(0, 0, 5) == 0.0
    print("✓ All aa → 0.0")

    assert abs(mod.mendels_first_law(0, 4, 0) - 0.75) < 1e-10
    print("✓ All Aa → 0.75")

    # breakdown function exists and sums to correct total
    breakdown = mod.mendels_law_all_crosses(2, 2, 2)
    total = sum(v['contribution'] for v in breakdown.values())
    assert abs(total - result) < 1e-10
    print(f"✓ Cross breakdown sums to {total:.5f}")

    print("✓ All IPRB tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: IEV – Calculating Expected Offspring
# ─────────────────────────────────────────────────────────────────────────────

def test_iev():
    print("\n" + "=" * 70)
    print("TEST 2: IEV – Calculating Expected Offspring")
    print("=" * 70)

    mod = load_module('02_iev_expected_offspring.py')

    # Rosalind sample: (1,0,0,1,0,1) → 3.5
    result = mod.expected_dominant_offspring(1, 0, 0, 1, 0, 1)
    assert result == 3.5, f"Expected 3.5, got {result}"
    print(f"✓ Sample dataset (1,0,0,1,0,1): {result}")

    # All aa-aa couples, 10 couples → 0 dominant offspring
    result2 = mod.expected_dominant_offspring(0, 0, 0, 0, 0, 10)
    assert result2 == 0.0
    print("✓ All aa-aa → 0.0")

    # All AA-AA couples, 10 couples → 20 dominant offspring (2 per couple)
    result3 = mod.expected_dominant_offspring(10, 0, 0, 0, 0, 0)
    assert result3 == 20.0
    print("✓ All AA-AA (10 couples) → 20.0")

    # breakdown function returns 6 rows with correct structure
    breakdown = mod.expected_offspring_breakdown(1, 0, 0, 1, 0, 1)
    assert len(breakdown) == 6
    for row in breakdown:
        assert {'cross', 'count', 'prob_dom', 'contribution'} == set(row.keys()), \
            f"Row missing expected keys: {row.keys()}"
    total = sum(row['contribution'] for row in breakdown)
    assert abs(total - 3.5) < 1e-10
    print(f"✓ Breakdown totals {total}")

    print("✓ All IEV tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: LIA – Independent Alleles
# ─────────────────────────────────────────────────────────────────────────────

def test_lia():
    print("\n" + "=" * 70)
    print("TEST 3: LIA – Independent Alleles")
    print("=" * 70)

    mod = load_module('03_lia_independent_alleles.py')

    # Rosalind sample: k=2, n=1 → 0.684
    result = mod.independent_alleles(2, 1)
    assert abs(result - 0.684) < 5e-4, f"Expected ~0.684, got {result}"
    print(f"✓ Sample dataset (k=2, n=1): {result:.3f}")

    # n=0 → always satisfied
    assert mod.independent_alleles(3, 0) == 1.0
    print("✓ n=0 → 1.0")

    # n > N → impossible
    assert mod.independent_alleles(1, 10) == 0.0
    print("✓ n > N → 0.0")

    # k=1: N=2, P(X>=1) = 1 - P(X=0) = 1 - (3/4)^2 = 7/16
    expected_k1 = 1 - (0.75 ** 2)
    result_k1 = mod.independent_alleles(1, 1)
    assert abs(result_k1 - expected_k1) < 1e-10
    print(f"✓ k=1, n=1: {result_k1:.6f}")

    # P(AaBb) per individual is always 0.25
    assert mod.prob_aabb(1) == 0.25
    assert mod.prob_aabb(5) == 0.25
    print("✓ P(AaBb) = 0.25 for all generations")

    # Distribution sums to 1
    dist = mod.independent_alleles_distribution(3)
    total = sum(p for _, p in dist)
    assert abs(total - 1.0) < 1e-10, f"Distribution sum = {total}"
    print(f"✓ Binomial distribution for k=3 sums to {total:.10f}")

    print("✓ All LIA tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: PROB – Introduction to Random Strings
# ─────────────────────────────────────────────────────────────────────────────

def test_prob():
    print("\n" + "=" * 70)
    print("TEST 4: PROB – Introduction to Random Strings")
    print("=" * 70)

    mod = load_module('04_prob_random_strings.py')

    s = "ACGATACAA"
    gc_values = [0.129, 0.287, 0.423, 0.499, 0.532, 0.81, 0.999]
    expected = [-5.737, -5.217, -5.263, -5.416, -5.51, -7.311, -20.711]

    result = mod.random_string_log_probs(s, gc_values)
    assert result == expected, f"Got {result}"
    print(f"✓ Sample dataset: {result}")

    # Single nucleotide probabilities
    import math
    lp_g = mod.nucleotide_log_prob('G', 0.5)
    assert abs(lp_g - math.log10(0.25)) < 1e-10
    print(f"✓ log10 P(G | GC=0.5) = {lp_g:.5f}")

    lp_a = mod.nucleotide_log_prob('A', 0.5)
    assert abs(lp_a - math.log10(0.25)) < 1e-10
    print(f"✓ log10 P(A | GC=0.5) = {lp_a:.5f}")

    # GC content helper
    assert mod.gc_content("GGCC") == 1.0
    assert mod.gc_content("AATT") == 0.0
    assert mod.gc_content("ACGT") == 0.5
    print("✓ GC content helper works correctly")

    # Invalid nucleotide raises ValueError
    try:
        mod.nucleotide_log_prob('X', 0.5)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ ValueError raised for invalid nucleotide")

    print("✓ All PROB tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: CONS – Consensus and Profile
# ─────────────────────────────────────────────────────────────────────────────

def test_cons():
    print("\n" + "=" * 70)
    print("TEST 5: CONS – Consensus and Profile")
    print("=" * 70)

    mod = load_module('05_cons_consensus_profile.py')

    fasta = """\
>Rosalind_1
ATCCAGCT
>Rosalind_2
GGGCAACT
>Rosalind_3
ATGGATCT
>Rosalind_4
AAGCAACC
>Rosalind_5
TTGGAACT
>Rosalind_6
ATGCCATT
>Rosalind_7
ATGGCACT
"""
    consensus, profile = mod.consensus_and_profile(fasta)

    assert consensus == "ATGCAACT", f"Expected 'ATGCAACT', got '{consensus}'"
    print(f"✓ Consensus: {consensus}")

    expected_profile = {
        'A': [5, 1, 0, 0, 5, 5, 0, 0],
        'C': [0, 0, 1, 4, 2, 0, 6, 1],
        'G': [1, 1, 6, 3, 0, 1, 0, 0],
        'T': [1, 5, 0, 0, 0, 1, 1, 6],
    }
    for nt in 'ACGT':
        assert profile[nt] == expected_profile[nt], (
            f"Profile row {nt}: got {profile[nt]}, expected {expected_profile[nt]}"
        )
    print("✓ Profile matrix correct")

    # FASTA parser handles multi-line sequences
    multi_line = ">seq1\nACGT\nACGT\n>seq2\nTTTT"
    parsed = mod.parse_fasta(multi_line)
    assert parsed == {'seq1': 'ACGTACGT', 'seq2': 'TTTT'}
    print("✓ Multi-line FASTA parsed correctly")

    # Build profile from identical sequences → all counts = len(seqs)
    seqs = ["AAAA", "AAAA", "AAAA"]
    p = mod.build_profile(seqs)
    assert p['A'] == [3, 3, 3, 3]
    assert p['C'] == [0, 0, 0, 0]
    print("✓ Profile for identical sequences correct")

    # Consensus on a tie resolves alphabetically (A beats C,G,T)
    tie_seqs = ["ACGT", "CAGT"]
    p_tie = mod.build_profile(tie_seqs)
    cons_tie = mod.consensus_string(p_tie)
    assert cons_tie[0] == 'A', f"Expected 'A' at pos 0 (tie A/C), got '{cons_tie[0]}'"
    print(f"✓ Tie-breaking: consensus starts with '{cons_tie[0]}' (alphabetical)")

    # Format profile output
    fmt = mod.format_profile(p)
    assert fmt.startswith("A: 3 3 3 3")
    print("✓ format_profile produces correct output")

    print("✓ All CONS tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("ROSALIND GENETICS – TEST SUITE (Episode 4)")
    print("=" * 70)
    print("Testing IPRB | IEV | LIA | PROB | CONS\n")

    tests = [test_iprb, test_iev, test_lia, test_prob, test_cons]
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
