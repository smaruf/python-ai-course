"""
Parsing Polling Data
====================

This module provides functions to parse polling data from CSV files.
Each state has polling data showing candidate percentages and electoral votes.

Learning Objectives:
- Read and parse CSV files in Python
- Structure data using dictionaries
- Validate data integrity
- Handle file I/O errors gracefully

Data Format:
CSV files should have columns: State, CandidateA, CandidateB, ElectoralVotes
Example:
    State,CandidateA,CandidateB,ElectoralVotes
    Pennsylvania,48.5,47.2,19
    Michigan,49.1,46.8,15
    Wisconsin,48.9,47.5,10

Returns state_polls dictionary:
    {
        'Pennsylvania': {'candidate_a': 48.5, 'candidate_b': 47.2, 'electoral_votes': 19},
        'Michigan': {'candidate_a': 49.1, 'candidate_b': 46.8, 'electoral_votes': 15},
        ...
    }
"""

import csv
import os


def parse_polling_file(filename):
    """
    Parse polling data from a CSV file.
    
    Args:
        filename (str): Path to the CSV file with polling data
        
    Returns:
        dict: Dictionary mapping state names to polling data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
        
    Example:
        >>> # Create a test file
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        ...     f.write('State,CandidateA,CandidateB,ElectoralVotes\\n')
        ...     f.write('TestState,51.0,49.0,10\\n')
        ...     temp_file = f.name
        >>> polls = parse_polling_file(temp_file)
        >>> polls['TestState']['candidate_a']
        51.0
        >>> polls['TestState']['electoral_votes']
        10
        >>> os.unlink(temp_file)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Polling file not found: {filename}")
    
    state_polls = {}
    
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            
            # Validate header
            required_fields = {'State', 'CandidateA', 'CandidateB', 'ElectoralVotes'}
            if not required_fields.issubset(set(reader.fieldnames or [])):
                raise ValueError(f"CSV must contain columns: {required_fields}")
            
            for row in reader:
                state = row['State'].strip()
                
                try:
                    candidate_a = float(row['CandidateA'])
                    candidate_b = float(row['CandidateB'])
                    electoral_votes = int(row['ElectoralVotes'])
                except (ValueError, KeyError) as e:
                    raise ValueError(f"Invalid data format for state {state}: {e}")
                
                # Validate data ranges
                if candidate_a < 0 or candidate_a > 100:
                    raise ValueError(f"Invalid percentage for Candidate A in {state}: {candidate_a}")
                if candidate_b < 0 or candidate_b > 100:
                    raise ValueError(f"Invalid percentage for Candidate B in {state}: {candidate_b}")
                if electoral_votes < 1:
                    raise ValueError(f"Invalid electoral votes for {state}: {electoral_votes}")
                
                state_polls[state] = {
                    'candidate_a': candidate_a,
                    'candidate_b': candidate_b,
                    'electoral_votes': electoral_votes
                }
    
    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    if not state_polls:
        raise ValueError("No valid polling data found in file")
    
    return state_polls


def validate_state_data(state_dict):
    """
    Validate that a state polling dictionary has correct structure.
    
    Args:
        state_dict (dict): State polling data to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Example:
        >>> valid_data = {'candidate_a': 48.5, 'candidate_b': 47.2, 'electoral_votes': 19}
        >>> validate_state_data(valid_data)
        True
        >>> invalid_data = {'candidate_a': 48.5}
        >>> validate_state_data(invalid_data)
        False
    """
    required_keys = {'candidate_a', 'candidate_b', 'electoral_votes'}
    
    if not isinstance(state_dict, dict):
        return False
    
    if not required_keys.issubset(state_dict.keys()):
        return False
    
    try:
        candidate_a = float(state_dict['candidate_a'])
        candidate_b = float(state_dict['candidate_b'])
        electoral_votes = int(state_dict['electoral_votes'])
        
        if candidate_a < 0 or candidate_a > 100:
            return False
        if candidate_b < 0 or candidate_b > 100:
            return False
        if electoral_votes < 1:
            return False
            
        return True
    except (ValueError, TypeError):
        return False


def get_state_poll(state_polls, state_name):
    """
    Get polling data for a specific state.
    
    Args:
        state_polls (dict): Dictionary of all state polling data
        state_name (str): Name of the state to retrieve
        
    Returns:
        dict: Polling data for the state, or None if not found
        
    Example:
        >>> polls = {'Pennsylvania': {'candidate_a': 48.5, 'candidate_b': 47.2, 'electoral_votes': 19}}
        >>> result = get_state_poll(polls, 'Pennsylvania')
        >>> result['candidate_a']
        48.5
        >>> get_state_poll(polls, 'NonExistent')
    """
    return state_polls.get(state_name)


def summarize_polls(state_polls):
    """
    Generate a summary of polling data.
    
    Args:
        state_polls (dict): Dictionary of all state polling data
        
    Returns:
        dict: Summary statistics
        
    Example:
        >>> polls = {
        ...     'State1': {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10},
        ...     'State2': {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 15}
        ... }
        >>> summary = summarize_polls(polls)
        >>> summary['total_states']
        2
        >>> summary['total_electoral_votes']
        25
    """
    total_states = len(state_polls)
    total_electoral_votes = sum(data['electoral_votes'] for data in state_polls.values())
    
    a_leading = sum(1 for data in state_polls.values() if data['candidate_a'] > data['candidate_b'])
    b_leading = sum(1 for data in state_polls.values() if data['candidate_b'] > data['candidate_a'])
    tied = total_states - a_leading - b_leading
    
    return {
        'total_states': total_states,
        'total_electoral_votes': total_electoral_votes,
        'candidate_a_leading': a_leading,
        'candidate_b_leading': b_leading,
        'tied': tied
    }


def main():
    """
    Demonstration of parsing polling data.
    """
    print("=" * 70)
    print("Polling Data Parser - Demonstration")
    print("=" * 70)
    print()
    
    # Create a sample data file for demonstration
    sample_data = """State,CandidateA,CandidateB,ElectoralVotes
