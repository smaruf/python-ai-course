"""
Krypton Chronicles - Multi-Faction Game of Life
================================================

A themed multi-state cellular automaton inspired by Superman's story.
The planet Krypton was destroyed, and Kal-El (Superman) came to Earth.
On Earth he faces:
  - Earthian allies who bond with him and help protect humanity
  - Earthian enemies who seek to destroy him, his cousins, and his allies
  - The constant risk of turning evil when overwhelmed by darkness

This simulation models that struggle as a multi-faction cellular automaton
where each cell can belong to one of five states, and the rules encode
the story dynamics.

States
------
  EMPTY          (0) - unoccupied space
  KRYPTONIAN     (1) - Superman and Kryptonian survivors (blue)
  EARTHIAN_ALLY  (2) - bonded earthians who protect the Kryptonians (green)
  EARTHIAN_ENEMY (3) - earthians / villains who seek to destroy them (red)
  EVIL           (4) - Kryptonian turned evil or corrupted agent (dark purple)

Rules
-----
For each cell, count its 8 neighbors by state and apply:

KRYPTONIAN:
  - Turns EVIL    if enemy_count >= 4  (overwhelmed → corrupted)
  - Stays alive   if ally_count >= 1 AND enemy_count <= 2
  - Dies otherwise (underpopulation / over-threat)

EARTHIAN_ALLY:
  - Survives      if 2 <= friendly_count <= 3  (friendly = Kryptonian + ally)
  - Dies          if enemy_count + evil_count >= 4 (destroyed by enemy mob)

EARTHIAN_ENEMY:
  - Survives      if 1 <= enemy_count + evil_count <= 4
  - Dies          if too few or too many of their own

EVIL:
  - Spreads/survives  if 1 <= evil_count <= 3
  - Dies              otherwise (unstable without enough support)

EMPTY:
  - Becomes KRYPTONIAN  if kryptonian_count >= 1 AND ally_count >= 2
                          (favorable race birth – new hope)
  - Becomes ALLY        if ally_count == 3 (earthians bond together)
  - Becomes ENEMY       if enemy_count == 3 (enemy mob forms)
  - Becomes EVIL        if evil_count >= 3 (corruption spreads)
  - Stays EMPTY         otherwise

Controls (pygame window)
------------------------
  SPACE  - Pause / Resume
  R      - Reset to initial layout
  ESC    - Quit
"""

# ── Cell state constants ──────────────────────────────────────────────────────
EMPTY         = 0
KRYPTONIAN    = 1
EARTHIAN_ALLY = 2
EARTHIAN_ENEMY = 3
EVIL          = 4

# ── Colors (R, G, B) for each state ──────────────────────────────────────────
STATE_COLORS = {
    EMPTY:          (15,  15,  15),   # near-black background
    KRYPTONIAN:     (60, 140, 255),   # Superman blue
    EARTHIAN_ALLY:  (50, 200,  80),   # hope green
    EARTHIAN_ENEMY: (200,  40,  40),  # threat red
    EVIL:           (140,  0,  200),  # corrupted purple
}

STATE_NAMES = {
    EMPTY:          "Empty",
    KRYPTONIAN:     "Kryptonian",
    EARTHIAN_ALLY:  "Earthian Ally",
    EARTHIAN_ENEMY: "Earthian Enemy",
    EVIL:           "Evil / Corrupted",
}

# ── Board / display configuration ────────────────────────────────────────────
BOARD_ROWS    = 40
BOARD_COLS    = 60
WINDOW_WIDTH  = 920
WINDOW_HEIGHT = 660
WINDOW_TITLE  = "Krypton Chronicles – Multi-Faction Game of Life"

CELL_SIZE     = 14   # pixels per cell (square area)
CELL_RADIUS   = 5    # circle radius drawn inside each cell
BOARD_MARGIN_X = 10
BOARD_MARGIN_Y = 10

