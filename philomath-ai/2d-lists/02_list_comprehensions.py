"""
List Comprehensions for 2-D Arrays
===================================

List comprehensions are a powerful and Pythonic way to create lists.
For 2-D arrays, they're not just elegant—they're essential for avoiding bugs!

Learning Objectives:
- Master list comprehension syntax for 1-D lists
- Create 2-D lists using nested list comprehensions
- Understand the order of iteration in nested comprehensions
- Build grids with computed values
- Use conditions in list comprehensions
- Create various patterns and structures efficiently

Key Concepts:
- List comprehensions are more readable and often faster than loops
- Nested comprehensions create nested structures
- The outer loop comes first in the syntax
- Comprehensions can include conditional logic
- Each iteration creates a new object (no reference sharing)
"""


def basic_1d_comprehension_examples():
    """
    Review basic 1-D list comprehensions before moving to 2-D.
    """
    print("=== Basic 1-D List Comprehensions ===\n")
    
    # Simple range
    squares = [x**2 for x in range(10)]
    print(f"Squares 0-9: {squares}")
    
    # With condition
    even_squares = [x**2 for x in range(10) if x % 2 == 0]
    print(f"Even squares: {even_squares}")
    
    # With transformation
    words = ["hello", "world", "python"]
    upper = [word.upper() for word in words]
    print(f"Uppercase: {upper}")
    
    # Multiple operations
    modified = [x * 2 + 1 for x in range(5)]
    print(f"Modified: {modified}")


def create_2d_zeros(rows, cols):
    """
    Create a 2-D list filled with zeros using list comprehension.
    
    This is the standard way to create a 2-D grid in Python.
    
    Time Complexity: O(rows * cols)
    Space Complexity: O(rows * cols)
    
    Args:
        rows: Number of rows
        cols: Number of columns
    
    Returns:
        2-D list filled with zeros
    
    Example:
        >>> create_2d_zeros(2, 3)
        [[0, 0, 0], [0, 0, 0]]
    """
    return [[0 for _ in range(cols)] for _ in range(rows)]


def create_2d_with_value(rows, cols, value):
    """
    Create a 2-D list filled with a specific value.
    
    Args:
        rows: Number of rows
        cols: Number of columns
        value: Value to fill the grid with
    
    Returns:
        2-D list filled with the specified value
    
    Example:
        >>> create_2d_with_value(2, 3, 'X')
        [['X', 'X', 'X'], ['X', 'X', 'X']]
    """
    return [[value for _ in range(cols)] for _ in range(rows)]


def create_2d_identity_matrix(n):
    """
    Create an n×n identity matrix (1s on diagonal, 0s elsewhere).
    
    This demonstrates using conditions in list comprehensions.
    
    Args:
        n: Size of the matrix
    
    Returns:
        n×n identity matrix
    
    Example:
        >>> create_2d_identity_matrix(3)
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    """
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def create_2d_multiplication_table(rows, cols):
    """
    Create a multiplication table using computed values.
    
    This shows how to use the loop variables to compute values.
    
    Args:
        rows: Number of rows
        cols: Number of columns
    
    Returns:
        Multiplication table where grid[i][j] = i * j
    
    Example:
        >>> create_2d_multiplication_table(3, 4)
        [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 4, 6]]
    """
    return [[i * j for j in range(cols)] for i in range(rows)]


def create_2d_coordinate_grid(rows, cols):
    """
    Create a grid where each cell contains its (row, col) coordinate.
    
    This demonstrates creating grids with complex values.
    
    Args:
        rows: Number of rows
        cols: Number of columns
    
    Returns:
        Grid where each cell is a tuple (row, col)
    
    Example:
        >>> create_2d_coordinate_grid(2, 3)
        [[(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)]]
    """
    return [[(i, j) for j in range(cols)] for i in range(rows)]


def create_2d_checkerboard(rows, cols):
    """
    Create a checkerboard pattern using list comprehension.
    
    This demonstrates using conditional logic based on position.
    
    Args:
        rows: Number of rows
        cols: Number of columns
    
    Returns:
        Checkerboard pattern with 'W' and 'B'
    
    Example:
        >>> create_2d_checkerboard(3, 3)
        [['W', 'B', 'W'], ['B', 'W', 'B'], ['W', 'B', 'W']]
    """
    return [['W' if (i + j) % 2 == 0 else 'B' for j in range(cols)] for i in range(rows)]


def demonstrate_comprehension_order():
    """
    Demonstrate the order of iteration in nested list comprehensions.
    
    Understanding this is crucial for working with 2-D structures.
    """
    print("\n=== Understanding Comprehension Order ===\n")
    
    print("Creating a 3x4 grid with values showing creation order:")
    counter = 0
    grid = []
    for i in range(3):  # rows
        row = []
        for j in range(4):  # cols
            row.append(counter)
            counter += 1
        grid.append(row)
    
    print("Using nested loops:")
    for row in grid:
        print(row)
    
    print("\nSame thing with list comprehension:")
    grid_comp = [[i * 4 + j for j in range(4)] for i in range(3)]
    for row in grid_comp:
        print(row)
    
    print("\nKey insight: Outer loop (rows) comes FIRST in comprehension")
    print("Syntax: [[inner_expression for j in range(cols)] for i in range(rows)]")


