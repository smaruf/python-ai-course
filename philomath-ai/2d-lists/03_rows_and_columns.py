"""
Rows and Columns - Working with 2-D Lists
==========================================

Understanding how to navigate, access, and modify rows and columns in 2-D lists
is essential for working with grids, matrices, and tabular data.

Learning Objectives:
- Access individual elements, entire rows, and columns
- Understand row-major vs column-major order
- Work with non-rectangular (jagged) lists
- Append and modify rows dynamically
- Extract and manipulate columns
- Understand the dimensions of 2-D structures

Key Concepts:
- In Python, 2-D lists are "lists of lists" (row-major order)
- grid[row][col] - row index comes first
- Rows are easy to access: grid[i] gives you row i
- Columns require iteration: [row[j] for row in grid]
- Lists don't have to be rectangular - rows can have different lengths
"""


def demonstrate_row_access():
    """
    Show how to access entire rows from a 2-D list.
    """
    print("=== Accessing Rows ===\n")
    
    # Create a sample grid
    grid = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    
    print("Original grid:")
    print_grid(grid)
    
    # Access individual rows
    print(f"\nRow 0: {grid[0]}")
    print(f"Row 1: {grid[1]}")
    print(f"Row 2: {grid[2]}")
    
    # Iterate through all rows
    print("\nIterating through all rows:")
    for i, row in enumerate(grid):
        print(f"  Row {i}: {row}")
    
    # Get number of rows
    print(f"\nNumber of rows: {len(grid)}")
    print(f"Number of columns in row 0: {len(grid[0])}")


def demonstrate_column_access():
    """
    Show how to access entire columns from a 2-D list.
    
    Columns are trickier than rows because Python uses row-major order.
    """
    print("\n=== Accessing Columns ===\n")
    
    grid = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12]
    ]
    
    print("Grid:")
    print_grid(grid)
    
    # Extract a column using list comprehension
    col_0 = [row[0] for row in grid]
    col_1 = [row[1] for row in grid]
    col_2 = [row[2] for row in grid]
    
    print(f"\nColumn 0: {col_0}")
    print(f"Column 1: {col_1}")
    print(f"Column 2: {col_2}")
    
    # Extract all columns
    num_cols = len(grid[0]) if grid else 0
    print("\nAll columns:")
    for j in range(num_cols):
        col = [row[j] for row in grid]
        print(f"  Column {j}: {col}")


def demonstrate_element_access():
    """
    Show how to access individual elements.
    """
    print("\n=== Accessing Individual Elements ===\n")
    
    grid = [
        ['A', 'B', 'C'],
        ['D', 'E', 'F'],
        ['G', 'H', 'I']
    ]
    
    print("Grid:")
    print_grid(grid)
    
    # Access specific elements
    print(f"\ngrid[0][0] = '{grid[0][0]}'  (top-left)")
    print(f"grid[0][2] = '{grid[0][2]}'  (top-right)")
    print(f"grid[1][1] = '{grid[1][1]}'  (center)")
    print(f"grid[2][0] = '{grid[2][0]}'  (bottom-left)")
    print(f"grid[2][2] = '{grid[2][2]}'  (bottom-right)")
    
    # Common pattern: iterate all elements
    print("\nIterating all elements (row by row):")
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            print(f"  grid[{i}][{j}] = '{grid[i][j]}'")


def demonstrate_row_modification():
    """
    Show how to modify rows in a 2-D list.
    """
    print("\n=== Modifying Rows ===\n")
    
    grid = [[0] * 4 for _ in range(3)]
    print("Initial grid:")
    print_grid(grid)
    
    # Replace entire row
    print("\nReplacing row 1 with [10, 20, 30, 40]:")
    grid[1] = [10, 20, 30, 40]
    print_grid(grid)
    
    # Modify elements in a row
    print("\nModifying elements in row 0:")
    grid[0][0] = 1
    grid[0][1] = 2
    print_grid(grid)
    
    # Append to a row
    print("\nAppending 99 to row 2:")
    grid[2].append(99)
    print_grid(grid)
    print("Note: Row 2 is now longer than other rows!")


def demonstrate_column_modification():
    """
    Show how to modify columns in a 2-D list.
    
    Modifying columns is less direct than rows.
    """
    print("\n=== Modifying Columns ===\n")
    
    grid = [[0] * 4 for _ in range(3)]
    print("Initial grid:")
    print_grid(grid)
    
    # Set entire column to a value
    print("\nSetting column 2 to all 5s:")
    for i in range(len(grid)):
        grid[i][2] = 5
    print_grid(grid)
    
    # Set column to different values
    print("\nSetting column 1 to [10, 20, 30]:")
    values = [10, 20, 30]
    for i in range(len(grid)):
        grid[i][1] = values[i]
    print_grid(grid)


def demonstrate_non_rectangular_lists():
    """
    Show that Python lists don't have to be rectangular.
    
    This is called a "jagged array" or "ragged array".
    """
    print("\n=== Non-Rectangular (Jagged) Lists ===\n")
    
    # Create a non-rectangular list
    jagged = [
        [1, 2, 3],
        [4, 5],
        [6, 7, 8, 9],
        [10]
    ]
    
    print("Jagged list:")
    for i, row in enumerate(jagged):
        print(f"  Row {i} (length {len(row)}): {row}")
    
    # Safely access elements
    print("\nSafely accessing elements:")
    for i in range(len(jagged)):
        for j in range(len(jagged[i])):
            print(f"  jagged[{i}][{j}] = {jagged[i][j]}")
    
    # Appending to create jagged structure
    print("\n\nBuilding a jagged list dynamically:")
    dynamic_jagged = []
    for i in range(5):
        row = list(range(i + 1))  # Row i has i+1 elements
        dynamic_jagged.append(row)
        print(f"  Added row {i}: {row}")
    
    print("\nFinal jagged list:")
    for i, row in enumerate(dynamic_jagged):
        print(f"  {row}")


