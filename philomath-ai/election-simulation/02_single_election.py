"""
Simulating a Single Election
=============================

This module simulates a single election based on polling data.
Uses the Electoral College system where each state awards all its
electoral votes to the winner (winner-take-all).

Learning Objectives:
- Simulate state-level elections
- Apply Electoral College rules
- Aggregate state results
- Determine overall winner

Electoral College Rules:
- Each state awards all electoral votes to the candidate with higher polling
- Need 270+ electoral votes to win (out of 538 total in real elections)
- Winner in each state gets all that state's electoral votes

This is a deterministic simulation - no randomness yet.
We'll add polling uncertainty in the next module.
"""


def simulate_state(poll_data):
    """
    Determine the winner of a state based on polling data.
    
    Args:
        poll_data (dict): State polling data with 'candidate_a', 'candidate_b', 'electoral_votes'
        
    Returns:
        str: 'A' if Candidate A wins, 'B' if Candidate B wins, 'TIE' if tied
        
    Example:
        >>> poll_data = {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10}
        >>> simulate_state(poll_data)
        'A'
        >>> poll_data = {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 10}
        >>> simulate_state(poll_data)
        'B'
        >>> poll_data = {'candidate_a': 50.0, 'candidate_b': 50.0, 'electoral_votes': 10}
        >>> simulate_state(poll_data)
        'TIE'
    """
    if poll_data['candidate_a'] > poll_data['candidate_b']:
        return 'A'
    elif poll_data['candidate_b'] > poll_data['candidate_a']:
        return 'B'
    else:
        return 'TIE'


def simulate_election(state_polls):
    """
    Simulate a complete election across all states.
    
    Args:
        state_polls (dict): Dictionary mapping state names to polling data
        
    Returns:
        dict: Election results including state winners and electoral vote totals
        
    Example:
        >>> state_polls = {
        ...     'State1': {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10},
        ...     'State2': {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 15},
        ...     'State3': {'candidate_a': 55.0, 'candidate_b': 45.0, 'electoral_votes': 8}
        ... }
        >>> results = simulate_election(state_polls)
        >>> results['candidate_a_electoral_votes']
        18
        >>> results['candidate_b_electoral_votes']
        15
        >>> results['winner']
        'A'
    """
    state_results = {}
    candidate_a_ev = 0
    candidate_b_ev = 0
    
    for state, poll_data in state_polls.items():
        winner = simulate_state(poll_data)
        state_results[state] = winner
        
        if winner == 'A':
            candidate_a_ev += poll_data['electoral_votes']
        elif winner == 'B':
            candidate_b_ev += poll_data['electoral_votes']
        # If TIE, no one gets the electoral votes (rare in practice)
    
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


def calculate_electoral_votes(state_results, state_polls):
    """
    Calculate electoral vote totals from state results.
    
    Args:
        state_results (dict): Dictionary mapping states to winners ('A' or 'B')
        state_polls (dict): Dictionary with electoral vote counts
        
    Returns:
        tuple: (candidate_a_total, candidate_b_total)
        
    Example:
        >>> state_results = {'State1': 'A', 'State2': 'B', 'State3': 'A'}
        >>> state_polls = {
        ...     'State1': {'electoral_votes': 10},
        ...     'State2': {'electoral_votes': 15},
        ...     'State3': {'electoral_votes': 8}
        ... }
        >>> calculate_electoral_votes(state_results, state_polls)
        (18, 15)
    """
    candidate_a_total = 0
    candidate_b_total = 0
    
    for state, winner in state_results.items():
        if winner == 'A':
            candidate_a_total += state_polls[state]['electoral_votes']
        elif winner == 'B':
            candidate_b_total += state_polls[state]['electoral_votes']
    
    return candidate_a_total, candidate_b_total


