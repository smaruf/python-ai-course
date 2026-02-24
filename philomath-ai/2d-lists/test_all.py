"""
Test Suite for 2-D Lists Module
================================

Comprehensive tests for all 2-D list operations and Game of Life.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules - using exec to handle numeric prefixes
def load_module(filename):
    """Load a module from filename."""
    with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
        code = f.read()
    module_dict = {}
    exec(code, module_dict)
    return module_dict


# Load modules
mod_01 = load_module('01_2d_tuples_and_lists.py')
mod_02 = load_module('02_list_comprehensions.py')
mod_03 = load_module('03_rows_and_columns.py')
mod_06 = load_module('06_game_of_life.py')


def test_2d_tuple_creation():
    """Test 2-D tuple creation."""
    print("Testing 2-D tuple creation...", end=' ')
    
    create_2d_tuple = mod_01['create_2d_tuple']
    result = create_2d_tuple(2, 3, 0)
    
    assert result == ((0, 0, 0), (0, 0, 0)), "2-D tuple creation failed"
    assert isinstance(result, tuple), "Result should be a tuple"
    assert isinstance(result[0], tuple), "Inner elements should be tuples"
    
    print("✓ PASSED")


def test_2d_list_wrong():
    """Test that wrong list creation creates shared references."""
    print("Testing wrong 2-D list creation...", end=' ')
    
    create_2d_list_wrong = mod_01['create_2d_list_wrong']
    grid = create_2d_list_wrong(3, 3, 0)
    
    # Modify one cell
    grid[0][0] = 1
    
    # All rows should be affected (this is the bug!)
    assert grid[0][0] == 1, "First row should be modified"
    assert grid[1][0] == 1, "Second row should also be modified (bug)"
    assert grid[2][0] == 1, "Third row should also be modified (bug)"
    
    # All rows should be the same object
    assert id(grid[0]) == id(grid[1]) == id(grid[2]), "All rows should be same object"
    
    print("✓ PASSED (bug demonstrated)")


def test_2d_list_correct():
    """Test correct 2-D list creation."""
    print("Testing correct 2-D list creation...", end=' ')
    
    create_2d_list_correct = mod_01['create_2d_list_correct']
    grid = create_2d_list_correct(3, 3, 0)
    
    # Modify one cell
    grid[0][0] = 1
    
    # Only first row should be affected
    assert grid[0][0] == 1, "First row should be modified"
    assert grid[1][0] == 0, "Second row should NOT be modified"
    assert grid[2][0] == 0, "Third row should NOT be modified"
    
    # All rows should be different objects
    assert id(grid[0]) != id(grid[1]), "Rows should be different objects"
    assert id(grid[1]) != id(grid[2]), "Rows should be different objects"
    
    print("✓ PASSED")


def test_list_comprehensions():
    """Test various list comprehension patterns."""
    print("Testing list comprehensions...", end=' ')
    
    create_2d_zeros = mod_02['create_2d_zeros']
    create_2d_identity_matrix = mod_02['create_2d_identity_matrix']
    create_2d_multiplication_table = mod_02['create_2d_multiplication_table']
    
    # Test zeros
    zeros = create_2d_zeros(2, 3)
    assert zeros == [[0, 0, 0], [0, 0, 0]], "Zeros creation failed"
    
    # Test identity matrix
    identity = create_2d_identity_matrix(3)
    assert identity == [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "Identity matrix failed"
    
    # Test multiplication table
    mult = create_2d_multiplication_table(3, 3)
    assert mult[2][2] == 4, "Multiplication table failed"
    assert mult[1][2] == 2, "Multiplication table failed"
    
    print("✓ PASSED")


def test_transpose():
    """Test grid transposition."""
    print("Testing grid transposition...", end=' ')
    
    transpose_grid = mod_03['transpose_grid']
    
    grid = [[1, 2, 3], [4, 5, 6]]
    transposed = transpose_grid(grid)
    
    assert transposed == [[1, 4], [2, 5], [3, 6]], "Transpose failed"
    
    # Test empty grid
    empty = transpose_grid([])
    assert empty == [], "Empty grid transpose failed"
    
    print("✓ PASSED")


def test_pascal_triangle():
    """Test Pascal's triangle generation."""
    print("Testing Pascal's triangle...", end=' ')
    
    create_pascal_triangle = mod_03['create_pascal_triangle']
    
    triangle = create_pascal_triangle(5)
    
    assert len(triangle) == 5, "Should have 5 rows"
    assert triangle[0] == [1], "First row should be [1]"
    assert triangle[4] == [1, 4, 6, 4, 1], "Fifth row should be [1, 4, 6, 4, 1]"
    
    # Test empty
    empty = create_pascal_triangle(0)
    assert empty == [], "Empty triangle failed"
    
    print("✓ PASSED")


