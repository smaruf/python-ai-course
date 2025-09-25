"""
Unit tests for sorting algorithms.
Tests are extracted from the original all_basic_sort_algoritm_with_test.py file.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import basic_sorting, radix_sort


def test_bubble_sort():
    """Test bubble sort algorithm."""
    test_arr = [64, 34, 25, 12, 22, 11, 90]
    expected = [11, 12, 22, 25, 34, 64, 90]
    basic_sorting.bubble_sort(test_arr)
    assert test_arr == expected


def test_selection_sort():
    """Test selection sort algorithm."""
    test_arr = [64, 25, 12, 22, 11]
    expected = [11, 12, 22, 25, 64]
    basic_sorting.selection_sort(test_arr)
    assert test_arr == expected


def test_insertion_sort():
    """Test insertion sort algorithm."""
    test_arr = [12, 11, 13, 5, 6]
    expected = [5, 6, 11, 12, 13]
    basic_sorting.insertion_sort(test_arr)
    assert test_arr == expected


def test_merge_sort():
    """Test merge sort algorithm."""
    test_arr = [12, 11, 13, 5, 6, 7]
    expected = [5, 6, 7, 11, 12, 13]
    basic_sorting.merge_sort(test_arr)
    assert test_arr == expected


def test_quick_sort():
    """Test quick sort algorithm."""
    test_arr = [10, 7, 8, 9, 1, 5]
    expected = [1, 5, 7, 8, 9, 10]
    basic_sorting.quick_sort(test_arr, 0, len(test_arr) - 1)
    assert test_arr == expected


def test_radix_sort():
    """Test radix sort algorithm."""
    test_arr = [170, 45, 75, 90, 2, 802, 24, 66]
    expected = [2, 24, 45, 66, 75, 90, 170, 802]
    result = radix_sort.radix_sort(test_arr)
    assert result == expected


def test_empty_arrays():
    """Test all algorithms with empty arrays."""
    empty_arr = []
    
    # Test bubble sort
    test_arr = empty_arr.copy()
    basic_sorting.bubble_sort(test_arr)
    assert test_arr == []
    
    # Test selection sort
    test_arr = empty_arr.copy()
    basic_sorting.selection_sort(test_arr)
    assert test_arr == []


def test_single_element():
    """Test all algorithms with single element arrays."""
    single_arr = [42]
    expected = [42]
    
    # Test bubble sort
    test_arr = single_arr.copy()
    basic_sorting.bubble_sort(test_arr)
    assert test_arr == expected
    
    # Test selection sort
    test_arr = single_arr.copy()
    basic_sorting.selection_sort(test_arr)
    assert test_arr == expected


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])