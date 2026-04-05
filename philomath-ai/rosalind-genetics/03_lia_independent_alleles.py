"""
LIA: Independent Alleles
========================

Rosalind Problem: https://rosalind.info/problems/lia/
Episode 4 of the Philomath live problem-solving series with Phillip Compeau
(Carnegie Mellon), streamed on the Rosalind platform.

Background
----------
Mendel's Second Law (Law of Independent Assortment):
  When two or more traits are determined by genes on DIFFERENT chromosomes
  (or far apart on the same chromosome), they assort independently during
  gamete formation.  Knowledge of one trait gives no information about the
  other.

Two-factor cross  Aa Bb × Aa Bb:
  Each trait independently follows a 3:1 dominant-to-recessive ratio.
  The probability of an Aa Bb offspring in any single cross is 1/4:

      P(Aa)  = 1/2   (from Aa × Aa)
      P(Bb)  = 1/2   (from Bb × Bb)
      P(AaBb) = P(Aa) × P(Bb) = 1/4   (independence)

After k generations of always mating the progeny with another Aa Bb
organism, we want the probability of having at least n Aa Bb individuals
in generation k.

Each generation k individual is an independent Bernoulli trial with
success probability 1/4, and there are 2^k individuals in generation k
(each parent produces exactly 2 offspring).

So the number of Aa Bb organisms X follows:

    X ~ Binomial(N = 2^k, p = 1/4)

We want:   P(X ≥ n) = 1 − P(X < n) = 1 − Σ_{i=0}^{n-1} C(N,i) p^i (1-p)^{N-i}

Problem Statement
-----------------
Given:  Two positive integers k and n
          k → number of generations (so N = 2^k individuals in gen k)
          n → minimum desired count of Aa Bb organisms

Return: Probability P(X ≥ n) where X ~ Binomial(2^k, 1/4)

Learning Objectives
-------------------
- Apply Mendel's Second Law (independent assortment)
- Model multi-generation breeding as a binomial experiment
- Use the binomial CDF complement to compute tail probabilities
"""

import math


def prob_aabb(generation: int) -> float:
    """
    Return the probability that a single individual in generation `generation`
    has genotype Aa Bb, starting from two Aa Bb parents.

    In each generation the cross is always (Aa Bb) × (Aa Bb), so
    P(Aa Bb) = 1/2 × 1/2 = 1/4 regardless of generation.

    Args:
        generation: generation number (≥ 1)

    Returns:
        Always 0.25
    """
    return 0.25


def independent_alleles(k: int, n: int) -> float:
    """
    Compute P(at least n Aa Bb organisms in generation k).

    Uses the binomial distribution complement:
        P(X ≥ n) = 1 − Σ_{i=0}^{n-1} C(N, i) · p^i · (1-p)^(N-i)
    where N = 2^k and p = 1/4.

    Args:
        k: number of generations
        n: minimum required Aa Bb count

    Returns:
        Probability P(X ≥ n) as a float

    Examples:
        >>> round(independent_alleles(2, 1), 3)
        0.684

        >>> independent_alleles(1, 1)
        0.25

        >>> independent_alleles(1, 0)
        1.0
    """
    N = 2 ** k
    p = 0.25
    q = 1.0 - p

    if n > N:
        return 0.0

    # P(X < n) = Σ_{i=0}^{n-1} binom_pmf(i)
    p_less_than_n = sum(
        math.comb(N, i) * (p ** i) * (q ** (N - i))
        for i in range(n)
    )

    return 1.0 - p_less_than_n


def binomial_pmf(k_val: int, n_trials: int, p: float) -> float:
    """
    Binomial probability mass function P(X = k_val).

    Args:
        k_val:     number of successes
        n_trials:  number of trials
        p:         probability of success per trial

    Returns:
        P(X = k_val)

    Examples:
        >>> round(binomial_pmf(1, 4, 0.25), 6)
        0.421875
    """
    return math.comb(n_trials, k_val) * (p ** k_val) * ((1 - p) ** (n_trials - k_val))


def independent_alleles_distribution(k: int) -> list:
    """
    Return the full probability distribution of Aa Bb organisms in generation k.

    Args:
        k: number of generations

    Returns:
        List of (count, probability) tuples for count = 0 … 2^k
    """
    N = 2 ** k
    p = 0.25
    return [(i, binomial_pmf(i, N, p)) for i in range(N + 1)]


# ── Demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("LIA: INDEPENDENT ALLELES")
    print("=" * 70)

    # Rosalind sample dataset
    k, n = 2, 1
    prob = independent_alleles(k, n)
    print(f"\nSample dataset: k={k}, n={n}")
    print(f"N = 2^{k} = {2**k} organisms in generation {k}")
    print(f"P(Aa Bb) per individual = 0.25")
    print(f"P(at least {n} Aa Bb) = {prob:.3f}")
    print(f"Rosalind expected:      0.684")

    # Show the binomial distribution for k=2
    print(f"\nFull Binomial(N={2**k}, p=0.25) distribution:")
    dist = independent_alleles_distribution(k)
    for count, p_val in dist:
        bar = "█" * int(p_val * 50)
        print(f"  X={count}: P={p_val:.4f} {bar}")

    # Cumulative tail
    print(f"\nTail probabilities P(X ≥ n) for k={k}:")
    for min_n in range(2 ** k + 1):
        tail = independent_alleles(k, min_n)
        print(f"  P(X ≥ {min_n}) = {tail:.4f}")

    # Larger example
    print("\nExamples with larger k:")
    for gen in [3, 5, 7]:
        p = independent_alleles(gen, 1)
        print(f"  k={gen}, n=1: P = {p:.6f}")

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Mendel's 2nd Law: independent genes assort independently")
    print("✓ P(Aa Bb from Aa Bb × Aa Bb) = 1/4 in every generation")
    print("✓ N = 2^k organisms after k generations of 2-offspring crosses")
    print("✓ X ~ Binomial(2^k, 1/4) models AaBb count in generation k")
    print("✓ P(X ≥ n) = 1 − P(X < n) — use complement for efficiency")
