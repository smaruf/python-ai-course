"""
Complete Electoral College Simulation
======================================

This module provides a complete election forecasting system that:
1. Loads polling data from files
2. Runs thousands of Monte Carlo simulations
3. Models polling uncertainty
4. Calculates win probabilities
5. Generates comprehensive reports

This is the highest-level module that brings everything together,
as shown in the Programming for Lovers video at timestamp 35:43.

Learning Objectives:
- Integrate multiple modules into a complete system
- Generate comprehensive forecasting reports
- Understand model limitations
- Compare to prediction markets

Key Limitation (from video at 1:38:58):
All polling simulators have the same fundamental problem - they model
random error but not systematic bias. Prediction markets like Kalshi
can aggregate information better because they use real money.
"""

import random
import sys
import os


# Import our previous modules
# Note: In production, these would be proper imports
# For this educational module, we keep everything standalone


def parse_polling_file(filename):
    """Parse polling data from CSV file. See 01_parsing_data.py"""
    import csv
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Polling file not found: {filename}")
    
    state_polls = {}
    
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            state = row['State'].strip()
            state_polls[state] = {
                'candidate_a': float(row['CandidateA']),
                'candidate_b': float(row['CandidateB']),
                'electoral_votes': int(row['ElectoralVotes'])
            }
    
    return state_polls


def add_polling_noise(poll_value, margin_of_error=3.0):
    """Add random noise to poll. See 03_multiple_elections.py"""
    std_dev = margin_of_error / 2.0
    noise = random.gauss(0, std_dev)
    noisy_value = poll_value + noise
    return max(0.0, min(100.0, noisy_value))


def simulate_single_election_with_noise(state_polls, margin_of_error=3.0):
    """Simulate one election with noise. See 03_multiple_elections.py"""
    state_results = {}
    candidate_a_ev = 0
    candidate_b_ev = 0
    
    for state, poll_data in state_polls.items():
        a_poll_noisy = add_polling_noise(poll_data['candidate_a'], margin_of_error)
        b_poll_noisy = add_polling_noise(poll_data['candidate_b'], margin_of_error)
        
        if a_poll_noisy > b_poll_noisy:
            winner = 'A'
            candidate_a_ev += poll_data['electoral_votes']
        elif b_poll_noisy > a_poll_noisy:
            winner = 'B'
            candidate_b_ev += poll_data['electoral_votes']
        else:
            winner = 'TIE'
        
        state_results[state] = winner
    
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


def simulate_electoral_college(state_polls, num_simulations=10000, margin_of_error=3.0, seed=None):
    """
    Run complete Electoral College simulation.
    
    This is the highest-level function that orchestrates the entire simulation,
    as discussed in the video at timestamp 35:43.
    
    Args:
        state_polls (dict): Dictionary of state polling data
        num_simulations (int): Number of elections to simulate (default 10,000)
        margin_of_error (float): Polling margin of error (default 3.0%)
        seed (int): Random seed for reproducibility (optional)
        
    Returns:
        dict: Complete simulation results with statistics
        
    Example:
        >>> polls = {
        ...     'State1': {'candidate_a': 52.0, 'candidate_b': 48.0, 'electoral_votes': 10},
        ... }
        >>> results = simulate_electoral_college(polls, num_simulations=100, seed=42)
        >>> 'candidate_a_win_probability' in results
        True
    """
    if seed is not None:
        random.seed(seed)
    
    candidate_a_wins = 0
    candidate_b_wins = 0
    ties = 0
    
    state_win_counts = {state: {'A': 0, 'B': 0, 'TIE': 0} for state in state_polls.keys()}
    ev_distribution = []
    
    for _ in range(num_simulations):
        result = simulate_single_election_with_noise(state_polls, margin_of_error)
        
        if result['winner'] == 'A':
            candidate_a_wins += 1
        elif result['winner'] == 'B':
            candidate_b_wins += 1
        else:
            ties += 1
        
        for state, winner in result['state_results'].items():
            state_win_counts[state][winner] += 1
        
        ev_distribution.append({
            'candidate_a': result['candidate_a_electoral_votes'],
            'candidate_b': result['candidate_b_electoral_votes']
        })
    
    return {
        'num_simulations': num_simulations,
        'margin_of_error': margin_of_error,
        'candidate_a_wins': candidate_a_wins,
        'candidate_b_wins': candidate_b_wins,
        'ties': ties,
        'candidate_a_win_probability': candidate_a_wins / num_simulations,
        'candidate_b_win_probability': candidate_b_wins / num_simulations,
        'state_win_counts': state_win_counts,
        'ev_distribution': ev_distribution,
        'state_polls': state_polls
    }


