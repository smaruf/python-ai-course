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
ANIMATION_DELAY_MS = 100   # Milliseconds between generations
MAX_GENERATIONS = 200       # Maximum generations to simulate

# Colors
BACKGROUND = (15, 15, 15)        # Near-black background
CELL_ALIVE_COLOR = (50, 200, 50)  # Bright green for living cells
CELL_DEAD_COLOR = (30, 30, 30)    # Dark gray for dead cells (subtle)
GRID_LINE_COLOR = (40, 40, 40)    # Very subtle grid lines
TEXT_COLOR = (200, 200, 200)      # Light gray for text


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


def draw_board(surface, board, cell_radius=CELL_RADIUS, cell_size=CELL_SIZE,
               alive_color=CELL_ALIVE_COLOR, dead_color=CELL_DEAD_COLOR):
    """
    Draw the entire Game of Life board on the surface.

    Each cell is drawn as a circle: alive cells are bright, dead cells are dark.

    Args:
        surface: pygame Surface to draw on
        board: 2-D list with cell states (0=dead, 1=alive)
        cell_radius: Radius of each circle in pixels
        cell_size: Total cell area size in pixels
        alive_color: Color for alive cells
        dead_color: Color for dead cells
    """
    import pygame
    rows = len(board)
    cols = len(board[0])

    for row in range(rows):
        for col in range(cols):
            center = cell_to_pixel(row, col, cell_size)
            color = alive_color if board[row][col] == 1 else dead_color
            pygame.draw.circle(surface, color, center, cell_radius)


def main():
    """
    Main demonstration: animate the R pentomino using pygame.
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

    # Initialize board with R pentomino
    board = create_empty_board(BOARD_ROWS, BOARD_COLS)
    place_r_pentomino(board, BOARD_ROWS // 2 - 1, BOARD_COLS // 2 - 1)

    generation = 0
    running = True
    paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset
                    board = create_empty_board(BOARD_ROWS, BOARD_COLS)
                    place_r_pentomino(board, BOARD_ROWS // 2 - 1, BOARD_COLS // 2 - 1)
                    generation = 0
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if not paused and generation < MAX_GENERATIONS:
            board = apply_rules(board)
            generation += 1

        # Draw
        screen.fill(BACKGROUND)
        draw_board(screen, board)

        # Status text
        alive = count_alive_cells(board)
        info = font.render(
            f"Gen: {generation}  Alive: {alive}  "
            f"{'[PAUSED]' if paused else '[RUNNING]'}  "
            f"SPACE=pause  R=reset  ESC=quit",
            True, TEXT_COLOR
        )
        screen.blit(info, (BOARD_MARGIN_X, WINDOW_HEIGHT - 25))

        pygame.display.flip()
        clock.tick(1000 // ANIMATION_DELAY_MS)

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
    print("  SPACE - Pause/Resume animation")
    print("  R     - Reset to initial R pentomino")
    print("  ESC   - Quit")
    print("\nStarting pygame window...")
    main()
