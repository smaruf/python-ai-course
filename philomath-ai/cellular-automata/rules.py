"""
Rules
=====
Rule implementations:
  - LifeRule              : Algorithmic Conway's Game of Life.
  - TableRule             : Moore (8-neighbor) table-driven rule.
  - VonNeumannTableRule   : Von Neumann (4-neighbor) table-driven rule for
                            automata such as Langton's Loops.
"""

from __future__ import annotations
from typing import Dict, Tuple
from neighborhood import count_moore_alive, moore_key, von_neumann_key


class LifeRule:
    """Conway's Game of Life rule (B3/S23)."""

    def next_state(self, board, row: int, col: int) -> int:
        center = board.get(row, col)
        alive_neighbors = count_moore_alive(board, row, col, alive_state=1)
        if center == 1:
            return 1 if alive_neighbors in (2, 3) else 0
        else:
            return 1 if alive_neighbors == 3 else 0


class TableRule:
    """
    Moore (8-neighbor) table-driven rule.

    Key format: (center, n0, n1, ..., n7) – 9-element integer tuple produced
    by ``neighborhood.moore_key``.

    Raises ``KeyError`` with a descriptive message when a key is missing.
    """

    def __init__(self, table: Dict[Tuple[int, ...], int], name: str = "TableRule"):
        self.table = table
        self.name = name

    def next_state(self, board, row: int, col: int) -> int:
        key = moore_key(board, row, col)
        if key not in self.table:
            raise KeyError(
                f"[{self.name}] No transition for neighborhood key {key}. "
                "Ensure the rule file covers all possible neighborhood combinations."
            )
        return self.table[key]


class VonNeumannTableRule:
    """
    Von Neumann (4-neighbor) table-driven rule.

    Key format: (center, north, west, east, south) – 5-element integer tuple
    produced by ``neighborhood.von_neumann_key``.

    Used by Langton's Loops and similar 5-cell-neighbourhood automata.
    Raises ``KeyError`` with a descriptive message when a key is missing.
    """

    def __init__(self, table: Dict[Tuple[int, ...], int], name: str = "VNTableRule"):
        self.table = table
        self.name = name

    def next_state(self, board, row: int, col: int) -> int:
        key = von_neumann_key(board, row, col)
        if key not in self.table:
            raise KeyError(
                f"[{self.name}] No transition for neighborhood key {key}. "
                "Ensure the rule file covers all possible neighborhood combinations."
            )
        return self.table[key]