def get_close_states(state_polls, margin_threshold=2.0):
    """
    Identify states with close polling (within margin_threshold).
    
    Args:
        state_polls (dict): Dictionary of state polling data
        margin_threshold (float): Maximum margin to be considered close (default 2.0%)
        
    Returns:
        list: List of (state, margin) tuples for close states
        
    Example:
        >>> polls = {
        ...     'State1': {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10},
        ...     'State2': {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 15},
        ...     'State3': {'candidate_a': 60.0, 'candidate_b': 40.0, 'electoral_votes': 8}
        ... }
        >>> close = get_close_states(polls, margin_threshold=5.0)
        >>> len(close)
        2
    """
    close_states = []
    
    for state, poll_data in state_polls.items():
        margin = abs(poll_data['candidate_a'] - poll_data['candidate_b'])
        if margin <= margin_threshold:
            close_states.append((state, margin))
    
    # Sort by margin (closest first)
    close_states.sort(key=lambda x: x[1])
    
    return close_states


def main():
    """
    Demonstration of simulating a single election.
    """
    print("=" * 70)
    print("Single Election Simulation - Demonstration")
    print("=" * 70)
    print()
    
    # Import the parsing module to get sample data
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        # Create sample polling data
        state_polls = {
            'Pennsylvania': {'candidate_a': 48.5, 'candidate_b': 47.2, 'electoral_votes': 19},
            'Michigan': {'candidate_a': 49.1, 'candidate_b': 46.8, 'electoral_votes': 15},
            'Wisconsin': {'candidate_a': 48.9, 'candidate_b': 47.5, 'electoral_votes': 10},
            'Arizona': {'candidate_a': 47.8, 'candidate_b': 48.5, 'electoral_votes': 11},
            'Georgia': {'candidate_a': 48.2, 'candidate_b': 48.1, 'electoral_votes': 16},
            'Nevada': {'candidate_a': 47.5, 'candidate_b': 48.2, 'electoral_votes': 6},
            'North Carolina': {'candidate_a': 47.9, 'candidate_b': 48.4, 'electoral_votes': 16},
        }
        
        print("Simulating election based on polling data...")
        print()
        
        # Run simulation
        results = simulate_election(state_polls)
        
        # Display state-by-state results
        print("State-by-State Results:")
        print("-" * 70)
        print(f"{'State':<20} {'A Poll':>10} {'B Poll':>10} {'Winner':>10} {'EV':>6}")
        print("-" * 70)
        
        for state in sorted(state_polls.keys()):
            poll = state_polls[state]
            winner = results['state_results'][state]
            winner_mark = '← A' if winner == 'A' else '← B' if winner == 'B' else 'TIE'
            print(f"{state:<20} {poll['candidate_a']:>9.1f}% {poll['candidate_b']:>9.1f}% {winner_mark:>10} {poll['electoral_votes']:>6}")
        
        print()
        
        # Display electoral vote totals
        print("Electoral Vote Totals:")
        print("-" * 70)
        print(f"Candidate A: {results['candidate_a_electoral_votes']} electoral votes")
        print(f"Candidate B: {results['candidate_b_electoral_votes']} electoral votes")
        print()
        
        # Display winner
        if results['winner'] == 'A':
            print(f"🎉 Winner: Candidate A (by {results['candidate_a_electoral_votes'] - results['candidate_b_electoral_votes']} electoral votes)")
        elif results['winner'] == 'B':
            print(f"🎉 Winner: Candidate B (by {results['candidate_b_electoral_votes'] - results['candidate_a_electoral_votes']} electoral votes)")
        else:
            print("Result: Electoral College Tie")
        
        print()
        
        # Identify close states
        print("Close States (within 2%):")
        print("-" * 70)
        close_states = get_close_states(state_polls, margin_threshold=2.0)
        
        if close_states:
            for state, margin in close_states:
                ev = state_polls[state]['electoral_votes']
                print(f"{state:<20} (margin: {margin:.1f}%, {ev} EV)")
        else:
            print("No states within 2% margin")
        
        print()
        print("=" * 70)
        print("Note: This is a deterministic simulation based on polling averages.")
        print("Next: Run 03_multiple_elections.py to add polling uncertainty!")
        print("=" * 70)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
