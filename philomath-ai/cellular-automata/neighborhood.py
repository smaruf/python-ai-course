"""
Neighborhood
============
Extract Moore (8-cell) or von Neumann (4-cell) neighborhood keys from a Board.
Keys are tuples of integers for efficient dictionary lookup in table-driven rules.
"""

from __future__ import annotations
from typing import Tuple
from board import Board


# Offsets for Moore neighborhood (8 surrounding cells, ordered by dr, dc)
_MOORE_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1),
]

# Offsets for von Neumann neighborhood (4 orthogonal cells, N/W/E/S)
_VON_NEUMANN_OFFSETS = [
    (-1, 0),
    ( 0, -1), ( 0, 1),
    ( 1, 0),
]


def moore_key(board: Board, row: int, col: int) -> Tuple[int, ...]:
    """Return the center state followed by 8 Moore neighbors as a tuple."""
    center = board.get(row, col)
    neighbors = tuple(board.get(row + dr, col + dc) for dr, dc in _MOORE_OFFSETS)
    return (center,) + neighbors


def moore_neighbors_only(board: Board, row: int, col: int) -> Tuple[int, ...]:
    """Return only the 8 Moore neighbor states (no center)."""
    return tuple(board.get(row + dr, col + dc) for dr, dc in _MOORE_OFFSETS)


def von_neumann_key(board: Board, row: int, col: int) -> Tuple[int, ...]:
    """Return the center state followed by 4 von Neumann neighbors as a tuple."""
    center = board.get(row, col)
    neighbors = tuple(board.get(row + dr, col + dc) for dr, dc in _VON_NEUMANN_OFFSETS)
    return (center,) + neighbors


def count_moore_alive(board: Board, row: int, col: int, alive_state: int = 1) -> int:
    """Count how many Moore neighbors match alive_state."""
    return sum(
        1 for dr, dc in _MOORE_OFFSETS
        if board.get(row + dr, col + dc) == alive_state
    )
