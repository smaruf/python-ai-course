"""
Pygame Renderer
===============
Renders a Board in a pygame window, drawing each cell as a filled circle.

Requires: pygame
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple
from board import Board

# Colour palette for up to 9 states (state → RGB tuple)
_DEFAULT_PALETTE: Dict[int, Tuple[int, int, int]] = {
    0: (20,  20,  20),   # dead / background
    1: (50, 220,  50),   # alive / state 1
    2: (220,  50,  50),
    3: ( 50,  50, 220),
    4: (220, 220,  50),
    5: ( 50, 220, 220),
    6: (220,  50, 220),
    7: (180, 180, 180),
    8: (255, 140,   0),
}


class PygameRenderer:
    """
    Interactive pygame window renderer.

    Key bindings
    ------------
    SPACE  – pause / resume
    Q / ESC – quit
    """

    def __init__(
        self,
        cell_size: int = 12,
        fps: int = 10,
        palette: Optional[Dict[int, Tuple[int, int, int]]] = None,
        title: str = "Cellular Automata",
    ):
        self.cell_size = cell_size
        self.fps = fps
        self.palette = dict(_DEFAULT_PALETTE)
        if palette:
            self.palette.update(palette)
        self.title = title

        self._pygame_init = False
        self._screen = None
        self._clock = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _init(self, board: Board) -> None:
        import pygame
        if not self._pygame_init:
            pygame.init()
            width = board.cols * self.cell_size
            height = board.rows * self.cell_size
            self._screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption(self.title)
            self._clock = pygame.time.Clock()
            self._pygame_init = True

    def close(self) -> None:
        if self._pygame_init:
            import pygame
            pygame.quit()
            self._pygame_init = False

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, board: Board) -> None:
        """Draw the board.  Must be called after _init()."""
        import pygame
        cs = self.cell_size
        radius = max(1, cs // 2 - 1)
        bg = self.palette.get(0, (20, 20, 20))
        self._screen.fill(bg)

        for r in range(board.rows):
            for c in range(board.cols):
                state = board.get(r, c)
                if state == 0:
                    continue
                color = self.palette.get(state, (200, 200, 200))
                cx = c * cs + cs // 2
                cy = r * cs + cs // 2
                pygame.draw.circle(self._screen, color, (cx, cy), radius)

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self, initial_board: Board, engine) -> None:
        """
        Run the automaton in a pygame window until the user closes it.

        Parameters
        ----------
        initial_board:
            Starting board state.
        engine:
            An Engine instance with a ``step(board) -> Board`` method.
        """
        import pygame

        self._init(initial_board)
        board = initial_board
        paused = False
        generation = 0

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused

            if not paused:
                self.render(board)
                board = engine.step(board)
                generation += 1

            self._clock.tick(self.fps)

        self.close()
