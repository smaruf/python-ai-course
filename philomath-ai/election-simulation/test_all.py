"""
Test Suite for Election Simulation Module
==========================================

Comprehensive tests for all election simulation functions.
Run with: python test_all.py
"""

import sys
import os
import random
import tempfile
import unittest

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import modules to test
import importlib.util


def load_module(filename):
    """Load a module from file."""
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load our modules
parsing = load_module('01_parsing_data.py')
single = load_module('02_single_election.py')
multiple = load_module('03_multiple_elections.py')
ec = load_module('04_electoral_college.py')


class TestParsingData(unittest.TestCase):
    """Tests for 01_parsing_data.py"""
    
    def test_parse_valid_file(self):
        """Test parsing a valid CSV file."""
        data = "State,CandidateA,CandidateB,ElectoralVotes\nPA,51.0,49.0,19\n"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(data)
            temp_file = f.name
        
        try:
            polls = parsing.parse_polling_file(temp_file)
            self.assertIn('PA', polls)
            self.assertEqual(polls['PA']['candidate_a'], 51.0)
            self.assertEqual(polls['PA']['candidate_b'], 49.0)
            self.assertEqual(polls['PA']['electoral_votes'], 19)
        finally:
            os.unlink(temp_file)
    
    def test_parse_nonexistent_file(self):
        """Test that parsing nonexistent file raises error."""
        with self.assertRaises(FileNotFoundError):
            parsing.parse_polling_file('nonexistent_file.csv')
    
    def test_validate_state_data(self):
        """Test state data validation."""
        valid_data = {
            'candidate_a': 48.5,
            'candidate_b': 47.2,
            'electoral_votes': 19
        }
        self.assertTrue(parsing.validate_state_data(valid_data))
        
        invalid_data = {'candidate_a': 48.5}
        self.assertFalse(parsing.validate_state_data(invalid_data))
        
        invalid_percentage = {
            'candidate_a': 150.0,  # Invalid percentage
            'candidate_b': 47.2,
            'electoral_votes': 19
        }
        self.assertFalse(parsing.validate_state_data(invalid_percentage))
    
    def test_get_state_poll(self):
        """Test retrieving specific state data."""
        polls = {
            'PA': {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 19}
        }
        
        result = parsing.get_state_poll(polls, 'PA')
        self.assertIsNotNone(result)
        self.assertEqual(result['candidate_a'], 51.0)
        
        result = parsing.get_state_poll(polls, 'NonExistent')
        self.assertIsNone(result)
    
    def test_summarize_polls(self):
        """Test poll summary generation."""
        polls = {
            'State1': {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10},
            'State2': {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 15},
        }
        
        summary = parsing.summarize_polls(polls)
        self.assertEqual(summary['total_states'], 2)
        self.assertEqual(summary['total_electoral_votes'], 25)
        self.assertEqual(summary['candidate_a_leading'], 1)
        self.assertEqual(summary['candidate_b_leading'], 1)


class TestSingleElection(unittest.TestCase):
    """Tests for 02_single_election.py"""
    
    def test_simulate_state(self):
        """Test simulating a single state."""
        poll_a_wins = {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10}
        self.assertEqual(single.simulate_state(poll_a_wins), 'A')
        
        poll_b_wins = {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 10}
        self.assertEqual(single.simulate_state(poll_b_wins), 'B')
        
        poll_tie = {'candidate_a': 50.0, 'candidate_b': 50.0, 'electoral_votes': 10}
        self.assertEqual(single.simulate_state(poll_tie), 'TIE')
    
    def test_simulate_election(self):
        """Test simulating a complete election."""
        polls = {
            'State1': {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10},
            'State2': {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 15},
            'State3': {'candidate_a': 55.0, 'candidate_b': 45.0, 'electoral_votes': 8},
        }
        
        results = single.simulate_election(polls)
        
        self.assertIn('state_results', results)
        self.assertIn('candidate_a_electoral_votes', results)
        self.assertIn('candidate_b_electoral_votes', results)
        self.assertIn('winner', results)
        
        self.assertEqual(results['candidate_a_electoral_votes'], 18)
        self.assertEqual(results['candidate_b_electoral_votes'], 15)
        self.assertEqual(results['winner'], 'A')
    
    def test_calculate_electoral_votes(self):
        """Test electoral vote calculation."""
        state_results = {'State1': 'A', 'State2': 'B', 'State3': 'A'}
        state_polls = {
            'State1': {'electoral_votes': 10},
            'State2': {'electoral_votes': 15},
            'State3': {'electoral_votes': 8},
        }
        
        a_total, b_total = single.calculate_electoral_votes(state_results, state_polls)
        self.assertEqual(a_total, 18)
        self.assertEqual(b_total, 15)
    
    def test_get_close_states(self):
        """Test identifying close states."""
        polls = {
            'State1': {'candidate_a': 51.0, 'candidate_b': 49.0, 'electoral_votes': 10},
            'State2': {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 15},
            'State3': {'candidate_a': 60.0, 'candidate_b': 40.0, 'electoral_votes': 8},
        }
        
        close = single.get_close_states(polls, margin_threshold=5.0)
        self.assertEqual(len(close), 2)  # State1 and State2 are within 5%
        
        close = single.get_close_states(polls, margin_threshold=1.0)
        self.assertEqual(len(close), 0)  # No states within 1%