def demonstrate_various_patterns():
    """
    Show various patterns that can be created with list comprehensions.
    """
    print("\n=== Various Patterns with List Comprehensions ===\n")
    
    # 1. Upper triangular matrix
    print("1. Upper Triangular Matrix (4x4):")
    upper_tri = [[1 if j >= i else 0 for j in range(4)] for i in range(4)]
    print_grid(upper_tri)
    
    # 2. Lower triangular matrix
    print("\n2. Lower Triangular Matrix (4x4):")
    lower_tri = [[1 if j <= i else 0 for j in range(4)] for i in range(4)]
    print_grid(lower_tri)
    
    # 3. Border pattern
    print("\n3. Border Pattern (5x5):")
    n = 5
    border = [['#' if i == 0 or i == n-1 or j == 0 or j == n-1 else '.'
               for j in range(n)] for i in range(n)]
    print_grid(border)
    
    # 4. Diamond pattern
    print("\n4. Diamond Pattern (7x7):")
    n = 7
    mid = n // 2
    diamond = [['*' if abs(i - mid) + abs(j - mid) <= mid else '.'
                for j in range(n)] for i in range(n)]
    print_grid(diamond)
    
    # 5. Gradient pattern
    print("\n5. Gradient Pattern (5x10):")
    gradient = [[j for j in range(10)] for i in range(5)]
    print_grid(gradient)


def create_chessboard(size=8):
    """
    Create a standard chessboard with alternating colors.
    
    Args:
        size: Size of the board (default 8 for standard chess)
    
    Returns:
        Chessboard pattern
    """
    return [['□' if (i + j) % 2 == 0 else '■' for j in range(size)] for i in range(size)]


def demonstrate_conditional_comprehensions():
    """
    Show how to use conditions in list comprehensions for 2-D arrays.
    """
    print("\n=== Conditional List Comprehensions ===\n")
    
    # Create grid with only even products
    print("Grid with only even products (0 for odd):")
    grid = [[i * j if (i * j) % 2 == 0 else 0 for j in range(5)] for i in range(5)]
    print_grid(grid)
    
    # Create grid with sentinel values for invalid positions
    print("\nGrid with diagonal marked specially:")
    grid = [['X' if i == j else i + j for j in range(5)] for i in range(5)]
    print_grid(grid)


def demonstrate_performance_comparison():
    """
    Compare performance of list comprehension vs traditional loops.
    """
    import time
    
    print("\n=== Performance Comparison ===\n")
    
    rows, cols = 100, 100
    
    # Method 1: Traditional nested loops
    start = time.time()
    grid1 = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(i * j)
        grid1.append(row)
    time1 = time.time() - start
    
    # Method 2: List comprehension
    start = time.time()
    grid2 = [[i * j for j in range(cols)] for i in range(rows)]
    time2 = time.time() - start
    
    print(f"Traditional loops: {time1:.6f} seconds")
    print(f"List comprehension: {time2:.6f} seconds")
    print(f"Speedup: {time1/time2:.2f}x faster")
    print("\n✓ List comprehensions are not only more readable but also faster!")


def print_grid(grid):
    """
    Pretty print a 2-D grid.
    
    Args:
        grid: 2-D list to print
    """
    for row in grid:
        print(' '.join(str(cell) for cell in row))


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("=" * 70)
    print("LIST COMPREHENSIONS FOR 2-D ARRAYS")
    print("Programming for Lovers in Python - Chapter 3")
    print("=" * 70)
    
    # Basic 1-D review
    basic_1d_comprehension_examples()
    
    # Understanding order
    demonstrate_comprehension_order()
    
    # Various patterns
    demonstrate_various_patterns()
    
    # Conditional comprehensions
    demonstrate_conditional_comprehensions()
    
    # Performance comparison
    demonstrate_performance_comparison()
    
    # Chessboard example
    print("\n=== Bonus: Standard Chessboard ===\n")
    board = create_chessboard()
    print_grid(board)
    
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS:")
    print("=" * 70)
    print("1. List comprehensions are more Pythonic and often faster")
    print("2. Syntax: [[expr for j in range(cols)] for i in range(rows)]")
    print("3. Outer loop (rows) comes FIRST in the comprehension")
    print("4. Each inner list is created independently (no reference sharing)")
    print("5. Can include conditions: [expr if condition else other_expr]")
    print("6. Can use loop variables: [[i*j for j in ...] for i in ...]")
    print("=" * 70)


if __name__ == "__main__":
    main()
