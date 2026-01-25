"""
Tests for coding interview questions
"""

import pytest
from examples.coding_problems.interview_questions import (
    two_sum, reverse_integer, is_palindrome,
    longest_substring_without_repeating, three_sum,
    max_subarray_sum, coin_change, trap_rain_water
)


class TestInterviewQuestions:
    """Test suite for interview coding questions"""
    
    def test_two_sum(self):
        """Test two sum solution"""
        assert two_sum([2, 7, 11, 15], 9) == [0, 1]
        assert two_sum([3, 2, 4], 6) == [1, 2]
        assert two_sum([3, 3], 6) == [0, 1]
    
    def test_reverse_integer(self):
        """Test reverse integer solution"""
        assert reverse_integer(123) == 321
        assert reverse_integer(-123) == -321
        assert reverse_integer(120) == 21
        assert reverse_integer(0) == 0
    
    def test_is_palindrome(self):
        """Test palindrome checker"""
        assert is_palindrome("A man, a plan, a canal: Panama") == True
        assert is_palindrome("race a car") == False
        assert is_palindrome("") == True
    
    def test_longest_substring(self):
        """Test longest substring without repeating characters"""
        assert longest_substring_without_repeating("abcabcbb") == 3
        assert longest_substring_without_repeating("bbbbb") == 1
        assert longest_substring_without_repeating("pwwkew") == 3
        assert longest_substring_without_repeating("") == 0
    
    def test_three_sum(self):
        """Test three sum solution"""
        result = three_sum([-1, 0, 1, 2, -1, -4])
        expected = [[-1, -1, 2], [-1, 0, 1]]
        assert sorted(result) == sorted(expected)
        
        assert three_sum([]) == []
        assert three_sum([0]) == []
    
    def test_max_subarray_sum(self):
        """Test maximum subarray sum (Kadane's algorithm)"""
        assert max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
        assert max_subarray_sum([1]) == 1
        assert max_subarray_sum([5, 4, -1, 7, 8]) == 23
    
    def test_coin_change(self):
        """Test coin change solution"""
        assert coin_change([1, 2, 5], 11) == 3
        assert coin_change([2], 3) == -1
        assert coin_change([1], 0) == 0
    
    def test_trap_rain_water(self):
        """Test trap rain water solution"""
        assert trap_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
        assert trap_rain_water([4, 2, 0, 3, 2, 5]) == 9
        assert trap_rain_water([]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