def test_game_of_life_neighbors():
    """Test neighbor counting in Game of Life."""
    print("Testing Game of Life neighbor counting...", end=' ')
    
    count_neighbors = mod_06['count_neighbors']
    
    # Create a test grid
    grid = [
        [1, 1, 0],
        [1, 0, 0],
        [0, 0, 0]
    ]
    
    # Test corner cell (0, 0) - should have 2 neighbors
    assert count_neighbors(grid, 0, 0) == 2, "Corner cell neighbor count wrong"
    
    # Test center cell (1, 1) - should have 3 neighbors
    assert count_neighbors(grid, 1, 1) == 3, "Center cell neighbor count wrong"
    
    # Test edge cell with no neighbors
    assert count_neighbors(grid, 2, 2) == 0, "Empty area neighbor count wrong"
    
    print("✓ PASSED")


def test_game_of_life_rules():
    """Test Game of Life rule application."""
    print("Testing Game of Life rules...", end=' ')
    
    apply_rules = mod_06['apply_rules']
    
    # Test birth rule (dead cell with 3 neighbors becomes alive)
    grid = [
        [0, 1, 0],
        [1, 0, 1],
        [0, 0, 0]
    ]
    new_grid = apply_rules(grid)
    assert new_grid[1][1] == 1, "Birth rule failed"
    
    # Test survival rule (live cell with 2-3 neighbors survives)
    grid = [
        [0, 1, 0],
        [1, 1, 0],
        [0, 0, 0]
    ]
    new_grid = apply_rules(grid)
    assert new_grid[1][1] == 1, "Survival rule failed"
    
    # Test death rule (live cell with < 2 neighbors dies)
    grid = [
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0]
    ]
    new_grid = apply_rules(grid)
    assert new_grid[1][1] == 0, "Death rule (underpopulation) failed"
    
    # Test death rule (live cell with > 3 neighbors dies)
    grid = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ]
    new_grid = apply_rules(grid)
    assert new_grid[1][1] == 0, "Death rule (overpopulation) failed"
    
    print("✓ PASSED")


def test_game_of_life_patterns():
    """Test known Game of Life patterns."""
    print("Testing Game of Life patterns...", end=' ')
    
    create_empty_grid = mod_06['create_empty_grid']
    place_pattern = mod_06['place_pattern']
    apply_rules = mod_06['apply_rules']
    create_blinker = mod_06['create_blinker']
    create_block = mod_06['create_block']
    
    # Test block (still life - should never change)
    grid = create_empty_grid(4, 4)
    block = create_block()
    place_pattern(grid, block, 1, 1)
    
    original = [row[:] for row in grid]  # Deep copy
    new_grid = apply_rules(grid)
    
    assert new_grid == original, "Block should be stable"
    
    # Test blinker (period-2 oscillator)
    grid = create_empty_grid(5, 5)
    blinker = create_blinker()
    place_pattern(grid, blinker, 2, 1)
    
    # After 2 generations, should return to original state
    gen1 = apply_rules(grid)
    gen2 = apply_rules(gen1)
    
    assert gen2 == grid, "Blinker should have period 2"
    
    print("✓ PASSED")


def test_count_living_cells():
    """Test counting living cells."""
    print("Testing counting living cells...", end=' ')
    
    count_living_cells = mod_06['count_living_cells']
    
    grid = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1]
    ]
    
    count = count_living_cells(grid)
    assert count == 5, "Living cell count wrong"
    
    # Test empty grid
    empty = [[0, 0], [0, 0]]
    assert count_living_cells(empty) == 0, "Empty grid should have 0 living cells"
    
    # Test full grid
    full = [[1, 1], [1, 1]]
    assert count_living_cells(full) == 4, "Full grid should have 4 living cells"
    
    print("✓ PASSED")


