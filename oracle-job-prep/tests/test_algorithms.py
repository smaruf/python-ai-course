"""
Tests for sorting algorithms
"""

import pytest
from src.algorithms.sorting import (
    quick_sort, merge_sort, heap_sort, 
    counting_sort, radix_sort
)


class TestSortingAlgorithms:
    """Test suite for sorting algorithms"""
    
    @pytest.fixture
    def sample_array(self):
        """Sample unsorted array"""
        return [64, 34, 25, 12, 22, 11, 90]
    
    @pytest.fixture
    def sorted_array(self):
        """Expected sorted array"""
        return [11, 12, 22, 25, 34, 64, 90]
    
    @pytest.fixture
    def empty_array(self):
        """Empty array"""
        return []
    
    @pytest.fixture
    def single_element(self):
        """Single element array"""
        return [42]
    
    def test_quick_sort(self, sample_array, sorted_array):
        """Test QuickSort algorithm"""
        result = quick_sort(sample_array.copy())
        assert result == sorted_array
    
    def test_merge_sort(self, sample_array, sorted_array):
        """Test MergeSort algorithm"""
        result = merge_sort(sample_array.copy())
        assert result == sorted_array
    
    def test_heap_sort(self, sample_array, sorted_array):
        """Test HeapSort algorithm"""
        result = heap_sort(sample_array.copy())
        assert result == sorted_array
    
    def test_counting_sort(self, sample_array, sorted_array):
        """Test Counting Sort algorithm"""
        result = counting_sort(sample_array.copy())
        assert result == sorted_array
    
    def test_radix_sort(self, sample_array, sorted_array):
        """Test Radix Sort algorithm"""
        result = radix_sort(sample_array.copy())
        assert result == sorted_array
    
    def test_empty_array(self, empty_array):
        """Test sorting empty array"""
        assert quick_sort(empty_array.copy()) == []
        assert merge_sort(empty_array.copy()) == []
    
    def test_single_element(self, single_element):
        """Test sorting single element array"""
        assert quick_sort(single_element.copy()) == [42]
        assert merge_sort(single_element.copy()) == [42]
    
    def test_already_sorted(self):
        """Test sorting already sorted array"""
        arr = [1, 2, 3, 4, 5]
        assert quick_sort(arr.copy()) == arr
        assert merge_sort(arr.copy()) == arr
    
    def test_reverse_sorted(self):
        """Test sorting reverse sorted array"""
        arr = [5, 4, 3, 2, 1]
        expected = [1, 2, 3, 4, 5]
        assert quick_sort(arr.copy()) == expected
        assert merge_sort(arr.copy()) == expected
    
    def test_duplicates(self):
        """Test sorting array with duplicates"""
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        expected = [1, 1, 2, 3, 4, 5, 5, 6, 9]
        assert quick_sort(arr.copy()) == expected
        assert merge_sort(arr.copy()) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
