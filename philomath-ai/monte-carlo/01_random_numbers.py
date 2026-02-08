"""
Random Number Generation and Seeding
=====================================

Understanding randomness is fundamental to Monte Carlo simulation.
In this module, we explore how to generate random numbers in Python,
understand seeding for reproducibility, and work with random number generators.

Learning Objectives:
- Generate random integers in Python
- Understand pseudo-random number generation
- Use seeding for reproducible results
- Work with time-based seeding
- Understand the importance of randomness in simulation

Key Concepts:
- Pseudo-random numbers are deterministic but appear random
- Seeds control the sequence of "random" numbers
- Same seed = same sequence (reproducibility)
- Different seeds = different sequences (variability)
"""

import random
import time


def generate_random_integers(n, min_val=1, max_val=6):
    """
    Generate n random integers between min_val and max_val (inclusive).
    
    This uses Python's random.randint() which generates uniformly
    distributed random integers in the specified range.
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    
    Args:
        n: Number of random integers to generate
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
    
    Returns:
        List of n random integers
    
    Example:
        >>> random.seed(42)  # For reproducibility
        >>> generate_random_integers(5, 1, 6)
        [6, 1, 1, 6, 3]
    """
    return [random.randint(min_val, max_val) for _ in range(n)]


def demonstrate_seeding():
    """
    Demonstrate how seeding affects random number generation.
    
    Key Insight: Using the same seed produces identical sequences.
    This is crucial for:
    - Debugging simulations
    - Reproducing research results
    - Testing code with known outputs
    - Verifying simulation correctness
    
    Returns:
        Dictionary with results from different seeding approaches
    """
    results = {}
    
    # First sequence with seed 42
    random.seed(42)
    results['seed_42_first'] = [random.randint(1, 100) for _ in range(5)]
    
    # Second sequence with seed 42 (should be identical!)
    random.seed(42)
    results['seed_42_second'] = [random.randint(1, 100) for _ in range(5)]
    
    # Sequence with different seed
    random.seed(123)
    results['seed_123'] = [random.randint(1, 100) for _ in range(5)]
    
    # Sequence with no explicit seed (uses system time/entropy)
    # Note: This will be different each time
    random.seed()
    results['no_seed'] = [random.randint(1, 100) for _ in range(5)]
    
    return results


def demonstrate_time_based_seeding():
    """
    Demonstrate using time as a seed for randomness.
    
    Using the current time as a seed is a common way to get
    "truly random" behavior, since the time is always changing.
    
    However, this makes results non-reproducible!
    
    Returns:
        Dictionary with timestamp and generated numbers
    """
    # Get current time in seconds since epoch
    current_time = int(time.time())
    
    # Use time as seed
    random.seed(current_time)
    
    # Generate some random numbers
    numbers = [random.randint(1, 100) for _ in range(10)]
    
    return {
        'timestamp': current_time,
        'numbers': numbers
    }


def compare_distributions(n_samples=1000):
    """
    Compare the distribution of random numbers to verify uniformity.
    
    For a fair random number generator:
    - Each outcome should appear roughly equally often
    - The more samples, the more uniform the distribution
    - This demonstrates the Law of Large Numbers
    
    Args:
        n_samples: Number of random samples to generate
    
    Returns:
        Dictionary mapping each outcome to its frequency
    
    Example:
        >>> random.seed(42)
        >>> dist = compare_distributions(1000)
        >>> all(140 < count < 200 for count in dist.values())  # Roughly uniform
        True
    """
    # Generate random numbers from 1 to 6 (like a die)
    samples = [random.randint(1, 6) for _ in range(n_samples)]
    
    # Count frequency of each outcome
    frequency = {}
    for outcome in range(1, 7):
        frequency[outcome] = samples.count(outcome)
    
    return frequency


