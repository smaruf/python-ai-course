#!/usr/bin/env python3
"""
Test suite for the rosalind-assembly module.
Run this file to verify both Rosalind problems are working correctly.

Problems covered:
  01  LONG – Genome Assembly as Shortest Superstring
  02  CORR – Error Correction in Reads
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
# TEST 1: LONG – Genome Assembly as Shortest Superstring
# ─────────────────────────────────────────────────────────────────────────────

def test_long():
    print("\n" + "=" * 70)
    print("TEST 1: LONG – Genome Assembly as Shortest Superstring")
    print("=" * 70)

    mod = load_module('01_shortest_superstring.py')

    # --- overlap() ---

    # Rosalind sample overlap: suffix "AGACCTG" (len 7) of ATTAGACCTG
    # matches prefix of AGACCTGCCG
    assert mod.overlap("ATTAGACCTG", "AGACCTGCCG") == 7
    print("✓ overlap(ATTAGACCTG, AGACCTGCCG) = 7")

    # Three-character overlap: ATCGG ends "CGG", CGGTA starts "CGG"
    assert mod.overlap("ATCGG", "CGGTA") == 3
    print("✓ overlap(ATCGG, CGGTA) = 3")

    # Three-character overlap: ACGT ends "CGT", CGTA starts "CGT"
    assert mod.overlap("ACGT", "CGTA") == 3
    print("✓ overlap(ACGT, CGTA) = 3")

    # No shared suffix/prefix characters at all
    assert mod.overlap("AAAA", "TTTT") == 0
    print("✓ overlap(AAAA, TTTT) = 0  (no overlap)")

    # Single-character overlap
    assert mod.overlap("ACGT", "TGCA") == 1
    print("✓ overlap(ACGT, TGCA) = 1  (single-char overlap)")

    # When b is an extension of a: full-length overlap of a
    assert mod.overlap("ACGT", "ACGTTT") == 4
    print("✓ overlap(ACGT, ACGTTT) = 4  (a is prefix of b)")

    # --- shortest_superstring() with Rosalind LONG sample ---
    sample_reads = ["ATTAGACCTG", "CCTGCCGGAA", "AGACCTGCCG", "GCCGGAATAC"]
    result = mod.shortest_superstring(sample_reads)
    expected = "ATTAGACCTGCCGGAATAC"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Rosalind LONG sample → '{result}'")

    # Verify result contains every read as a substring
    for read in sample_reads:
        assert read in result, f"Read '{read}' missing from superstring '{result}'"
    print("✓ All reads are substrings of the assembled superstring")

    # Verify the assembly is minimal (no shorter string could contain all reads)
    # The Rosalind problem guarantees a unique Hamiltonian path, so 19 chars
    assert len(result) == 19
    print(f"✓ Superstring length = {len(result)} (expected 19)")

    # --- Two-read assembly ---
    two_reads = ["AACGT", "CGTTA"]
    # overlap("AACGT", "CGTTA") → AACGT[-3:] = "CGT", CGTTA[:3] = "CGT" → 3
    two_result = mod.shortest_superstring(two_reads)
    assert two_result == "AACGTTA", f"Expected 'AACGTTA', got '{two_result}'"
    print(f"✓ Two-read assembly ['AACGT','CGTTA'] → '{two_result}'")

    # --- Single-read edge case ---
    single = mod.shortest_superstring(["ATCG"])
    assert single == "ATCG"
    print(f"✓ Single-read assembly ['ATCG'] → '{single}'")

    # --- parse_fasta() ---
    long_fasta = """\
