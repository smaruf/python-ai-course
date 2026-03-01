"""
Board
=====
Manages the integer-state grid with fixed or wrapping boundary conditions.
"""

from __future__ import annotations
from typing import List


class Board:
    """2-D integer-state grid with configurable boundary conditions."""

    FIXED = "fixed"
    WRAP = "wrap"

    def __init__(self, rows: int, cols: int, boundary: str = FIXED, default: int = 0):
        if boundary not in (self.FIXED, self.WRAP):
            raise ValueError(f"boundary must be '{self.FIXED}' or '{self.WRAP}'")
        self.rows = rows
        self.cols = cols
        self.boundary = boundary
        self._grid: List[List[int]] = [
            [default] * cols for _ in range(rows)
        ]

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_list(cls, data: List[List[int]], boundary: str = FIXED) -> "Board":
        rows = len(data)
        cols = max(len(r) for r in data) if rows else 0
        board = cls(rows, cols, boundary)
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                board._grid[r][c] = val
        return board

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get(self, row: int, col: int) -> int:
        if self.boundary == self.WRAP:
            return self._grid[row % self.rows][col % self.cols]
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self._grid[row][col]
        return 0  # fixed boundary: out-of-bounds is 0

    def set(self, row: int, col: int, value: int) -> None:
        if self.boundary == self.WRAP:
            self._grid[row % self.rows][col % self.cols] = value
        elif 0 <= row < self.rows and 0 <= col < self.cols:
            self._grid[row][col] = value

    def to_list(self) -> List[List[int]]:
        return [row[:] for row in self._grid]

    def copy(self) -> "Board":
        b = Board(self.rows, self.cols, self.boundary)
        b._grid = [row[:] for row in self._grid]
        return b

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Board):
            return NotImplemented
        return self._grid == other._grid

    def __repr__(self) -> str:
        return f"Board({self.rows}x{self.cols}, boundary={self.boundary!r})"
