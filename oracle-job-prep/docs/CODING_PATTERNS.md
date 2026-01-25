# Common Coding Interview Patterns

This guide covers the most common patterns you'll encounter in coding interviews at Oracle and similar tech companies.

## 🎯 Pattern Recognition is Key

Learning to recognize patterns helps you:
- Solve problems faster
- Apply known solutions to new problems
- Communicate your approach clearly
- Optimize solutions efficiently

## 📚 Essential Patterns

### 1. Two Pointers

**When to use:**
- Sorted array or linked list
- Need to find pairs with certain properties
- Need to compare elements at different positions

**Common problems:**
- Two Sum (sorted array)
- Three Sum
- Container With Most Water
- Remove Duplicates
- Reverse String

**Example:**
```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return []
```

### 2. Sliding Window

**When to use:**
- Substring or subarray problems
- Fixed or variable window size
- Need to track elements in a range

**Common problems:**
- Longest Substring Without Repeating Characters
- Minimum Window Substring
- Maximum Sum Subarray of Size K
- Longest Substring with K Distinct Characters

**Example:**
```python
def max_sum_subarray(arr, k):
    window_sum = sum(arr[:k])
    max_sum = window_sum
    
    for i in range(k, len(arr)):
        window_sum = window_sum - arr[i - k] + arr[i]
        max_sum = max(max_sum, window_sum)
    
    return max_sum
```

### 3. Fast & Slow Pointers (Floyd's Cycle Detection)

**When to use:**
- Linked list cycle detection
- Finding middle element
- Detecting patterns in sequences

**Common problems:**
- Linked List Cycle
- Happy Number
- Middle of Linked List
- Palindrome Linked List

**Example:**
```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

### 4. Merge Intervals

**When to use:**
- Overlapping intervals
- Scheduling problems
- Range consolidation

**Common problems:**
- Merge Intervals
- Insert Interval
- Meeting Rooms
- Non-overlapping Intervals

**Example:**
```python
def merge_intervals(intervals):
    if not intervals:
        return []
    
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        if current[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], current[1])
        else:
            merged.append(current)
    
    return merged
```

### 5. BFS (Breadth-First Search)

**When to use:**
- Tree level-order traversal
- Shortest path in unweighted graph
- Finding nearest/closest elements

**Common problems:**
- Binary Tree Level Order Traversal
- Rotting Oranges
- Word Ladder
- Number of Islands

**Example:**
```python
from collections import deque

def level_order_traversal(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(level)
    
    return result
```

### 6. DFS (Depth-First Search)

**When to use:**
- Tree/graph traversal
- Backtracking problems
- Finding all paths

**Common problems:**
- Path Sum
- Clone Graph
- Course Schedule
- Number of Islands

**Example:**
```python
def dfs_inorder(root):
    result = []
    
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        result.append(node.val)
        dfs(node.right)
    
    dfs(root)
    return result
```

### 7. Dynamic Programming

**When to use:**
- Optimization problems (min/max)
- Counting problems
- Overlapping subproblems
- Optimal substructure

**Common patterns:**
- 0/1 Knapsack
- Unbounded Knapsack
- Fibonacci-like sequences
- Longest Common Subsequence

**Example:**
```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1
```

### 8. Top K Elements (Heap)

**When to use:**
- Finding K largest/smallest elements
- K closest points
- Frequency-based problems

**Common problems:**
- Kth Largest Element
- Top K Frequent Elements
- K Closest Points to Origin

**Example:**
```python
import heapq

def k_largest_elements(nums, k):
    # Min heap of size k
    heap = nums[:k]
    heapq.heapify(heap)
    
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)
    
    return heap
```

### 9. Binary Search

**When to use:**
- Sorted array
- Finding boundaries
- Search space reduction
- "Find minimum/maximum satisfying condition"

**Common problems:**
- Search in Rotated Sorted Array
- Find First and Last Position
- Search Insert Position
- Find Peak Element

**Example:**
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
```

### 10. Backtracking

**When to use:**
- Generate all combinations/permutations
- Constraint satisfaction
- Decision trees
- "Find all solutions"

