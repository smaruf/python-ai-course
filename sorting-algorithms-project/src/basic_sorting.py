def bubble_sort(arr):
    """Sort a list in-place using the bubble sort algorithm.

    Repeatedly steps through the list, compares adjacent elements and swaps
    them if they are in the wrong order. The pass is repeated until no swaps
    are needed, indicating the list is sorted.

    Time complexity: O(n^2). Space complexity: O(1).

    Args:
        arr (list): The list to sort. Modified in-place.

    Example:
        >>> data = [64, 34, 25, 12]
        >>> bubble_sort(data)
        >>> data
        [12, 25, 34, 64]
    """
    n = len(arr)
    for i in range(n-1):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

def selection_sort(arr):
    """Sort a list in-place using the selection sort algorithm.

    Divides the list into a sorted and an unsorted portion. Repeatedly finds
    the minimum element from the unsorted portion and moves it to the end of
    the sorted portion.

    Time complexity: O(n^2). Space complexity: O(1).

    Args:
        arr (list): The list to sort. Modified in-place.

    Example:
        >>> data = [64, 25, 12, 22, 11]
        >>> selection_sort(data)
        >>> data
        [11, 12, 22, 25, 64]
    """
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[min_idx] > arr[j]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]

def insertion_sort(arr):
    """Sort a list in-place using the insertion sort algorithm.

    Builds the sorted list one element at a time by inserting each new element
    into its correct position among the already-sorted elements.

    Time complexity: O(n^2). Space complexity: O(1).

    Args:
        arr (list): The list to sort. Modified in-place.

    Example:
        >>> data = [29, 10, 14, 37, 13]
        >>> insertion_sort(data)
        >>> data
        [10, 13, 14, 29, 37]
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

def merge_sort(arr):
    """Sort a list in-place using the merge sort algorithm.

    Uses a divide-and-conquer strategy: splits the list in half, recursively
    sorts each half, then merges the two sorted halves back together.

    Time complexity: O(n log n). Space complexity: O(n).

    Args:
        arr (list): The list to sort. Modified in-place.

    Example:
        >>> data = [38, 27, 43, 3, 9, 82, 10]
        >>> merge_sort(data)
        >>> data
        [3, 9, 10, 27, 38, 43, 82]
    """
    if len(arr) > 1:
        mid = len(arr)//2
        L = arr[:mid]
        R = arr[mid:]
        merge_sort(L)
        merge_sort(R)
        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1

def quick_sort(arr):
    """Sort a list and return the sorted result using the quick sort algorithm.

    Uses a divide-and-conquer strategy: picks the last element as a pivot,
    partitions the remaining elements into those less than or equal to the
    pivot and those greater, then recursively sorts each partition.

    Note: Unlike the other sort functions in this module, this function does
    NOT sort in-place — it returns a new sorted list and consumes the input
    via ``list.pop()``.

    Time complexity: O(n log n) average, O(n^2) worst case.
    Space complexity: O(n) due to recursion and new lists.

    Args:
        arr (list): The list to sort.

    Returns:
        list: A new sorted list containing all elements of ``arr``.

    Example:
        >>> quick_sort([99, 97, 98, 95, 94, 96])
        [94, 95, 96, 97, 98, 99]
    """
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr.pop()
        greater, lesser = [], []
        for element in arr:
            if element > pivot:
                greater.append(element)
            else:
                lesser.append(element)
        return quick_sort(lesser) + [pivot] + quick_sort(greater)

import unittest

class TestSortingAlgorithms(unittest.TestCase):
    def test_bubble_sort_success(self):
        # Given: An unsorted array
        data = [64, 34, 25, 12, 22, 11, 90]
        # When: Bubble Sort is applied
        bubble_sort(data)
        # Then: The array is sorted
        self.assertEqual(data, [11, 12, 22, 25, 34, 64, 90])

    def test_selection_sort_success(self):
        # Given
        data = [64, 25, 12, 22, 11]
        # When
        selection_sort(data)
        # Then
        self.assertEqual(data, [11, 12, 22, 25, 64])

    def test_insertion_sort_success(self):
        # Given
        data = [29, 10, 14, 37, 13]
        # When
        insertion_sort(data)
        # Then
        self.assertEqual(data, [10, 13, 14, 29, 37])

    def test_merge_sort_success(self):
        # Given
        data = [38, 27, 43, 3, 9, 82, 10]
        # When
        merge_sort(data)
        # Then
        self.assertEqual(data, [3, 9, 10, 27, 38, 43, 82])

    def test_quick_sort_success(self):
        # Given
        data = [99, 97, 98, 95, 94, 96]
        # When
        sorted_data = quick_sort(data)
        # Then
        self.assertEqual(sorted_data, [94, 95, 96, 97, 98, 99])

if __name__ == '__main__':
    unittest.main()
