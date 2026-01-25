"""
Common Interview Coding Questions for Oracle

This module contains solutions to frequently asked coding problems
in Oracle technical interviews, similar to LeetCode-style questions.
"""

from typing import List, Optional, Dict
from collections import Counter, defaultdict


def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Given an array of integers, return indices of two numbers that add up to target.
    
    Example: nums = [2, 7, 11, 15], target = 9
    Output: [0, 1] (because nums[0] + nums[1] = 9)
    
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


def reverse_integer(x: int) -> int:
    """
    Reverse digits of a 32-bit signed integer.
    Return 0 if reversed integer overflows.
    
    Example: x = 123, Output: 321
    Example: x = -123, Output: -321
    
    Time Complexity: O(log n) where n is the number of digits
    """
    INT_MAX = 2**31 - 1
    INT_MIN = -2**31
    
    sign = -1 if x < 0 else 1
    x = abs(x)
    
    result = 0
    while x != 0:
        digit = x % 10
        x //= 10
        
        # Check for overflow before updating result
        if result > INT_MAX // 10 or (result == INT_MAX // 10 and digit > 7):
            return 0
        
        result = result * 10 + digit
    
    return sign * result


def is_palindrome(s: str) -> bool:
    """
    Check if a string is a palindrome, considering only alphanumeric characters
    and ignoring cases.
    
    Example: "A man, a plan, a canal: Panama" → True
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    left, right = 0, len(s) - 1
    
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        
        if s[left].lower() != s[right].lower():
            return False
        
        left += 1
        right -= 1
    
    return True


def longest_substring_without_repeating(s: str) -> int:
    """
    Find the length of the longest substring without repeating characters.
    
    Example: s = "abcabcbb" → 3 (substring "abc")
    
    Time Complexity: O(n)
    Space Complexity: O(min(n, m)) where m is character set size
    """
    char_index = {}
    max_length = 0
    start = 0
    
    for end, char in enumerate(s):
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        
        char_index[char] = end
        max_length = max(max_length, end - start + 1)
    
    return max_length


def longest_common_prefix(strs: List[str]) -> str:
    """
    Find the longest common prefix string amongst an array of strings.
    
    Example: ["flower", "flow", "flight"] → "fl"
    
    Time Complexity: O(S) where S is sum of all characters
    """
    if not strs:
        return ""
    
    # Use the first string as reference
    prefix = strs[0]
    
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    
    return prefix


def three_sum(nums: List[int]) -> List[List[int]]:
    """
    Find all unique triplets that sum to zero.
    
    Example: nums = [-1, 0, 1, 2, -1, -4]
    Output: [[-1, -1, 2], [-1, 0, 1]]
    
    Time Complexity: O(n²)
    Space Complexity: O(1) excluding output
    """
    nums.sort()
    result = []
    
    for i in range(len(nums) - 2):
        # Skip duplicates
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        
        left, right = i + 1, len(nums) - 1
        
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                
                # Skip duplicates
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                
                left += 1
                right -= 1
    
    return result


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """
    Merge overlapping intervals.
    
    Example: [[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not intervals:
        return []
    
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        if current[0] <= merged[-1][1]:
            # Overlapping intervals, merge them
            merged[-1][1] = max(merged[-1][1], current[1])
        else:
            # Non-overlapping interval
            merged.append(current)
    
    return merged


def rotate_array(nums: List[int], k: int) -> None:
    """
    Rotate array to the right by k steps in-place.
    
    Example: nums = [1,2,3,4,5,6,7], k = 3 → [5,6,7,1,2,3,4]
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    n = len(nums)
    k = k % n
    
    def reverse(start: int, end: int):
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1
    
    # Reverse entire array
    reverse(0, n - 1)
    # Reverse first k elements
    reverse(0, k - 1)
    # Reverse remaining elements
    reverse(k, n - 1)


def find_peak_element(nums: List[int]) -> int:
    """
    Find a peak element (an element greater than its neighbors).
    
    Example: nums = [1,2,3,1] → 2 (index of peak element 3)
    
    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = left + (right - left) // 2
        
        if nums[mid] > nums[mid + 1]:
            # Peak is in left half (including mid)
            right = mid
        else:
            # Peak is in right half
            left = mid + 1
    
    return left


def max_subarray_sum(nums: List[int]) -> int:
    """
    Find the contiguous subarray with the largest sum (Kadane's Algorithm).
    
    Example: nums = [-2,1,-3,4,-1,2,1,-5,4] → 6 (subarray [4,-1,2,1])
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    max_sum = current_sum = nums[0]
    
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    return max_sum


def longest_palindromic_substring(s: str) -> str:
    """
    Find the longest palindromic substring.
    
    Example: s = "babad" → "bab" or "aba"
    
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    if not s:
        return ""
    
    def expand_around_center(left: int, right: int) -> int:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1
    
    start = end = 0
    
    for i in range(len(s)):
        # Check for odd-length palindromes
        len1 = expand_around_center(i, i)
        # Check for even-length palindromes
        len2 = expand_around_center(i, i + 1)
        
        max_len = max(len1, len2)
        if max_len > end - start:
            start = i - (max_len - 1) // 2
            end = i + max_len // 2
    
    return s[start:end + 1]


def group_anagrams(strs: List[str]) -> List[List[str]]:
    """
    Group anagrams together.
    
    Example: ["eat","tea","tan","ate","nat","bat"]
    Output: [["bat"],["nat","tan"],["ate","eat","tea"]]
    
    Time Complexity: O(n * k log k) where k is max string length
    Space Complexity: O(n * k)
    """
    anagrams = defaultdict(list)
    
    for s in strs:
        # Sort the string to use as key
        key = ''.join(sorted(s))
        anagrams[key].append(s)
    
    return list(anagrams.values())


def coin_change(coins: List[int], amount: int) -> int:
    """
    Find minimum number of coins needed to make up the amount.
    
    Example: coins = [1,2,5], amount = 11 → 3 (5+5+1)
    
    Time Complexity: O(amount * n)
    Space Complexity: O(amount)
    """
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1


def product_except_self(nums: List[int]) -> List[int]:
    """
    Return array where output[i] is product of all elements except nums[i].
    Cannot use division.
    
    Example: nums = [1,2,3,4] → [24,12,8,6]
    
    Time Complexity: O(n)
    Space Complexity: O(1) excluding output array
    """
    n = len(nums)
    result = [1] * n
    
    # Calculate left products
    left_product = 1
    for i in range(n):
        result[i] = left_product
        left_product *= nums[i]
    
    # Calculate right products and multiply
    right_product = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right_product
        right_product *= nums[i]
    
    return result


def trap_rain_water(height: List[int]) -> int:
    """
    Calculate how much water can be trapped after raining.
    
    Example: height = [0,1,0,2,1,0,1,3,2,1,2,1] → 6
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if not height:
        return 0
    
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    
    return water


def test_all_solutions():
    """Test all implemented solutions"""
    print("Testing Interview Coding Solutions\n")
    print("=" * 60)
    
    # Test two_sum
    print("\n1. Two Sum")
    print(f"   Input: [2, 7, 11, 15], target=9")
    print(f"   Output: {two_sum([2, 7, 11, 15], 9)}")
    
    # Test reverse_integer
    print("\n2. Reverse Integer")
    print(f"   Input: 123")
    print(f"   Output: {reverse_integer(123)}")
    
    # Test is_palindrome
    print("\n3. Is Palindrome")
    print(f"   Input: 'A man, a plan, a canal: Panama'")
    print(f"   Output: {is_palindrome('A man, a plan, a canal: Panama')}")
    
    # Test longest_substring
    print("\n4. Longest Substring Without Repeating")
    print(f"   Input: 'abcabcbb'")
    print(f"   Output: {longest_substring_without_repeating('abcabcbb')}")
    
    # Test three_sum
    print("\n5. Three Sum")
    print(f"   Input: [-1, 0, 1, 2, -1, -4]")
    print(f"   Output: {three_sum([-1, 0, 1, 2, -1, -4])}")
    
    # Test max_subarray_sum
    print("\n6. Maximum Subarray Sum (Kadane's Algorithm)")
    print(f"   Input: [-2,1,-3,4,-1,2,1,-5,4]")
    print(f"   Output: {max_subarray_sum([-2,1,-3,4,-1,2,1,-5,4])}")
    
    # Test coin_change
    print("\n7. Coin Change")
    print(f"   Input: coins=[1,2,5], amount=11")
    print(f"   Output: {coin_change([1, 2, 5], 11)}")
    
    # Test trap_rain_water
    print("\n8. Trap Rain Water")
    print(f"   Input: [0,1,0,2,1,0,1,3,2,1,2,1]")
    print(f"   Output: {trap_rain_water([0,1,0,2,1,0,1,3,2,1,2,1])}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_all_solutions()
