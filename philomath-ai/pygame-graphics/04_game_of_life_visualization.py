"""
Visualizing Conway's Game of Life with Pygame
==============================================

This module adds a visual pygame interface to the Game of Life simulation
from the 2d-lists module. We draw the board as a grid of circular cells,
and animate the R pentomino evolving over time.

Learning Objectives:
- Draw a grid-based board using pygame
- Represent cells as filled circles for a nicer look
- Animate the Game of Life step by step
- Control animation speed with pygame.time.delay
- Change cell colors based on state
- Scale and position cells on the screen

Key Design Decisions:
- Each cell is drawn as a circle (prettier than squares)
- Cell size can be adjusted to fit more/fewer cells on screen
- Alive cells are bright green; dead cells are dark gray
- A small gap between circles makes them distinct

Video Timestamps:
- 1:25:24 - Drawing a Game of Life board
- 1:47:34 - Visualizing the R pentomino
- 1:55:01 - Prettifying the visualization with circular cells
- 2:02:27 - Scaling down the circle size to separate them
- 2:08:01 - Changing colors, looking ahead, and happy coding

Game of Life Rules (from Chapter 3):
1. Birth: Dead cell with exactly 3 live neighbors becomes alive
2. Survival: Live cell with 2 or 3 live neighbors stays alive
3. Death: All other cells die (or stay dead)
"""

# Board configuration
BOARD_ROWS = 40
BOARD_COLS = 60

# Display configuration
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Game of Life - R Pentomino Visualization"

# Cell display settings
CELL_SIZE = 14          # Total cell area in pixels
CELL_RADIUS = 5         # Radius of the circle drawn for each cell
CELL_GAP = 2            # Gap between circles (CELL_SIZE - 2*CELL_RADIUS - extra)
BOARD_MARGIN_X = 10     # Left margin for the board
BOARD_MARGIN_Y = 10     # Top margin for the board

# Animation settings
ANIMATION_DELAY_MS = 100   # Milliseconds between generations (default)
DELAY_STEP_MS = 20         # How much UP/DOWN arrow adjusts the delay
DELAY_MIN_MS = 20          # Fastest possible speed
DELAY_MAX_MS = 500         # Slowest possible speed
MAX_GENERATIONS = 2000     # Maximum generations before auto-stop

# Colors
BACKGROUND = (15, 15, 15)        # Near-black background
CELL_ALIVE_COLOR = (50, 200, 50)  # Bright green for living cells (age 1)
CELL_DEAD_COLOR = (30, 30, 30)    # Dark gray for dead cells (subtle)
GRID_LINE_COLOR = (40, 40, 40)    # Very subtle grid lines
TEXT_COLOR = (200, 200, 200)      # Light gray for text

# Age-based colour gradient: young cells are bright green, older cells fade
# towards yellow then white as they age.
AGE_COLOR_YOUNG = (50, 200, 50)    # Generation 1 – bright green
AGE_COLOR_MID   = (200, 200, 50)   # Generation ~20 – yellow
AGE_COLOR_OLD   = (220, 220, 220)  # Generation 50+ – near-white
AGE_SATURATE    = 50               # Generations at which colour stops changing


def create_empty_board(rows, cols):
    """
    Create an empty Game of Life board (all dead cells).

    Args:
        rows: Number of rows
        cols: Number of columns

    Returns:
        2-D list of 0s (dead cells)
    """
    return [[0 for _ in range(cols)] for _ in range(rows)]


def count_neighbors(board, row, col):
    """
    Count the number of live neighbors for a cell.

    A cell has up to 8 neighbors (including diagonals).
    Cells outside the board boundaries are treated as dead.

    Args:
        board: 2-D list representing the current state
        row: Row index of the cell
        col: Column index of the cell

    Returns:
        Number of live neighbors (0-8)
    """
    rows = len(board)
    cols = len(board[0])
    count = 0

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr = row + dr
            nc = col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                count += board[nr][nc]

    return count


def apply_rules(board):
    """
    Apply Game of Life rules to generate the next generation.

    Rules:
    - Birth: Dead cell (0) with exactly 3 live neighbors → alive (1)
    - Survival: Live cell (1) with 2 or 3 live neighbors → stays alive
    - Death: All other cells → dead (0)

    Args:
        board: Current state of the board

    Returns:
        New board representing the next generation
    """
    rows = len(board)
    cols = len(board[0])
    new_board = create_empty_board(rows, cols)

    for i in range(rows):
        for j in range(cols):
            neighbors = count_neighbors(board, i, j)
            if board[i][j] == 1:
                new_board[i][j] = 1 if neighbors in (2, 3) else 0
            else:
                new_board[i][j] = 1 if neighbors == 3 else 0

    return new_board


def place_r_pentomino(board, start_row, start_col):
    """
    Place the R pentomino pattern on the board.

    The R pentomino is a famous 5-cell pattern:
      .##
      ##.
      .#.

    It evolves chaotically for over 1000 generations before stabilizing.

    Args:
        board: The board to place the pattern on
        start_row: Row to start placing the pattern
        start_col: Column to start placing the pattern
    """
    r_pentomino = [
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 0],
    ]
    for i, row in enumerate(r_pentomino):
        for j, cell in enumerate(row):
            if cell == 1:
                board[start_row + i][start_col + j] = 1


