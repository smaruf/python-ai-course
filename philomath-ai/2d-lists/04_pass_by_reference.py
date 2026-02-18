"""
Pass by Reference - Understanding Mutable Objects
==================================================

Understanding how Python handles function arguments is crucial for working with lists.
Lists are mutable objects and are passed by reference, not by value.
This has important implications for how functions modify data.

Learning Objectives:
- Understand pass by reference vs pass by value
- Recognize when functions modify original lists
- Learn how to avoid unintended modifications
- Use copying techniques when needed
- Understand the difference between shallow and deep copies
- Debug common issues with mutable default arguments

Key Concepts:
- Python passes objects by reference (actually "pass by object reference")
- Mutable objects (lists, dicts) CAN be modified by functions
- Immutable objects (int, str, tuple) CANNOT be modified
- Changes to mutable parameters affect the original object
- Use copy() or deepcopy() to avoid this behavior
- NEVER use mutable default arguments!
"""

import copy


def demonstrate_basic_pass_by_reference():
    """
    Show how lists are passed by reference to functions.
    """
    print("=== Basic Pass by Reference ===\n")
    
    def modify_list(lst):
        """Modify the list that's passed in."""
        print(f"  Inside function, before: {lst}")
        lst[0] = 999
        lst.append(100)
        print(f"  Inside function, after:  {lst}")
    
    # Create a list
    my_list = [1, 2, 3]
    print(f"Before function call: {my_list}")
    
    # Call function
    modify_list(my_list)
    
    # Check the list
    print(f"After function call:  {my_list}")
    print("\n✓ The original list WAS modified!")
    print("✓ Lists are passed by reference, not by value")


def demonstrate_immutable_vs_mutable():
    """
    Contrast pass by reference behavior for mutable vs immutable types.
    """
    print("\n=== Mutable vs Immutable Objects ===\n")
    
    def try_modify_int(x):
        """Try to modify an integer."""
        print(f"  Inside function, x = {x}")
        x = 999
        print(f"  After assignment, x = {x}")
        return x
    
    def try_modify_list(lst):
        """Modify a list."""
        print(f"  Inside function, lst = {lst}")
        lst[0] = 999
        print(f"  After modification, lst = {lst}")
    
    # Integer (immutable)
    print("With integer (immutable):")
    num = 42
    print(f"Before: num = {num}")
    try_modify_int(num)
    print(f"After:  num = {num}")
    print("✓ Integer was NOT modified - integers are immutable")
    
    # List (mutable)
    print("\nWith list (mutable):")
    my_list = [1, 2, 3]
    print(f"Before: my_list = {my_list}")
    try_modify_list(my_list)
    print(f"After:  my_list = {my_list}")
    print("✓ List WAS modified - lists are mutable")


def demonstrate_2d_list_reference():
    """
    Show how 2-D lists are also passed by reference.
    """
    print("\n=== 2-D Lists and Pass by Reference ===\n")
    
    def modify_grid(grid):
        """Modify a 2-D list."""
        grid[0][0] = 'X'
        grid[1][1] = 'X'
        grid[2][2] = 'X'
    
    # Create a 3x3 grid
    grid = [['-' for _ in range(3)] for _ in range(3)]
    
    print("Before function call:")
    print_grid(grid)
    
    modify_grid(grid)
    
    print("\nAfter function call:")
    print_grid(grid)
    print("\n✓ The original 2-D list was modified!")


def demonstrate_reassignment_vs_modification():
    """
    Show the difference between reassigning a variable and modifying its contents.
    """
    print("\n=== Reassignment vs Modification ===\n")
    
    def reassign_list(lst):
        """Try to reassign the list parameter."""
        print(f"  Inside function, before: lst = {lst}")
        lst = [100, 200, 300]  # This creates a NEW local variable!
        print(f"  Inside function, after:  lst = {lst}")
    
    def modify_list_contents(lst):
        """Modify the contents of the list."""
        print(f"  Inside function, before: lst = {lst}")
        lst[0] = 100
        lst[1] = 200
        lst[2] = 300
        print(f"  Inside function, after:  lst = {lst}")
    
    # Test reassignment
    print("Reassignment (creates new local variable):")
    list1 = [1, 2, 3]
    print(f"Before: list1 = {list1}")
    reassign_list(list1)
    print(f"After:  list1 = {list1}")
    print("✗ Original list was NOT modified")
    
    # Test modification
    print("\nModification (changes original list):")
    list2 = [1, 2, 3]
    print(f"Before: list2 = {list2}")
    modify_list_contents(list2)
    print(f"After:  list2 = {list2}")
    print("✓ Original list WAS modified")


def demonstrate_shallow_copy():
    """
    Show how to use shallow copy to avoid modifying the original list.
    """
    print("\n=== Shallow Copy ===\n")
    
    def modify_list(lst):
        """Modify a list."""
        lst[0] = 999
        lst.append(100)
    
    # Original list
    original = [1, 2, 3, 4, 5]
    print(f"Original list: {original}")
    
    # Create a shallow copy
    copied = original.copy()  # or copied = original[:]
    print(f"Copied list:   {copied}")
    
    # Modify the copy
    modify_list(copied)
    
    print(f"\nAfter modifying copy:")
    print(f"Original list: {original}")
    print(f"Copied list:   {copied}")
    print("\n✓ Original was NOT modified!")


