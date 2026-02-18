"""
2-D Tuples and Lists
====================

Understanding multi-dimensional data structures is fundamental to many programming tasks.
In this module, we explore how to work with 2-D tuples and lists in Python,
and learn the critical difference between correct and incorrect list initialization.

Learning Objectives:
- Understand 2-D tuples (immutable nested structures)
- Create 2-D lists correctly
- Avoid the common pitfall of shallow copying
- Recognize when to use tuples vs lists
- Debug issues with mutable vs immutable structures

Key Concepts:
- Tuples are immutable - once created, elements cannot be changed
- Lists are mutable - elements can be modified after creation
- 2-D structures contain nested sequences (lists within lists, tuples within tuples)
- Shallow vs deep copying affects how changes propagate
- The * operator with lists creates references, not copies!
"""


def create_2d_tuple(rows, cols, default_value=0):
    """
    Create a 2-D tuple (immutable nested structure).
    
    Tuples are immutable, so once created they cannot be modified.
    This is useful when you want to ensure data integrity.
    
    Time Complexity: O(rows * cols)
    Space Complexity: O(rows * cols)
    
    Args:
        rows: Number of rows
        cols: Number of columns
        default_value: Value to fill the tuple with
    
    Returns:
        A 2-D tuple of specified dimensions
    
    Example:
        >>> create_2d_tuple(2, 3, 0)
        ((0, 0, 0), (0, 0, 0))
    """
    return tuple(tuple(default_value for _ in range(cols)) for _ in range(rows))


def create_2d_list_wrong(rows, cols, default_value=0):
    """
    WRONG WAY: Create a 2-D list using * operator.
    
    ⚠️ WARNING: This is a common mistake! ⚠️
    
    The * operator creates references to the SAME inner list.
    Modifying one row will modify ALL rows!
    
    Time Complexity: O(cols + rows)  # Fast but buggy!
    Space Complexity: O(rows + cols)  # Shares memory incorrectly
    
    Args:
        rows: Number of rows
        cols: Number of columns
        default_value: Value to fill the list with
    
    Returns:
        A 2-D list (but with shared row references - BUG!)
    
    Example:
        >>> grid = create_2d_list_wrong(3, 3, 0)
        >>> grid[0][0] = 1
        >>> print(grid)
        [[1, 0, 0], [1, 0, 0], [1, 0, 0]]  # All rows changed!
    """
    # This creates one inner list and replicates the reference
    return [[default_value] * cols] * rows


def create_2d_list_correct(rows, cols, default_value=0):
    """
    CORRECT WAY: Create a 2-D list using list comprehension.
    
    ✅ This is the right way! ✅
    
    Each row is created independently, so modifying one row
    does not affect other rows.
    
    Time Complexity: O(rows * cols)
    Space Complexity: O(rows * cols)
    
    Args:
        rows: Number of rows
        cols: Number of columns
        default_value: Value to fill the list with
    
    Returns:
        A properly constructed 2-D list
    
    Example:
        >>> grid = create_2d_list_correct(3, 3, 0)
        >>> grid[0][0] = 1
        >>> print(grid)
        [[1, 0, 0], [0, 0, 0], [0, 0, 0]]  # Only first row changed!
    """
    return [[default_value for _ in range(cols)] for _ in range(rows)]


def demonstrate_tuple_immutability():
    """
    Demonstrate that tuples cannot be modified after creation.
    
    This shows the key difference between tuples and lists.
    """
    print("=== Tuple Immutability Demo ===\n")
    
    # Create a 2-D tuple
    tuple_2d = ((1, 2, 3), (4, 5, 6))
    print(f"Original tuple: {tuple_2d}")
    
    # Try to modify (this will fail)
    try:
        tuple_2d[0][0] = 999
        print("✗ Modification succeeded (this shouldn't happen!)")
    except TypeError as e:
        print(f"✓ Cannot modify tuple: {e}")
    
    # Tuples are good for constant data
    print("\n✓ Tuples are perfect for data that shouldn't change!")
    print("  Examples: coordinates, RGB colors, mathematical constants")


