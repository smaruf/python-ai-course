"""
Bangladesh Election 2026 Simulation
====================================

Demonstration of election simulation using Bangladesh 2026 election data.

This script simulates the landmark Bangladesh 2026 general election where
BNP (Bangladesh Nationalist Party) achieved a landslide victory, winning
209-213 seats out of 299 in parliament.

The simulation uses pre-election polling data to model the electoral outcome
and demonstrates how Monte Carlo methods can forecast election results.

Historical Context:
- First election after the 2024 political upheaval
- BNP led by Tarique Rahman (son of Khaleda Zia)
- Jamaat-e-Islami as main opposition
- Awami League was banned and did not participate
- High voter turnout with 127 million registered voters
- Held alongside constitutional reform referendum

Learning Objectives:
- Apply election simulation to real-world scenarios
- Understand parliamentary seat allocation
- Model single-member constituency systems
- Compare to Electoral College systems
"""

import sys
import os
import random

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import our modules
import importlib.util

def load_module(filename):
    """Load a module from file."""
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules
parsing = load_module('01_parsing_data.py')
ec = load_module('04_electoral_college.py')


def simulate_bd_election_2026():
    """
    Simulate Bangladesh 2026 election using actual polling data.
    """
    print("=" * 70)
    print("Bangladesh Election 2026 Simulation")
    print("=" * 70)
    print()
    print("Historical Context:")
    print("-" * 70)
    print("This simulation models Bangladesh's landmark 2026 general election:")
    print("- First election after 2024 political upheaval")
    print("- BNP (Bangladesh Nationalist Party) vs Jamaat-e-Islami")
    print("- 299 parliamentary constituencies (single-member districts)")
    print("- BNP won 209-213 seats (landslide victory)")
    print("- Tarique Rahman became Prime Minister")
    print()
    
    # Load different datasets
    datasets = [
        ('data/bd_2026_swing_constituencies.csv', 'Swing Constituencies (10 close races)'),
        ('data/bd_2026_polls.csv', 'Key Constituencies (15 important seats)'),
        ('data/bd_2026_comprehensive.csv', 'Comprehensive Data (75 constituencies)'),
    ]
    
    for filename, description in datasets:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if not os.path.exists(filepath):
            print(f"⚠ {description} file not found: {filename}")
            continue
        
        print("=" * 70)
        print(f"Simulating: {description}")
        print("=" * 70)
        print()
        
        # Parse data
        constituency_polls = parsing.parse_polling_file(filepath)
        print(f"Loaded {len(constituency_polls)} constituencies")
        print()
        
        # Run simulation
        print("Running 10,000 Monte Carlo simulations...")
        random.seed(42)  # For reproducibility
        
        results = ec.simulate_electoral_college(
            constituency_polls,
            num_simulations=10000,
            margin_of_error=3.0,
            seed=42
        )
        
        # Display results
        print()
        print("Simulation Results:")
        print("-" * 70)
        
        bnp_wins = results['candidate_a_wins']
        jamaat_wins = results['candidate_b_wins']
        total_sims = results['num_simulations']
        
        bnp_pct = bnp_wins / total_sims * 100
        jamaat_pct = jamaat_wins / total_sims * 100
        
        print(f"BNP wins: {bnp_wins:,} simulations ({bnp_pct:.1f}%)")
        print(f"Jamaat wins: {jamaat_wins:,} simulations ({jamaat_pct:.1f}%)")
        print()
        
        # Calculate average seats
        avg_bnp = sum(ev['candidate_a'] for ev in results['ev_distribution']) / total_sims
        avg_jamaat = sum(ev['candidate_b'] for ev in results['ev_distribution']) / total_sims
        
        print(f"Average Seats:")
        print(f"  BNP: {avg_bnp:.1f} seats")
        print(f"  Jamaat: {avg_jamaat:.1f} seats")
        print()
        
        # Show close constituencies
        print("Constituencies with Closest Polling:")
        print("-" * 70)
        margins = []
        for const, data in constituency_polls.items():
            margin = abs(data['candidate_a'] - data['candidate_b'])
            margins.append((const, margin, data))
        
        margins.sort(key=lambda x: x[1])
        
        for const, margin, data in margins[:5]:
            bnp_win_pct = results['state_win_counts'][const]['A'] / total_sims * 100
            print(f"{const:<25} Margin: {margin:>5.1f}%  BNP wins {bnp_win_pct:>5.1f}% of simulations")
        
        print()
    
    print("=" * 70)
    print("Key Insights:")
    print("-" * 70)
    print("1. Parliamentary Systems: Each constituency awards 1 seat to winner")
    print("2. Winner-Take-All: Unlike proportional representation, winner gets all")
    print("3. Polling Uncertainty: Even small margins can swing results")
    print("4. Historical Validation: Actual 2026 results showed BNP landslide")
    print()
    print("Compare to US Electoral College:")
    print("- Both use winner-take-all for geographic units")
    print("- US: States with varying electoral votes (3-55)")
    print("- BD: Constituencies with equal representation (1 seat each)")
    print("=" * 70)


def compare_election_systems():
    """
    Compare US Electoral College vs Bangladesh Parliamentary system.
    """
    print()
    print("=" * 70)
    print("Comparing Election Systems")
    print("=" * 70)
    print()
    
    print("United States Electoral College:")
    print("-" * 70)
    print("- 50 states + DC = 538 total electoral votes")
    print("- Each state gets votes based on population")
    print("- Winner-take-all in 48 states")
    print("- Need 270 votes to win presidency")
    print("- Example: California = 55 votes, Wyoming = 3 votes")
    print()
    
    print("Bangladesh Parliamentary System:")
    print("-" * 70)
    print("- 300 constituencies (299 in 2026 due to postponements)")
    print("- Each constituency = 1 parliamentary seat")
    print("- Winner-take-all in each constituency")
    print("- Need 151 seats for majority (out of 300)")
    print("- All constituencies have equal representation")
    print()
    
    print("Key Differences:")
    print("-" * 70)
    print("1. Representation: US varies by population, BD is uniform")
    print("2. Scale: US has 538 votes, BD has 300 seats")
    print("3. Executive: US elects president directly via EC, BD PM from majority party")
    print("4. Fairness: Both criticized - US for small state advantage, BD for gerrymandering")
    print("=" * 70)


def main():
    """
    Main demonstration function.
    """
    simulate_bd_election_2026()
    compare_election_systems()
    
    print()
    print("For more information:")
    print("- See data/README.md for dataset documentation")
    print("- Run other modules for US election simulations")
    print("- Visit programmingforlovers.com for the full course")
    print()


if __name__ == "__main__":
    main()