def calculate_expected_frequency(n_samples, n_outcomes=6):
    """
    Calculate the expected frequency for uniform distribution.
    
    In a fair random generator with n_outcomes equally likely values,
    each outcome should appear approximately n_samples / n_outcomes times.
    
    Args:
        n_samples: Total number of samples
        n_outcomes: Number of possible outcomes
    
    Returns:
        Expected frequency per outcome
    
    Example:
        >>> calculate_expected_frequency(1000, 6)
        166.66666666666666
    """
    return n_samples / n_outcomes


def demonstrate_reproducibility():
    """
    Show how seeding enables reproducible scientific computing.
    
    This is critical for:
    - Scientific research (others can verify results)
    - Software testing (consistent test outcomes)
    - Debugging (same sequence every run)
    - Teaching (students get same results)
    """
    print("\n" + "="*70)
    print("REPRODUCIBILITY DEMONSTRATION")
    print("="*70)
    
    # Run 1 with seed
    random.seed(2025)
    run1 = [random.randint(1, 100) for _ in range(5)]
    print(f"\nRun 1 (seed=2025): {run1}")
    
    # Run 2 with same seed
    random.seed(2025)
    run2 = [random.randint(1, 100) for _ in range(5)]
    print(f"Run 2 (seed=2025): {run2}")
    
    print(f"\nAre they identical? {run1 == run2}")
    
    # Run 3 with different seed
    random.seed(2026)
    run3 = [random.randint(1, 100) for _ in range(5)]
    print(f"\nRun 3 (seed=2026): {run3}")
    print(f"Different from Run 1? {run1 != run3}")


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("="*70)
    print("RANDOM NUMBER GENERATION IN PYTHON")
    print("="*70)
    
    # 1. Basic random number generation
    print("\n1. GENERATING RANDOM INTEGERS")
    print("-" * 70)
    random.seed(42)  # For reproducible output
    numbers = generate_random_integers(10, 1, 6)
    print(f"10 random dice rolls (1-6): {numbers}")
    
    # 2. Demonstrate seeding
    print("\n2. SEEDING DEMONSTRATION")
    print("-" * 70)
    seed_results = demonstrate_seeding()
    print(f"First sequence  (seed=42):  {seed_results['seed_42_first']}")
    print(f"Second sequence (seed=42):  {seed_results['seed_42_second']}")
    print(f"Identical? {seed_results['seed_42_first'] == seed_results['seed_42_second']}")
    print(f"\nDifferent seed  (seed=123): {seed_results['seed_123']}")
    print(f"No explicit seed:           {seed_results['no_seed']}")
    
    # 3. Time-based seeding
    print("\n3. TIME-BASED SEEDING")
    print("-" * 70)
    time_result = demonstrate_time_based_seeding()
    print(f"Timestamp: {time_result['timestamp']}")
    print(f"Random numbers: {time_result['numbers']}")
    
    # 4. Distribution analysis
    print("\n4. DISTRIBUTION ANALYSIS")
    print("-" * 70)
    random.seed(42)
    freq = compare_distributions(10000)
    expected = calculate_expected_frequency(10000, 6)
    
    print(f"Generated 10,000 random numbers (1-6):")
    print(f"Expected frequency per outcome: {expected:.2f}")
    print(f"\nActual frequencies:")
    for outcome in sorted(freq.keys()):
        count = freq[outcome]
        deviation = ((count - expected) / expected) * 100
        print(f"  {outcome}: {count:4d} ({deviation:+.2f}% from expected)")
    
    # 5. Reproducibility
    demonstrate_reproducibility()
    
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("✓ random.randint(a, b) generates integers from a to b (inclusive)")
    print("✓ random.seed(n) sets the seed for reproducibility")
    print("✓ Same seed → same sequence (reproducible)")
    print("✓ Different seeds → different sequences (variability)")
    print("✓ No seed → uses system time (non-reproducible)")
    print("✓ Large samples → uniform distribution (Law of Large Numbers)")
    print("="*70)


if __name__ == "__main__":
    main()
