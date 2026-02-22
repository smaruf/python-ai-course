"""
Test Suite for Pygame Graphics Module
=======================================

Tests for pure-logic functions that don't require a display.
Pygame rendering functions are excluded from testing as they
require an active display surface.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_module(filename):
    """Load a module from filename using exec."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'r') as f:
        code = f.read()
    module_dict = {}
    exec(code, module_dict)
    return module_dict


# Load modules (pure logic only - no pygame import needed)
mod_01 = load_module('01_pygame_basics.py')
mod_02 = load_module('02_rgb_colors.py')
mod_03 = load_module('03_snowperson.py')
mod_04 = load_module('04_game_of_life_visualization.py')


# ──────────────────────────────────────────────
# Tests for 01_pygame_basics.py
# ──────────────────────────────────────────────

def test_window_dimensions():
    """Test that window dimensions are reasonable positive integers."""
    print("Testing window dimensions...", end=' ')
    w, h = mod_01['get_window_dimensions']()
    assert w > 0, "Window width must be positive"
    assert h > 0, "Window height must be positive"
    assert isinstance(w, int), "Width must be an integer"
    assert isinstance(h, int), "Height must be an integer"
    print("✓ PASSED")


def test_rect_params():
    """Test that rectangle parameters are valid."""
    print("Testing rectangle parameters...", end=' ')
    x, y, w, h = mod_01['get_rect_params']()
    assert w > 0, "Rectangle width must be positive"
    assert h > 0, "Rectangle height must be positive"
    assert x >= 0, "Rectangle x must be non-negative"
    assert y >= 0, "Rectangle y must be non-negative"
    print("✓ PASSED")


def test_point_in_rect():
    """Test point-in-rectangle detection."""
    print("Testing point in rectangle...", end=' ')
    is_in = mod_01['is_point_in_rect']
    # Center of the rectangle should be inside
    assert is_in(250, 250, 100, 100, 300, 300), "Center point should be inside"
    # Corners should be inside
    assert is_in(100, 100, 100, 100, 300, 300), "Top-left corner should be inside"
    assert is_in(400, 400, 100, 100, 300, 300), "Bottom-right corner should be inside"
    # Point outside the rectangle
    assert not is_in(50, 50, 100, 100, 300, 300), "Point at (50,50) should be outside"
    assert not is_in(500, 250, 100, 100, 300, 300), "Point far right should be outside"
    print("✓ PASSED")


def test_rect_center():
    """Test rectangle center calculation."""
    print("Testing rectangle center...", end=' ')
    get_center = mod_01['get_rect_center']
    cx, cy = get_center(100, 100, 300, 300)
    assert cx == 250, f"Center x should be 250, got {cx}"
    assert cy == 250, f"Center y should be 250, got {cy}"
    # Zero-size rectangle
    cx2, cy2 = get_center(50, 75, 0, 0)
    assert cx2 == 50, "Zero-width rect center x should equal x"
    assert cy2 == 75, "Zero-height rect center y should equal y"
    print("✓ PASSED")


# ──────────────────────────────────────────────
# Tests for 02_rgb_colors.py
# ──────────────────────────────────────────────

def test_color_constants():
    """Test that color constants are valid RGB tuples."""
    print("Testing color constants...", end=' ')
    for name in ('BLACK', 'WHITE', 'RED', 'GREEN', 'BLUE',
                 'YELLOW', 'CYAN', 'MAGENTA'):
        color = mod_02[name]
        assert len(color) == 3, f"{name} must have 3 components"
        for component in color:
            assert 0 <= component <= 255, f"{name} component {component} out of range"
    print("✓ PASSED")


def test_known_color_values():
    """Test that well-known colors have the right RGB values."""
    print("Testing known color values...", end=' ')
    assert mod_02['BLACK'] == (0, 0, 0), "Black should be (0,0,0)"
    assert mod_02['WHITE'] == (255, 255, 255), "White should be (255,255,255)"
    assert mod_02['RED'] == (255, 0, 0), "Red should be (255,0,0)"
    assert mod_02['GREEN'] == (0, 255, 0), "Green should be (0,255,0)"
    assert mod_02['BLUE'] == (0, 0, 255), "Blue should be (0,0,255)"
    assert mod_02['YELLOW'] == (255, 255, 0), "Yellow should be (255,255,0)"
    print("✓ PASSED")


