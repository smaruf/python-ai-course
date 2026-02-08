"""
Advanced Statistical Analysis for Monte Carlo Simulations
==========================================================

This module extends the basic Monte Carlo simulations with advanced
statistical analysis techniques including confidence intervals,
hypothesis testing, and statistical validation.

Learning Objectives:
- Calculate confidence intervals for simulation results
- Understand statistical significance and p-values
- Perform chi-square goodness-of-fit tests
- Analyze variance and standard deviation
- Understand sampling distributions
- Apply the Central Limit Theorem

Key Concepts:
- Confidence Interval: Range likely to contain the true parameter
- Standard Error: Measure of sampling variability
- Chi-Square Test: Validates distribution fits
- p-value: Probability of observing results under null hypothesis
"""

import random
import math


def calculate_confidence_interval(successes, trials, confidence_level=0.95):
    """
    Calculate confidence interval for a proportion using normal approximation.
    
    This uses the Wald method with normal approximation:
    CI = p ± z * sqrt(p(1-p)/n)
    
    where:
    - p is the sample proportion
    - z is the z-score for desired confidence level
    - n is the number of trials
    
    Args:
        successes: Number of successes
        trials: Total number of trials
        confidence_level: Confidence level (default: 0.95 for 95%)
    
    Returns:
        Dictionary containing:
        - proportion: Sample proportion
        - lower_bound: Lower bound of CI
        - upper_bound: Upper bound of CI
        - margin_of_error: Half-width of CI
        - standard_error: Standard error
    
    Example:
        >>> ci = calculate_confidence_interval(493, 1000, 0.95)
        >>> 0.46 < ci['lower_bound'] < ci['proportion'] < ci['upper_bound'] < 0.53
        True
    """
    # Z-scores for common confidence levels
    z_scores = {
        0.90: 1.645,
        0.95: 1.960,
        0.99: 2.576,
        0.999: 3.291
    }
    
    if confidence_level not in z_scores:
        raise ValueError(f"Confidence level must be one of {list(z_scores.keys())}")
    
    p = successes / trials
    z = z_scores[confidence_level]
    
    # Standard error of the proportion
    standard_error = math.sqrt(p * (1 - p) / trials)
    
    # Margin of error
    margin_of_error = z * standard_error
    
    # Confidence interval
    lower_bound = max(0, p - margin_of_error)
    upper_bound = min(1, p + margin_of_error)
    
    return {
        'proportion': p,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'margin_of_error': margin_of_error,
        'standard_error': standard_error,
        'confidence_level': confidence_level
    }


def calculate_variance_and_std(data):
    """
    Calculate variance and standard deviation of a dataset.
    
    Variance measures how spread out the data is from the mean.
    Standard deviation is the square root of variance.
    
    Args:
        data: List of numerical values
    
    Returns:
        Dictionary containing:
        - mean: Average value
        - variance: Variance
        - std_dev: Standard deviation
        - min: Minimum value
        - max: Maximum value
        - range: Range (max - min)
    
    Example:
        >>> data = [1, 2, 3, 4, 5]
        >>> stats = calculate_variance_and_std(data)
        >>> stats['mean']
        3.0
    """
    n = len(data)
    mean = sum(data) / n
    
    # Calculate variance
    variance = sum((x - mean) ** 2 for x in data) / n
    std_dev = math.sqrt(variance)
    
    return {
        'mean': mean,
        'variance': variance,
        'std_dev': std_dev,
        'min': min(data),
        'max': max(data),
        'range': max(data) - min(data),
        'n': n
    }


def chi_square_test(observed, expected):
    """
    Perform chi-square goodness-of-fit test.
    
    Tests whether observed frequencies match expected frequencies.
    
    Chi-square statistic: χ² = Σ((O - E)² / E)
    
    Args:
        observed: Dictionary of observed frequencies
        expected: Dictionary of expected frequencies
    
    Returns:
        Dictionary containing:
        - chi_square: Chi-square statistic
        - degrees_of_freedom: Number of categories - 1
        - critical_values: Critical values for common significance levels
        - interpretation: Whether to reject null hypothesis
    
    Example:
        >>> obs = {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100}
        >>> exp = {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100}
        >>> result = chi_square_test(obs, exp)
        >>> result['chi_square']
        0.0
    """
    # Calculate chi-square statistic
    chi_square = 0
    for category in observed:
        o = observed[category]
        e = expected[category]
        chi_square += (o - e) ** 2 / e
    
    # Degrees of freedom
    df = len(observed) - 1
    
    # Critical values for df=5 (six-sided die) at different significance levels
    # These are approximations - in practice, use scipy.stats.chi2
    critical_values_df5 = {
        0.10: 9.236,   # 90% confidence
        0.05: 11.070,  # 95% confidence
        0.01: 15.086,  # 99% confidence
    }
    
    critical_values_df11 = {
        0.10: 17.275,
        0.05: 19.675,
        0.01: 24.725,
    }
    
    # Select appropriate critical values based on df
    if df == 5:
        critical_values = critical_values_df5
    elif df == 11:
        critical_values = critical_values_df11
    else:
        critical_values = {0.05: "N/A"}  # Simplified for other df
    
    # Interpretation
    interpretation = {}
    for alpha, critical_value in critical_values.items():
        if critical_value != "N/A":
            if chi_square < critical_value:
                interpretation[alpha] = f"Fail to reject H0 at α={alpha} (χ²={chi_square:.3f} < {critical_value})"
            else:
                interpretation[alpha] = f"Reject H0 at α={alpha} (χ²={chi_square:.3f} > {critical_value})"
    
    return {
        'chi_square': chi_square,
        'degrees_of_freedom': df,
        'critical_values': critical_values,
        'interpretation': interpretation
    }


