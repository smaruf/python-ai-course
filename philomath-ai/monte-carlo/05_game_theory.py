"""
Game Theory and Optimal Betting Strategies
===========================================

This module explores game theory concepts and optimal betting strategies
using Monte Carlo simulation and mathematical analysis.

Learning Objectives:
- Understand expected value in gambling
- Calculate optimal bet sizes (Kelly Criterion)
- Analyze different betting strategies
- Simulate bankroll management
- Understand risk of ruin
- Compare betting systems (Martingale, etc.)

Key Concepts:
- Expected Value: Average outcome over many trials
- Kelly Criterion: Optimal fraction of bankroll to bet
- Risk of Ruin: Probability of losing entire bankroll
- Betting Systems: Strategies for managing bets
- House Edge: Casino's mathematical advantage
"""

import random
import math


def calculate_expected_value(outcomes):
    """
    Calculate the expected value of a bet.
    
    Expected value is the average outcome if you repeat
    the bet many times.
    
    EV = Σ(probability × outcome)
    
    Args:
        outcomes: List of tuples (probability, payout)
                 where payout is net gain/loss
    
    Returns:
        Expected value
    
    Example:
        >>> # Fair coin flip: win $1 on heads, lose $1 on tails
        >>> ev = calculate_expected_value([(0.5, 1), (0.5, -1)])
        >>> ev
        0.0
        >>> # Unfair: 49% to win $1, 51% to lose $1
        >>> ev = calculate_expected_value([(0.49, 1), (0.51, -1)])
        >>> -0.02 < ev < 0.0
        True
    """
    return sum(prob * payout for prob, payout in outcomes)


def kelly_criterion(win_prob, win_amount, loss_amount):
    """
    Calculate optimal bet size using Kelly Criterion.
    
    The Kelly Criterion maximizes long-term growth rate.
    
    For a simple bet:
    f* = (p × b - q) / b
    
    where:
    - f* is the fraction of bankroll to bet
    - p is probability of winning
    - q is probability of losing (1 - p)
    - b is the ratio of win to loss (win_amount / loss_amount)
    
    Args:
        win_prob: Probability of winning (0 to 1)
        win_amount: Amount won on a winning bet (per unit wagered)
        loss_amount: Amount lost on a losing bet (per unit wagered)
    
    Returns:
        Optimal fraction of bankroll to bet (0 to 1)
        Returns 0 if bet has negative expected value
    
    Example:
        >>> # 60% to win $1, 40% to lose $1
        >>> kelly_criterion(0.6, 1, 1)
        0.2
        >>> # Unfavorable bet
        >>> kelly_criterion(0.4, 1, 1)
        0.0
    """
    q = 1 - win_prob
    b = win_amount / loss_amount
    
    kelly_fraction = (win_prob * b - q) / b
    
    # Don't bet if expected value is negative
    return max(0, kelly_fraction)


def simulate_flat_betting(initial_bankroll, bet_size, n_games, win_prob):
    """
    Simulate flat betting strategy (same bet every time).
    
    Args:
        initial_bankroll: Starting money
        bet_size: Fixed bet amount
        n_games: Number of games to play
        win_prob: Probability of winning each game
    
    Returns:
        Dictionary with simulation results
    """
    bankroll = initial_bankroll
    history = [bankroll]
    wins = 0
    losses = 0
    
    for _ in range(n_games):
        if bankroll < bet_size:
            break  # Bankrupt
        
        if random.random() < win_prob:
            bankroll += bet_size
            wins += 1
        else:
            bankroll -= bet_size
            losses += 1
        
        history.append(bankroll)
    
    return {
        'strategy': 'Flat Betting',
        'initial_bankroll': initial_bankroll,
        'final_bankroll': bankroll,
        'profit': bankroll - initial_bankroll,
        'games_played': len(history) - 1,
        'wins': wins,
        'losses': losses,
        'bankrupted': bankroll <= 0,
        'history': history
    }


