"""
Simulating Multiple Elections with Uncertainty
===============================================

This module simulates thousands of elections by adding random variation
to polling data to model polling uncertainty.

Learning Objectives:
- Model polling uncertainty with random sampling
- Use normal distribution to add noise
- Run Monte Carlo simulations
- Calculate win probabilities from simulation results
- Understand why simulations are more confident than they should be

Polling Uncertainty:
- Polls have margin of error (typically ±3-4%)
- We add random noise to each poll using normal distribution
- This models the uncertainty in our polling averages
- Running 10,000 simulations gives us probability estimates

The Key Insight (from video timestamp 1:30:05):
Why is our simulation so confident? Because we're modeling random error
but not systematic bias. All polls can be wrong in the same direction!
"""

import random


def add_polling_noise(poll_value, margin_of_error=3.0):
    """
    Add random noise to a poll value to simulate polling uncertainty.
    
    Uses normal distribution with standard deviation = margin_of_error/2
    (since margin of error is typically 95% confidence interval, ±2 std dev)
    
    Args:
        poll_value (float): Original poll percentage
        margin_of_error (float): Margin of error (default 3.0%)
        
    Returns:
        float: Poll value with added noise
        
    Example:
        >>> random.seed(42)
        >>> result = add_polling_noise(50.0, margin_of_error=3.0)
        >>> 47.0 < result < 53.0  # Should be within margin of error most of the time
        True
    """
    # Convert margin of error to standard deviation
    # Margin of error is typically ±2 standard deviations (95% confidence)
    std_dev = margin_of_error / 2.0
    
    # Add random noise from normal distribution
    noise = random.gauss(0, std_dev)
    noisy_value = poll_value + noise
    
    # Clamp to valid percentage range
    return max(0.0, min(100.0, noisy_value))


def simulate_single_election_with_noise(state_polls, margin_of_error=3.0):
    """
    Simulate one election with polling noise added to each state.
    
    Args:
        state_polls (dict): Dictionary of state polling data
        margin_of_error (float): Margin of error for polling (default 3.0%)
        
    Returns:
        dict: Election results with winner and electoral vote totals
        
    Example:
        >>> random.seed(42)
        >>> polls = {
        ...     'State1': {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10},
        ... }
        >>> result = simulate_single_election_with_noise(polls, margin_of_error=3.0)
        >>> 'winner' in result
        True
    """
    state_results = {}
    candidate_a_ev = 0
    candidate_b_ev = 0
    
    for state, poll_data in state_polls.items():
        # Add noise to both candidates' polling numbers
        a_poll_noisy = add_polling_noise(poll_data['candidate_a'], margin_of_error)
        b_poll_noisy = add_polling_noise(poll_data['candidate_b'], margin_of_error)
        
        # Determine winner based on noisy polls
        if a_poll_noisy > b_poll_noisy:
            winner = 'A'
            candidate_a_ev += poll_data['electoral_votes']
        elif b_poll_noisy > a_poll_noisy:
            winner = 'B'
            candidate_b_ev += poll_data['electoral_votes']
        else:
            winner = 'TIE'
        
        state_results[state] = winner
    
    # Determine overall winner
    if candidate_a_ev > candidate_b_ev:
        overall_winner = 'A'
    elif candidate_b_ev > candidate_a_ev:
        overall_winner = 'B'
    else:
        overall_winner = 'TIE'
    
    return {
        'state_results': state_results,
        'candidate_a_electoral_votes': candidate_a_ev,
        'candidate_b_electoral_votes': candidate_b_ev,
        'winner': overall_winner
    }


def simulate_multiple_elections(state_polls, num_simulations=10000, margin_of_error=3.0):
    """
    Run multiple election simulations and aggregate results.
    
    Args:
        state_polls (dict): Dictionary of state polling data
        num_simulations (int): Number of elections to simulate (default 10,000)
        margin_of_error (float): Margin of error for polling (default 3.0%)
        
    Returns:
        dict: Aggregated simulation results with win counts and probabilities
        
    Example:
        >>> random.seed(42)
        >>> polls = {
        ...     'State1': {'candidate_a': 52.0, 'candidate_b': 48.0, 'electoral_votes': 10},
        ... }
        >>> results = simulate_multiple_elections(polls, num_simulations=100)
        >>> results['num_simulations']
        100
        >>> results['candidate_a_wins'] > 50  # A should win most with 52% polling
        True
    """
    candidate_a_wins = 0
    candidate_b_wins = 0
    ties = 0
    
    # Track state-level win frequencies
    state_win_counts = {state: {'A': 0, 'B': 0, 'TIE': 0} for state in state_polls.keys()}
    
    # Track electoral vote distribution
    ev_distribution = []
    
    for _ in range(num_simulations):
        result = simulate_single_election_with_noise(state_polls, margin_of_error)
        
        # Count overall winners
        if result['winner'] == 'A':
            candidate_a_wins += 1
        elif result['winner'] == 'B':
            candidate_b_wins += 1
        else:
            ties += 1
        
        # Track state-level results
        for state, winner in result['state_results'].items():
            state_win_counts[state][winner] += 1
        
        # Track electoral vote totals
        ev_distribution.append({
            'candidate_a': result['candidate_a_electoral_votes'],
            'candidate_b': result['candidate_b_electoral_votes']
        })
    
    return {
        'num_simulations': num_simulations,
        'candidate_a_wins': candidate_a_wins,
        'candidate_b_wins': candidate_b_wins,
        'ties': ties,
        'candidate_a_win_probability': candidate_a_wins / num_simulations,
        'candidate_b_win_probability': candidate_b_wins / num_simulations,
        'state_win_counts': state_win_counts,
        'ev_distribution': ev_distribution
    }