class TestMultipleElections(unittest.TestCase):
    """Tests for 03_multiple_elections.py"""
    
    def test_add_polling_noise(self):
        """Test adding noise to polling data."""
        random.seed(42)
        
        # Run multiple times to test distribution
        results = [multiple.add_polling_noise(50.0, margin_of_error=3.0) for _ in range(100)]
        
        # All results should be valid percentages
        for result in results:
            self.assertGreaterEqual(result, 0.0)
            self.assertLessEqual(result, 100.0)
        
        # Results should vary (not all the same)
        self.assertGreater(len(set(results)), 50)
    
    def test_simulate_single_election_with_noise(self):
        """Test simulating one election with noise."""
        random.seed(42)
        
        polls = {
            'State1': {'candidate_a': 55.0, 'candidate_b': 45.0, 'electoral_votes': 10},
        }
        
        result = multiple.simulate_single_election_with_noise(polls, margin_of_error=3.0)
        
        self.assertIn('state_results', result)
        self.assertIn('winner', result)
        self.assertIn('candidate_a_electoral_votes', result)
    
    def test_simulate_multiple_elections(self):
        """Test running multiple simulations."""
        random.seed(42)
        
        polls = {
            'State1': {'candidate_a': 52.0, 'candidate_b': 48.0, 'electoral_votes': 10},
        }
        
        results = multiple.simulate_multiple_elections(polls, num_simulations=100, margin_of_error=3.0)
        
        self.assertEqual(results['num_simulations'], 100)
        self.assertIn('candidate_a_wins', results)
        self.assertIn('candidate_b_wins', results)
        
        # With A at 52% and margin of error, A should win most simulations
        self.assertGreater(results['candidate_a_wins'], 50)
    
    def test_analyze_results(self):
        """Test results analysis."""
        results = {
            'num_simulations': 100,
            'candidate_a_wins': 60,
            'candidate_b_wins': 40,
            'ties': 0,
            'candidate_a_win_probability': 0.6,
            'candidate_b_win_probability': 0.4,
        }
        
        analysis = multiple.analyze_results(results)
        
        self.assertEqual(analysis['favorite'], 'A')
        self.assertEqual(analysis['favorite_win_pct'], 60.0)
        self.assertEqual(analysis['underdog_win_pct'], 40.0)


class TestElectoralCollege(unittest.TestCase):
    """Tests for 04_electoral_college.py"""
    
    def test_simulate_electoral_college(self):
        """Test complete Electoral College simulation."""
        polls = {
            'State1': {'candidate_a': 52.0, 'candidate_b': 48.0, 'electoral_votes': 10},
            'State2': {'candidate_a': 48.0, 'candidate_b': 52.0, 'electoral_votes': 15},
        }
        
        results = ec.simulate_electoral_college(polls, num_simulations=100, seed=42)
        
        self.assertEqual(results['num_simulations'], 100)
        self.assertIn('candidate_a_win_probability', results)
        self.assertIn('state_win_counts', results)
        self.assertIn('ev_distribution', results)
        
        # Verify total wins add up
        total_wins = results['candidate_a_wins'] + results['candidate_b_wins'] + results['ties']
        self.assertEqual(total_wins, 100)
    
    def test_generate_report(self):
        """Test report generation."""
        polls = {
            'State1': {'candidate_a': 52.0, 'candidate_b': 48.0, 'electoral_votes': 10},
        }
        
        results = ec.simulate_electoral_college(polls, num_simulations=100, seed=42)
        report = ec.generate_report(results)
        
        self.assertIsInstance(report, str)
        self.assertIn('ELECTORAL COLLEGE', report)
        self.assertIn('State1', report)
        self.assertIn('MODEL LIMITATIONS', report)


def run_tests():
    """Run all tests and display results."""
    print("=" * 70)
    print("Election Simulation Test Suite")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestParsingData))
    suite.addTests(loader.loadTestsFromTestCase(TestSingleElection))
    suite.addTests(loader.loadTestsFromTestCase(TestMultipleElections))
    suite.addTests(loader.loadTestsFromTestCase(TestElectoralCollege))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed.")
        if result.failures:
            print(f"  Failures: {len(result.failures)}")
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