def test_mix_colors():
    """Test color mixing."""
    print("Testing color mixing...", end=' ')
    mix = mod_02['mix_colors']
    WHITE = mod_02['WHITE']
    BLACK = mod_02['BLACK']
    RED = mod_02['RED']
    BLUE = mod_02['BLUE']

    # 50/50 mix of black and white → gray
    gray = mix(WHITE, BLACK, 0.5)
    assert gray == (127, 127, 127), f"50/50 white+black should be gray, got {gray}"

    # Full color1 → same as color1
    result = mix(RED, BLUE, 1.0)
    assert result == RED, "ratio=1.0 should return color1"

    # Full color2 → same as color2
    result = mix(RED, BLUE, 0.0)
    assert result == BLUE, "ratio=0.0 should return color2"

    print("✓ PASSED")


def test_darken_color():
    """Test color darkening."""
    print("Testing color darkening...", end=' ')
    darken = mod_02['darken_color']
    WHITE = mod_02['WHITE']
    RED = mod_02['RED']

    dark = darken(WHITE, 0.5)
    assert dark == (127, 127, 127), "Half-darkened white should be mid-gray"

    full_dark = darken(RED, 0.0)
    assert full_dark == (0, 0, 0), "Factor 0.0 should produce black"

    original = darken(RED, 1.0)
    assert original == RED, "Factor 1.0 should return original color"

    print("✓ PASSED")


def test_invert_color():
    """Test color inversion."""
    print("Testing color inversion...", end=' ')
    invert = mod_02['invert_color']
    BLACK = mod_02['BLACK']
    WHITE = mod_02['WHITE']
    RED = mod_02['RED']

    assert invert(BLACK) == WHITE, "Inverted black should be white"
    assert invert(WHITE) == BLACK, "Inverted white should be black"
    assert invert(RED) == (0, 255, 255), "Inverted red should be cyan"

    print("✓ PASSED")


def test_color_brightness():
    """Test brightness calculation."""
    print("Testing color brightness...", end=' ')
    brightness = mod_02['color_brightness']
    BLACK = mod_02['BLACK']
    WHITE = mod_02['WHITE']

    assert brightness(BLACK) == 0.0, "Black brightness should be 0"
    assert brightness(WHITE) == 255.0, "White brightness should be 255.0"

    # White should be brighter than black
    assert brightness(WHITE) > brightness(BLACK), "White should be brighter than black"

    print("✓ PASSED")


def test_is_light_color():
    """Test light vs dark color detection."""
    print("Testing light/dark color detection...", end=' ')
    is_light = mod_02['is_light_color']
    WHITE = mod_02['WHITE']
    BLACK = mod_02['BLACK']
    YELLOW = mod_02['YELLOW']
    BLUE = mod_02['BLUE']

    assert is_light(WHITE), "White should be light"
    assert not is_light(BLACK), "Black should not be light"
    assert is_light(YELLOW), "Yellow should be light"
    assert not is_light(BLUE), "Pure blue should not be light"

    print("✓ PASSED")


def test_create_gradient():
    """Test color gradient creation."""
    print("Testing color gradient...", end=' ')
    gradient = mod_02['create_gradient']
    BLACK = mod_02['BLACK']
    WHITE = mod_02['WHITE']

    # Single step gradient
    single = gradient(BLACK, WHITE, 1)
    assert len(single) == 1, "Single step gradient should have 1 color"

    # Multi-step gradient
    steps = gradient(BLACK, WHITE, 5)
    assert len(steps) == 5, "5-step gradient should have 5 colors"
    assert steps[0] == BLACK, "First color should be BLACK"
    assert steps[-1] == WHITE, "Last color should be WHITE"

    # Each step should be getting lighter
    brightness = mod_02['color_brightness']
    for i in range(len(steps) - 1):
        assert brightness(steps[i]) <= brightness(steps[i + 1]), \
            f"Gradient step {i} should be darker than step {i+1}"

    print("✓ PASSED")