>Rosalind_56
ATTAGACCTG
>Rosalind_57
CCTGCCGGAA
>Rosalind_58
AGACCTGCCG
>Rosalind_59
GCCGGAATAC
"""
    parsed = mod.parse_fasta(long_fasta)
    assert len(parsed) == 4, f"Expected 4 sequences, got {len(parsed)}"
    assert parsed[0] == "ATTAGACCTG"
    assert parsed[3] == "GCCGGAATAC"
    print("✓ parse_fasta returns 4 sequences in FASTA order")

    # Multi-line sequence concatenation
    multi = ">id1\nACGT\nACGT\n>id2\nGGGG"
    parsed_multi = mod.parse_fasta(multi)
    assert parsed_multi == ["ACGTACGT", "GGGG"]
    print("✓ parse_fasta concatenates multi-line sequences correctly")

    # FASTA round-trip: parsing then assembling gives correct superstring
    rt_reads = mod.parse_fasta(long_fasta)
    rt_result = mod.shortest_superstring(rt_reads)
    assert rt_result == expected
    print(f"✓ FASTA parse → assemble round-trip → '{rt_result}'")

    print("✓ All LONG tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: CORR – Error Correction in Reads
# ─────────────────────────────────────────────────────────────────────────────

def test_corr():
    print("\n" + "=" * 70)
    print("TEST 2: CORR – Error Correction in Reads")
    print("=" * 70)

    mod = load_module('02_error_correction.py')

    # --- reverse_complement() ---
    assert mod.reverse_complement("AAAACCCGGT") == "ACCGGGTTTT"
    print("✓ reverse_complement(AAAACCCGGT) = ACCGGGTTTT")

    assert mod.reverse_complement("ATCG") == "CGAT"
    print("✓ reverse_complement(ATCG) = CGAT")

    assert mod.reverse_complement("AAAA") == "TTTT"
    print("✓ reverse_complement(AAAA) = TTTT")

    # RC is its own inverse
    seq = "ATTAGACCTGCCGGAATAC"
    assert mod.reverse_complement(mod.reverse_complement(seq)) == seq
    print("✓ RC(RC(s)) = s  (involution)")

    # ACGT is palindromic: RC = itself
    assert mod.reverse_complement("ACGT") == "ACGT"
    print("✓ reverse_complement(ACGT) = ACGT  (palindrome)")

    # --- hamming_distance() ---
    assert mod.hamming_distance("ACGT", "ACGT") == 0
    print("✓ hamming_distance(ACGT, ACGT) = 0")

    assert mod.hamming_distance("ACGT", "ACGG") == 1
    print("✓ hamming_distance(ACGT, ACGG) = 1")

    assert mod.hamming_distance("AAAA", "TTTT") == 4
    print("✓ hamming_distance(AAAA, TTTT) = 4")

    # Hamming distance is symmetric
    assert mod.hamming_distance("TGAAA", "GGAAA") == mod.hamming_distance("GGAAA", "TGAAA")
    print("✓ hamming_distance is symmetric")

    # The key correction in the Rosalind sample: TGAAA is distance 1 from GGAAA
    assert mod.hamming_distance("TGAAA", "GGAAA") == 1
    print("✓ hamming_distance(TGAAA, GGAAA) = 1  (the sample correction)")

    # --- find_correct_reads() ---
    corr_fasta = """\
