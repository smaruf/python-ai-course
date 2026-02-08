"""
Dice Simulation and the Law of Large Numbers
==============================================

Rolling dice is one of the simplest random processes to simulate.
This module demonstrates dice rolling, computing averages, and 
observing the Law of Large Numbers in action.

Learning Objectives:
- Simulate rolling a single die
- Simulate rolling multiple dice
- Calculate running averages
- Observe the Law of Large Numbers
- Understand convergence of simulations

Key Concepts:
- Expected value: The theoretical average outcome
- Empirical average: The actual average from simulation
- Law of Large Numbers: Empirical → Expected as n → ∞
- Convergence: How quickly simulation approaches theory
"""

import random


def roll_die(sides=6):
    """
    Simulate rolling a single die.
    
    Args:
        sides: Number of sides on the die (default: 6)
    
    Returns:
        Integer from 1 to sides (inclusive)
    
    Example:
        >>> random.seed(42)
        >>> roll_die()
        6
    """
    return random.randint(1, sides)


def roll_multiple_dice(n_dice, sides=6):
    """
    Simulate rolling multiple dice and return their sum.
    
    This is useful for games like Craps (2 dice), Yahtzee (5 dice),
    or Dungeons & Dragons (various dice).
    
    Args:
        n_dice: Number of dice to roll
        sides: Number of sides per die
    
    Returns:
        Sum of all dice rolls
    
    Example:
        >>> random.seed(42)
        >>> roll_multiple_dice(2)  # Roll 2d6
        7
    """
    return sum(roll_die(sides) for _ in range(n_dice))


def expected_value_single_die(sides=6):
    """
    Calculate the expected value (theoretical average) of a single die.
    
    For a fair die with sides labeled 1 to n:
    Expected value = (1 + 2 + ... + n) / n = (n + 1) / 2
    
    For a standard 6-sided die: (1 + 2 + 3 + 4 + 5 + 6) / 6 = 3.5
    
    Args:
        sides: Number of sides on the die
    
    Returns:
        Expected value of a single die roll
    
    Example:
        >>> expected_value_single_die(6)
        3.5
        >>> expected_value_single_die(20)
        10.5
    """
    return (sides + 1) / 2


def expected_value_multiple_dice(n_dice, sides=6):
    """
    Calculate the expected value for rolling multiple dice.
    
    By linearity of expectation:
    E[sum of n dice] = n * E[single die]
    
    Args:
        n_dice: Number of dice
        sides: Number of sides per die
    
    Returns:
        Expected value of the sum
    
    Example:
        >>> expected_value_multiple_dice(2, 6)  # 2d6
        7.0
        >>> expected_value_multiple_dice(3, 6)  # 3d6
        10.5
    """
    return n_dice * expected_value_single_die(sides)


def simulate_dice_rolls(n_rolls, n_dice=1, sides=6):
    """
    Simulate rolling dice n_rolls times and compute statistics.
    
    Args:
        n_rolls: Number of times to roll the dice
        n_dice: Number of dice to roll each time
        sides: Number of sides per die
    
    Returns:
        Dictionary containing:
        - all_rolls: List of all roll results
        - average: Empirical average
        - expected: Theoretical expected value
        - error: Difference between empirical and expected
    
    Example:
        >>> random.seed(42)
        >>> result = simulate_dice_rolls(1000, n_dice=1, sides=6)
        >>> 3.4 < result['average'] < 3.6  # Should be close to 3.5
        True
    """
    all_rolls = [roll_multiple_dice(n_dice, sides) for _ in range(n_rolls)]
    
    average = sum(all_rolls) / len(all_rolls)
    expected = expected_value_multiple_dice(n_dice, sides)
    error = abs(average - expected)
    
    return {
        'all_rolls': all_rolls,
        'average': average,
        'expected': expected,
        'error': error,
        'percent_error': (error / expected) * 100
    }