# ──────────────────────────────────────────────
# Tests for 03_snowperson.py
# ──────────────────────────────────────────────

def test_snowperson_parts():
    """Test snowperson body part positions."""
    print("Testing snowperson part positions...", end=' ')
    get_parts = mod_03['get_snowperson_parts']

    cx, cy = 250, 500
    parts = get_parts(cx, cy)

    assert 'bottom' in parts, "Parts should include 'bottom'"
    assert 'middle' in parts, "Parts should include 'middle'"
    assert 'head' in parts, "Parts should include 'head'"

    # Bottom is at the given position
    assert parts['bottom'] == (cx, cy), "Bottom should be at given position"

    # Middle is above bottom
    assert parts['middle'][1] < parts['bottom'][1], "Middle should be above bottom"

    # Head is above middle
    assert parts['head'][1] < parts['middle'][1], "Head should be above middle"

    # All parts share the same x-coordinate (centered)
    assert parts['bottom'][0] == cx, "Bottom should be centered"
    assert parts['middle'][0] == cx, "Middle should be centered"
    assert parts['head'][0] == cx, "Head should be centered"

    print("✓ PASSED")


def test_eye_positions():
    """Test eye position calculation."""
    print("Testing eye positions...", end=' ')
    get_eyes = mod_03['get_eye_positions']

    head_cx, head_cy = 250, 200
    left_eye, right_eye = get_eyes(head_cx, head_cy)

    # Eyes should be above the head center
    assert left_eye[1] < head_cy, "Eyes should be above the head center"
    assert right_eye[1] < head_cy, "Eyes should be above the head center"

    # Eyes should be symmetric around center x
    assert left_eye[0] < head_cx, "Left eye should be left of center"
    assert right_eye[0] > head_cx, "Right eye should be right of center"

    # Eyes should be at the same height
    assert left_eye[1] == right_eye[1], "Both eyes should be at the same height"

    # Symmetric offsets
    assert head_cx - left_eye[0] == right_eye[0] - head_cx, \
        "Eyes should be symmetric"

    print("✓ PASSED")


def test_nose_position():
    """Test nose position calculation."""
    print("Testing nose position...", end=' ')
    get_nose = mod_03['get_nose_position']

    head_cx, head_cy = 250, 200
    nose = get_nose(head_cx, head_cy)

    # Nose should be below the head center (in pygame, y increases downward)
    assert nose[1] >= head_cy, "Nose should be at or below head center"

    # Nose should be horizontally centered
    assert nose[0] == head_cx, "Nose should be centered horizontally"

    print("✓ PASSED")


def test_mouth_rect():
    """Test mouth rectangle calculation."""
    print("Testing mouth rectangle...", end=' ')
    get_mouth = mod_03['get_mouth_rect']

    head_cx, head_cy = 250, 200
    x, y, w, h = get_mouth(head_cx, head_cy)

    # Mouth should be below the nose (below center)
    assert y > head_cy, "Mouth should be below head center"

    # Mouth should be horizontally centered
    assert x + w // 2 == head_cx, "Mouth should be centered horizontally"

    # Mouth should have positive dimensions
    assert w > 0, "Mouth width must be positive"
    assert h > 0, "Mouth height must be positive"

    print("✓ PASSED")


def test_eyebrow_rects():
    """Test eyebrow rectangle calculation."""
    print("Testing eyebrow rectangles...", end=' ')
    get_eyebrows = mod_03['get_eyebrow_rects']
    get_eyes = mod_03['get_eye_positions']

    head_cx, head_cy = 250, 200
    left_brow, right_brow = get_eyebrows(head_cx, head_cy)
    left_eye, _ = get_eyes(head_cx, head_cy)

    # Eyebrows should be above the eyes
    assert left_brow[1] < left_eye[1], "Eyebrows should be above the eyes"

    # Both eyebrows at same height
    assert left_brow[1] == right_brow[1], "Both eyebrows should be at same height"

    # Both should have positive dimensions
    assert left_brow[2] > 0, "Eyebrow width must be positive"
    assert left_brow[3] > 0, "Eyebrow height must be positive"

    print("✓ PASSED")


