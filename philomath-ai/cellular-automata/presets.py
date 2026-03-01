"""
Presets / Gallery
=================
Built-in presets that combine an initial board, a rule, and display hints.

Usage
-----
    from presets import list_presets, get_preset
    print(list_presets())
    preset = get_preset("blinker")
    board  = preset.make_board()
    rule   = preset.make_rule()
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from board import Board
from rules import LifeRule, TableRule
from pattern_loader import pattern_from_rows


# ---------------------------------------------------------------------------
# Preset dataclass
# ---------------------------------------------------------------------------

@dataclass
class Preset:
    name: str
    description: str
    make_board: Callable[[], Board]
    make_rule: Callable[[], object]
    boundary: str = Board.WRAP
    n_states: int = 2
    tags: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Board factories for Life presets
# ---------------------------------------------------------------------------

def _life_board(pattern: List[List[int]], size: int = 40) -> Board:
    """Place *pattern* centred in a *size*×*size* board."""
    board = Board(size, size, boundary=Board.WRAP)
    r0 = (size - len(pattern)) // 2
    c0 = (size - len(pattern[0])) // 2
    for dr, row in enumerate(pattern):
        for dc, val in enumerate(row):
            board.set(r0 + dr, c0 + dc, val)
    return board


_BLINKER = [[1, 1, 1]]
_BLOCK   = [[1, 1], [1, 1]]
_GLIDER  = [[0, 1, 0], [0, 0, 1], [1, 1, 1]]
_TOAD    = [[0, 1, 1, 1], [1, 1, 1, 0]]
_BEACON  = [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]]
_PULSAR  = [
    [0,0,1,1,1,0,0,0,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [0,0,1,1,1,0,0,0,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,0,0,0,1,1,1,0,0],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,0,0,0,1,1,1,0,0],
]
_R_PENT  = [[0, 1, 1], [1, 1, 0], [0, 1, 0]]

# ---------------------------------------------------------------------------
# Langton's Loops board factory
# ---------------------------------------------------------------------------

_ASSETS = os.path.join(os.path.dirname(__file__), "assets")


def _langton_board() -> Board:
    seed_path = os.path.join(_ASSETS, "patterns", "langton_seed.txt")
    from pattern_loader import load_pattern
    from symbol_table import SymbolTable
    sym = SymbolTable({i: str(i) for i in range(8)})
    return load_pattern(seed_path, symbol_table=sym, boundary=Board.WRAP)


def _langton_rule() -> "VonNeumannTableRule":
    rule_path = os.path.join(_ASSETS, "rules", "langton_loops.txt")
    from rule_loader import load_table_rule
    from symbol_table import SymbolTable
    sym = SymbolTable({i: str(i) for i in range(8)})
    return load_table_rule(rule_path, symbol_table=sym, name="LangtonLoops")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_PRESETS: Dict[str, Preset] = {}


def _register(preset: Preset) -> None:
    _PRESETS[preset.name] = preset


_register(Preset(
    name="blinker",
    description="Period-2 oscillator (Game of Life).",
    make_board=lambda: _life_board(_BLINKER),
    make_rule=LifeRule,
    tags=["life", "oscillator"],
))
_register(Preset(
    name="block",
    description="2×2 still life (Game of Life).",
    make_board=lambda: _life_board(_BLOCK),
    make_rule=LifeRule,
    tags=["life", "still-life"],
))
_register(Preset(
    name="glider",
    description="Diagonal-travelling spaceship (Game of Life).",
    make_board=lambda: _life_board(_GLIDER),
    make_rule=LifeRule,
    tags=["life", "spaceship"],
))
_register(Preset(
    name="toad",
    description="Period-2 oscillator (Game of Life).",
    make_board=lambda: _life_board(_TOAD),
    make_rule=LifeRule,
    tags=["life", "oscillator"],
))
_register(Preset(
    name="beacon",
    description="Period-2 oscillator (Game of Life).",
    make_board=lambda: _life_board(_BEACON),
    make_rule=LifeRule,
    tags=["life", "oscillator"],
))
_register(Preset(
    name="pulsar",
    description="Period-3 oscillator (Game of Life).",
    make_board=lambda: _life_board(_PULSAR),
    make_rule=LifeRule,
    tags=["life", "oscillator"],
))
_register(Preset(
    name="r-pentomino",
    description="Methuselah that takes 1103 generations to stabilise (Game of Life).",
    make_board=lambda: _life_board(_R_PENT, size=80),
    make_rule=LifeRule,
    boundary=Board.WRAP,
    tags=["life", "methuselah"],
))
_register(Preset(
    name="langton-loops",
    description="Langton's Loops: self-replicating loop automaton (8 states, table-driven).",
    make_board=_langton_board,
    make_rule=_langton_rule,
    boundary=Board.WRAP,
    n_states=8,
    tags=["langton", "table-driven", "self-replication"],
))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def list_presets() -> List[str]:
    """Return names of all registered presets."""
    return list(_PRESETS.keys())


def get_preset(name: str) -> Preset:
    """Return the Preset with *name*, or raise KeyError."""
    if name not in _PRESETS:
        raise KeyError(
            f"Unknown preset {name!r}. Available: {list(_PRESETS.keys())}"
        )
    return _PRESETS[name]


def describe_presets() -> str:
    """Return a formatted table of all presets."""
    lines = ["Available presets:", ""]
    for name, p in _PRESETS.items():
        tags = ', '.join(p.tags) if p.tags else '-'
        lines.append(f"  {name:<20} {p.description}")
        lines.append(f"  {'':20} tags: {tags}")
        lines.append("")
    return '\n'.join(lines)
