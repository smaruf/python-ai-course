"""
Terminal Renderer
=================
Renders a Board to stdout using configurable symbols.
"""

from __future__ import annotations
import os
import sys
from typing import Optional
from board import Board
from symbol_table import SymbolTable


# Default symbols for binary (2-state) automata
_DEFAULT_SYMBOLS = {0: '·', 1: '█'}


class TerminalRenderer:
    """Render a Board to the terminal."""

    def __init__(
        self,
        symbol_table: Optional[SymbolTable] = None,
        clear: bool = False,
    ):
        if symbol_table is None:
            symbol_table = SymbolTable(_DEFAULT_SYMBOLS)
        self.symbol_table = symbol_table
        self.clear = clear

    def render(self, board: Board, generation: Optional[int] = None) -> None:
        if self.clear:
            os.system('clear' if os.name == 'posix' else 'cls')

        if generation is not None:
            print(f"=== Generation {generation} ===")

        for r in range(board.rows):
            line = ''
            for c in range(board.cols):
                state = board.get(r, c)
                if self.symbol_table.has_state(state):
                    line += self.symbol_table.state_to_symbol(state)
                else:
                    line += str(state)
            print(line)

    def render_multistate(self, board: Board, generation: Optional[int] = None) -> None:
        """Render with space-separated integer states (debugging aid)."""
        if generation is not None:
            print(f"=== Generation {generation} ===")
        for r in range(board.rows):
            print(' '.join(str(board.get(r, c)) for c in range(board.cols)))