def analyze_results(simulation_results):
    """
    Analyze and format simulation results for display.
    
    Args:
        simulation_results (dict): Results from simulate_multiple_elections
        
    Returns:
        dict: Formatted analysis including key statistics
        
    Example:
        >>> results = {
        ...     'num_simulations': 100,
        ...     'candidate_a_wins': 60,
        ...     'candidate_b_wins': 40,
        ...     'ties': 0,
        ...     'candidate_a_win_probability': 0.6,
        ...     'candidate_b_win_probability': 0.4,
        ... }
        >>> analysis = analyze_results(results)
        >>> analysis['favorite']
        'A'
    """
    num_sims = simulation_results['num_simulations']
    a_wins = simulation_results['candidate_a_wins']
    b_wins = simulation_results['candidate_b_wins']
    
    favorite = 'A' if a_wins > b_wins else 'B' if b_wins > a_wins else 'TIE'
    
    return {
        'favorite': favorite,
        'favorite_win_pct': max(a_wins, b_wins) / num_sims * 100,
        'underdog_win_pct': min(a_wins, b_wins) / num_sims * 100,
        'total_simulations': num_sims
    }


def main():
    """
    Demonstration of multiple election simulations with polling uncertainty.
    """
    print("=" * 70)
    print("Multiple Election Simulation - Demonstration")
    print("=" * 70)
    print()
    
    # Sample polling data
    state_polls = {
        'Pennsylvania': {'candidate_a': 48.5, 'candidate_b': 47.2, 'electoral_votes': 19},
        'Michigan': {'candidate_a': 49.1, 'candidate_b': 46.8, 'electoral_votes': 15},
        'Wisconsin': {'candidate_a': 48.9, 'candidate_b': 47.5, 'electoral_votes': 10},
        'Arizona': {'candidate_a': 47.8, 'candidate_b': 48.5, 'electoral_votes': 11},
        'Georgia': {'candidate_a': 48.2, 'candidate_b': 48.1, 'electoral_votes': 16},
        'Nevada': {'candidate_a': 47.5, 'candidate_b': 48.2, 'electoral_votes': 6},
        'North Carolina': {'candidate_a': 47.9, 'candidate_b': 48.4, 'electoral_votes': 16},
    }
    
    num_simulations = 10000
    margin_of_error = 3.0
    
    print(f"Running {num_simulations:,} election simulations...")
    print(f"Margin of error: ±{margin_of_error}%")
    print()
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Run simulations
    results = simulate_multiple_elections(state_polls, num_simulations, margin_of_error)
    
    # Display overall results
    print("Overall Results:")
    print("-" * 70)
    print(f"Candidate A wins: {results['candidate_a_wins']:,} times ({results['candidate_a_win_probability']*100:.1f}%)")
    print(f"Candidate B wins: {results['candidate_b_wins']:,} times ({results['candidate_b_win_probability']*100:.1f}%)")
    print(f"Ties: {results['ties']:,} times")
    print()
    
    # Display state-level probabilities
    print("State Win Probabilities:")
    print("-" * 70)
    print(f"{'State':<20} {'A Wins':>10} {'B Wins':>10} {'A Win %':>10}")
    print("-" * 70)
    
    for state in sorted(state_polls.keys()):
        counts = results['state_win_counts'][state]
        a_pct = counts['A'] / num_simulations * 100
        print(f"{state:<20} {counts['A']:>10} {counts['B']:>10} {a_pct:>9.1f}%")
    
    print()
    
    # Analyze results
    analysis = analyze_results(results)
    print("Analysis:")
    print("-" * 70)
    print(f"Favorite: Candidate {analysis['favorite']}")
    print(f"Win Probability: {analysis['favorite_win_pct']:.1f}%")
    print()
    
    # Calculate average electoral votes
    avg_a_ev = sum(ev['candidate_a'] for ev in results['ev_distribution']) / num_simulations
    avg_b_ev = sum(ev['candidate_b'] for ev in results['ev_distribution']) / num_simulations
    
    print(f"Average Electoral Votes:")
    print(f"  Candidate A: {avg_a_ev:.1f}")
    print(f"  Candidate B: {avg_b_ev:.1f}")
    print()
    
    print("=" * 70)
    print("Key Insight (from video at 1:30:05):")
    print("Why is our simulation so confident?")
    print()
    print("We're modeling RANDOM error in polls, but polls can have")
    print("SYSTEMATIC bias - all polls wrong in the same direction!")
    print()
    print("This is why real forecasters add correlation between states")
    print("and why prediction markets can be better than models.")
    print("=" * 70)
    print()
    print("Next: Run 04_electoral_college.py for the complete simulation!")
    print("=" * 70)


if __name__ == "__main__":
    main()