def test_button_positions():
    """Test button position calculation."""
    print("Testing button positions...", end=' ')
    get_buttons = mod_03['get_button_positions']

    middle_cx, middle_cy = 250, 350
    buttons = get_buttons(middle_cx, middle_cy)

    assert len(buttons) == 3, "Should have exactly 3 buttons"

    # All buttons should share the same x (centered)
    for btn in buttons:
        assert btn[0] == middle_cx, "All buttons should be centered"

    # Buttons should be at different y positions
    y_positions = [btn[1] for btn in buttons]
    assert len(set(y_positions)) == 3, "All buttons should be at different heights"

    # Buttons should be in order (top to bottom)
    assert y_positions[0] < y_positions[1] < y_positions[2], \
        "Buttons should be ordered top to bottom"

    print("✓ PASSED")


# ──────────────────────────────────────────────
# Tests for 04_game_of_life_visualization.py
# ──────────────────────────────────────────────

def test_create_empty_board():
    """Test empty board creation."""
    print("Testing empty board creation...", end=' ')
    create_board = mod_04['create_empty_board']

    board = create_board(10, 15)
    assert len(board) == 10, "Board should have 10 rows"
    assert len(board[0]) == 15, "Board should have 15 columns"

    # All cells should be dead (0)
    for row in board:
        for cell in row:
            assert cell == 0, "All cells should be dead initially"

    print("✓ PASSED")


def test_count_neighbors_visualization():
    """Test neighbor counting in the visualization module."""
    print("Testing neighbor counting (visualization)...", end=' ')
    count_neighbors = mod_04['count_neighbors']

    grid = [
        [1, 1, 0],
        [1, 0, 0],
        [0, 0, 0],
    ]

    # Corner cell (0,0) has neighbors: (0,1)=1, (1,0)=1, (1,1)=0 → 2
    assert count_neighbors(grid, 0, 0) == 2, "Corner (0,0) should have 2 neighbors"

    # Center cell (1,1) has neighbors: all cells around it
    assert count_neighbors(grid, 1, 1) == 3, "Center (1,1) should have 3 neighbors"

    # Bottom-right corner has no neighbors
    assert count_neighbors(grid, 2, 2) == 0, "Corner (2,2) should have 0 neighbors"

    print("✓ PASSED")


def test_apply_rules_visualization():
    """Test rule application in the visualization module."""
    print("Testing rule application (visualization)...", end=' ')
    apply_rules = mod_04['apply_rules']

    # Blinker: horizontal → vertical → horizontal
    grid = create_blinker_grid()
    gen1 = apply_rules(grid)
    gen2 = apply_rules(gen1)
    assert gen2 == grid, "Blinker should have period 2"

    # Block: still life (never changes)
    block_grid = create_block_grid()
    new_grid = apply_rules(block_grid)
    assert new_grid == block_grid, "Block should be stable"

    print("✓ PASSED")


def create_blinker_grid():
    """Helper: create a 5x5 grid with a blinker at row 2."""
    create_board = mod_04['create_empty_board']
    grid = create_board(5, 5)
    grid[2][1] = 1
    grid[2][2] = 1
    grid[2][3] = 1
    return grid


def create_block_grid():
    """Helper: create a 4x4 grid with a block at (1,1)."""
    create_board = mod_04['create_empty_board']
    grid = create_board(4, 4)
    grid[1][1] = 1
    grid[1][2] = 1
    grid[2][1] = 1
    grid[2][2] = 1
    return grid


def test_place_r_pentomino():
    """Test placing the R pentomino on the board."""
    print("Testing R pentomino placement...", end=' ')
    create_board = mod_04['create_empty_board']
    place = mod_04['place_r_pentomino']
    count_alive = mod_04['count_alive_cells']

    board = create_board(10, 10)
    place(board, 3, 3)

    # R pentomino has exactly 5 cells
    assert count_alive(board) == 5, "R pentomino should have 5 alive cells"

    # Check specific cells of the R pentomino pattern:
    # .##   → (3,4)=1, (3,5)=1
    # ##.   → (4,3)=1, (4,4)=1
    # .#.   → (5,4)=1
    assert board[3][3] == 0
    assert board[3][4] == 1
    assert board[3][5] == 1
    assert board[4][3] == 1
    assert board[4][4] == 1
    assert board[4][5] == 0
    assert board[5][3] == 0
    assert board[5][4] == 1
    assert board[5][5] == 0

    print("✓ PASSED")