ANIMATION_DELAY_MS = 120
MAX_GENERATIONS    = 500

BACKGROUND_COLOR = (10, 10, 20)   # deep-space background
TEXT_COLOR       = (210, 210, 210)
LEGEND_BG_COLOR  = (30, 30, 45)


# ── Board helpers ─────────────────────────────────────────────────────────────

def create_empty_board(rows, cols):
    """
    Create a board with all cells set to EMPTY.

    Args:
        rows: Number of rows
        cols: Number of columns

    Returns:
        2-D list of EMPTY (0) values
    """
    return [[EMPTY for _ in range(cols)] for _ in range(rows)]


def count_state_neighbors(board, row, col):
    """
    Count neighbors of each state for a given cell.

    Args:
        board: 2-D list of cell states
        row: Row index
        col: Column index

    Returns:
        dict mapping state → count of that state in the 8 neighbors
    """
    rows = len(board)
    cols = len(board[0])
    counts = {EMPTY: 0, KRYPTONIAN: 0, EARTHIAN_ALLY: 0,
              EARTHIAN_ENEMY: 0, EVIL: 0}

    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                counts[board[nr][nc]] += 1

    return counts


def apply_krypton_rules(board):
    """
    Compute the next generation of the Krypton multi-faction board.

    Applies the themed rules described in the module docstring.

    Args:
        board: Current 2-D list of cell states

    Returns:
        New 2-D list representing the next generation
    """
    rows = len(board)
    cols = len(board[0])
    new_board = create_empty_board(rows, cols)

    for r in range(rows):
        for c in range(cols):
            n = count_state_neighbors(board, r, c)
            state = board[r][c]

            enemy_count   = n[EARTHIAN_ENEMY]
            evil_count    = n[EVIL]
            ally_count    = n[EARTHIAN_ALLY]
            kryp_count    = n[KRYPTONIAN]
            friendly_count = kryp_count + ally_count

            if state == KRYPTONIAN:
                if enemy_count >= 4:
                    new_board[r][c] = EVIL           # overwhelmed → turns evil
                elif ally_count >= 1 and enemy_count <= 2:
                    new_board[r][c] = KRYPTONIAN     # protected → survives
                else:
                    new_board[r][c] = EMPTY          # isolated / overpowered

            elif state == EARTHIAN_ALLY:
                if (enemy_count + evil_count) >= 4:
                    new_board[r][c] = EMPTY          # destroyed by enemy mob
                elif 2 <= friendly_count <= 3:
                    new_board[r][c] = EARTHIAN_ALLY  # community survives
                else:
                    new_board[r][c] = EMPTY

            elif state == EARTHIAN_ENEMY:
                combined = enemy_count + evil_count
                if 1 <= combined <= 4:
                    new_board[r][c] = EARTHIAN_ENEMY  # gang holds together
                else:
                    new_board[r][c] = EMPTY

            elif state == EVIL:
                if 1 <= evil_count <= 3:
                    new_board[r][c] = EVIL           # corruption sustains
                else:
                    new_board[r][c] = EMPTY          # collapses without support

            else:  # EMPTY
                if kryp_count >= 1 and ally_count >= 2:
                    new_board[r][c] = KRYPTONIAN     # favorable-race birth
                elif ally_count == 3:
                    new_board[r][c] = EARTHIAN_ALLY  # earthian community forms
                elif enemy_count == 3:
                    new_board[r][c] = EARTHIAN_ENEMY # enemy cell spawns
                elif evil_count >= 3:
                    new_board[r][c] = EVIL           # corruption spreads
                else:
                    new_board[r][c] = EMPTY

    return new_board


def count_by_state(board):
    """
    Count cells in each state across the whole board.

    Args:
        board: 2-D list of cell states

    Returns:
        dict mapping state → count
    """
    counts = {s: 0 for s in STATE_COLORS}
    for row in board:
        for cell in row:
            counts[cell] += 1
    return counts


