"""
Engine
======
Synchronous single-step engine: produces the next Board without mutating
the current one.
"""

from __future__ import annotations
from board import Board


class Engine:
    """Drives one cellular-automaton step."""

    def __init__(self, rule):
        self.rule = rule

    def step(self, board: Board) -> Board:
        """Return a NEW Board representing the next generation."""
        next_board = Board(board.rows, board.cols, board.boundary)
        for r in range(board.rows):
            for c in range(board.cols):
                next_board.set(r, c, self.rule.next_state(board, r, c))
        return next_board

    def run(self, board: Board, generations: int) -> Board:
        """Advance *board* by *generations* steps and return the final Board."""
        current = board
        for _ in range(generations):
            current = self.step(current)
        return current