def simulate_kelly_betting(initial_bankroll, win_prob, win_amount, loss_amount, 
                          n_games, kelly_fraction=1.0):
    """
    Simulate Kelly Criterion betting strategy.
    
    Args:
        initial_bankroll: Starting money
        win_prob: Probability of winning
        win_amount: Amount won per unit bet
        loss_amount: Amount lost per unit bet
        n_games: Number of games to play
        kelly_fraction: Fraction of Kelly bet to use (1.0 = full Kelly)
    
    Returns:
        Dictionary with simulation results
    """
    optimal_fraction = kelly_criterion(win_prob, win_amount, loss_amount)
    bet_fraction = optimal_fraction * kelly_fraction
    
    bankroll = initial_bankroll
    history = [bankroll]
    wins = 0
    losses = 0
    
    for _ in range(n_games):
        if bankroll <= 0:
            break
        
        bet_size = bankroll * bet_fraction
        
        if random.random() < win_prob:
            bankroll += bet_size * win_amount
            wins += 1
        else:
            bankroll -= bet_size * loss_amount
            losses += 1
        
        history.append(bankroll)
    
    return {
        'strategy': f'Kelly ({kelly_fraction*100:.0f}%)',
        'initial_bankroll': initial_bankroll,
        'final_bankroll': bankroll,
        'profit': bankroll - initial_bankroll,
        'games_played': len(history) - 1,
        'wins': wins,
        'losses': losses,
        'bankrupted': bankroll <= 0,
        'optimal_fraction': optimal_fraction,
        'bet_fraction_used': bet_fraction,
        'history': history
    }


def simulate_martingale(initial_bankroll, base_bet, n_games, win_prob):
    """
    Simulate Martingale betting system (double bet after each loss).
    
    WARNING: This system can lead to catastrophic losses!
    
    Args:
        initial_bankroll: Starting money
        base_bet: Initial bet size
        n_games: Number of games to play
        win_prob: Probability of winning each game
    
    Returns:
        Dictionary with simulation results
    """
    bankroll = initial_bankroll
    history = [bankroll]
    current_bet = base_bet
    wins = 0
    losses = 0
    
    for _ in range(n_games):
        if bankroll < current_bet:
            break  # Can't afford next bet
        
        if random.random() < win_prob:
            bankroll += current_bet
            wins += 1
            current_bet = base_bet  # Reset to base bet
        else:
            bankroll -= current_bet
            losses += 1
            current_bet *= 2  # Double the bet
        
        history.append(bankroll)
    
    return {
        'strategy': 'Martingale',
        'initial_bankroll': initial_bankroll,
        'final_bankroll': bankroll,
        'profit': bankroll - initial_bankroll,
        'games_played': len(history) - 1,
        'wins': wins,
        'losses': losses,
        'bankrupted': bankroll <= 0,
        'history': history
    }


def calculate_risk_of_ruin(initial_bankroll, bet_size, win_prob, target_bankroll=None):
    """
    Calculate theoretical risk of ruin.
    
    Risk of ruin is the probability of losing your entire bankroll
    before reaching a target amount.
    
    For equal bets with win probability p:
    If p = 0.5: RoR = 1 - (initial / target)
    If p ≠ 0.5: RoR = ((q/p)^initial - (q/p)^target) / (1 - (q/p)^target)
    
    where q = 1 - p
    
    Args:
        initial_bankroll: Starting bankroll
        bet_size: Size of each bet
        win_prob: Probability of winning
        target_bankroll: Target bankroll (None = infinity)
    
    Returns:
        Probability of ruin (0 to 1)
    """
    if target_bankroll is None:
        # Infinite target
        if win_prob <= 0.5:
            return 1.0  # Certain ruin with unfavorable odds
        else:
            q = 1 - win_prob
            ratio = q / win_prob
            initial_units = initial_bankroll / bet_size
            return ratio ** initial_units
    else:
        initial_units = initial_bankroll / bet_size
        target_units = target_bankroll / bet_size
        
        if win_prob == 0.5:
            return 1 - (initial_units / target_units)
        else:
            q = 1 - win_prob
            ratio = q / win_prob
            
            numerator = ratio ** initial_units - ratio ** target_units
            denominator = 1 - ratio ** target_units
            
            return numerator / denominator


