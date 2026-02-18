"""
Nested Loops - Iterating Through 2-D Arrays
============================================

Nested loops are essential for working with 2-D data structures.
This module explores different patterns for iterating through grids,
printing formatted output, and avoiding nested loops when possible.

Learning Objectives:
- Master nested loop patterns for 2-D arrays
- Print 2-D structures in various formats
- Understand when nested loops are necessary
- Learn alternatives to nested loops
- Work with both index-based and value-based iteration
- Format output professionally

Key Concepts:
- Outer loop iterates rows, inner loop iterates columns
- Can iterate by index: for i in range(len(grid))
- Can iterate by value: for row in grid
- Order matters: row-by-row vs column-by-column
- Many operations can use list comprehensions instead
- Consider readability vs cleverness
"""


def demonstrate_basic_nested_loops():
    """
    Show the most basic nested loop pattern for 2-D arrays.
    """
    print("=== Basic Nested Loops ===\n")
    
    grid = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    print("Grid:")
    print_grid_simple(grid)
    
    print("\nIterating with nested loops (by index):")
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            print(f"  grid[{i}][{j}] = {grid[i][j]}")
    
    print("\nIterating with nested loops (by value):")
    for row_idx, row in enumerate(grid):
        for col_idx, value in enumerate(row):
            print(f"  Position ({row_idx},{col_idx}): {value}")


def demonstrate_row_vs_column_iteration():
    """
    Show the difference between row-major and column-major iteration.
    """
    print("\n=== Row-Major vs Column-Major Iteration ===\n")
    
    grid = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    
    print("Grid:")
    print_grid_simple(grid)
    
    # Row-major (natural Python order)
    print("\nRow-major order (natural):")
    values = []
    for row in grid:
        for value in row:
            values.append(value)
    print(f"  {values}")
    
    # Column-major
    print("\nColumn-major order:")
    values = []
    for j in range(len(grid[0])):
        for i in range(len(grid)):
            values.append(grid[i][j])
    print(f"  {values}")


def demonstrate_printing_patterns():
    """
    Show various ways to print 2-D arrays.
    """
    print("\n=== Printing Patterns ===\n")
    
    grid = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    # Pattern 1: Simple list representation
    print("1. Simple list representation:")
    for row in grid:
        print(f"  {row}")
    
    # Pattern 2: Space-separated values
    print("\n2. Space-separated values:")
    for row in grid:
        print('  ', end='')
        for value in row:
            print(value, end=' ')
        print()
    
    # Pattern 3: Formatted columns
    print("\n3. Formatted columns (right-aligned):")
    for row in grid:
        print('  ', end='')
        for value in row:
            print(f"{value:3}", end='')
        print()
    
    # Pattern 4: Using join
    print("\n4. Using join:")
    for row in grid:
        print('  ' + ' '.join(str(x) for x in row))
    
    # Pattern 5: Comma-separated (CSV style)
    print("\n5. CSV style:")
    for row in grid:
        print('  ' + ', '.join(str(x) for x in row))


def demonstrate_pattern_drawing():
    """
    Use nested loops to draw various patterns.
    """
    print("\n=== Drawing Patterns with Nested Loops ===\n")
    
    # Pattern 1: Rectangle
    print("1. Rectangle (5x8):")
    for i in range(5):
        for j in range(8):
            print('*', end=' ')
        print()
    
    # Pattern 2: Right triangle
    print("\n2. Right Triangle:")
    for i in range(1, 7):
        for j in range(i):
            print('*', end=' ')
        print()
    
    # Pattern 3: Inverted triangle
    print("\n3. Inverted Triangle:")
    for i in range(6, 0, -1):
        for j in range(i):
            print('*', end=' ')
        print()
    
    # Pattern 4: Pyramid
    print("\n4. Pyramid:")
    n = 5
    for i in range(n):
        # Print spaces
        for j in range(n - i - 1):
            print(' ', end=' ')
        # Print stars
        for j in range(2 * i + 1):
            print('*', end=' ')
        print()
    
    # Pattern 5: Number pyramid
    print("\n5. Number Pyramid:")
    for i in range(1, 6):
        for j in range(1, i + 1):
            print(j, end=' ')
        print()


def demonstrate_conditional_printing():
    """
    Show how to use conditions inside nested loops.
    """
    print("\n=== Conditional Printing ===\n")
    
    # Create a checkerboard
    print("Checkerboard (8x8):")
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                print('□', end=' ')
            else:
                print('■', end=' ')
        print()
    
    # Print only even numbers
    print("\nGrid with only even numbers:")
    grid = [[i * j for j in range(5)] for i in range(5)]
    for row in grid:
        for value in row:
            if value % 2 == 0:
                print(f"{value:3}", end='')
            else:
                print('  -', end='')
        print()


