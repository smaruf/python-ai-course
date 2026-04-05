"""
IEV: Calculating Expected Offspring
====================================

Rosalind Problem: https://rosalind.info/problems/iev/
Episode 4 of the Philomath live problem-solving series with Phillip Compeau
(Carnegie Mellon), streamed on the Rosalind platform.

Background
----------
In probability theory, the *expected value* of a random variable X is the
average outcome weighted by probability:

    E[X] = Σ x · P(X = x)

For a population of couples each producing a fixed number of offspring,
the expected number of offspring with a given phenotype is simply the sum
over all couple types of:

    (number of that type of couple) × (offspring per couple) × P(phenotype | cross)

The six possible Mendelian couple genotypes and their probability of
producing a dominant-phenotype offspring (i.e., at least one dominant allele):

  AA-AA → 1.00   (all offspring are AA)
  AA-Aa → 1.00   (offspring are AA or Aa)
  AA-aa → 1.00   (all offspring are Aa)
  Aa-Aa → 0.75   (offspring: 1/4 AA, 2/4 Aa, 1/4 aa)
  Aa-aa → 0.50   (offspring: 1/2 Aa, 1/2 aa)
  aa-aa → 0.00   (all offspring are aa)

Problem Statement
-----------------
Given:  Six non-negative integers c1 … c6, representing the number of
        couples in a population for each of the six crossing types above.

Return: Expected number of offspring displaying the dominant phenotype
        among the next generation of 2 children per couple.

Learning Objectives
-------------------
- Apply linearity of expectation to a genetics setting
- Enumerate all Mendelian cross types and their phenotypic ratios
- Compute expected values as weighted sums
"""


# Probability of dominant-phenotype offspring for each cross type
DOMINANT_PROBS = {
    'AA_AA': 1.00,
    'AA_Aa': 1.00,
    'AA_aa': 1.00,
    'Aa_Aa': 0.75,
    'Aa_aa': 0.50,
    'aa_aa': 0.00,
}

OFFSPRING_PER_COUPLE = 2


def expected_dominant_offspring(
    c_AA_AA: int,
    c_AA_Aa: int,
    c_AA_aa: int,
    c_Aa_Aa: int,
    c_Aa_aa: int,
    c_aa_aa: int,
    offspring_per_couple: int = OFFSPRING_PER_COUPLE,
) -> float:
    """
    Compute the expected number of offspring displaying the dominant phenotype.

    Uses linearity of expectation: E[total dominant] = Σ E[dominant from type i].

    Args:
        c_AA_AA: couples of type AA × AA
        c_AA_Aa: couples of type AA × Aa
        c_AA_aa: couples of type AA × aa
        c_Aa_Aa: couples of type Aa × Aa
        c_Aa_aa: couples of type Aa × aa
        c_aa_aa: couples of type aa × aa
        offspring_per_couple: children produced per couple (default 2)

    Returns:
        Expected count of dominant-phenotype offspring (float)

    Examples:
        >>> expected_dominant_offspring(1, 0, 0, 1, 0, 1)
        3.5

        >>> expected_dominant_offspring(0, 0, 0, 0, 0, 10)
        0.0

        >>> expected_dominant_offspring(10, 0, 0, 0, 0, 0)
        20.0
    """
    counts = [c_AA_AA, c_AA_Aa, c_AA_aa, c_Aa_Aa, c_Aa_aa, c_aa_aa]
    probs  = list(DOMINANT_PROBS.values())

    expected = sum(
        count * offspring_per_couple * prob
        for count, prob in zip(counts, probs)
    )
    return expected


def expected_offspring_breakdown(
    c_AA_AA: int,
    c_AA_Aa: int,
    c_AA_aa: int,
    c_Aa_Aa: int,
    c_Aa_aa: int,
    c_aa_aa: int,
    offspring_per_couple: int = OFFSPRING_PER_COUPLE,
) -> list:
    """
    Return the per-cross-type contribution to the total expected count.

    Args:
        c_*: couple counts for each cross type
        offspring_per_couple: children per couple

    Returns:
        List of dicts with keys: cross, count, prob_dom, contribution
    """
    counts = [c_AA_AA, c_AA_Aa, c_AA_aa, c_Aa_Aa, c_Aa_aa, c_aa_aa]
    result = []
    for (cross, prob), count in zip(DOMINANT_PROBS.items(), counts):
        result.append({
            'cross':        cross,
            'count':        count,
            'prob_dom':     prob,
            'contribution': count * offspring_per_couple * prob,
        })
    return result


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("IEV: CALCULATING EXPECTED OFFSPRING")
    print("=" * 70)

    # Rosalind sample dataset
    counts = (1, 0, 0, 1, 0, 1)
    c_AA_AA, c_AA_Aa, c_AA_aa, c_Aa_Aa, c_Aa_aa, c_aa_aa = counts

    expected = expected_dominant_offspring(*counts)
    print(f"\nSample dataset: {counts}")
    print(f"Expected dominant offspring = {expected}")
    print(f"Rosalind expected answer    = 3.5")

    # Detailed breakdown
    print("\nPer-cross contribution:")
    print(f"{'Cross':<10} {'Couples':<10} {'P(dom)':<10} {'Expected':<12}")
    print("-" * 45)
    breakdown = expected_offspring_breakdown(*counts)
    for row in breakdown:
        print(
            f"{row['cross']:<10} {row['count']:<10} "
            f"{row['prob_dom']:<10.2f} {row['contribution']:<12.2f}"
        )
    print(f"\nTotal expected dominant offspring: {expected:.1f}")

    # Larger example
    print("\nLarger example (c1=4, c2=2, c3=2, c4=1, c5=1, c6=0):")
    large = (4, 2, 2, 1, 1, 0)
    print(f"  Expected = {expected_dominant_offspring(*large):.2f}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ E[dominant offspring] = Σ (couples_i × offspring × P(dominant_i))")
    print("✓ Linearity of expectation makes this a simple weighted sum")
    print("✓ Phenotypic ratios: AA-AA=1, AA-Aa=1, AA-aa=1, Aa-Aa=0.75, Aa-aa=0.5, aa-aa=0")
    print("✓ Each couple contributes independently to the total expectation")