Pennsylvania,48.5,47.2,19
Michigan,49.1,46.8,15
Wisconsin,48.9,47.5,10
Arizona,47.8,48.5,11
Georgia,48.2,48.1,16
Nevada,47.5,48.2,6
North Carolina,47.9,48.4,16"""
    
    # Write to a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write(sample_data)
        temp_file = f.name
    
    try:
        # Parse the data
        print("Parsing sample polling data...")
        state_polls = parse_polling_file(temp_file)
        print(f"✓ Successfully parsed {len(state_polls)} states")
        print()
        
        # Display the data
        print("State-by-State Polling:")
        print("-" * 70)
        print(f"{'State':<20} {'Candidate A':>12} {'Candidate B':>12} {'EV':>6}")
        print("-" * 70)
        
        for state, data in sorted(state_polls.items()):
            print(f"{state:<20} {data['candidate_a']:>11.1f}% {data['candidate_b']:>11.1f}% {data['electoral_votes']:>6}")
        
        print()
        
        # Show summary
        summary = summarize_polls(state_polls)
        print("Summary Statistics:")
        print("-" * 70)
        print(f"Total States: {summary['total_states']}")
        print(f"Total Electoral Votes: {summary['total_electoral_votes']}")
        print(f"Candidate A Leading: {summary['candidate_a_leading']} states")
        print(f"Candidate B Leading: {summary['candidate_b_leading']} states")
        print(f"Tied: {summary['tied']} states")
        print()
        
        # Demonstrate validation
        print("Data Validation:")
        print("-" * 70)
        sample_state = list(state_polls.keys())[0]
        is_valid = validate_state_data(state_polls[sample_state])
        print(f"✓ {sample_state} data is valid: {is_valid}")
        print()
        
        # Demonstrate retrieval
        print("Retrieving Specific State:")
        print("-" * 70)
        pa_data = get_state_poll(state_polls, 'Pennsylvania')
        if pa_data:
            print(f"Pennsylvania: A={pa_data['candidate_a']}%, B={pa_data['candidate_b']}%, EV={pa_data['electoral_votes']}")
        print()
        
        print("=" * 70)
        print("Next: Run 02_single_election.py to simulate an election!")
        print("=" * 70)
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file)


if __name__ == "__main__":
    main()