def simulate_craps_with_statistics(n_games):
    """
    Simulate Craps games and calculate comprehensive statistics.
    
    Args:
        n_games: Number of games to simulate
    
    Returns:
        Dictionary with simulation results and statistical analysis
    """
    # Import craps functions
    import sys
    import os
    import importlib.util
    
    # Load craps module
    path = os.path.join(os.path.dirname(__file__), '03_craps_simulation.py')
    spec = importlib.util.spec_from_file_location('craps', path)
    craps = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(craps)
    
    # Run simulation
    wins = 0
    rolls_per_game = []
    
    for _ in range(n_games):
        result = craps.play_craps_once()
        if result['outcome'] == 'win':
            wins += 1
        rolls_per_game.append(result['n_rolls'])
    
    # Calculate basic statistics
    win_rate = wins / n_games
    
    # Calculate confidence interval
    ci_95 = calculate_confidence_interval(wins, n_games, 0.95)
    ci_99 = calculate_confidence_interval(wins, n_games, 0.99)
    
    # Calculate statistics on rolls per game
    rolls_stats = calculate_variance_and_std(rolls_per_game)
    
    # Theoretical values
    theoretical_win_prob = craps.calculate_theoretical_probabilities()['total_win_prob']
    
    return {
        'n_games': n_games,
        'wins': wins,
        'losses': n_games - wins,
        'win_rate': win_rate,
        'theoretical_win_rate': theoretical_win_prob,
        'error': abs(win_rate - theoretical_win_prob),
        'confidence_interval_95': ci_95,
        'confidence_interval_99': ci_99,
        'rolls_per_game_stats': rolls_stats,
    }


def test_dice_fairness(n_rolls=10000):
    """
    Test if a die is fair using chi-square test.
    
    Args:
        n_rolls: Number of times to roll the die
    
    Returns:
        Dictionary with test results
    """
    # Roll the die n_rolls times
    rolls = [random.randint(1, 6) for _ in range(n_rolls)]
    
    # Count observed frequencies
    observed = {i: rolls.count(i) for i in range(1, 7)}
    
    # Expected frequencies (uniform distribution)
    expected = {i: n_rolls / 6 for i in range(1, 7)}
    
    # Perform chi-square test
    test_result = chi_square_test(observed, expected)
    
    return {
        'n_rolls': n_rolls,
        'observed_frequencies': observed,
        'expected_frequencies': expected,
        'chi_square_test': test_result
    }


