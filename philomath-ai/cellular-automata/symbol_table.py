"""
Symbol Table
============
Bidirectional mapping between integer states and display symbols.
"""

from __future__ import annotations
from typing import Dict, List, Optional


class SymbolTable:
    """Maps integer state ↔ symbol character."""

    def __init__(self, state_to_symbol: Dict[int, str]):
        self._s2sym: Dict[int, str] = dict(state_to_symbol)
        self._sym2s: Dict[str, int] = {v: k for k, v in state_to_symbol.items()}

    @classmethod
    def from_symbols(cls, symbols: List[str]) -> "SymbolTable":
        """Create a SymbolTable where state i maps to symbols[i]."""
        return cls({i: s for i, s in enumerate(symbols)})

    def state_to_symbol(self, state: int) -> str:
        return self._s2sym[state]

    def symbol_to_state(self, sym: str) -> int:
        return self._sym2s[sym]

    def has_state(self, state: int) -> bool:
        return state in self._s2sym

    def has_symbol(self, sym: str) -> bool:
        return sym in self._sym2s

    def states(self) -> List[int]:
        return list(self._s2sym.keys())

    def symbols(self) -> List[str]:
        return list(self._s2sym.values())

    def __repr__(self) -> str:
        return f"SymbolTable({self._s2sym!r})"