def generate_report(results):
    """
    Generate a comprehensive text report from simulation results.
    
    Args:
        results (dict): Results from simulate_electoral_college
        
    Returns:
        str: Formatted report text
    """
    report_lines = []
    
    report_lines.append("=" * 70)
    report_lines.append("ELECTORAL COLLEGE SIMULATION REPORT")
    report_lines.append("=" * 70)
    report_lines.append("")
    
    # Simulation parameters
    report_lines.append("Simulation Parameters:")
    report_lines.append("-" * 70)
    report_lines.append(f"Number of simulations: {results['num_simulations']:,}")
    report_lines.append(f"Margin of error: ±{results['margin_of_error']}%")
    report_lines.append("")
    
    # Overall results
    report_lines.append("Overall Results:")
    report_lines.append("-" * 70)
    a_pct = results['candidate_a_win_probability'] * 100
    b_pct = results['candidate_b_win_probability'] * 100
    
    report_lines.append(f"Candidate A wins: {results['candidate_a_wins']:,} ({a_pct:.1f}%)")
    report_lines.append(f"Candidate B wins: {results['candidate_b_wins']:,} ({b_pct:.1f}%)")
    
    if results['ties'] > 0:
        tie_pct = results['ties'] / results['num_simulations'] * 100
        report_lines.append(f"Ties: {results['ties']:,} ({tie_pct:.1f}%)")
    
    report_lines.append("")
    
    # Winner announcement
    if a_pct > b_pct:
        report_lines.append(f"🎯 FORECAST: Candidate A favored to win ({a_pct:.1f}% probability)")
    elif b_pct > a_pct:
        report_lines.append(f"🎯 FORECAST: Candidate B favored to win ({b_pct:.1f}% probability)")
    else:
        report_lines.append("🎯 FORECAST: Race is a toss-up")
    
    report_lines.append("")
    
    # State-by-state results
    report_lines.append("State-by-State Analysis:")
    report_lines.append("-" * 70)
    report_lines.append(f"{'State':<20} {'A Poll':>9} {'B Poll':>9} {'A Win %':>10} {'EV':>6}")
    report_lines.append("-" * 70)
    
    state_polls = results['state_polls']
    for state in sorted(state_polls.keys()):
        poll = state_polls[state]
        counts = results['state_win_counts'][state]
        a_win_pct = counts['A'] / results['num_simulations'] * 100
        
        report_lines.append(
            f"{state:<20} {poll['candidate_a']:>8.1f}% {poll['candidate_b']:>8.1f}% "
            f"{a_win_pct:>9.1f}% {poll['electoral_votes']:>6}"
        )
    
    report_lines.append("")
    
    # Electoral vote statistics
    avg_a_ev = sum(ev['candidate_a'] for ev in results['ev_distribution']) / results['num_simulations']
    avg_b_ev = sum(ev['candidate_b'] for ev in results['ev_distribution']) / results['num_simulations']
    
    report_lines.append("Electoral Vote Statistics:")
    report_lines.append("-" * 70)
    report_lines.append(f"Average Candidate A electoral votes: {avg_a_ev:.1f}")
    report_lines.append(f"Average Candidate B electoral votes: {avg_b_ev:.1f}")
    report_lines.append("")
    
    # Model limitations (key insight from video)
    report_lines.append("⚠️  MODEL LIMITATIONS:")
    report_lines.append("-" * 70)
    report_lines.append("This simulation models RANDOM polling error but NOT systematic bias.")
    report_lines.append("In reality, polls can be wrong in the SAME DIRECTION across states.")
    report_lines.append("")
    report_lines.append("As discussed in the course (timestamp 1:38:58):")
    report_lines.append("- Polls may systematically miss certain voter groups")
    report_lines.append("- Turnout modeling introduces correlated errors")
    report_lines.append("- Late-deciding voters aren't captured in polls")
    report_lines.append("")
    report_lines.append("Consider using prediction markets (like Kalshi) as a complement")
    report_lines.append("to polling-based forecasts for better probability estimates.")
    report_lines.append("")
    
    report_lines.append("=" * 70)
    
    return "\n".join(report_lines)


def main():
    """
    Demonstration of complete Electoral College simulation.
    """
    print("=" * 70)
    print("Complete Electoral College Simulation")
    print("=" * 70)
    print()
    
    # Create sample data if no file provided
    state_polls = {
        'Pennsylvania': {'candidate_a': 48.5, 'candidate_b': 47.2, 'electoral_votes': 19},
        'Michigan': {'candidate_a': 49.1, 'candidate_b': 46.8, 'electoral_votes': 15},
        'Wisconsin': {'candidate_a': 48.9, 'candidate_b': 47.5, 'electoral_votes': 10},
        'Arizona': {'candidate_a': 47.8, 'candidate_b': 48.5, 'electoral_votes': 11},
        'Georgia': {'candidate_a': 48.2, 'candidate_b': 48.1, 'electoral_votes': 16},
        'Nevada': {'candidate_a': 47.5, 'candidate_b': 48.2, 'electoral_votes': 6},
        'North Carolina': {'candidate_a': 47.9, 'candidate_b': 48.4, 'electoral_votes': 16},
    }
    
    # Run simulation
    print("Running Electoral College simulation...")
    print("This may take a moment...")
    print()
    
    results = simulate_electoral_college(
        state_polls,
        num_simulations=10000,
        margin_of_error=3.0,
        seed=42  # For reproducibility
    )
    
    # Generate and display report
    report = generate_report(results)
    print(report)
    
    print()
    print("For more information:")
    print("- See README.md for detailed documentation")
    print("- Visit https://programmingforlovers.com for the full course")
    print("- Consider prediction markets like Kalshi for real-world forecasting")
    print()


if __name__ == "__main__":
    main()