def demonstrate_law_of_large_numbers(max_rolls=100000, checkpoints=None):
    """
    Demonstrate the Law of Large Numbers with increasing sample sizes.
    
    The Law of Large Numbers states that as the number of trials increases,
    the empirical average converges to the theoretical expected value.
    
    Args:
        max_rolls: Maximum number of rolls to simulate
        checkpoints: List of sample sizes to check (default: powers of 10)
    
    Returns:
        List of dictionaries with results at each checkpoint
    
    Example:
        >>> random.seed(42)
        >>> results = demonstrate_law_of_large_numbers(10000, [100, 1000, 10000])
        >>> errors = [r['error'] for r in results]
        >>> # Error generally decreases (though not always strictly monotonic due to randomness)
        >>> errors[-1] < errors[0]  # Final error smaller than initial
        True
    """
    if checkpoints is None:
        checkpoints = [10, 100, 1000, 10000, max_rolls]
    
    results = []
    all_rolls = []
    
    for checkpoint in checkpoints:
        # Generate additional rolls needed to reach this checkpoint
        rolls_needed = checkpoint - len(all_rolls)
        all_rolls.extend([roll_die() for _ in range(rolls_needed)])
        
        # Compute statistics
        average = sum(all_rolls) / len(all_rolls)
        expected = expected_value_single_die()
        error = abs(average - expected)
        
        results.append({
            'n_rolls': len(all_rolls),
            'average': average,
            'expected': expected,
            'error': error,
            'percent_error': (error / expected) * 100
        })
    
    return results


def compute_running_average(rolls):
    """
    Compute the running average at each step.
    
    For visualization purposes, this shows how the average
    evolves as more data is collected.
    
    Args:
        rolls: List of roll results
    
    Returns:
        List of running averages
    
    Example:
        >>> compute_running_average([1, 2, 3, 4, 5])
        [1.0, 1.5, 2.0, 2.5, 3.0]
    """
    running_avg = []
    cumsum = 0
    
    for i, roll in enumerate(rolls, 1):
        cumsum += roll
        running_avg.append(cumsum / i)
    
    return running_avg


def analyze_two_dice_distribution(n_rolls=10000):
    """
    Analyze the distribution of rolling two dice (like in Craps).
    
    Key insights:
    - Possible sums: 2 through 12
    - Most common sum: 7 (can be made 6 ways)
    - Least common sums: 2 and 12 (only 1 way each)
    
    Args:
        n_rolls: Number of times to roll two dice
    
    Returns:
        Dictionary mapping each sum to its frequency and probability
    
    Example:
        >>> random.seed(42)
        >>> dist = analyze_two_dice_distribution(10000)
        >>> dist[7]['frequency'] > dist[2]['frequency']  # 7 more common than 2
        True
    """
    # Roll two dice n_rolls times
    rolls = [roll_multiple_dice(2) for _ in range(n_rolls)]
    
    # Count frequency of each sum
    distribution = {}
    for total in range(2, 13):
        count = rolls.count(total)
        distribution[total] = {
            'frequency': count,
            'probability': count / n_rolls,
            'theoretical_probability': get_theoretical_probability_two_dice(total)
        }
    
    return distribution


