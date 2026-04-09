"""
Recursion: Introduction and Classic Examples
=============================================

Chapter 5 of "Programming for Lovers in Python" — Trees Part 2
by Phillip Compeau (Carnegie Mellon University).

Background
----------
Recursion is a programming paradigm where a function calls itself to solve
a smaller version of the same problem.  Every recursive function needs:

  1. A **base case** — the simplest version of the problem that can be solved
     directly without recursion (prevents infinite loops).
  2. A **recursive case** — the function calls itself with a simpler input,
     moving toward the base case.

"Big Tree Bad" — Why naive Fibonacci is exponentially slow
----------------------------------------------------------
The naive recursive Fibonacci makes *overlapping* sub-calls:

    fib(5)
    ├── fib(4)
    │   ├── fib(3)
    │   │   ├── fib(2) → fib(1)+fib(0)
    │   │   └── fib(1)
    │   └── fib(2) → fib(1)+fib(0)   ← recomputed!
    └── fib(3) → ...                  ← recomputed again!

Each call spawns two sub-calls → O(2^n) total calls.

**Memoization** caches previously computed values so each sub-problem is
solved only once → O(n) time.

Learning Objectives
-------------------
- Understand base cases and recursive structure
- Implement factorial and Fibonacci recursively
- Observe the exponential blow-up of naive Fibonacci
- Apply memoization to reduce exponential → linear time
- Compare naive, memoized, and iterative implementations
"""

import time
from functools import lru_cache


# ─────────────────────────────────────────────────────────────────────────────
# Factorial
# ─────────────────────────────────────────────────────────────────────────────

def factorial(n: int) -> int:
    """
    Compute n! (n factorial) recursively.

    Base case:  0! = 1  and  1! = 1
    Recursive:  n! = n * (n-1)!

    Args:
        n: Non-negative integer

    Returns:
        n!  as an integer

    Raises:
        ValueError: if n is negative

    Examples:
        >>> factorial(0)
        1
        >>> factorial(5)
        120
        >>> factorial(10)
        3628800
    """
    if n < 0:
        raise ValueError(f"factorial is not defined for negative integers, got {n}")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


# ─────────────────────────────────────────────────────────────────────────────
# Fibonacci — three implementations
# ─────────────────────────────────────────────────────────────────────────────

def fibonacci_naive(n: int) -> int:
    """
    Compute the nth Fibonacci number using naive recursion — O(2^n).

    WARNING: This is intentionally slow for large n.  For n > 35 the
    exponential blow-up becomes very noticeable.

    Sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, ...
              F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2) for n >= 2

    Args:
        n: Non-negative integer index into the Fibonacci sequence

    Returns:
        F(n), the nth Fibonacci number

    Examples:
        >>> fibonacci_naive(0)
        0
        >>> fibonacci_naive(1)
        1
        >>> fibonacci_naive(10)
        55
    """
    if n < 0:
        raise ValueError(f"Fibonacci not defined for negative index, got {n}")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


def fibonacci_memo(n: int, memo: dict | None = None) -> int:
    """
    Compute the nth Fibonacci number using memoized recursion — O(n).

    Each unique sub-problem F(k) is computed only once and cached in `memo`.
    Subsequent calls for the same k return the cached value immediately.

    Args:
        n:    Non-negative integer index
        memo: Dictionary mapping n → F(n).  Pass None (default) to create a
              fresh cache; or pass a shared dict to reuse across calls.

    Returns:
        F(n), the nth Fibonacci number

    Examples:
        >>> fibonacci_memo(10)
        55
        >>> fibonacci_memo(50)
        12586269025
    """
    if n < 0:
        raise ValueError(f"Fibonacci not defined for negative index, got {n}")
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n == 0:
        return 0
    if n == 1:
        return 1
    result = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    memo[n] = result
    return result


