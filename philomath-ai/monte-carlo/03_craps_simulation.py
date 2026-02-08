"""
Craps Simulation and House Edge
================================

Craps is a classic casino dice game with interesting probability.
This module simulates the game of Craps and calculates the house edge
through Monte Carlo simulation.

Learning Objectives:
- Implement the rules of Craps
- Simulate thousands of games
- Calculate win probability empirically
- Understand house edge
- Compare simulation results to theoretical values

Craps Rules:
1. Come-out roll: Roll two dice
   - 7 or 11: Win immediately
   - 2, 3, or 12: Lose immediately (craps)
   - 4, 5, 6, 8, 9, 10: Establish "point", continue to phase 2

2. Point phase: Keep rolling until:
   - Roll the point again: Win
   - Roll a 7: Lose (seven-out)

House Edge:
The theoretical probability of winning at Craps is approximately 49.29%,
giving the house an edge of approximately 1.41%.
"""

import random


def roll_two_dice():
    """
    Roll two standard six-sided dice and return their sum.
    
    Returns:
        Sum of two dice (2-12)
    
    Example:
        >>> random.seed(42)
        >>> roll_two_dice()
        7
    """
    return random.randint(1, 6) + random.randint(1, 6)


def play_craps_once():
    """
    Play one complete game of Craps.
    
    Returns:
        Dictionary containing:
        - outcome: 'win' or 'lose'
        - come_out_roll: The initial roll
        - point: The point (if established), or None
        - rolls: List of all rolls in the game
        - n_rolls: Total number of rolls
    
    Example:
        >>> random.seed(42)
        >>> result = play_craps_once()
        >>> result['outcome'] in ['win', 'lose']
        True
    """
    rolls = []
    
    # Come-out roll
    come_out = roll_two_dice()
    rolls.append(come_out)
    
    # Check for immediate win
    if come_out in [7, 11]:
        return {
            'outcome': 'win',
            'come_out_roll': come_out,
            'point': None,
            'rolls': rolls,
            'n_rolls': len(rolls)
        }
    
    # Check for immediate loss (craps)
    if come_out in [2, 3, 12]:
        return {
            'outcome': 'lose',
            'come_out_roll': come_out,
            'point': None,
            'rolls': rolls,
            'n_rolls': len(rolls)
        }
    
    # Point is established
    point = come_out
    
    # Point phase: Keep rolling until we hit point or 7
    while True:
        current_roll = roll_two_dice()
        rolls.append(current_roll)
        
        if current_roll == point:
            # Hit the point - win!
            return {
                'outcome': 'win',
                'come_out_roll': come_out,
                'point': point,
                'rolls': rolls,
                'n_rolls': len(rolls)
            }
        
        if current_roll == 7:
            # Seven-out - lose!
            return {
                'outcome': 'lose',
                'come_out_roll': come_out,
                'point': point,
                'rolls': rolls,
                'n_rolls': len(rolls)
            }
        
        # Otherwise, keep rolling


def simulate_craps_games(n_games):
    """
    Simulate multiple games of Craps and collect statistics.
    
    Args:
        n_games: Number of games to simulate
    
    Returns:
        Dictionary containing:
        - n_games: Number of games played
        - wins: Number of wins
        - losses: Number of losses
        - win_rate: Empirical win probability
        - house_edge: Empirical house edge (1 - 2*win_rate)
        - avg_rolls_per_game: Average number of rolls per game
        - all_results: List of all game results
    
    Example:
        >>> random.seed(42)
        >>> results = simulate_craps_games(1000)
        >>> 0.45 < results['win_rate'] < 0.55  # Should be around 0.493
        True
    """
    all_results = []
    total_rolls = 0
    
    for _ in range(n_games):
        result = play_craps_once()
        all_results.append(result)
        total_rolls += result['n_rolls']
    
    wins = sum(1 for r in all_results if r['outcome'] == 'win')
    losses = sum(1 for r in all_results if r['outcome'] == 'lose')
    win_rate = wins / n_games
    
    # House edge = Expected loss per game
    # If win_rate = p, then house_edge = (1-p) - p = 1 - 2p
    house_edge = 1 - 2 * win_rate
    
    return {
        'n_games': n_games,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'house_edge': house_edge,
        'avg_rolls_per_game': total_rolls / n_games,
        'all_results': all_results
    }