def get_theoretical_probability_two_dice(total):
    """
    Get the theoretical probability of rolling a given total with two dice.
    
    There are 36 possible outcomes when rolling two dice (6 × 6).
    The number of ways to achieve each sum:
    2: 1 way   (1+1)
    3: 2 ways  (1+2, 2+1)
    4: 3 ways  (1+3, 2+2, 3+1)
    5: 4 ways  (1+4, 2+3, 3+2, 4+1)
    6: 5 ways  (1+5, 2+4, 3+3, 4+2, 5+1)
    7: 6 ways  (1+6, 2+5, 3+4, 4+3, 5+2, 6+1)
    8: 5 ways  (2+6, 3+5, 4+4, 5+3, 6+2)
    9: 4 ways  (3+6, 4+5, 5+4, 6+3)
    10: 3 ways (4+6, 5+5, 6+4)
    11: 2 ways (5+6, 6+5)
    12: 1 way  (6+6)
    
    Args:
        total: Sum of two dice (2-12)
    
    Returns:
        Theoretical probability of rolling that total
    """
    ways_to_make = {
        2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6,
        8: 5, 9: 4, 10: 3, 11: 2, 12: 1
    }
    return ways_to_make.get(total, 0) / 36


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("="*70)
    print("DICE SIMULATION AND THE LAW OF LARGE NUMBERS")
    print("="*70)
    
    random.seed(42)  # For reproducibility
    
    # 1. Single die rolls
    print("\n1. ROLLING A SINGLE DIE")
    print("-" * 70)
    print("Rolling a 6-sided die 10 times:")
    rolls = [roll_die() for _ in range(10)]
    print(f"Results: {rolls}")
    print(f"Average: {sum(rolls) / len(rolls):.2f}")
    print(f"Expected: {expected_value_single_die():.2f}")
    
    # 2. Multiple dice
    print("\n2. ROLLING MULTIPLE DICE")
    print("-" * 70)
    print("Rolling 2d6 (two dice) 10 times:")
    rolls_2d6 = [roll_multiple_dice(2) for _ in range(10)]
    print(f"Results: {rolls_2d6}")
    print(f"Average: {sum(rolls_2d6) / len(rolls_2d6):.2f}")
    print(f"Expected: {expected_value_multiple_dice(2):.2f}")
    
    # 3. Law of Large Numbers
    print("\n3. LAW OF LARGE NUMBERS")
    print("-" * 70)
    print("Demonstrating convergence with increasing sample sizes:")
    print(f"\n{'Rolls':>10} {'Average':>10} {'Expected':>10} {'Error':>10} {'% Error':>10}")
    print("-" * 70)
    
    checkpoints = [10, 100, 1000, 10000, 100000]
    results = demonstrate_law_of_large_numbers(100000, checkpoints)
    
    for result in results:
        print(f"{result['n_rolls']:>10,} {result['average']:>10.4f} "
              f"{result['expected']:>10.4f} {result['error']:>10.4f} "
              f"{result['percent_error']:>9.2f}%")
    
    print("\n✓ Notice: Error decreases as sample size increases!")
    print("✓ This is the Law of Large Numbers in action")
    
    # 4. Two dice distribution
    print("\n4. TWO DICE DISTRIBUTION ANALYSIS")
    print("-" * 70)
    print("Rolling 2d6 (Craps-style) 100,000 times:")
    print(f"\n{'Sum':>5} {'Count':>10} {'Empirical':>12} {'Theoretical':>12} {'Difference':>12}")
    print("-" * 70)
    
    dist = analyze_two_dice_distribution(100000)
    for total in range(2, 13):
        emp = dist[total]['probability']
        theo = dist[total]['theoretical_probability']
        diff = abs(emp - theo)
        print(f"{total:>5} {dist[total]['frequency']:>10,} "
              f"{emp:>11.4f} {theo:>12.4f} {diff:>11.4f}")
    
    print("\n✓ Sum of 7 is most common (appears ~1/6 of the time)")
    print("✓ Sums of 2 and 12 are least common (appear ~1/36 of the time)")
    print("✓ Empirical probabilities closely match theoretical values")
    
    # 5. Running average demonstration
    print("\n5. RUNNING AVERAGE CONVERGENCE")
    print("-" * 70)
    print("First 20 rolls and running average:")
    test_rolls = [roll_die() for _ in range(20)]
    running_avg = compute_running_average(test_rolls)
    
    print(f"\n{'Roll #':>8} {'Value':>8} {'Running Avg':>15}")
    print("-" * 70)
    for i, (roll, avg) in enumerate(zip(test_rolls, running_avg), 1):
        print(f"{i:>8} {roll:>8} {avg:>15.4f}")
    
    print(f"\nExpected value: {expected_value_single_die():.2f}")
    print(f"Final average:  {running_avg[-1]:.4f}")
    
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("✓ Single die expected value: 3.5")
    print("✓ Two dice expected value: 7.0")
    print("✓ Law of Large Numbers: More trials → Better accuracy")
    print("✓ Convergence: Empirical average approaches expected value")
    print("✓ Rolling 7 with two dice is most likely (1/6 probability)")
    print("="*70)


if __name__ == "__main__":
    main()