# ── Coordinate helpers ────────────────────────────────────────────────────────

def cell_to_pixel(row, col):
    """
    Convert (row, col) board coordinates to pixel center of the cell.

    Args:
        row: Row index
        col: Column index

    Returns:
        (px, py) pixel coordinates of the circle center
    """
    px = BOARD_MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
    py = BOARD_MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
    return (px, py)


# ── Initial scenario ──────────────────────────────────────────────────────────

def setup_krypton_scenario(board):
    """
    Place the initial factions on the board to tell Superman's story.

    Layout:
      - A cluster of Kryptonians near the centre (Kal-El and cousins)
      - A ring of earthian allies surrounding them
      - Groups of earthian enemies approaching from the sides
      - One small seed of evil in a corner (waiting to corrupt)

    Args:
        board: The board to initialise (modified in place)
    """
    rows = len(board)
    cols = len(board[0])
    cr   = rows // 2
    cc   = cols // 2

    # ── Kryptonian core (glider-like 5-cell seed) ────────────────────────────
    kryp_pattern = [
        (cr,     cc),
        (cr - 1, cc + 1),
        (cr,     cc + 1),
        (cr + 1, cc + 1),
        (cr - 1, cc + 2),
    ]
    for r, c in kryp_pattern:
        board[r][c] = KRYPTONIAN

    # ── Earthian ally ring (protective shell) ────────────────────────────────
    ally_ring = [
        (cr - 2, cc - 1), (cr - 2, cc),     (cr - 2, cc + 1),
        (cr - 1, cc - 2),                                       (cr - 1, cc + 3),
        (cr,     cc - 2),                                       (cr,     cc + 3),
        (cr + 1, cc - 2),                                       (cr + 1, cc + 3),
        (cr + 2, cc - 1), (cr + 2, cc),     (cr + 2, cc + 1),
    ]
    for r, c in ally_ring:
        if 0 <= r < rows and 0 <= c < cols:
            board[r][c] = EARTHIAN_ALLY

    # ── Enemy squads approaching from the left and right ─────────────────────
    enemy_left = [
        (cr - 1, cc - 6), (cr, cc - 6), (cr + 1, cc - 6),
        (cr - 1, cc - 7), (cr, cc - 7),
    ]
    enemy_right = [
        (cr - 1, cc + 7), (cr, cc + 7), (cr + 1, cc + 7),
        (cr,     cc + 8), (cr + 1, cc + 8),
    ]
    for r, c in enemy_left + enemy_right:
        if 0 <= r < rows and 0 <= c < cols:
            board[r][c] = EARTHIAN_ENEMY

    # ── Small evil seed in the bottom-left corner ─────────────────────────────
    evil_seed = [
        (rows - 4, 3), (rows - 4, 4),
        (rows - 3, 3), (rows - 3, 5),
        (rows - 2, 4),
    ]
    for r, c in evil_seed:
        if 0 <= r < rows and 0 <= c < cols:
            board[r][c] = EVIL


# ── Main visualization ────────────────────────────────────────────────────────