def count_alive_cells(board):
    """
    Count the total number of alive cells on the board.

    Args:
        board: 2-D list representing the board

    Returns:
        Number of alive cells
    """
    return sum(sum(row) for row in board)


def create_age_board(rows, cols):
    """
    Create an age board (all cells start at age 0).

    Each cell stores how many consecutive generations it has been alive.
    A dead cell always has age 0.

    Args:
        rows: Number of rows
        cols: Number of columns

    Returns:
        2-D list of ints, all initialised to 0
    """
    return [[0 for _ in range(cols)] for _ in range(rows)]


def update_age_board(board, age_board):
    """
    Update the age board to match the current alive/dead state.

    Alive cells increment by 1; dead cells reset to 0.

    Args:
        board:     2-D list with current cell states (0=dead, 1=alive)
        age_board: 2-D list with current cell ages (modified in place)
    """
    rows = len(board)
    cols = len(board[0])
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 1:
                age_board[r][c] += 1
            else:
                age_board[r][c] = 0


def age_to_color(age,
                 young=AGE_COLOR_YOUNG,
                 mid=AGE_COLOR_MID,
                 old=AGE_COLOR_OLD,
                 saturate=AGE_SATURATE):
    """
    Map a cell's age to an RGB colour.

    Young cells (age 1) are bright green.  As they age they shift through
    yellow and eventually to near-white once they exceed *saturate* generations.

    Args:
        age:      How many consecutive generations the cell has been alive (>= 1)
        young:    Colour tuple for age == 1
        mid:      Colour tuple for age == saturate // 2
        old:      Colour tuple for age >= saturate
        saturate: Age at which the colour stops changing

    Returns:
        (r, g, b) colour tuple
    """
    if age <= 0:
        return (0, 0, 0)

    # Normalise: age=1 → t=0.0 (young), age=saturate → t=1.0 (old).
    # When saturate <= 1 (edge case) every alive cell gets the young colour.
    if saturate <= 1:
        return young
    t = min((age - 1) / (saturate - 1), 1.0)

    if t <= 0.5:
        # Interpolate young → mid
        s = t / 0.5
        r = int(young[0] + s * (mid[0] - young[0]))
        g = int(young[1] + s * (mid[1] - young[1]))
        b = int(young[2] + s * (mid[2] - young[2]))
    else:
        # Interpolate mid → old
        s = (t - 0.5) / 0.5
        r = int(mid[0] + s * (old[0] - mid[0]))
        g = int(mid[1] + s * (old[1] - mid[1]))
        b = int(mid[2] + s * (old[2] - mid[2]))

    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def cell_to_pixel(row, col, cell_size=CELL_SIZE,
                  margin_x=BOARD_MARGIN_X, margin_y=BOARD_MARGIN_Y):
    """
    Convert a board cell (row, col) to pixel coordinates.

    The pixel coordinates are the CENTER of the circle drawn for this cell.

    Args:
        row: Row index on the board
        col: Column index on the board
        cell_size: Size of each cell in pixels
        margin_x: Left margin in pixels
        margin_y: Top margin in pixels

    Returns:
        Tuple (pixel_x, pixel_y) of the cell center
    """
    px = margin_x + col * cell_size + cell_size // 2
    py = margin_y + row * cell_size + cell_size // 2
    return (px, py)


def pixel_to_cell(px, py, cell_size=CELL_SIZE,
                  margin_x=BOARD_MARGIN_X, margin_y=BOARD_MARGIN_Y):
    """
    Convert pixel coordinates to a board cell (row, col).

    Args:
        px: Pixel x-coordinate
        py: Pixel y-coordinate
        cell_size: Size of each cell in pixels
        margin_x: Left margin in pixels
        margin_y: Top margin in pixels

    Returns:
        Tuple (row, col) or None if outside the board
    """
    col = (px - margin_x) // cell_size
    row = (py - margin_y) // cell_size
    if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
        return (row, col)
    return None


def draw_board(surface, board, age_board=None,
               cell_radius=CELL_RADIUS, cell_size=CELL_SIZE,
               alive_color=CELL_ALIVE_COLOR, dead_color=CELL_DEAD_COLOR):
    """
    Draw the entire Game of Life board on the surface.

    Each cell is drawn as a circle.  When *age_board* is provided the colour
    of alive cells is determined by their age (young = green, old = white);
    otherwise a single *alive_color* is used for all alive cells.

    Args:
        surface:    pygame Surface to draw on
        board:      2-D list with cell states (0=dead, 1=alive)
        age_board:  Optional 2-D list with cell ages; enables age colouring
        cell_radius: Radius of each circle in pixels
        cell_size:  Total cell area size in pixels
        alive_color: Fallback colour for alive cells (no age board)
        dead_color:  Colour for dead cells
    """
    import pygame
    rows = len(board)
    cols = len(board[0])

    for row in range(rows):
        for col in range(cols):
            center = cell_to_pixel(row, col, cell_size)
            if board[row][col] == 1:
                if age_board is not None:
                    color = age_to_color(age_board[row][col])
                else:
                    color = alive_color
            else:
                color = dead_color
            pygame.draw.circle(surface, color, center, cell_radius)