def test_count_alive_cells():
    """Test alive cell counting."""
    print("Testing alive cell counting...", end=' ')
    count_alive = mod_04['count_alive_cells']

    grid = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ]
    assert count_alive(grid) == 5, "Should count 5 alive cells"

    empty = [[0, 0], [0, 0]]
    assert count_alive(empty) == 0, "Empty grid should have 0 alive cells"

    full = [[1, 1], [1, 1]]
    assert count_alive(full) == 4, "Full grid should have 4 alive cells"

    print("✓ PASSED")


def test_cell_to_pixel():
    """Test cell-to-pixel coordinate conversion."""
    print("Testing cell-to-pixel conversion...", end=' ')
    cell_to_pixel = mod_04['cell_to_pixel']
    CELL_SIZE = mod_04['CELL_SIZE']
    BOARD_MARGIN_X = mod_04['BOARD_MARGIN_X']
    BOARD_MARGIN_Y = mod_04['BOARD_MARGIN_Y']

    # Cell (0,0) should be at (margin + half_cell, margin + half_cell)
    px, py = cell_to_pixel(0, 0)
    assert px == BOARD_MARGIN_X + CELL_SIZE // 2, \
        f"Cell (0,0) x should be {BOARD_MARGIN_X + CELL_SIZE // 2}, got {px}"
    assert py == BOARD_MARGIN_Y + CELL_SIZE // 2, \
        f"Cell (0,0) y should be {BOARD_MARGIN_Y + CELL_SIZE // 2}, got {py}"

    # Cell (1,1) should be offset by CELL_SIZE
    px2, py2 = cell_to_pixel(1, 1)
    assert px2 == px + CELL_SIZE, "Cell (1,1) x should be cell (0,0) x + CELL_SIZE"
    assert py2 == py + CELL_SIZE, "Cell (1,1) y should be cell (0,0) y + CELL_SIZE"

    print("✓ PASSED")


def test_pixel_to_cell():
    """Test pixel-to-cell coordinate conversion."""
    print("Testing pixel-to-cell conversion...", end=' ')
    pixel_to_cell = mod_04['pixel_to_cell']
    cell_to_pixel = mod_04['cell_to_pixel']

    # Converting to pixel and back should give the same cell
    for row in range(5):
        for col in range(5):
            px, py = cell_to_pixel(row, col)
            result = pixel_to_cell(px, py)
            assert result == (row, col), \
                f"Round-trip conversion failed for ({row},{col}): got {result}"

    # Pixel outside the board should return None
    result = pixel_to_cell(-100, -100)
    assert result is None, "Pixel outside board should return None"

    print("✓ PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("RUNNING TESTS FOR PYGAME GRAPHICS MODULE")
    print("=" * 70)
    print()

    tests = [
        # 01_pygame_basics.py
        test_window_dimensions,
        test_rect_params,
        test_point_in_rect,
        test_rect_center,
        # 02_rgb_colors.py
        test_color_constants,
        test_known_color_values,
        test_mix_colors,
        test_darken_color,
        test_invert_color,
        test_color_brightness,
        test_is_light_color,
        test_create_gradient,
        # 03_snowperson.py
        test_snowperson_parts,
        test_eye_positions,
        test_nose_position,
        test_mouth_rect,
        test_eyebrow_rects,
        test_button_positions,
        # 04_game_of_life_visualization.py
        test_create_empty_board,
        test_count_neighbors_visualization,
        test_apply_rules_visualization,
        test_place_r_pentomino,
        test_count_alive_cells,
        test_cell_to_pixel,
        test_pixel_to_cell,
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
            print(f"✗ ERROR in {test.__name__}: {e}")
            failed += 1

    print()
    print("=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