def demonstrate_wrong_list_creation():
    """
    Demonstrate the bug that occurs when using * operator for 2-D lists.
    
    This is one of the most common mistakes in Python!
    """
    print("\n=== WRONG Way to Create 2-D List ===\n")
    
    # Create a 3x3 grid the WRONG way
    grid = [[0] * 3] * 3
    print(f"Created grid (wrong way): {grid}")
    print("Grid appears correct: [[0, 0, 0], [0, 0, 0], [0, 0, 0]]")
    
    # Try to modify just one cell
    print("\nTrying to set grid[0][0] = 1...")
    grid[0][0] = 1
    
    print(f"Result: {grid}")
    print("❌ BUG: All rows changed, not just the first!")
    print("❌ This is because all rows reference the SAME list object")
    
    # Show that all rows are the same object
    print("\nProof - checking object identities:")
    print(f"  id(grid[0]): {id(grid[0])}")
    print(f"  id(grid[1]): {id(grid[1])}")
    print(f"  id(grid[2]): {id(grid[2])}")
    print(f"  All same? {id(grid[0]) == id(grid[1]) == id(grid[2])}")


def demonstrate_correct_list_creation():
    """
    Demonstrate the correct way to create 2-D lists using list comprehension.
    """
    print("\n=== CORRECT Way to Create 2-D List ===\n")
    
    # Create a 3x3 grid the CORRECT way
    grid = [[0 for _ in range(3)] for _ in range(3)]
    print(f"Created grid (correct way): {grid}")
    
    # Try to modify just one cell
    print("\nSetting grid[0][0] = 1...")
    grid[0][0] = 1
    
    print(f"Result: {grid}")
    print("✓ CORRECT: Only the first row changed!")
    print("✓ Each row is an independent list object")
    
    # Show that all rows are different objects
    print("\nProof - checking object identities:")
    print(f"  id(grid[0]): {id(grid[0])}")
    print(f"  id(grid[1]): {id(grid[1])}")
    print(f"  id(grid[2]): {id(grid[2])}")
    print(f"  All different? {id(grid[0]) != id(grid[1]) and id(grid[1]) != id(grid[2])}")


def create_face_pattern():
    """
    Create a simple smiley face pattern using a 2-D list.
    
    This demonstrates a practical use of 2-D lists for visual patterns.
    """
    print("\n=== Drawing a Face with 2-D List ===\n")
    
    # Create a 7x7 grid for a simple face
    face = [[' ' for _ in range(7)] for _ in range(7)]
    
    # Draw eyes (row 2, cols 2 and 5)
    face[2][2] = 'O'
    face[2][5] = 'O'
    
    # Draw nose (row 3, col 3)
    face[3][3] = '^'
    
    # Draw smile (row 5)
    face[5][1] = '\\'
    face[5][2] = '_'
    face[5][3] = '_'
    face[5][4] = '_'
    face[5][5] = '/'
    
    # Print the face
    print("Here's a simple face:")
    for row in face:
        print(''.join(row))
    
    return face


def access_and_modify_demo():
    """
    Demonstrate how to access and modify individual elements in a 2-D list.
    """
    print("\n=== Accessing and Modifying 2-D List Elements ===\n")
    
    # Create a 3x4 grid with different values
    grid = [[i * 10 + j for j in range(4)] for i in range(3)]
    print("Initial grid:")
    print_2d_list(grid)
    
    # Access individual elements
    print(f"\nAccessing grid[1][2]: {grid[1][2]}")
    print(f"Accessing grid[0][3]: {grid[0][3]}")
    
    # Modify elements
    print("\nModifying grid[1][2] = 99")
    grid[1][2] = 99
    print_2d_list(grid)
    
    # Access entire rows
    print(f"\nAccessing entire row 0: {grid[0]}")
    print(f"Accessing entire row 2: {grid[2]}")


def print_2d_list(grid):
    """
    Pretty print a 2-D list with proper formatting.
    
    Args:
        grid: A 2-D list to print
    """
    for row in grid:
        print(row)


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("=" * 60)
    print("2-D TUPLES AND LISTS - Programming for Lovers in Python")
    print("Chapter 3: Multi-Dimensional Data Structures")
    print("=" * 60)
    
    # Demonstrate tuples
    demonstrate_tuple_immutability()
    
    # Show the WRONG way (common mistake)
    demonstrate_wrong_list_creation()
    
    # Show the CORRECT way
    demonstrate_correct_list_creation()
    
    # Practical example: drawing a face
    create_face_pattern()
    
    # Show access and modification
    access_and_modify_demo()
    
    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS:")
    print("=" * 60)
    print("1. Use tuples for immutable data (can't be changed)")
    print("2. Use lists for mutable data (can be changed)")
    print("3. NEVER use [[0] * cols] * rows - creates references!")
    print("4. ALWAYS use [[0 for _ in range(cols)] for _ in range(rows)]")
    print("5. Remember: grid[row][column] - row comes first!")
    print("=" * 60)


if __name__ == "__main__":
    main()
