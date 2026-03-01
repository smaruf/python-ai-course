"""
Rule Loader
===========
Load table-driven rules from plain-text rule files.

Supported formats
-----------------
**Moore (10-token)** – one transition per line:

    <center> <n0> <n1> <n2> <n3> <n4> <n5> <n6> <n7> <next_state>

where n0..n7 are the 8 Moore neighbors in the order produced by
``neighborhood.moore_key`` (row-major, skipping center).

**Von Neumann (6-token)** – one transition per line:

    <center> <north> <west> <east> <south> <next_state>

The format is auto-detected from the token count of the first data line.
Comment lines begin with ``#``.
"""

from __future__ import annotations
import os
from typing import Dict, Optional, Tuple
from symbol_table import SymbolTable
from alphabet_detect import detect_alphabet
from rules import TableRule, VonNeumannTableRule


def load_table_rule(
    path: str,
    symbol_table: Optional[SymbolTable] = None,
    name: Optional[str] = None,
):
    """
    Parse a rule file and return a TableRule or VonNeumannTableRule.

    The neighborhood format (Moore vs. von Neumann) is auto-detected from
    the number of tokens on the first data line (10 → Moore, 6 → von Neumann).

    Parameters
    ----------
    path:
        Path to the rule file.
    symbol_table:
        Optional SymbolTable for translating symbol characters to states.
        If *None*, the loader attempts to detect the alphabet automatically.
    name:
        Optional human-readable name for error messages.
    """
    with open(path, "r") as fh:
        raw = fh.read()

    if symbol_table is None:
        symbol_table = detect_alphabet(raw)

    if name is None:
        name = os.path.basename(path)

    table: Dict[Tuple[int, ...], int] = {}
    detected_format: Optional[str] = None  # 'moore' | 'vn'

    for lineno, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        tokens = line.split()
        n = len(tokens)

        if detected_format is None:
            if n == 10:
                detected_format = 'moore'
            elif n == 6:
                detected_format = 'vn'
            else:
                raise ValueError(
                    f"[{name}] Line {lineno}: expected 10 tokens (Moore) or "
                    f"6 tokens (von Neumann), got {n}: {line!r}"
                )
        else:
            expected = 10 if detected_format == 'moore' else 6
            if n != expected:
                raise ValueError(
                    f"[{name}] Line {lineno}: inconsistent token count "
                    f"(expected {expected}, got {n}): {line!r}"
                )

        states = [_parse_token(tok, symbol_table, name, lineno) for tok in tokens]
        key: Tuple[int, ...] = tuple(states[:-1])
        next_state: int = states[-1]
        table[key] = next_state

    if detected_format == 'vn':
        return VonNeumannTableRule(table, name=name)
    return TableRule(table, name=name)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_token(tok: str, sym_table: SymbolTable, name: str, lineno: int) -> int:
    """Convert a token string to an integer state."""
    if len(tok) == 1 and sym_table.has_symbol(tok):
        return sym_table.symbol_to_state(tok)
    try:
        return int(tok)
    except ValueError:
        raise ValueError(
            f"[{name}] Line {lineno}: cannot parse token {tok!r} as state."
        )