def analyze_sampling_distribution(n_samples=1000, sample_size=100):
    """
    Demonstrate the Central Limit Theorem with dice rolls.
    
    The CLT states that the distribution of sample means approaches
    a normal distribution as sample size increases, regardless of
    the underlying distribution.
    
    Args:
        n_samples: Number of samples to take
        sample_size: Size of each sample
    
    Returns:
        Dictionary with sampling distribution statistics
    """
    sample_means = []
    
    for _ in range(n_samples):
        # Take a sample
        sample = [random.randint(1, 6) for _ in range(sample_size)]
        sample_mean = sum(sample) / len(sample)
        sample_means.append(sample_mean)
    
    # Calculate statistics of sampling distribution
    stats = calculate_variance_and_std(sample_means)
    
    # Theoretical values
    population_mean = 3.5  # Expected value of a die
    population_std = math.sqrt(35/12)  # Variance of uniform discrete
    standard_error_theoretical = population_std / math.sqrt(sample_size)
    
    return {
        'n_samples': n_samples,
        'sample_size': sample_size,
        'sampling_distribution': stats,
        'theoretical_mean': population_mean,
        'theoretical_se': standard_error_theoretical,
        'sample_means': sample_means
    }


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("="*70)
    print("ADVANCED STATISTICAL ANALYSIS FOR MONTE CARLO SIMULATIONS")
    print("="*70)
    
    random.seed(42)
    
    # 1. Confidence Intervals
    print("\n1. CONFIDENCE INTERVALS")
    print("-" * 70)
    print("Simulating 10,000 Craps games to calculate confidence intervals:")
    
    stats = simulate_craps_with_statistics(10000)
    print(f"\nWin rate: {stats['win_rate']:.4f}")
    print(f"Theoretical: {stats['theoretical_win_rate']:.4f}")
    print(f"Error: {stats['error']:.4f}")
    
    ci95 = stats['confidence_interval_95']
    print(f"\n95% Confidence Interval:")
    print(f"  [{ci95['lower_bound']:.4f}, {ci95['upper_bound']:.4f}]")
    print(f"  Margin of Error: ±{ci95['margin_of_error']:.4f}")
    print(f"  Standard Error: {ci95['standard_error']:.4f}")
    
    ci99 = stats['confidence_interval_99']
    print(f"\n99% Confidence Interval:")
    print(f"  [{ci99['lower_bound']:.4f}, {ci99['upper_bound']:.4f}]")
    print(f"  Margin of Error: ±{ci99['margin_of_error']:.4f}")
    
    # Check if theoretical value is in CI
    in_ci_95 = ci95['lower_bound'] <= stats['theoretical_win_rate'] <= ci95['upper_bound']
    in_ci_99 = ci99['lower_bound'] <= stats['theoretical_win_rate'] <= ci99['upper_bound']
    
    print(f"\n✓ Theoretical value in 95% CI: {in_ci_95}")
    print(f"✓ Theoretical value in 99% CI: {in_ci_99}")
    
    # 2. Variance and Standard Deviation
    print("\n2. VARIANCE AND STANDARD DEVIATION")
    print("-" * 70)
    rolls_stats = stats['rolls_per_game_stats']
    print(f"Rolls per game statistics (from {stats['n_games']:,} games):")
    print(f"  Mean: {rolls_stats['mean']:.2f} rolls")
    print(f"  Std Dev: {rolls_stats['std_dev']:.2f}")
    print(f"  Variance: {rolls_stats['variance']:.2f}")
    print(f"  Range: [{rolls_stats['min']}, {rolls_stats['max']}]")
    
    # 3. Chi-Square Test
    print("\n3. CHI-SQUARE GOODNESS-OF-FIT TEST")
    print("-" * 70)
    print("Testing die fairness with 60,000 rolls:")
    
    fairness_test = test_dice_fairness(60000)
    print(f"\nObserved frequencies:")
    for face, count in sorted(fairness_test['observed_frequencies'].items()):
        expected = fairness_test['expected_frequencies'][face]
        deviation = count - expected
        print(f"  Face {face}: {count:5d} (expected: {expected:.1f}, deviation: {deviation:+.1f})")
    
    chi_result = fairness_test['chi_square_test']
    print(f"\nChi-square statistic: {chi_result['chi_square']:.3f}")
    print(f"Degrees of freedom: {chi_result['degrees_of_freedom']}")
    print(f"\nCritical values:")
    for alpha, critical in chi_result['critical_values'].items():
        print(f"  α = {alpha}: {critical}")
    
    print(f"\nInterpretation:")
    for alpha, interpretation in chi_result['interpretation'].items():
        print(f"  {interpretation}")
    
    # 4. Central Limit Theorem
    print("\n4. CENTRAL LIMIT THEOREM")
    print("-" * 70)
    print("Demonstrating CLT with 1,000 samples of 100 die rolls each:")
    
    clt_result = analyze_sampling_distribution(1000, 100)
    sampling_stats = clt_result['sampling_distribution']
    
    print(f"\nSampling distribution of means:")
    print(f"  Mean of sample means: {sampling_stats['mean']:.4f}")
    print(f"  Theoretical mean: {clt_result['theoretical_mean']:.4f}")
    print(f"  Error: {abs(sampling_stats['mean'] - clt_result['theoretical_mean']):.4f}")
    
    print(f"\nStandard error:")
    print(f"  Empirical: {sampling_stats['std_dev']:.4f}")
    print(f"  Theoretical: {clt_result['theoretical_se']:.4f}")
    print(f"  Error: {abs(sampling_stats['std_dev'] - clt_result['theoretical_se']):.4f}")
    
    print(f"\nRange of sample means: [{sampling_stats['min']:.4f}, {sampling_stats['max']:.4f}]")
    
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("✓ Confidence intervals quantify uncertainty in estimates")
    print("✓ 95% CI means we're 95% confident the true value is in the interval")
    print("✓ Larger samples → narrower confidence intervals")
    print("✓ Chi-square test validates distribution assumptions")
    print("✓ Central Limit Theorem: sample means → normal distribution")
    print("✓ Standard error decreases with √n (Law of Large Numbers)")
    print("="*70)


if __name__ == "__main__":
    main()