def analyze_come_out_outcomes(n_games):
    """
    Analyze what happens on the come-out roll.
    
    Args:
        n_games: Number of games to simulate
    
    Returns:
        Dictionary with statistics about come-out rolls
    
    Example:
        >>> random.seed(42)
        >>> results = analyze_come_out_outcomes(10000)
        >>> results['immediate_wins'] + results['immediate_losses'] + results['point_established'] == 10000
        True
    """
    immediate_wins = 0  # 7 or 11
    immediate_losses = 0  # 2, 3, or 12
    point_established = 0  # 4, 5, 6, 8, 9, 10
    point_counts = {4: 0, 5: 0, 6: 0, 8: 0, 9: 0, 10: 0}
    
    for _ in range(n_games):
        come_out = roll_two_dice()
        
        if come_out in [7, 11]:
            immediate_wins += 1
        elif come_out in [2, 3, 12]:
            immediate_losses += 1
        else:
            point_established += 1
            point_counts[come_out] += 1
    
    return {
        'immediate_wins': immediate_wins,
        'immediate_losses': immediate_losses,
        'point_established': point_established,
        'immediate_win_rate': immediate_wins / n_games,
        'immediate_loss_rate': immediate_losses / n_games,
        'point_rate': point_established / n_games,
        'point_distribution': point_counts
    }


def calculate_theoretical_probabilities():
    """
    Calculate the theoretical probabilities for Craps.
    
    This uses exact probability calculations rather than simulation.
    
    Returns:
        Dictionary with theoretical probabilities
    """
    # Probabilities for two dice sums
    prob_two_dice = {
        2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36,
        7: 6/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36
    }
    
    # Probability of immediate win (7 or 11)
    p_immediate_win = prob_two_dice[7] + prob_two_dice[11]
    
    # Probability of immediate loss (2, 3, or 12)
    p_immediate_loss = prob_two_dice[2] + prob_two_dice[3] + prob_two_dice[12]
    
    # Probability of winning when point is established
    # For a point p, win probability = p(roll p before 7)
    # = P(p) / (P(p) + P(7))
    point_win_probabilities = {
        4: (3/36) / (3/36 + 6/36),   # = 3/9 = 1/3
        5: (4/36) / (4/36 + 6/36),   # = 4/10 = 2/5
        6: (5/36) / (5/36 + 6/36),   # = 5/11
        8: (5/36) / (5/36 + 6/36),   # = 5/11
        9: (4/36) / (4/36 + 6/36),   # = 4/10 = 2/5
        10: (3/36) / (3/36 + 6/36),  # = 3/9 = 1/3
    }
    
    # Total probability of winning via point
    p_point_win = sum(prob_two_dice[p] * point_win_probabilities[p] 
                      for p in [4, 5, 6, 8, 9, 10])
    
    # Total win probability
    p_win = p_immediate_win + p_point_win
    
    # House edge
    house_edge = 1 - 2 * p_win
    
    return {
        'immediate_win_prob': p_immediate_win,
        'immediate_loss_prob': p_immediate_loss,
        'point_win_prob': p_point_win,
        'total_win_prob': p_win,
        'house_edge': house_edge,
        'house_edge_percent': house_edge * 100
    }


def compare_simulation_to_theory(n_games):
    """
    Compare simulation results to theoretical probabilities.
    
    Args:
        n_games: Number of games to simulate
    
    Returns:
        Dictionary comparing simulation and theory
    """
    # Get simulation results
    sim_results = simulate_craps_games(n_games)
    
    # Get theoretical probabilities
    theory = calculate_theoretical_probabilities()
    
    return {
        'n_games': n_games,
        'simulation': {
            'win_rate': sim_results['win_rate'],
            'house_edge': sim_results['house_edge'],
            'house_edge_percent': sim_results['house_edge'] * 100
        },
        'theory': {
            'win_rate': theory['total_win_prob'],
            'house_edge': theory['house_edge'],
            'house_edge_percent': theory['house_edge_percent']
        },
        'difference': {
            'win_rate': abs(sim_results['win_rate'] - theory['total_win_prob']),
            'house_edge': abs(sim_results['house_edge'] - theory['house_edge'])
        }
    }