def test_count_neighbors_toroidal():
    """Test toroidal neighbor counting (cells wrap at edges)."""
    print("Testing toroidal neighbor counting...", end=' ')

    count_neighbors_toroidal = mod_06['count_neighbors_toroidal']

    grid = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 1],
    ]

    # Corner (0,0): neighbours include the wrapping cells at row=-1/col=-1
    # Toroidal neighbours of (0,0): (2,2)=1, (0,2)=0, (2,0)=0,
    #   (0,1)=0, (1,0)=0, (1,1)=0, (2,1)=0, (1,2)=0  → 1
    assert count_neighbors_toroidal(grid, 0, 0) == 1, \
        "Toroidal corner (0,0) should see the wrapped cell at (2,2)"

    # A live cell one step away from the corner that wraps
    grid2 = [[0] * 4 for _ in range(4)]
    grid2[0][0] = 1   # top-left corner
    grid2[3][3] = 1   # bottom-right corner (wraps to be a neighbour of (0,0))
    assert count_neighbors_toroidal(grid2, 0, 0) == 1, \
        "Bottom-right cell should be a toroidal neighbour of top-left"

    print("✓ PASSED")


def test_apply_rules_toroidal():
    """Test toroidal rule application – edges wrap so patterns are preserved."""
    print("Testing toroidal rule application...", end=' ')

    apply_rules_toroidal = mod_06['apply_rules_toroidal']
    create_empty_grid = mod_06['create_empty_grid']
    place_pattern = mod_06['place_pattern']
    create_blinker = mod_06['create_blinker']
    count_living_cells = mod_06['count_living_cells']

    # Blinker in a toroidal grid must still oscillate with period 2
    grid = create_empty_grid(5, 5)
    place_pattern(grid, create_blinker(), 2, 1)
    gen1 = apply_rules_toroidal(grid)
    gen2 = apply_rules_toroidal(gen1)
    assert gen2 == grid, "Blinker should have period 2 on a toroidal grid"

    # A glider placed at the bottom-right edge should survive (not die at boundary)
    size = 12
    torus = create_empty_grid(size, size)
    place_pattern(torus, [[0, 1, 0], [0, 0, 1], [1, 1, 1]], size - 4, size - 4)
    initial_alive = count_living_cells(torus)
    for _ in range(4):
        torus = apply_rules_toroidal(torus)
    # A glider keeps 5 alive cells as it moves; on a toroidal grid it wraps
    assert count_living_cells(torus) == initial_alive, \
        "Glider should maintain its cell count on a toroidal grid"

    print("✓ PASSED")


def test_create_random_grid():
    """Test random grid initialisation."""
    print("Testing random grid creation...", end=' ')

    create_random_grid = mod_06['create_random_grid']

    # Dimensions are correct
    grid = create_random_grid(6, 8, density=0.5, seed=0)
    assert len(grid) == 6, "Random grid should have 6 rows"
    assert len(grid[0]) == 8, "Random grid should have 8 columns"

    # All values are 0 or 1
    for row in grid:
        for cell in row:
            assert cell in (0, 1), f"Cell value {cell} must be 0 or 1"

    # Seeded calls are reproducible
    grid_a = create_random_grid(5, 5, density=0.4, seed=42)
    grid_b = create_random_grid(5, 5, density=0.4, seed=42)
    assert grid_a == grid_b, "Same seed must produce identical grids"

    # Different seeds give different grids (probabilistically certain)
    grid_c = create_random_grid(5, 5, density=0.4, seed=1)
    assert grid_a != grid_c, "Different seeds should (almost certainly) differ"

    # density=0.0 → all dead; density=1.0 → all alive
    all_dead = create_random_grid(4, 4, density=0.0)
    assert all(cell == 0 for row in all_dead for cell in row), \
        "density=0.0 should produce all-dead grid"
    all_alive = create_random_grid(4, 4, density=1.0)
    assert all(cell == 1 for row in all_alive for cell in row), \
        "density=1.0 should produce all-alive grid"

    print("✓ PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("RUNNING TESTS FOR 2-D LISTS MODULE")
    print("=" * 70)
    print()
    
    tests = [
        test_2d_tuple_creation,
        test_2d_list_wrong,
        test_2d_list_correct,
        test_list_comprehensions,
        test_transpose,
        test_pascal_triangle,
        test_game_of_life_neighbors,
        test_game_of_life_rules,
        test_game_of_life_patterns,
        test_count_living_cells,
        test_count_neighbors_toroidal,
        test_apply_rules_toroidal,
        test_create_random_grid,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