def demonstrate_appending():
    """
    Show different ways to append to 2-D lists.
    """
    print("\n=== Appending to 2-D Lists ===\n")
    
    # Start with empty list
    grid = []
    print("Starting with empty list: []")
    
    # Append rows one at a time
    print("\nAppending rows:")
    grid.append([1, 2, 3])
    print(f"After append: {grid}")
    
    grid.append([4, 5, 6])
    print(f"After append: {grid}")
    
    grid.append([7, 8, 9])
    print(f"After append: {grid}")
    
    # Append element to specific row
    print("\nAppending element to row 1:")
    grid[1].append(10)
    print_grid(grid)
    
    # Build triangle structure by appending
    print("\nBuilding a triangle by appending:")
    triangle = []
    for i in range(1, 6):
        row = list(range(1, i + 1))
        triangle.append(row)
    
    for row in triangle:
        print(f"  {row}")


def demonstrate_dimensions():
    """
    Show how to work with dimensions of 2-D lists.
    """
    print("\n=== Working with Dimensions ===\n")
    
    # Rectangular grid
    rect_grid = [[1, 2, 3, 4] for _ in range(3)]
    print("Rectangular grid:")
    print_grid(rect_grid)
    print(f"Dimensions: {len(rect_grid)} rows × {len(rect_grid[0])} columns")
    print(f"Total elements: {len(rect_grid) * len(rect_grid[0])}")
    
    # Jagged grid
    jagged_grid = [[1], [2, 3], [4, 5, 6]]
    print("\nJagged grid:")
    print_grid(jagged_grid)
    print(f"Number of rows: {len(jagged_grid)}")
    print("Column counts per row:")
    for i, row in enumerate(jagged_grid):
        print(f"  Row {i}: {len(row)} columns")
    
    # Get total elements in jagged grid
    total = sum(len(row) for row in jagged_grid)
    print(f"Total elements: {total}")


def transpose_grid(grid):
    """
    Transpose a rectangular grid (swap rows and columns).
    
    Args:
        grid: A rectangular 2-D list
    
    Returns:
        Transposed grid
    
    Example:
        >>> transpose_grid([[1, 2, 3], [4, 5, 6]])
        [[1, 4], [2, 5], [3, 6]]
    """
    if not grid:
        return []
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Create transposed grid
    transposed = [[grid[i][j] for i in range(rows)] for j in range(cols)]
    return transposed


def demonstrate_transpose():
    """
    Demonstrate transposing a grid.
    """
    print("\n=== Transposing a Grid ===\n")
    
    original = [
        [1, 2, 3, 4],
        [5, 6, 7, 8]
    ]
    
    print("Original grid (2×4):")
    print_grid(original)
    
    transposed = transpose_grid(original)
    
    print("\nTransposed grid (4×2):")
    print_grid(transposed)


def create_pascal_triangle(n):
    """
    Create Pascal's triangle with n rows.
    
    This is a classic example of a jagged 2-D list.
    
    Args:
        n: Number of rows
    
    Returns:
        Pascal's triangle as a jagged list
    """
    if n == 0:
        return []
    
    triangle = [[1]]  # First row
    
    for i in range(1, n):
        prev_row = triangle[i - 1]
        new_row = [1]  # Start with 1
        
        # Middle elements are sum of two above
        for j in range(len(prev_row) - 1):
            new_row.append(prev_row[j] + prev_row[j + 1])
        
        new_row.append(1)  # End with 1
        triangle.append(new_row)
    
    return triangle


def demonstrate_pascal_triangle():
    """
    Demonstrate Pascal's triangle as a jagged list.
    """
    print("\n=== Pascal's Triangle (Jagged List) ===\n")
    
    triangle = create_pascal_triangle(7)
    
    # Print with nice formatting
    for i, row in enumerate(triangle):
        spaces = ' ' * (7 - i) * 2
        row_str = '   '.join(str(x).center(3) for x in row)
        print(f"{spaces}{row_str}")


def print_grid(grid):
    """
    Pretty print a 2-D grid.
    
    Args:
        grid: 2-D list to print
    """
    for row in grid:
        print('  ', row)


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("=" * 70)
    print("ROWS AND COLUMNS - Working with 2-D Lists")
    print("Programming for Lovers in Python - Chapter 3")
    print("=" * 70)
    
    # Basic access patterns
    demonstrate_row_access()
    demonstrate_column_access()
    demonstrate_element_access()
    
    # Modification
    demonstrate_row_modification()
    demonstrate_column_modification()
    
    # Non-rectangular lists
    demonstrate_non_rectangular_lists()
    
    # Appending
    demonstrate_appending()
    
    # Dimensions
    demonstrate_dimensions()
    
    # Transpose
    demonstrate_transpose()
    
    # Pascal's triangle
    demonstrate_pascal_triangle()
    
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS:")
    print("=" * 70)
    print("1. Rows are easy: grid[i] gives you row i")
    print("2. Columns need comprehension: [row[j] for row in grid]")
    print("3. Access syntax: grid[row][col] - row comes first!")
    print("4. Lists can be jagged (non-rectangular)")
    print("5. Use len(grid) for row count, len(grid[i]) for row i's length")
    print("6. Can append to rows: grid[i].append(value)")
    print("7. Can append rows: grid.append(new_row)")
    print("=" * 70)


if __name__ == "__main__":
    main()
