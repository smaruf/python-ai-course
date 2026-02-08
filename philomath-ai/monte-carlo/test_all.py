#!/usr/bin/env python3
"""
Test script for Monte Carlo simulation modules.
Run this to verify all modules are working correctly.
"""

import sys
import os
import importlib.util
import random


def load_module(filename):
    """Load a module from a file with numeric prefix."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_random_numbers():
    """Test the random numbers module."""
    print("\n" + "="*70)
    print("TEST 1: Random Number Generation")
    print("="*70)
    
    module = load_module('01_random_numbers.py')
    
    # Test reproducibility
    random.seed(42)
    seq1 = module.generate_random_integers(10, 1, 6)
    random.seed(42)
    seq2 = module.generate_random_integers(10, 1, 6)
    
    print(f"✓ Module loaded successfully")
    print(f"✓ First sequence:  {seq1}")
    print(f"✓ Second sequence: {seq2}")
    
    # Verify reproducibility
    assert seq1 == seq2, "Sequences with same seed should be identical"
    print(f"✓ Reproducibility test passed!")
    
    # Test seeding
    seed_results = module.demonstrate_seeding()
    assert seed_results['seed_42_first'] == seed_results['seed_42_second'], \
        "Same seed should produce same sequence"
    assert seed_results['seed_42_first'] != seed_results['seed_123'], \
        "Different seeds should produce different sequences"
    print(f"✓ Seeding test passed!")
    
    # Test distribution
    random.seed(42)
    freq = module.compare_distributions(10000)
    expected = module.calculate_expected_frequency(10000, 6)
    
    # Each outcome should be within 20% of expected
    for outcome, count in freq.items():
        deviation = abs(count - expected) / expected
        assert deviation < 0.20, f"Outcome {outcome} has {deviation:.1%} deviation"
    
    print(f"✓ Distribution test passed!")
    print("✓ All tests passed!")
    return True


def test_dice_simulation():
    """Test the dice simulation module."""
    print("\n" + "="*70)
    print("TEST 2: Dice Simulation")
    print("="*70)
    
    module = load_module('02_dice_simulation.py')
    
    # Test single die
    random.seed(42)
    roll = module.roll_die()
    assert 1 <= roll <= 6, f"Die roll {roll} out of range"
    print(f"✓ Module loaded successfully")
    print(f"✓ Single die roll: {roll}")
    
    # Test multiple dice
    random.seed(42)
    two_dice = module.roll_multiple_dice(2)
    assert 2 <= two_dice <= 12, f"Two dice sum {two_dice} out of range"
    print(f"✓ Two dice roll: {two_dice}")
    
    # Test expected values
    assert module.expected_value_single_die(6) == 3.5, "Expected value wrong"
    assert module.expected_value_multiple_dice(2, 6) == 7.0, "Expected value wrong"
    print(f"✓ Expected value calculations correct")
    
    # Test simulation
    random.seed(42)
    result = module.simulate_dice_rolls(10000, n_dice=1, sides=6)
    assert 3.4 < result['average'] < 3.6, f"Average {result['average']} too far from 3.5"
    print(f"✓ Simulation converges to expected value: {result['average']:.3f} ≈ 3.5")
    
    # Test Law of Large Numbers
    random.seed(42)
    results = module.demonstrate_law_of_large_numbers(10000, [100, 1000, 10000])
    errors = [r['error'] for r in results]
    
    # Errors should generally decrease (may not be strictly monotonic due to randomness)
    print(f"✓ Law of Large Numbers demonstration:")
    for r in results:
        print(f"  {r['n_rolls']:>6,} rolls: error = {r['error']:.4f}")
    
    # Test two dice distribution
    random.seed(42)
    dist = module.analyze_two_dice_distribution(10000)
    
    # 7 should be most common
    assert dist[7]['frequency'] > dist[2]['frequency'], "7 should be more common than 2"
    assert dist[7]['frequency'] > dist[12]['frequency'], "7 should be more common than 12"
    print(f"✓ Two dice distribution correct (7 most common)")
    
    print("✓ All tests passed!")
    return True


def test_craps_simulation():
    """Test the craps simulation module."""
    print("\n" + "="*70)
    print("TEST 3: Craps Simulation")
    print("="*70)
    
    module = load_module('03_craps_simulation.py')
    
    # Test dice rolling
    random.seed(42)
    roll = module.roll_two_dice()
    assert 2 <= roll <= 12, f"Two dice roll {roll} out of range"
    print(f"✓ Module loaded successfully")
    print(f"✓ Two dice roll: {roll}")
    
    # Test single game
    random.seed(42)
    game = module.play_craps_once()
    assert game['outcome'] in ['win', 'lose'], f"Invalid outcome: {game['outcome']}"
    assert len(game['rolls']) >= 1, "Game should have at least one roll"
    print(f"✓ Single game: {game['outcome'].upper()} in {game['n_rolls']} rolls")
    
    # Test simulation
    random.seed(42)
    sim = module.simulate_craps_games(10000)
    assert sim['wins'] + sim['losses'] == 10000, "Wins + losses should equal total games"
    assert 0.45 < sim['win_rate'] < 0.55, f"Win rate {sim['win_rate']} seems wrong"
    print(f"✓ 10,000 games simulated")
    print(f"✓ Win rate: {sim['win_rate']*100:.2f}% (expected ~49.3%)")
    
    # Test theoretical calculations
    theory = module.calculate_theoretical_probabilities()
    assert 0.492 < theory['total_win_prob'] < 0.494, "Theoretical probability wrong"
    assert 0.013 < theory['house_edge'] < 0.015, "House edge wrong"
    print(f"✓ Theoretical win probability: {theory['total_win_prob']*100:.2f}%")
    print(f"✓ Theoretical house edge: {theory['house_edge_percent']:.2f}%")
    
    # Test convergence
    random.seed(42)
    convergence = module.demonstrate_convergence([100, 1000, 10000])
    print(f"✓ Convergence demonstration:")
    for r in convergence:
        print(f"  {r['n_games']:>6,} games: win rate = {r['win_rate']:.4f}, error = {r['error']:.4f}")
    
    # Test come-out analysis
    random.seed(42)
    come_out = module.analyze_come_out_outcomes(1000)
    total = come_out['immediate_wins'] + come_out['immediate_losses'] + come_out['point_established']
    assert total == 1000, "Come-out analysis count mismatch"
    print(f"✓ Come-out analysis correct")
    
    # Compare simulation to theory
    random.seed(42)
    comparison = module.compare_simulation_to_theory(100000)
    sim_win = comparison['simulation']['win_rate']
    theo_win = comparison['theory']['win_rate']
    diff = abs(sim_win - theo_win)
    
    assert diff < 0.01, f"Simulation {sim_win:.4f} too far from theory {theo_win:.4f}"
    print(f"✓ Simulation matches theory within {diff:.4f}")
    
    print("✓ All tests passed!")
    return True


def main():
    """Run all tests."""
    print("="*70)
    print("MONTE CARLO SIMULATION - TEST SUITE")
    print("="*70)
    
    # Track test results
    results = []
    
    try:
        results.append(("Random Numbers", test_random_numbers()))
    except Exception as e:
        print(f"✗ Random Numbers test failed: {e}")
        results.append(("Random Numbers", False))
    
    try:
        results.append(("Dice Simulation", test_dice_simulation()))
    except Exception as e:
        print(f"✗ Dice Simulation test failed: {e}")
        results.append(("Dice Simulation", False))
    
    try:
        results.append(("Craps Simulation", test_craps_simulation()))
    except Exception as e:
        print(f"✗ Craps Simulation test failed: {e}")
        results.append(("Craps Simulation", False))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:20s}: {status}")
    
    print("="*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70)
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