def main():
    """
    Main demonstration: animate the R pentomino using pygame.

    Enhancements beyond the basic implementation:
    - Cell-age colour gradient (young=green → old=white)
    - Mouse click / drag to toggle cells while paused
    - Speed control with UP / DOWN arrow keys
    - 'A' key to toggle age colouring on/off
    """
    try:
        import pygame
    except ImportError:
        print("pygame is not installed. Run: pip install pygame")
        print("\nRunning Game of Life simulation without display:\n")

        board = create_empty_board(BOARD_ROWS, BOARD_COLS)
        place_r_pentomino(board, BOARD_ROWS // 2, BOARD_COLS // 2)

        print(f"Initial state: {count_alive_cells(board)} alive cells")
        print("Simulating 10 generations...")

        for gen in range(1, 11):
            board = apply_rules(board)
            print(f"  Generation {gen:3}: {count_alive_cells(board):3} alive cells")

        print(f"\nCell pixel position for (0,0): {cell_to_pixel(0, 0)}")
        print(f"Cell pixel position for (20,30): {cell_to_pixel(20, 30)}")
        print(f"Pixel (10, 10) → cell: {pixel_to_cell(10, 10)}")
        return

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    font = pygame.font.SysFont("monospace", 14)
    clock = pygame.time.Clock()

    # Initialise board and age tracking
    board = create_empty_board(BOARD_ROWS, BOARD_COLS)
    place_r_pentomino(board, BOARD_ROWS // 2 - 1, BOARD_COLS // 2 - 1)
    age_board = create_age_board(BOARD_ROWS, BOARD_COLS)
    update_age_board(board, age_board)

    generation = 0
    running = True
    paused = False
    show_age_color = True           # Toggle with 'A'
    delay_ms = ANIMATION_DELAY_MS   # Adjustable speed
    mouse_held = False              # Track mouse drag state

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset board and age tracking
                    board = create_empty_board(BOARD_ROWS, BOARD_COLS)
                    place_r_pentomino(board, BOARD_ROWS // 2 - 1, BOARD_COLS // 2 - 1)
                    age_board = create_age_board(BOARD_ROWS, BOARD_COLS)
                    update_age_board(board, age_board)
                    generation = 0
                elif event.key == pygame.K_a:
                    show_age_color = not show_age_color
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    delay_ms = max(DELAY_MIN_MS, delay_ms - DELAY_STEP_MS)
                elif event.key == pygame.K_DOWN:
                    delay_ms = min(DELAY_MAX_MS, delay_ms + DELAY_STEP_MS)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_held = True
                    cell = pixel_to_cell(event.pos[0], event.pos[1])
                    if cell is not None:
                        r, c = cell
                        board[r][c] = 1 - board[r][c]  # Toggle cell
                        if board[r][c] == 0:
                            age_board[r][c] = 0
                        else:
                            age_board[r][c] = 1

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_held = False

            elif event.type == pygame.MOUSEMOTION and mouse_held:
                cell = pixel_to_cell(event.pos[0], event.pos[1])
                if cell is not None:
                    r, c = cell
                    board[r][c] = 1   # Draw mode: drag to paint live cells
                    age_board[r][c] = 1  # Reset age to 1 when painting

        if not paused and generation < MAX_GENERATIONS:
            board = apply_rules(board)
            update_age_board(board, age_board)
            generation += 1

        # Draw
        screen.fill(BACKGROUND)
        draw_board(screen, board,
                   age_board=age_board if show_age_color else None)

        # Status text
        alive = count_alive_cells(board)
        age_label = "age-color=ON" if show_age_color else "age-color=OFF"
        info = font.render(
            f"Gen:{generation}  Alive:{alive}  delay:{delay_ms}ms  "
            f"{'[PAUSED]' if paused else '[RUNNING]'}  "
            f"SPACE  R  A={age_label}  ↑↓speed  click=draw  ESC",
            True, TEXT_COLOR
        )
        screen.blit(info, (BOARD_MARGIN_X, WINDOW_HEIGHT - 25))

        pygame.display.flip()
        clock.tick(1000 // delay_ms)

    pygame.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("GAME OF LIFE VISUALIZATION")
    print("=" * 60)
    print("\nVisualizing the R pentomino with circular cells.")
    print(f"Board: {BOARD_ROWS} rows x {BOARD_COLS} columns")
    print(f"Cell size: {CELL_SIZE}px total, {CELL_RADIUS}px radius")
    print(f"Animation delay: {ANIMATION_DELAY_MS}ms per generation")
    print("\nControls:")
    print("  SPACE      - Pause/Resume animation")
    print("  R          - Reset to initial R pentomino")
    print("  A          - Toggle age-based cell colouring")
    print("  UP / DOWN  - Increase / decrease animation speed")
    print("  Click/drag - Paint live cells (draw mode)")
    print("  ESC        - Quit")
    print("\nStarting pygame window...")
    main()