def demonstrate_shallow_vs_deep_copy():
    """
    Show the difference between shallow and deep copy for nested lists.
    """
    print("\n=== Shallow Copy vs Deep Copy (Nested Lists) ===\n")
    
    # Original 2-D list
    original = [[1, 2], [3, 4], [5, 6]]
    print("Original 2-D list:")
    print_grid(original)
    
    # Shallow copy
    shallow = original.copy()
    print("\nModifying shallow copy[0][0] = 999:")
    shallow[0][0] = 999
    print("Original:")
    print_grid(original)
    print("Shallow copy:")
    print_grid(shallow)
    print("⚠️ BOTH were modified! Shallow copy shares inner lists")
    
    # Reset
    original = [[1, 2], [3, 4], [5, 6]]
    
    # Deep copy
    deep = copy.deepcopy(original)
    print("\nModifying deep copy[0][0] = 999:")
    deep[0][0] = 999
    print("Original:")
    print_grid(original)
    print("Deep copy:")
    print_grid(deep)
    print("✓ Only deep copy was modified!")


def demonstrate_mutable_default_argument_bug():
    """
    Show the dangerous bug with mutable default arguments.
    
    This is one of the most common Python pitfalls!
    """
    print("\n=== Mutable Default Argument BUG ===\n")
    
    def append_to_list_buggy(item, lst=[]):  # BUG!
        """BUGGY: Default argument is mutable."""
        lst.append(item)
        return lst
    
    print("⚠️ BUGGY version with mutable default:")
    result1 = append_to_list_buggy(1)
    print(f"First call with 1:  {result1}")
    
    result2 = append_to_list_buggy(2)
    print(f"Second call with 2: {result2}")
    
    result3 = append_to_list_buggy(3)
    print(f"Third call with 3:  {result3}")
    
    print("❌ BUG: Default list is shared across calls!")
    
    # Correct version
    def append_to_list_correct(item, lst=None):
        """CORRECT: Use None as default and create new list if needed."""
        if lst is None:
            lst = []
        lst.append(item)
        return lst
    
    print("\n✓ CORRECT version with None default:")
    result1 = append_to_list_correct(1)
    print(f"First call with 1:  {result1}")
    
    result2 = append_to_list_correct(2)
    print(f"Second call with 2: {result2}")
    
    result3 = append_to_list_correct(3)
    print(f"Third call with 3:  {result3}")
    
    print("✓ Each call gets a fresh list!")


def demonstrate_practical_use_case():
    """
    Show a practical example where pass by reference is useful.
    """
    print("\n=== Practical Use Case: Initializing a Grid ===\n")
    
    def initialize_grid(grid, value=0):
        """
        Initialize all cells in a grid to a given value.
        
        This modifies the grid in place (efficient).
        """
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                grid[i][j] = value
    
    # Create a grid
    grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    
    print("Before initialization:")
    print_grid(grid)
    
    # Initialize to zeros
    initialize_grid(grid, 0)
    
    print("\nAfter initialize_grid(grid, 0):")
    print_grid(grid)
    print("\n✓ Function modified the original grid (efficient!)")


def demonstrate_returning_modified_list():
    """
    Show different approaches to function design with lists.
    """
    print("\n=== Function Design Patterns ===\n")
    
    # Pattern 1: Modify in place (no return)
    def double_in_place(lst):
        """Double each element in place."""
        for i in range(len(lst)):
            lst[i] *= 2
    
    # Pattern 2: Return new list (original unchanged)
    def double_copy(lst):
        """Return a new list with doubled elements."""
        return [x * 2 for x in lst]
    
    # Pattern 3: Modify in place AND return (common pattern)
    def double_with_return(lst):
        """Double elements in place and return the list."""
        for i in range(len(lst)):
            lst[i] *= 2
        return lst
    
    # Test Pattern 1
    print("Pattern 1: Modify in place (no return)")
    list1 = [1, 2, 3, 4]
    print(f"Before: {list1}")
    double_in_place(list1)
    print(f"After:  {list1}")
    
    # Test Pattern 2
    print("\nPattern 2: Return new list")
    list2 = [1, 2, 3, 4]
    print(f"Before: {list2}")
    result = double_copy(list2)
    print(f"After:  {list2} (original unchanged)")
    print(f"Result: {result}")
    
    # Test Pattern 3
    print("\nPattern 3: Modify and return")
    list3 = [1, 2, 3, 4]
    print(f"Before: {list3}")
    result = double_with_return(list3)
    print(f"After:  {list3}")
    print(f"Result: {result} (same object)")
    print(f"Same object? {result is list3}")


def print_grid(grid):
    """Pretty print a 2-D grid."""
    for row in grid:
        print(f"  {row}")


def main():
    """
    Main demonstration function showing all concepts.
    """
    print("=" * 70)
    print("PASS BY REFERENCE - Understanding Mutable Objects")
    print("Programming for Lovers in Python - Chapter 3")
    print("=" * 70)
    
    # Basic pass by reference
    demonstrate_basic_pass_by_reference()
    
    # Mutable vs immutable
    demonstrate_immutable_vs_mutable()
    
    # 2-D lists
    demonstrate_2d_list_reference()
    
    # Reassignment vs modification
    demonstrate_reassignment_vs_modification()
    
    # Copying
    demonstrate_shallow_copy()
    demonstrate_shallow_vs_deep_copy()
    
    # Mutable default argument bug
    demonstrate_mutable_default_argument_bug()
    
    # Practical examples
    demonstrate_practical_use_case()
    demonstrate_returning_modified_list()
    
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS:")
    print("=" * 70)
    print("1. Lists are passed by reference - functions CAN modify them")
    print("2. Reassigning parameter (lst = ...) doesn't affect original")
    print("3. Modifying contents (lst[0] = ...) DOES affect original")
    print("4. Use lst.copy() for shallow copy of 1-D lists")
    print("5. Use copy.deepcopy() for deep copy of nested lists")
    print("6. NEVER use mutable default arguments (lst=[])")
    print("7. Use lst=None and create new list inside function")
    print("=" * 70)


if __name__ == "__main__":
    main()