def demonstrate_avoiding_nested_loops():
    """
    Show when and how to avoid nested loops.
    
    As mentioned in the video: "I don't like nested loops"
    """
    print("\n=== Avoiding Nested Loops ===\n")
    
    grid = [[i * j for j in range(5)] for i in range(5)]
    
    # Using nested loops (traditional)
    print("1. Traditional nested loops:")
    print("for row in grid:")
    print("    for value in row:")
    print("        print(value, end=' ')")
    print("\nResult:")
    for row in grid:
        for value in row:
            print(f"{value:3}", end='')
        print()
    
    # Using join (avoids inner loop)
    print("\n2. Using join (avoids inner loop):")
    print("for row in grid:")
    print("    print(' '.join(str(x) for x in row))")
    print("\nResult:")
    for row in grid:
        print('  ' + ' '.join(f"{x:3}" for x in row))
    
    # Using list comprehension (most Pythonic)
    print("\n3. List comprehension (most Pythonic):")
    print("'\\n'.join(' '.join(str(x) for x in row) for row in grid)")
    print("\nResult:")
    result = '\n'.join('  ' + ' '.join(f"{x:3}" for x in row) for row in grid)
    print(result)


def demonstrate_sum_and_aggregate():
    """
    Show how to compute aggregates over 2-D arrays.
    """
    print("\n=== Sum and Aggregate Operations ===\n")
    
    grid = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    
    print("Grid:")
    print_grid_simple(grid)
    
    # Sum all elements (with nested loops)
    total = 0
    for row in grid:
        for value in row:
            total += value
    print(f"\nTotal sum (nested loops): {total}")
    
    # Sum all elements (without nested loops)
    total = sum(sum(row) for row in grid)
    print(f"Total sum (comprehension): {total}")
    
    # Row sums
    print("\nRow sums:")
    for i, row in enumerate(grid):
        row_sum = sum(row)
        print(f"  Row {i}: {row_sum}")
    
    # Column sums
    print("\nColumn sums:")
    num_cols = len(grid[0])
    for j in range(num_cols):
        col_sum = sum(grid[i][j] for i in range(len(grid)))
        print(f"  Column {j}: {col_sum}")
    
    # Maximum value
    max_value = max(max(row) for row in grid)
    print(f"\nMaximum value: {max_value}")
    
    # Minimum value
    min_value = min(min(row) for row in grid)
    print(f"Minimum value: {min_value}")


def demonstrate_searching():
    """
    Show how to search for values in 2-D arrays.
    """
    print("\n=== Searching in 2-D Arrays ===\n")
    
    grid = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    print("Grid:")
    print_grid_simple(grid)
    
    # Find position of a value
    target = 5
    print(f"\nSearching for {target}:")
    found = False
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == target:
                print(f"  Found at position ({i}, {j})")
                found = True
                break
        if found:
            break
    
    # Find all occurrences of a value
    target = 5
    print(f"\nFinding all positions where value > {target}:")
    positions = []
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] > target:
                positions.append((i, j))
    
    for pos in positions:
        print(f"  Position {pos}: value = {grid[pos[0]][pos[1]]}")


def print_grid_formatted(grid, cell_width=3):
    """
    Print a grid with proper formatting and borders.
    
    Args:
        grid: 2-D list to print
        cell_width: Width of each cell
    """
    if not grid:
        return
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Top border
    print('  ┌' + '─' * (cols * (cell_width + 1) + 1) + '┐')
    
    # Rows
    for row in grid:
        print('  │ ', end='')
        for value in row:
            print(f"{str(value):^{cell_width}}", end=' ')
        print('│')
    
    # Bottom border
    print('  └' + '─' * (cols * (cell_width + 1) + 1) + '┘')


def demonstrate_pretty_printing():
    """
    Show advanced printing techniques.
    """
    print("\n=== Pretty Printing ===\n")
    
    grid = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    
    print("Basic grid:")
    print_grid_simple(grid)
    
    print("\nWith borders:")
    print_grid_formatted(grid)
    
    # Character grid
    char_grid = [
        ['O', '.', '.', 'O'],
        ['.', '.', '.', '.'],
        ['.', '^', '^', '.'],
        ['\\', '_', '_', '/']
    ]
    
    print("\nCharacter grid (face):")
    print_grid_formatted(char_grid, cell_width=2)


def print_grid_simple(grid):
    """Simple grid printing."""
    for row in grid:
        print(f"  {row}")


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("=" * 70)
    print("NESTED LOOPS - Iterating Through 2-D Arrays")
    print("Programming for Lovers in Python - Chapter 3")
    print("=" * 70)
    
    # Basic patterns
    demonstrate_basic_nested_loops()
    
    # Iteration orders
    demonstrate_row_vs_column_iteration()
    
    # Printing
    demonstrate_printing_patterns()
    
    # Drawing patterns
    demonstrate_pattern_drawing()
    
    # Conditional printing
    demonstrate_conditional_printing()
    
    # Avoiding nested loops
    demonstrate_avoiding_nested_loops()
    
    # Aggregates
    demonstrate_sum_and_aggregate()
    
    # Searching
    demonstrate_searching()
    
    # Pretty printing
    demonstrate_pretty_printing()
    
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS:")
    print("=" * 70)
    print("1. Outer loop = rows, inner loop = columns")
    print("2. Can iterate by index or by value")
    print("3. Use enumerate() to get both index and value")
    print("4. Many operations can avoid nested loops with comprehensions")
    print("5. join() is great for printing rows")
    print("6. sum(sum(row) for row in grid) for total sum")
    print("7. Consider readability when choosing iteration style")
    print("=" * 70)


if __name__ == "__main__":
    main()