def fibonacci_iterative(n: int) -> int:
    """
    Compute the nth Fibonacci number iteratively — O(n) time, O(1) space.

    The iterative approach avoids recursion overhead entirely and uses only
    two variables to track the last two Fibonacci values.

    Args:
        n: Non-negative integer index

    Returns:
        F(n), the nth Fibonacci number

    Examples:
        >>> fibonacci_iterative(10)
        55
        >>> fibonacci_iterative(0)
        0
        >>> fibonacci_iterative(1)
        1
    """
    if n < 0:
        raise ValueError(f"Fibonacci not defined for negative index, got {n}")
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


# ─────────────────────────────────────────────────────────────────────────────
# lru_cache variant for reference
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def fibonacci_lru(n: int) -> int:
    """
    Fibonacci using Python's built-in @lru_cache decorator — O(n).

    Functionally identical to fibonacci_memo but uses Python's standard
    library decorator instead of a manual cache dict.

    Args:
        n: Non-negative integer index

    Returns:
        F(n), the nth Fibonacci number
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)


# ─────────────────────────────────────────────────────────────────────────────
# Performance comparison helpers
# ─────────────────────────────────────────────────────────────────────────────

def time_call(func, *args) -> tuple[float, object]:
    """
    Time a single function call.

    Returns:
        (elapsed_seconds, return_value)
    """
    start = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start
    return elapsed, result


def compare_fibonacci_performance(max_n_naive: int = 35, max_n_fast: int = 50) -> None:
    """
    Print a timing comparison table for the three Fibonacci implementations.

    The naive implementation is only tested up to max_n_naive because it
    grows exponentially (each +5 doubles the time roughly).

    Args:
        max_n_naive: Largest n tested for naive recursion (default 35)
        max_n_fast:  Largest n tested for memo/iterative (default 50)
    """
    print("\n" + "─" * 70)
    print("FIBONACCI PERFORMANCE COMPARISON")
    print("─" * 70)
    print(f"{'n':<6} {'naive (s)':<14} {'memo (s)':<14} {'iterative (s)':<14} {'result'}")
    print("─" * 70)

    test_points_naive = [5, 10, 15, 20, 25, 30, max_n_naive]
    test_points_fast = test_points_naive + [40, max_n_fast]

    seen = set()
    for n in sorted(set(test_points_fast)):
        if n in seen:
            continue
        seen.add(n)

        t_memo, result = time_call(fibonacci_memo, n)
        t_iter, _ = time_call(fibonacci_iterative, n)

        if n <= max_n_naive:
            t_naive, _ = time_call(fibonacci_naive, n)
            naive_str = f"{t_naive:.6f}"
        else:
            naive_str = "   (skip)"

        print(f"{n:<6} {naive_str:<14} {t_memo:<14.8f} {t_iter:<14.8f} {result}")

    print("─" * 70)
    print("Note: naive Fibonacci is O(2^n) — it roughly doubles every +1 in n.")
    print("      Memoized and iterative are both O(n).")


# ─────────────────────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("RECURSION: FACTORIAL AND FIBONACCI")
    print("=" * 70)

    # Factorial demos
    print("\n── Factorial ──")
    for i in [0, 1, 5, 10, 12]:
        print(f"  {i}! = {factorial(i)}")

    # Fibonacci sequence
    print("\n── First 15 Fibonacci numbers ──")
    seq = [fibonacci_iterative(i) for i in range(15)]
    print("  " + ", ".join(map(str, seq)))

    # All three implementations agree
    print("\n── Consistency check (F(30)) ──")
    n = 30
    naive_val = fibonacci_naive(n)
    memo_val  = fibonacci_memo(n)
    iter_val  = fibonacci_iterative(n)
    print(f"  naive:     F({n}) = {naive_val}")
    print(f"  memoized:  F({n}) = {memo_val}")
    print(f"  iterative: F({n}) = {iter_val}")
    print(f"  All equal: {naive_val == memo_val == iter_val}")

    # Performance comparison
    compare_fibonacci_performance(max_n_naive=35, max_n_fast=60)

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("✓ Every recursive function needs a base case + recursive case")
    print("✓ Naive Fibonacci is O(2^n) — exponentially slow")
    print("✓ Memoization caches results → O(n) time")
    print("✓ Iterative is O(n) time, O(1) space (most efficient)")
    print("✓ Python's @lru_cache automates memoization")
