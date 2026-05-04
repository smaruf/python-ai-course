#!/usr/bin/env python3
"""
Test suite for the rosalind-dna module.
Run this file to verify all three Rosalind problems are working correctly.

Problems covered:
  01  DNA  – Counting DNA Nucleotides
  02  REVC – Complementing a Strand of DNA
  03  GC   – Computing GC Content
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
# TEST 1: DNA – Counting DNA Nucleotides
# ─────────────────────────────────────────────────────────────────────────────

def test_dna():
    print("\n" + "=" * 70)
    print("TEST 1: DNA – Counting DNA Nucleotides")
    print("=" * 70)

    mod = load_module('01_count_nucleotides.py')

    # Rosalind sample dataset
    sample = "AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC"
    counts = mod.count_nucleotides(sample)
    assert counts == {'A': 20, 'C': 12, 'G': 17, 'T': 21}, \
        f"Expected {{'A':20,'C':12,'G':17,'T':21}}, got {counts}"
    print(f"✓ Sample dataset counts: A={counts['A']} C={counts['C']} G={counts['G']} T={counts['T']}")

    # format_counts produces correct string
    result = mod.format_counts(counts)
    assert result == "20 12 17 21", f"Expected '20 12 17 21', got '{result}'"
    print(f"✓ format_counts output: '{result}'")

    # Empty string returns all-zero dict
    empty = mod.count_nucleotides("")
    assert empty == {'A': 0, 'C': 0, 'G': 0, 'T': 0}
    print("✓ Empty string → all zeros")

    # Single-character strings
    for base in "ACGT":
        c = mod.count_nucleotides(base)
        assert c[base] == 1
        assert sum(c.values()) == 1
    print("✓ Single-character inputs count correctly")

    # All same base
    counts_aaaa = mod.count_nucleotides("AAAA")
    assert counts_aaaa == {'A': 4, 'C': 0, 'G': 0, 'T': 0}
    print("✓ All-A string: A=4, C=0, G=0, T=0")

    # format_counts on all-zeros
    assert mod.format_counts({'A': 0, 'C': 0, 'G': 0, 'T': 0}) == "0 0 0 0"
    print("✓ format_counts on zeros: '0 0 0 0'")

    # Counts sum to length
    long_dna = "ACGTACGTACGT"
    c2 = mod.count_nucleotides(long_dna)
    assert sum(c2.values()) == len(long_dna)
    print(f"✓ Counts sum to sequence length ({len(long_dna)})")

    print("✓ All DNA tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: REVC – Reverse Complement
# ─────────────────────────────────────────────────────────────────────────────

def test_revc():
    print("\n" + "=" * 70)
    print("TEST 2: REVC – Complementing a Strand of DNA")
    print("=" * 70)

    mod = load_module('02_reverse_complement.py')

    # Rosalind sample dataset
    result = mod.reverse_complement("AAAACCCGGT")
    assert result == "ACCGGGTTTT", f"Expected 'ACCGGGTTTT', got '{result}'"
    print(f"✓ Sample dataset: AAAACCCGGT → {result}")

    # Individual complements
    assert mod.complement('A') == 'T'
    assert mod.complement('T') == 'A'
    assert mod.complement('C') == 'G'
    assert mod.complement('G') == 'C'
    print("✓ All four Watson-Crick complement rules correct")

    # Reverse complement of single bases
    assert mod.reverse_complement('A') == 'T'
    assert mod.reverse_complement('T') == 'A'
    assert mod.reverse_complement('C') == 'G'
    assert mod.reverse_complement('G') == 'C'
    print("✓ Reverse complement of single nucleotides correct")

    # Empty string
    assert mod.reverse_complement("") == ""
    print("✓ Empty string → empty string")

    # Palindrome: ACGT is its own reverse complement
    assert mod.reverse_complement("ACGT") == "ACGT"
    print("✓ ACGT is a palindrome (equals its own reverse complement)")

    # EcoRI recognition site palindrome
    assert mod.reverse_complement("GAATTC") == "GAATTC"
    print("✓ EcoRI site GAATTC is a palindrome")

    # Applying reverse complement twice returns the original
    original = "GCTAGCTAGC"
    assert mod.reverse_complement(mod.reverse_complement(original)) == original
    print(f"✓ RevComp(RevComp(s)) == s for '{original}'")

    # Invalid nucleotide raises ValueError
    try:
        mod.complement('X')
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ ValueError raised for invalid nucleotide 'X'")

    print("✓ All REVC tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: GC – Computing GC Content
# ─────────────────────────────────────────────────────────────────────────────

def test_gc():
    print("\n" + "=" * 70)
    print("TEST 3: GC – Computing GC Content")
    print("=" * 70)

    mod = load_module('03_gc_content.py')

    # Rosalind sample dataset
    sample_fasta = """\