def main():
    """
    Run the Krypton Chronicles pygame visualization.

    Displays the multi-faction board with a legend and live statistics.
    """
    try:
        import pygame
    except ImportError:
        print("pygame is not installed. Run: pip install pygame")
        _run_text_demo()
        return

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    font_sm = pygame.font.SysFont("monospace", 12)
    font_md = pygame.font.SysFont("monospace", 14, bold=True)
    clock   = pygame.time.Clock()

    # ── Initialise board ─────────────────────────────────────────────────────
    board = create_empty_board(BOARD_ROWS, BOARD_COLS)
    setup_krypton_scenario(board)
    generation = 0
    paused = False

    # ── Legend / stats panel geometry ────────────────────────────────────────
    panel_x = BOARD_MARGIN_X + BOARD_COLS * CELL_SIZE + 12
    panel_w = WINDOW_WIDTH - panel_x - 8
    panel_y = BOARD_MARGIN_Y

    while True:
        # ── Events ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    board = create_empty_board(BOARD_ROWS, BOARD_COLS)
                    setup_krypton_scenario(board)
                    generation = 0
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        # ── Advance simulation ────────────────────────────────────────────────
        if not paused and generation < MAX_GENERATIONS:
            board = apply_krypton_rules(board)
            generation += 1

        # ── Draw background ───────────────────────────────────────────────────
        screen.fill(BACKGROUND_COLOR)

        # ── Draw board ────────────────────────────────────────────────────────
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                center = cell_to_pixel(row, col)
                color  = STATE_COLORS[board[row][col]]
                pygame.draw.circle(screen, color, center, CELL_RADIUS)

        # ── Side panel ────────────────────────────────────────────────────────
        pygame.draw.rect(screen, LEGEND_BG_COLOR,
                         (panel_x, panel_y, panel_w, WINDOW_HEIGHT - 2 * BOARD_MARGIN_Y),
                         border_radius=8)

        title_surf = font_md.render("KRYPTON", True, (100, 180, 255))
        screen.blit(title_surf, (panel_x + 8, panel_y + 8))
        title_surf2 = font_md.render("CHRONICLES", True, (100, 180, 255))
        screen.blit(title_surf2, (panel_x + 8, panel_y + 24))

        # Generation counter
        gen_surf = font_sm.render(f"Gen: {generation}", True, TEXT_COLOR)
        screen.blit(gen_surf, (panel_x + 8, panel_y + 52))

        status = "[PAUSED]" if paused else "[RUNNING]"
        st_surf = font_sm.render(status, True,
                                  (255, 200, 80) if paused else (80, 255, 80))
        screen.blit(st_surf, (panel_x + 8, panel_y + 68))

        # Legend + counts
        counts = count_by_state(board)
        ly = panel_y + 100
        for state in (KRYPTONIAN, EARTHIAN_ALLY, EARTHIAN_ENEMY, EVIL, EMPTY):
            color = STATE_COLORS[state]
            pygame.draw.circle(screen, color, (panel_x + 14, ly + 6), 7)
            label = font_sm.render(
                f"{STATE_NAMES[state]}", True, TEXT_COLOR)
            count_lbl = font_sm.render(
                f"{counts[state]:4}", True, (180, 180, 180))
            screen.blit(label,     (panel_x + 26, ly))
            screen.blit(count_lbl, (panel_x + 26, ly + 14))
            ly += 40

        # Controls hint
        ly += 10
        for line in ("SPACE: pause", "R: reset", "ESC: quit"):
            surf = font_sm.render(line, True, (120, 120, 150))
            screen.blit(surf, (panel_x + 8, ly))
            ly += 16

        pygame.display.flip()
        clock.tick(1000 // ANIMATION_DELAY_MS)


def _run_text_demo():
    """
    Run a short text-mode demo when pygame is unavailable.
    """
    print("\nKrypton Chronicles – text demo (10 generations)\n")
    board = create_empty_board(BOARD_ROWS, BOARD_COLS)
    setup_krypton_scenario(board)

    for gen in range(11):
        counts = count_by_state(board)
        print(f"Gen {gen:3d} | "
              f"Kryptonian={counts[KRYPTONIAN]:3}  "
              f"Ally={counts[EARTHIAN_ALLY]:3}  "
              f"Enemy={counts[EARTHIAN_ENEMY]:3}  "
              f"Evil={counts[EVIL]:3}")
        if gen < 10:
            board = apply_krypton_rules(board)


if __name__ == "__main__":
    print("=" * 60)
    print("KRYPTON CHRONICLES")
    print("Multi-Faction Game of Life")
    print("=" * 60)
    print("\nFactions:")
    for state, name in STATE_NAMES.items():
        if state != EMPTY:
            print(f"  {name}")
    print("\nStarting simulation...")
    main()
