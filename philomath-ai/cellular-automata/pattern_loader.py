"""
Pattern Loader
==============
Load initial board configurations from plain-text pattern files.

Supported formats
-----------------
- **Plain text grid** – each non-empty line is a row; characters are mapped
  via a SymbolTable.  Leading/trailing blank lines are stripped.
- Auto-detect the SymbolTable when none is provided.
"""

from __future__ import annotations
from typing import List, Optional
from board import Board
from symbol_table import SymbolTable
from alphabet_detect import detect_alphabet


def load_pattern(
    path: str,
    symbol_table: Optional[SymbolTable] = None,
    boundary: str = Board.FIXED,
) -> Board:
    """
    Load a pattern file and return a Board.

    Parameters
    ----------
    path:
        Path to the pattern file.
    symbol_table:
        Optional explicit SymbolTable.  If *None*, auto-detection is used.
    boundary:
        Boundary mode for the returned Board (``'fixed'`` or ``'wrap'``).
    """
    with open(path, "r") as fh:
        raw = fh.read()

    lines = [line.rstrip('\n') for line in raw.splitlines()]
    # Strip leading/trailing blank lines
    while lines and lines[0].strip() == '':
        lines.pop(0)
    while lines and lines[-1].strip() == '':
        lines.pop()

    # Skip comment lines starting with '#'
    data_lines = [l for l in lines if not l.startswith('#')]

    if symbol_table is None:
        symbol_table = detect_alphabet('\n'.join(data_lines))

    rows = len(data_lines)
    cols = max(len(l) for l in data_lines) if rows else 0

    grid: List[List[int]] = []
    for line in data_lines:
        row = []
        for ch in line:
            if symbol_table.has_symbol(ch):
                row.append(symbol_table.symbol_to_state(ch))
            else:
                row.append(0)
        # Pad shorter rows
        row.extend([0] * (cols - len(row)))
        grid.append(row)

    return Board.from_list(grid, boundary=boundary)


def load_pattern_from_list(
    rows_of_chars: List[str],
    symbol_table: Optional[SymbolTable] = None,
    boundary: str = Board.FIXED,
) -> Board:
    """Load a pattern from a list of strings (already split into rows)."""
    text = '\n'.join(rows_of_chars)
    if symbol_table is None:
        symbol_table = detect_alphabet(text)
    rows = len(rows_of_chars)
    cols = max(len(l) for l in rows_of_chars) if rows else 0
    grid: List[List[int]] = []
    for line in rows_of_chars:
        row = [symbol_table.symbol_to_state(ch) if symbol_table.has_symbol(ch) else 0 for ch in line]
        row.extend([0] * (cols - len(row)))
        grid.append(row)
    return Board.from_list(grid, boundary=boundary)


def pattern_from_rows(
    rows_of_ints: List[List[int]],
    boundary: str = Board.FIXED,
) -> Board:
    """Convenience: create a Board directly from a nested integer list."""
    return Board.from_list(rows_of_ints, boundary=boundary)