>Rosalind_52
TCATC
>Rosalind_44
TTCAT
>Rosalind_68
TCATC
>Rosalind_28
TGAAA
>Rosalind_95
GAGGT
>Rosalind_75
TTTCC
>Rosalind_21
ATCAA
>Rosalind_54
TTGAT
>Rosalind_34
TTTCC
"""
    sample_reads = mod.parse_fasta(corr_fasta)
    correct = mod.find_correct_reads(sample_reads)

    # TCATC appears ×2 → correct; its RC (GATGA) is also correct
    assert "TCATC" in correct
    print("✓ TCATC in correct set (appears ×2)")

    rc_tcatc = mod.reverse_complement("TCATC")  # GATGA
    assert rc_tcatc in correct
    print(f"✓ RC(TCATC)={rc_tcatc} in correct set")

    # TTTCC appears ×2 → correct; its RC (GGAAA) is also correct
    assert "TTTCC" in correct
    print("✓ TTTCC in correct set (appears ×2)")

    rc_tttcc = mod.reverse_complement("TTTCC")  # GGAAA
    assert rc_tttcc == "GGAAA"
    assert rc_tttcc in correct
    print(f"✓ RC(TTTCC)={rc_tttcc} in correct set")

    # Erroneous reads (appear once and RC also appears once or not at all)
    for erroneous in ["TTCAT", "TGAAA", "GAGGT"]:
        assert erroneous not in correct, f"Expected '{erroneous}' to be erroneous"
    print("✓ TTCAT, TGAAA, GAGGT correctly identified as erroneous")

    # ATCAA and TTGAT are RC of each other, each appears ×1 → both erroneous
    assert "ATCAA" not in correct
    assert "TTGAT" not in correct
    print("✓ ATCAA and TTGAT (RC pair, each ×1) are both erroneous")

    # Total correct set size: {TCATC, GATGA, TTTCC, GGAAA}
    assert len(correct) == 4, f"Expected 4 correct reads, got {len(correct)}: {sorted(correct)}"
    print(f"✓ Correct set has exactly 4 members: {sorted(correct)}")

    # --- find_correct_reads() with RC-count trigger ---
    # A read appearing once whose RC appears ×2 should still be "correct"
    rc_reads = ["ACGG", "ACGG", "CCGT"]  # CCGT = RC(ACGG)
    rc_correct = mod.find_correct_reads(rc_reads)
    assert "CCGT" in rc_correct, "RC of a ×2 read should be in correct set"
    print("✓ RC of a ×2 read is added to the correct set")

    # --- correct_errors() with Rosalind CORR sample ---
    corrections = mod.correct_errors(sample_reads)

    # Only TGAAA → GGAAA is within Hamming distance 1 of a correct read
    assert len(corrections) == 1, (
        f"Expected 1 correction, got {len(corrections)}: {corrections}"
    )
    assert corrections[0] == ("TGAAA", "GGAAA"), (
        f"Expected ('TGAAA', 'GGAAA'), got {corrections[0]}"
    )
    print(f"✓ Rosalind CORR sample → correction: TGAAA -> GGAAA")

    # --- correct_errors() with controlled custom examples ---

    # Simple substitution error at last base
    simple_reads = ["ACGT", "ACGT", "ACGG"]
    simple_corr = mod.correct_errors(simple_reads)
    assert ("ACGG", "ACGT") in simple_corr, f"Expected ACGG->ACGT, got {simple_corr}"
    print("✓ Simple error: ACGG -> ACGT (last base corrected)")

    # Error at first base
    first_base = ["GCTA", "GCTA", "ACTA"]
    fb_corr = mod.correct_errors(first_base)
    assert ("ACTA", "GCTA") in fb_corr, f"Expected ACTA->GCTA, got {fb_corr}"
    print("✓ First-base error: ACTA -> GCTA corrected")

    # Multiple errors in the same dataset, each corrected independently
    # AAAG has last base error (G→A) → corrected to AAAA
    # GGGA has last base error (A→G) → corrected to GGGG
    multi_err = ["AAAA", "AAAA", "GGGG", "GGGG", "AAAG", "GGGA"]
    multi_corr = mod.correct_errors(multi_err)
    corrections_dict = dict(multi_corr)
    assert "AAAG" in corrections_dict and corrections_dict["AAAG"] == "AAAA", (
        f"Expected AAAG->AAAA, got {corrections_dict}"
    )
    assert "GGGA" in corrections_dict and corrections_dict["GGGA"] == "GGGG", (
        f"Expected GGGA->GGGG, got {corrections_dict}"
    )
    print("✓ Multiple errors in dataset each corrected independently")

    # Correct reads are not included in corrections output
    pure_correct = ["ACGT", "ACGT", "TGCA", "TGCA"]
    no_corr = mod.correct_errors(pure_correct)
    assert no_corr == [], f"Expected no corrections, got {no_corr}"
    print("✓ All-correct dataset produces no corrections")

    # --- parse_fasta() ---
    corr_parsed = mod.parse_fasta(corr_fasta)
    assert len(corr_parsed) == 9   # 9 sequences, including duplicates
    assert corr_parsed.count("TCATC") == 2
    assert corr_parsed.count("TTTCC") == 2
    print("✓ parse_fasta preserves duplicates (TCATC ×2, TTTCC ×2)")

    print("✓ All CORR tests passed!")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("ROSALIND GENOME ASSEMBLY – TEST SUITE (Session 8)")
    print("=" * 70)
    print("Testing LONG (shortest superstring) | CORR (error correction)\n")

    tests = [test_long, test_corr]
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
