"""
Alphabet Detection
==================
Auto-detect the symbol set used in a pattern or rule file so the caller
does not need to specify it manually.

Detection priority
------------------
1. **Digit-only**   – all non-whitespace chars are ASCII digits 0-9.
2. **Dot+digit**    – chars are dots (.) and ASCII digits; dot → state 0.
3. **Custom**       – anything else; symbols ordered by first appearance.
"""

from __future__ import annotations
from typing import List
from symbol_table import SymbolTable


def detect_alphabet(text: str) -> SymbolTable:
    """
    Inspect *text* and return an appropriate SymbolTable.

    Parameters
    ----------
    text:
        Raw content of a pattern or rule file (may contain whitespace /
        newlines which are ignored during detection).

    Returns
    -------
    SymbolTable
        Auto-detected mapping of symbols → integer states.
    """
    chars = [c for c in text if not c.isspace()]
    unique = _ordered_unique(chars)

    if all(c.isdigit() for c in unique):
        # Each digit is its own state
        mapping = {int(c): c for c in unique}
        return SymbolTable(mapping)

    if all(c == '.' or c.isdigit() for c in unique):
        # Dot-and-digit format: '.' → 0, '1' → 1, '2' → 2, …
        mapping: dict = {0: '.'}
        for c in unique:
            if c.isdigit():
                mapping[int(c)] = c
        return SymbolTable(mapping)

    # Custom symbol set: assign states by first appearance order
    return SymbolTable({i: s for i, s in enumerate(unique)})


def detect_alphabet_from_lines(lines: List[str]) -> SymbolTable:
    """Convenience wrapper that accepts a list of lines."""
    return detect_alphabet('\n'.join(lines))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ordered_unique(seq) -> List:
    """Return items in *seq* in first-appearance order, deduplicated."""
    seen = set()
    result = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
