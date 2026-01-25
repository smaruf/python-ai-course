#!/usr/bin/env python3
"""
Quick Start Guide - Oracle Job Preparation

This script demonstrates the key features of the Oracle job preparation project.
Run this to get familiar with the structure and available resources.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def demonstrate_algorithms():
    """Demonstrate algorithm implementations"""
    from src.algorithms.sorting import quick_sort, merge_sort
    from src.algorithms.graphs import Graph
    
    print_section("ALGORITHMS DEMONSTRATION")
    
    # Sorting
    print("1. Sorting Algorithms")
    print("-" * 80)
    arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original array: {arr}")
    print(f"QuickSort result: {quick_sort(arr.copy())}")
    print(f"MergeSort result: {merge_sort(arr.copy())}")
    
    # Graphs
    print("\n2. Graph Algorithms")
    print("-" * 80)
    g = Graph(directed=True)
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 4)
    g.add_edge(1, 2, 2)
    g.add_edge(2, 3, 1)
    
    print(f"Graph BFS from vertex 0: {g.bfs(0)}")
    print(f"Graph DFS from vertex 0: {g.dfs(0)}")
    print(f"Shortest paths (Dijkstra): {g.dijkstra(0)}")


def demonstrate_coding_problems():
    """Demonstrate coding interview solutions"""
    from examples.coding_problems.interview_questions import (
        two_sum, is_palindrome, max_subarray_sum
    )
    
    print_section("CODING INTERVIEW PROBLEMS")
    
    print("1. Two Sum Problem")
    print("-" * 80)
    nums = [2, 7, 11, 15]
    target = 9
    print(f"Input: nums={nums}, target={target}")
    print(f"Output: {two_sum(nums, target)}")
    
    print("\n2. Palindrome Check")
    print("-" * 80)
    test_str = "A man, a plan, a canal: Panama"
    print(f"Input: '{test_str}'")
    print(f"Is palindrome: {is_palindrome(test_str)}")
    
    print("\n3. Maximum Subarray Sum (Kadane's Algorithm)")
    print("-" * 80)
    arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    print(f"Input: {arr}")
    print(f"Max subarray sum: {max_subarray_sum(arr)}")


def demonstrate_system_design():
    """Demonstrate system design patterns"""
    from examples.system_design.design_patterns import (
        LRUCache, RateLimiter, URLShortener
    )
    
    print_section("SYSTEM DESIGN PATTERNS")
    
    # LRU Cache
    print("1. LRU Cache Implementation")
    print("-" * 80)
    cache = LRUCache(3)
    cache.put(1, 100)
    cache.put(2, 200)
    cache.put(3, 300)
    print(f"Cache operations:")
    print(f"  put(1, 100), put(2, 200), put(3, 300)")
    print(f"  get(1) = {cache.get(1)}")
    cache.put(4, 400)
    print(f"  put(4, 400) - evicts key 2")
    print(f"  get(2) = {cache.get(2)} (evicted)")
    
    # Rate Limiter
    print("\n2. Rate Limiter (Token Bucket)")
    print("-" * 80)
    limiter = RateLimiter(max_tokens=3, refill_rate=1.0)
    print("Configured: 3 max tokens, refill 1 token/second")
    for i in range(4):
        allowed = limiter.allow_request()
        print(f"  Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}")
    
    # URL Shortener
    print("\n3. URL Shortener")
    print("-" * 80)
    shortener = URLShortener()
    urls = [
        "https://www.oracle.com/careers",
        "https://docs.oracle.com/en/database/"
    ]
    for url in urls:
        short = shortener.shorten(url)
        print(f"  {url}")
        print(f"    → Short code: {short}")
        print(f"    → Expanded: {shortener.expand(short)}")


def demonstrate_sql():
    """Demonstrate SQL query examples"""
    from src.database.sql_queries import SQL_QUERIES
    
    print_section("SQL QUERY EXAMPLES")
    
    examples = [
        ("Second Highest Salary", "second_highest_salary"),
        ("Department Statistics", "department_wise_salary"),
        ("Employee Hierarchy", "hierarchical_query"),
    ]
    
    for name, key in examples:
        if key in SQL_QUERIES:
            print(f"{name}")
            print("-" * 80)
            # Show first 10 lines of the query
            lines = SQL_QUERIES[key].strip().split('\n')[:10]
            for line in lines:
                print(f"  {line}")
            if len(SQL_QUERIES[key].strip().split('\n')) > 10:
                print("  ...")
            print()


def show_project_structure():
    """Show the project structure"""
    print_section("PROJECT STRUCTURE")
    
    structure = """