def demonstrate_convergence(sample_sizes=None):
    """
    Demonstrate how simulation converges to theory with more games.
    
    Args:
        sample_sizes: List of sample sizes to test
    
    Returns:
        List of results at each sample size
    """
    if sample_sizes is None:
        sample_sizes = [100, 1000, 10000, 100000]
    
    theory = calculate_theoretical_probabilities()
    results = []
    
    for n in sample_sizes:
        sim = simulate_craps_games(n)
        error = abs(sim['win_rate'] - theory['total_win_prob'])
        
        results.append({
            'n_games': n,
            'win_rate': sim['win_rate'],
            'theoretical': theory['total_win_prob'],
            'error': error,
            'percent_error': (error / theory['total_win_prob']) * 100
        })
    
    return results


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("="*70)
    print("CRAPS SIMULATION AND HOUSE EDGE")
    print("="*70)
    
    random.seed(42)  # For reproducibility
    
    # 1. Play a few sample games
    print("\n1. SAMPLE GAMES")
    print("-" * 70)
    for i in range(5):
        result = play_craps_once()
        outcome_str = "WIN " if result['outcome'] == 'win' else "LOSE"
        
        if result['point'] is None:
            print(f"Game {i+1}: Come-out={result['come_out_roll']:2d} → {outcome_str} "
                  f"(immediate, {result['n_rolls']} roll)")
        else:
            print(f"Game {i+1}: Come-out={result['come_out_roll']:2d}, Point={result['point']:2d} → {outcome_str} "
                  f"({result['n_rolls']} rolls)")
    
    # 2. Theoretical probabilities
    print("\n2. THEORETICAL PROBABILITIES")
    print("-" * 70)
    theory = calculate_theoretical_probabilities()
    print(f"Immediate win (7 or 11):      {theory['immediate_win_prob']:.4f} ({theory['immediate_win_prob']*100:.2f}%)")
    print(f"Immediate loss (2, 3, or 12): {theory['immediate_loss_prob']:.4f} ({theory['immediate_loss_prob']*100:.2f}%)")
    print(f"Win via point:                {theory['point_win_prob']:.4f} ({theory['point_win_prob']*100:.2f}%)")
    print(f"\nTotal win probability:        {theory['total_win_prob']:.4f} ({theory['total_win_prob']*100:.2f}%)")
    print(f"Total loss probability:       {1-theory['total_win_prob']:.4f} ({(1-theory['total_win_prob'])*100:.2f}%)")
    print(f"\n✓ House edge:                  {theory['house_edge_percent']:.2f}%")
    
    # 3. Simulate many games
    print("\n3. SIMULATION RESULTS (100,000 games)")
    print("-" * 70)
    sim = simulate_craps_games(100000)
    print(f"Games played:                 {sim['n_games']:,}")
    print(f"Wins:                         {sim['wins']:,} ({sim['win_rate']*100:.2f}%)")
    print(f"Losses:                       {sim['losses']:,} ({(1-sim['win_rate'])*100:.2f}%)")
    print(f"Average rolls per game:       {sim['avg_rolls_per_game']:.2f}")
    print(f"\n✓ Empirical house edge:        {sim['house_edge']*100:.2f}%")
    print(f"✓ Theoretical house edge:      {theory['house_edge_percent']:.2f}%")
    print(f"✓ Difference:                  {abs(sim['house_edge']*100 - theory['house_edge_percent']):.3f}%")
    
    # 4. Convergence demonstration
    print("\n4. CONVERGENCE TO THEORETICAL VALUE")
    print("-" * 70)
    print(f"{'Games':>15} {'Win Rate':>12} {'Theory':>12} {'Error':>12} {'% Error':>12}")
    print("-" * 70)
    
    convergence = demonstrate_convergence([100, 1000, 10000, 100000, 1000000])
    for result in convergence:
        print(f"{result['n_games']:>15,} {result['win_rate']:>12.6f} "
              f"{result['theoretical']:>12.6f} {result['error']:>12.6f} "
              f"{result['percent_error']:>11.3f}%")
    
    print("\n✓ Error decreases as sample size increases")
    print("✓ Law of Large Numbers in action!")
    
    # 5. Come-out analysis
    print("\n5. COME-OUT ROLL ANALYSIS (10,000 games)")
    print("-" * 70)
    come_out = analyze_come_out_outcomes(10000)
    print(f"Immediate wins (7, 11):       {come_out['immediate_wins']:>5,} ({come_out['immediate_win_rate']*100:.2f}%)")
    print(f"Immediate losses (2, 3, 12):  {come_out['immediate_losses']:>5,} ({come_out['immediate_loss_rate']*100:.2f}%)")
    print(f"Point established:            {come_out['point_established']:>5,} ({come_out['point_rate']*100:.2f}%)")
    
    print("\nPoint distribution:")
    for point in sorted(come_out['point_distribution'].keys()):
        count = come_out['point_distribution'][point]
        print(f"  Point {point:2d}: {count:>5,} times")
    
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print(f"✓ Craps win probability: ~{theory['total_win_prob']*100:.2f}%")
    print(f"✓ House edge: ~{theory['house_edge_percent']:.2f}% (one of the best casino bets)")
    print("✓ Most games decided on come-out or within a few rolls")
    print("✓ Simulation closely matches theoretical probabilities")
    print("✓ Monte Carlo methods can estimate complex probabilities")
    print("="*70)


if __name__ == "__main__":
    main()