**Common problems:**
- Subsets
- Permutations
- N-Queens
- Sudoku Solver
- Word Search

**Example:**
```python
def subsets(nums):
    result = []
    
    def backtrack(start, current):
        result.append(current[:])
        
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()
    
    backtrack(0, [])
    return result
```

### 11. Modified Binary Search

**When to use:**
- Variations of binary search
- Finding boundaries
- Rotated arrays

**Example:**
```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if nums[mid] == target:
            return mid
        
        # Determine which half is sorted
        if nums[left] <= nums[mid]:
            # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1
```

### 12. Monotonic Stack

**When to use:**
- Next greater/smaller element
- Histogram problems
- Stock span problems

**Example:**
```python
def next_greater_element(nums):
    result = [-1] * len(nums)
    stack = []  # Stores indices
    
    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            idx = stack.pop()
            result[idx] = num
        stack.append(i)
    
    return result
```

## 🎯 Pattern Selection Guide

When you see a problem, ask yourself:

1. **Is the array/list sorted?** → Consider Binary Search or Two Pointers
2. **Need to find substring/subarray?** → Consider Sliding Window
3. **Involves a linked list?** → Consider Fast & Slow Pointers
4. **Tree or graph traversal?** → Consider BFS or DFS
5. **Need all combinations?** → Consider Backtracking
6. **Optimization problem?** → Consider Dynamic Programming
7. **Need top K elements?** → Consider Heap
8. **Involves intervals?** → Consider Merge Intervals
9. **Next greater/smaller?** → Consider Monotonic Stack
10. **Overlapping subproblems?** → Consider DP with Memoization

## 💡 Problem-Solving Framework

1. **Understand the Problem**
   - Read carefully
   - Ask clarifying questions
   - Identify constraints

2. **Identify the Pattern**
   - Does it match a known pattern?
   - What data structure fits best?

3. **Plan Your Approach**
   - Start with brute force
   - Optimize using pattern
   - Consider edge cases

4. **Implement**
   - Write clean code
   - Use meaningful names
   - Add comments for complex logic

5. **Test**
   - Walk through examples
   - Test edge cases
   - Verify complexity

6. **Optimize**
   - Can you do better?
   - Space-time tradeoffs?

## 📊 Complexity Cheat Sheet

| Pattern | Time Complexity | Space Complexity |
|---------|----------------|------------------|
| Two Pointers | O(n) | O(1) |
| Sliding Window | O(n) | O(k) |
| Fast & Slow Pointers | O(n) | O(1) |
| Merge Intervals | O(n log n) | O(n) |
| BFS | O(V + E) | O(V) |
| DFS | O(V + E) | O(V) |
| Dynamic Programming | O(n²) typical | O(n) typical |
| Top K Elements | O(n log k) | O(k) |
| Binary Search | O(log n) | O(1) |
| Backtracking | O(2ⁿ) or O(n!) | O(n) |

## 🎓 Practice Strategy

1. **Week 1-2:** Master Two Pointers and Sliding Window
2. **Week 3-4:** Learn BFS, DFS, and Tree patterns
3. **Week 5-6:** Focus on Dynamic Programming
4. **Week 7-8:** Practice Backtracking and Advanced patterns
5. **Week 9-10:** Mix all patterns, focus on speed

**Daily Goal:** Solve 2-3 problems using different patterns

## ✅ Pattern Mastery Checklist

Track your progress:

- [ ] Two Pointers (10 problems)
- [ ] Sliding Window (10 problems)
- [ ] Fast & Slow Pointers (5 problems)
- [ ] Merge Intervals (5 problems)
- [ ] BFS (10 problems)
- [ ] DFS (10 problems)
- [ ] Dynamic Programming (15 problems)
- [ ] Top K Elements (5 problems)
- [ ] Binary Search (10 problems)
- [ ] Backtracking (10 problems)
- [ ] Monotonic Stack (5 problems)
- [ ] Modified Binary Search (5 problems)

**Total: 100 problems** - This gives you solid interview preparation!

---

*Remember: The goal is not to memorize solutions, but to recognize patterns and apply them!*
