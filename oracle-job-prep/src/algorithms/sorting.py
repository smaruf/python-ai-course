"""
Advanced Sorting Algorithms for Oracle Interview Preparation

This module contains implementations of advanced sorting algorithms
commonly asked in technical interviews at Oracle and similar companies.
"""

from typing import List, Callable
import time


def quick_sort(arr: List[int]) -> List[int]:
    """
    QuickSort implementation with in-place partitioning.
    
    Time Complexity: O(n log n) average, O(n²) worst case
    Space Complexity: O(log n) due to recursion stack
    
    Args:
        arr: List of integers to sort
        
    Returns:
        Sorted list in ascending order
    """
    if len(arr) <= 1:
        return arr
    
    def partition(low: int, high: int) -> int:
        """Partition array and return pivot index"""
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quick_sort_helper(low: int, high: int):
        """Recursive helper function"""
        if low < high:
            pi = partition(low, high)
            quick_sort_helper(low, pi - 1)
            quick_sort_helper(pi + 1, high)
    
    quick_sort_helper(0, len(arr) - 1)
    return arr


def merge_sort(arr: List[int]) -> List[int]:
    """
    MergeSort implementation with divide and conquer approach.
    
    Time Complexity: O(n log n) in all cases
    Space Complexity: O(n) for temporary arrays
    
    Args:
        arr: List of integers to sort
        
    Returns:
        Sorted list in ascending order
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)


def merge(left: List[int], right: List[int]) -> List[int]:
    """
    Merge two sorted arrays into one sorted array.
    
    Args:
        left: First sorted array
        right: Second sorted array
        
    Returns:
        Merged sorted array
    """
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heap_sort(arr: List[int]) -> List[int]:
    """
    HeapSort implementation using max heap.
    
    Time Complexity: O(n log n) in all cases
    Space Complexity: O(1) - sorts in place
    
    Args:
        arr: List of integers to sort
        
    Returns:
        Sorted list in ascending order
    """
    def heapify(n: int, i: int):
        """Maintain max heap property"""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(n, largest)
    
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)
    
    # Extract elements from heap one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(i, 0)
    
    return arr


def counting_sort(arr: List[int]) -> List[int]:
    """
    Counting Sort - efficient for small range of integers.
    
    Time Complexity: O(n + k) where k is the range of input
    Space Complexity: O(k)
    
    Args:
        arr: List of non-negative integers to sort
        
    Returns:
        Sorted list in ascending order
    """
    if not arr:
        return arr
    
    max_val = max(arr)
    min_val = min(arr)
    range_val = max_val - min_val + 1
    
    # Create count array
    count = [0] * range_val
    output = [0] * len(arr)
    
    # Store count of each element
    for num in arr:
        count[num - min_val] += 1
    
    # Modify count array to store actual positions
    for i in range(1, len(count)):
        count[i] += count[i - 1]
    
    # Build output array
    for i in range(len(arr) - 1, -1, -1):
        num = arr[i]
        output[count[num - min_val] - 1] = num
        count[num - min_val] -= 1
    
    return output


def radix_sort(arr: List[int]) -> List[int]:
    """
    Radix Sort - sorts integers digit by digit.
    
    Time Complexity: O(d * (n + k)) where d is number of digits
    Space Complexity: O(n + k)
    
    Args:
        arr: List of non-negative integers to sort
        
    Returns:
        Sorted list in ascending order
    """
    if not arr:
        return arr
    
    def counting_sort_for_radix(arr: List[int], exp: int) -> List[int]:
        """Helper counting sort for specific digit"""
        n = len(arr)
        output = [0] * n
        count = [0] * 10
        
        # Store count of occurrences
        for i in range(n):
            index = arr[i] // exp
            count[index % 10] += 1
        
        # Change count[i] to actual position
        for i in range(1, 10):
            count[i] += count[i - 1]
        
        # Build output array
        for i in range(n - 1, -1, -1):
            index = arr[i] // exp
            output[count[index % 10] - 1] = arr[i]
            count[index % 10] -= 1
        
        return output
    
    # Find maximum number to know number of digits
    max_val = max(arr)
    
    # Do counting sort for every digit
    exp = 1
    while max_val // exp > 0:
        arr = counting_sort_for_radix(arr, exp)
        exp *= 10
    
    return arr


def benchmark_sorting_algorithms():
    """
    Benchmark different sorting algorithms on various input sizes.
    Useful for understanding practical performance characteristics.
    """
    import random
    
    sizes = [100, 1000, 5000]
    algorithms = {
        'QuickSort': quick_sort,
        'MergeSort': merge_sort,
        'HeapSort': heap_sort,
        'CountingSort': counting_sort,
        'RadixSort': radix_sort
    }
    
    print("Sorting Algorithm Performance Benchmark")
    print("=" * 60)
    
    for size in sizes:
        print(f"\nArray Size: {size}")
        print("-" * 60)
        
        # Generate random array
        test_array = [random.randint(0, 10000) for _ in range(size)]
        
        for name, algorithm in algorithms.items():
            arr_copy = test_array.copy()
            
            start_time = time.time()
            algorithm(arr_copy)
            end_time = time.time()
            
            elapsed = (end_time - start_time) * 1000  # Convert to ms
            print(f"{name:15s}: {elapsed:8.4f} ms")


if __name__ == "__main__":
    # Example usage
    test_array = [64, 34, 25, 12, 22, 11, 90, 88, 45, 50, 23, 36, 18]
    
    print("Original array:", test_array)
    print("\nSorting with different algorithms:\n")
    
    print("QuickSort:", quick_sort(test_array.copy()))
    print("MergeSort:", merge_sort(test_array.copy()))
    print("HeapSort:", heap_sort(test_array.copy()))
    print("CountingSort:", counting_sort(test_array.copy()))
    print("RadixSort:", radix_sort(test_array.copy()))
    
    print("\n" + "=" * 60)
    print("Running Performance Benchmark...")
    print("=" * 60)
    benchmark_sorting_algorithms()
