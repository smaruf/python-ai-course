"""
IPRB: Mendel's First Law
========================

Rosalind Problem: https://rosalind.info/problems/iprb/
Episode 4 of the Philomath live problem-solving series with Phillip Compeau
(Carnegie Mellon), streamed on the Rosalind platform.

Background
----------
Gregor Mendel observed that traits are controlled by discrete "factors"
(what we now call alleles).  For a given gene a diploid organism carries
two alleles — one inherited from each parent.

Dominance and recessiveness:
  • AA  — homozygous dominant (displays dominant phenotype)
  • Aa  — heterozygous      (displays dominant phenotype)
  • aa  — homozygous recessive (displays recessive phenotype)

Mendel's First Law (Law of Segregation):
  During gamete formation, the two alleles of a gene separate so that
  each gamete receives exactly one allele at random.

Problem Statement
-----------------
Given:  Three non-negative integers k, m, n
        representing a population of k+m+n organisms:
          k  →  AA (homozygous dominant)
          m  →  Aa (heterozygous)
          n  →  aa (homozygous recessive)

Return: Probability that two randomly chosen organisms produce an
        offspring that displays the DOMINANT phenotype (i.e., carries
        at least one dominant allele).

Learning Objectives
-------------------
- Apply the rules of Mendelian inheritance to compute genotype probabilities
- Practice conditional probability with sampling without replacement
- Use the complement rule: P(dominant) = 1 − P(recessive)
"""


def mendels_first_law(k: int, m: int, n: int) -> float:
    """
    Compute the probability that two randomly selected organisms produce
    an offspring with the dominant phenotype.

    Strategy (complement rule):
      P(dominant offspring) = 1 − P(offspring is aa)

    To get an 'aa' offspring both parents must contribute an 'a' gamete:
      • AA parent  → never contributes 'a'  (prob 0)
      • Aa parent  → contributes 'a' with prob 1/2
      • aa parent  → always contributes 'a'  (prob 1)

    We enumerate all ordered parent pairs (p1, p2) with
    p1 ≠ p2 selected without replacement and weight each pair by the
    probability that their cross yields aa.

    Args:
        k: Number of AA (homozygous dominant) organisms
        m: Number of Aa (heterozygous) organisms
        n: Number of aa (homozygous recessive) organisms

    Returns:
        Probability (float) that a random mating produces dominant phenotype

    Examples:
        >>> round(mendels_first_law(2, 2, 2), 5)
        0.78333

        >>> mendels_first_law(1, 0, 0)
        1.0

        >>> mendels_first_law(0, 0, 2)
        0.0
    """
    total = k + m + n
    if total < 2:
        raise ValueError("Population must contain at least 2 organisms.")

    # Total ways to choose an ordered pair (total × total-1)
    total_pairs = total * (total - 1)

    # P(aa offspring) from each cross type:
    #   AA × AA → 0      AA × Aa → 0      AA × aa → 0
    #   Aa × AA → 0      Aa × Aa → 1/4    Aa × aa → 1/2
    #   aa × AA → 0      aa × Aa → 1/2    aa × aa → 1

    p_recessive_ordered = (
        # Aa × Aa pairs: m*(m-1) ordered pairs, each yielding aa with prob 1/4
        m * (m - 1) * (1 / 4)
        # Aa × aa pairs: m*n ordered pairs, prob 1/2
        + m * n * (1 / 2)
        # aa × Aa pairs: n*m ordered pairs, prob 1/2
        + n * m * (1 / 2)
        # aa × aa pairs: n*(n-1) ordered pairs, prob 1
        + n * (n - 1) * 1
    )

    p_recessive = p_recessive_ordered / total_pairs
    return 1.0 - p_recessive


def mendels_law_all_crosses(k: int, m: int, n: int) -> dict:
    """
    Return detailed probability breakdown for every possible cross type.

    Useful for teaching / visualising each contribution.

    Args:
        k, m, n: counts of AA, Aa, aa organisms

    Returns:
        dict with keys 'AA_AA', 'AA_Aa', 'AA_aa', 'Aa_Aa', 'Aa_aa', 'aa_aa'
        and their probabilities of occurring, plus offspring probabilities.
    """
    total = k + m + n
    tp = total * (total - 1)  # ordered pairs

    crosses = {
        'AA_AA': {'prob_cross': k * (k - 1) / tp,      'prob_dom': 1.0},
        'AA_Aa': {'prob_cross': 2 * k * m / tp,         'prob_dom': 1.0},
        'AA_aa': {'prob_cross': 2 * k * n / tp,         'prob_dom': 1.0},
        'Aa_Aa': {'prob_cross': m * (m - 1) / tp,       'prob_dom': 3 / 4},
        'Aa_aa': {'prob_cross': 2 * m * n / tp,         'prob_dom': 1 / 2},
        'aa_aa': {'prob_cross': n * (n - 1) / tp,       'prob_dom': 0.0},
    }

    for key, data in crosses.items():
        data['contribution'] = data['prob_cross'] * data['prob_dom']

    return crosses


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("IPRB: MENDEL'S FIRST LAW")
    print("=" * 70)

    # Rosalind sample dataset
    k, m, n = 2, 2, 2
    prob = mendels_first_law(k, m, n)
    print(f"\nSample dataset: k={k}, m={m}, n={n}")
    print(f"P(dominant offspring) = {prob:.5f}")
    print(f"Expected:              0.78333")

    # Detailed breakdown
    print("\nDetailed cross breakdown:")
    print(f"{'Cross':<10} {'P(cross)':<12} {'P(dom|cross)':<16} {'Contribution':<14}")
    print("-" * 55)
    crosses = mendels_law_all_crosses(k, m, n)
    total_dom = 0.0
    for cross_name, data in crosses.items():
        total_dom += data['contribution']
        print(
            f"{cross_name:<10} {data['prob_cross']:<12.5f} "
            f"{data['prob_dom']:<16.4f} {data['contribution']:<14.5f}"
        )
    print(f"\nTotal P(dominant) = {total_dom:.5f}")

    # Edge cases
    print("\nEdge cases:")
    print(f"  All AA (k=5,m=0,n=0): {mendels_first_law(5,0,0):.4f}  (expect 1.0)")
    print(f"  All aa (k=0,m=0,n=5): {mendels_first_law(0,0,5):.4f}  (expect 0.0)")
    print(f"  All Aa (k=0,m=4,n=0): {mendels_first_law(0,4,0):.4f}  (expect 0.75)")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ P(dominant) = 1 – P(recessive)  (complement rule)")
    print("✓ Only Aa×Aa, Aa×aa, aa×Aa, aa×aa crosses can yield aa offspring")
    print("✓ Sampling without replacement → use n*(n-1) not n^2")
    print("✓ Mendel's First Law: alleles segregate equally into gametes")