>Rosalind_6404
CCTGCGGAAGATCGGCACTAGAATAGCCAGAACCGTTTCTCTGAGTTTACGCTTT
>Rosalind_5959
CCATCGGTAGCGCATCCTTAGTCCAATTAAGTCCCTATCCAGGCGCTCCGCCGAAGGTCTATATCCATTT
>Rosalind_0808
CCACCCTCGTGGTATGGCTAGGCATTCAGGAACCGGAGAACGCTTCAGACCAGCCCGGACTGGGAACCTGCGGGCAGTAGGTGGAAT
"""
    label, pct = mod.highest_gc(sample_fasta)
    assert label == "Rosalind_0808", f"Expected 'Rosalind_0808', got '{label}'"
    assert abs(pct - 60.919540) < 1e-4, f"Expected ~60.919540%, got {pct}"
    print(f"✓ Sample dataset winner: {label} ({pct:.6f}%)")

    # gc_content basic values
    assert mod.gc_content("GGCC") == 1.0
    print("✓ GGCC → GC content 1.0")

    assert mod.gc_content("AATT") == 0.0
    print("✓ AATT → GC content 0.0")

    assert mod.gc_content("ACGT") == 0.5
    print("✓ ACGT → GC content 0.5")

    # gc_content single bases
    assert mod.gc_content("G") == 1.0
    assert mod.gc_content("C") == 1.0
    assert mod.gc_content("A") == 0.0
    assert mod.gc_content("T") == 0.0
    print("✓ Single-base GC content correct for all four bases")

    # gc_content raises on empty string
    try:
        mod.gc_content("")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ ValueError raised for empty sequence")

    # parse_fasta single record
    parsed = mod.parse_fasta(">seq1\nACGT")
    assert parsed == {'seq1': 'ACGT'}, f"Got {parsed}"
    print("✓ parse_fasta single-record correct")

    # parse_fasta multi-line sequence
    multi = ">seq1\nAC\nGT\nAC"
    parsed2 = mod.parse_fasta(multi)
    assert parsed2 == {'seq1': 'ACGTAC'}, f"Got {parsed2}"
    print("✓ parse_fasta concatenates multi-line sequences")

    # parse_fasta two records
    two = ">seq1\nACGT\n>seq2\nTTTT"
    parsed3 = mod.parse_fasta(two)
    assert parsed3 == {'seq1': 'ACGT', 'seq2': 'TTTT'}
    print("✓ parse_fasta handles two records correctly")

    # highest_gc with two records: all-GC wins over all-AT
    simple = ">A\nGGGG\n>B\nAAAA"
    lbl, p = mod.highest_gc(simple)
    assert lbl == 'A' and p == 100.0
    print("✓ highest_gc selects all-GC record (100.0%)")

    print("✓ All GC tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("ROSALIND DNA BASICS – TEST SUITE (Sessions 1–2)")
    print("=" * 70)
    print("Testing DNA | REVC | GC\n")

    tests = [test_dna, test_revc, test_gc]
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