oracle-job-prep/
├── README.md                          # Project overview
├── STUDY_GUIDE.md                     # 10-week study plan
├── requirements.txt                   # Python dependencies
│
├── src/                               # Source code
│   ├── algorithms/                    # Algorithm implementations
│   │   ├── sorting.py                # Sorting algorithms
│   │   └── graphs.py                 # Graph algorithms
│   ├── database/                      # Database examples
│   │   └── sql_queries.py            # Complex SQL queries
│   ├── system_design/                 # System design patterns
│   └── cloud/                         # Cloud concepts
│
├── examples/                          # Practical examples
│   ├── coding_problems/              
│   │   └── interview_questions.py    # LeetCode-style problems
│   └── system_design/
│       └── design_patterns.py        # Design pattern implementations
│
├── tests/                             # Unit tests
│   ├── test_algorithms.py
│   └── test_interview_questions.py
│
└── docs/                              # Documentation
    └── RESOURCES.md                   # Learning resources
    """
    
    print(structure)


def show_next_steps():
    """Show recommended next steps"""
    print_section("NEXT STEPS - YOUR LEARNING PATH")
    
    steps = """
📚 Recommended Learning Path:

Week 1-2: Fundamentals
  □ Review Python basics and data structures
  □ Solve 20 easy LeetCode problems
  □ Practice basic SQL queries
  □ Read: src/algorithms/sorting.py
  
Week 3-4: Intermediate Concepts
  □ Solve 15 medium LeetCode problems
  □ Study graph algorithms (BFS, DFS)
  □ Practice complex SQL (joins, window functions)
  □ Read: src/algorithms/graphs.py
  
Week 5-6: Advanced Topics
  □ Solve 20 medium/hard problems
  □ Master dynamic programming
  □ Study database design and optimization
  □ Read: src/database/sql_queries.py
  
Week 7-8: System Design
  □ Complete 5 system design exercises
  □ Practice Oracle-specific SQL
  □ Study PL/SQL basics
  □ Read: examples/system_design/design_patterns.py
  
Week 9-10: Mock Interviews & Review
  □ Take 5 mock technical interviews
  □ Review all weak areas
  □ Practice behavioral questions (STAR method)
  □ Read: STUDY_GUIDE.md

🎯 Daily Routine:
  • 1-2 coding problems (morning)
  • 30 min SQL practice (afternoon)
  • 1 system design topic (evening)
  • Review notes before bed

📖 Key Resources:
  • LeetCode: https://leetcode.com
  • Oracle Docs: https://docs.oracle.com/en/database/
  • System Design Primer: https://github.com/donnemartin/system-design-primer
  
💡 Pro Tips:
  • Practice explaining your thought process out loud
  • Time yourself while solving problems
  • Focus on understanding, not memorizing
  • Join Oracle interview preparation groups
  • Review Oracle's company culture and values
    """
    
    print(steps)


def main():
    """Main function to run all demonstrations"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "ORACLE JOB PREPARATION PROJECT" + " "*28 + "║")
    print("║" + " "*17 + "Comprehensive Interview Preparation" + " "*26 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\nThis quick start guide demonstrates the key features of this project.")
    print("Choose what you'd like to explore:\n")
    
    options = {
        '1': ('Project Structure', show_project_structure),
        '2': ('Algorithm Demonstrations', demonstrate_algorithms),
        '3': ('Coding Interview Problems', demonstrate_coding_problems),
        '4': ('System Design Patterns', demonstrate_system_design),
        '5': ('SQL Query Examples', demonstrate_sql),
        '6': ('Next Steps & Learning Path', show_next_steps),
        '7': ('Run All Demonstrations', None),
    }
    
    for key, (name, _) in options.items():
        print(f"  {key}. {name}")
    print(f"  0. Exit\n")
    
    choice = input("Enter your choice (0-7): ").strip()
    
    if choice == '0':
        print("\nGood luck with your Oracle interview preparation! 🚀\n")
        return
    
    print()
    
    if choice == '7':
        # Run all demonstrations
        for key in ['1', '2', '3', '4', '5', '6']:
            _, func = options[key]
            func()
            input("\n[Press Enter to continue...]")
    elif choice in options and options[choice][1]:
        _, func = options[choice]
        func()
    else:
        print("Invalid choice. Please run the script again.")
    
    print("\n")
    print("="*80)
    print("For more details, check out:")
    print("  • README.md - Project overview and setup")
    print("  • STUDY_GUIDE.md - Comprehensive 10-week study plan")
    print("  • docs/RESOURCES.md - Additional learning resources")
    print("="*80)
    print("\nGood luck with your Oracle interview preparation! 🚀\n")


if __name__ == "__main__":
    main()