def compare_betting_strategies(initial_bankroll, n_games, win_prob, n_simulations=1000):
    """
    Compare different betting strategies over multiple simulations.
    
    Args:
        initial_bankroll: Starting bankroll
        n_games: Number of games per simulation
        win_prob: Probability of winning
        n_simulations: Number of simulations to run
    
    Returns:
        Dictionary comparing strategies
    """
    strategies = []
    
    # Flat betting (5% of bankroll)
    flat_results = []
    for _ in range(n_simulations):
        result = simulate_flat_betting(initial_bankroll, initial_bankroll * 0.05, 
                                      n_games, win_prob)
        flat_results.append(result['final_bankroll'])
    
    strategies.append({
        'name': 'Flat Betting (5%)',
        'final_bankrolls': flat_results,
        'avg_final': sum(flat_results) / len(flat_results),
        'bankruptcy_rate': sum(1 for x in flat_results if x <= 0) / len(flat_results),
        'median': sorted(flat_results)[len(flat_results) // 2]
    })
    
    # Kelly betting (assuming 55% win rate, even money)
    if win_prob > 0.5:
        kelly_results = []
        for _ in range(n_simulations):
            result = simulate_kelly_betting(initial_bankroll, win_prob, 1, 1, n_games)
            kelly_results.append(result['final_bankroll'])
        
        strategies.append({
            'name': 'Full Kelly',
            'final_bankrolls': kelly_results,
            'avg_final': sum(kelly_results) / len(kelly_results),
            'bankruptcy_rate': sum(1 for x in kelly_results if x <= 0) / len(kelly_results),
            'median': sorted(kelly_results)[len(kelly_results) // 2]
        })
        
        # Half Kelly (more conservative)
        half_kelly_results = []
        for _ in range(n_simulations):
            result = simulate_kelly_betting(initial_bankroll, win_prob, 1, 1, 
                                           n_games, kelly_fraction=0.5)
            half_kelly_results.append(result['final_bankroll'])
        
        strategies.append({
            'name': 'Half Kelly',
            'final_bankrolls': half_kelly_results,
            'avg_final': sum(half_kelly_results) / len(half_kelly_results),
            'bankruptcy_rate': sum(1 for x in half_kelly_results if x <= 0) / len(half_kelly_results),
            'median': sorted(half_kelly_results)[len(half_kelly_results) // 2]
        })
    
    # Martingale (DANGEROUS!)
    martingale_results = []
    for _ in range(n_simulations):
        result = simulate_martingale(initial_bankroll, initial_bankroll * 0.01, 
                                     n_games, win_prob)
        martingale_results.append(result['final_bankroll'])
    
    strategies.append({
        'name': 'Martingale (1% base)',
        'final_bankrolls': martingale_results,
        'avg_final': sum(martingale_results) / len(martingale_results),
        'bankruptcy_rate': sum(1 for x in martingale_results if x <= 0) / len(martingale_results),
        'median': sorted(martingale_results)[len(martingale_results) // 2]
    })
    
    return strategies


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("="*70)
    print("GAME THEORY AND OPTIMAL BETTING STRATEGIES")
    print("="*70)
    
    random.seed(42)
    
    # 1. Expected Value
    print("\n1. EXPECTED VALUE CALCULATIONS")
    print("-" * 70)
    
    # Craps
    craps_ev = calculate_expected_value([(0.4929, 1), (0.5071, -1)])
    print(f"Craps (pass line bet):")
    print(f"  Win: 49.29% chance to win $1")
    print(f"  Lose: 50.71% chance to lose $1")
    print(f"  Expected Value: ${craps_ev:.4f} per $1 bet")
    print(f"  House Edge: {-craps_ev * 100:.2f}%")
    
    # Favorable bet
    favorable_ev = calculate_expected_value([(0.55, 1), (0.45, -1)])
    print(f"\nFavorable bet (55% win rate):")
    print(f"  Expected Value: ${favorable_ev:.4f} per $1 bet")
    print(f"  Player Edge: {favorable_ev * 100:.2f}%")
    
    # 2. Kelly Criterion
    print("\n2. KELLY CRITERION")
    print("-" * 70)
    
    kelly_55 = kelly_criterion(0.55, 1, 1)
    print(f"Optimal bet size for 55% win rate (even money):")
    print(f"  Kelly fraction: {kelly_55:.2%} of bankroll")
    print(f"  With $1000 bankroll: ${1000 * kelly_55:.2f}")
    
    kelly_60 = kelly_criterion(0.60, 1, 1)
    print(f"\nOptimal bet size for 60% win rate (even money):")
    print(f"  Kelly fraction: {kelly_60:.2%} of bankroll")
    print(f"  With $1000 bankroll: ${1000 * kelly_60:.2f}")
    
    kelly_craps = kelly_criterion(0.4929, 1, 1)
    print(f"\nOptimal bet size for Craps (49.29% win rate):")
    print(f"  Kelly fraction: {kelly_craps:.2%} of bankroll")
    print(f"  ✓ Don't bet with negative expectation!")
    
    # 3. Strategy Comparison
    print("\n3. BETTING STRATEGY COMPARISON")
    print("-" * 70)
    print("Comparing strategies with $1000 bankroll, 55% win rate, 100 games:")
    print("Running 1000 simulations per strategy...")
    
    strategies = compare_betting_strategies(1000, 100, 0.55, 1000)
    
    print(f"\n{'Strategy':<25} {'Avg Final':<15} {'Median':<15} {'Bankruptcy %':<15}")
    print("-" * 70)
    for s in strategies:
        print(f"{s['name']:<25} ${s['avg_final']:<14.2f} ${s['median']:<14.2f} {s['bankruptcy_rate']*100:<14.1f}%")
    
    # 4. Individual Strategy Examples
    print("\n4. INDIVIDUAL STRATEGY EXAMPLES")
    print("-" * 70)
    
    # Flat betting
    print("\nFlat Betting ($50 per game):")
    flat = simulate_flat_betting(1000, 50, 100, 0.55)
    print(f"  Games played: {flat['games_played']}")
    print(f"  Wins: {flat['wins']}, Losses: {flat['losses']}")
    print(f"  Final bankroll: ${flat['final_bankroll']:.2f}")
    print(f"  Profit: ${flat['profit']:.2f}")
    
    # Kelly betting
    print("\nKelly Criterion (100% Kelly):")
    kelly = simulate_kelly_betting(1000, 0.55, 1, 1, 100)
    print(f"  Optimal fraction: {kelly['optimal_fraction']:.2%}")
    print(f"  Games played: {kelly['games_played']}")
    print(f"  Wins: {kelly['wins']}, Losses: {kelly['losses']}")
    print(f"  Final bankroll: ${kelly['final_bankroll']:.2f}")
    print(f"  Profit: ${kelly['profit']:.2f}")
    
    # Martingale
    print("\nMartingale (starting with $10 bet):")
    martingale = simulate_martingale(1000, 10, 100, 0.55)
    print(f"  Games played: {martingale['games_played']}")
    print(f"  Wins: {martingale['wins']}, Losses: {martingale['losses']}")
    print(f"  Final bankroll: ${martingale['final_bankroll']:.2f}")
    print(f"  Profit: ${martingale['profit']:.2f}")
    if martingale['bankrupted']:
        print(f"  ⚠ BANKRUPTED!")
    
    # 5. Risk of Ruin
    print("\n5. RISK OF RUIN ANALYSIS")
    print("-" * 70)
    
    ror_50 = calculate_risk_of_ruin(1000, 50, 0.50)
    print(f"Fair coin flip (50% win rate):")
    print(f"  Bankroll: $1000, Bet: $50")
    print(f"  Risk of ruin: {ror_50*100:.1f}%")
    
    ror_49 = calculate_risk_of_ruin(1000, 50, 0.49)
    print(f"\nUnfavorable game (49% win rate):")
    print(f"  Bankroll: $1000, Bet: $50")
    print(f"  Risk of ruin: {ror_49*100:.1f}%")
    
    ror_55 = calculate_risk_of_ruin(1000, 50, 0.55)
    print(f"\nFavorable game (55% win rate):")
    print(f"  Bankroll: $1000, Bet: $50")
    print(f"  Risk of ruin: {ror_55*100:.1f}%")
    
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("✓ Never bet when expected value is negative (house edge)")
    print("✓ Kelly Criterion maximizes long-term growth")
    print("✓ Half-Kelly is more conservative but still effective")
    print("✓ Martingale is EXTREMELY risky despite seeming safe")
    print("✓ Smaller bets = lower risk of ruin")
    print("✓ Even small edges compound over time with proper betting")
    print("="*70)


if __name__ == "__main__":
    main()
