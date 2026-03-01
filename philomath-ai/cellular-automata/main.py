"""
Cellular Automata Engine – CLI entry point
==========================================

Usage examples
--------------
  python main.py --list
  python main.py --preset glider
  python main.py --preset glider --renderer terminal --fps 5
  python main.py --preset langton-loops --renderer pygame --cell-size 8
  python main.py --preset blinker --boundary fixed --generations 10
  python main.py --pattern assets/patterns/glider.txt --rule life
"""

from __future__ import annotations
import argparse
import os
import sys
import time

# ---------------------------------------------------------------------------
# Allow running from any cwd by adding this directory to sys.path
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from board import Board
from engine import Engine
from rules import LifeRule
from presets import describe_presets, get_preset, list_presets
from render_terminal import TerminalRenderer
from symbol_table import SymbolTable


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _symbol_table_for_n(n_states: int) -> SymbolTable:
    """Return a simple digit SymbolTable for n_states <= 10."""
    return SymbolTable({i: str(i) for i in range(n_states)})


def _build_life_symbol_table() -> SymbolTable:
    return SymbolTable({0: '·', 1: '█'})


def _run_terminal(
    board: Board,
    engine: Engine,
    symbol_table: SymbolTable,
    generations: int,
    fps: float,
    clear: bool,
) -> None:
    renderer = TerminalRenderer(symbol_table=symbol_table, clear=clear)
    delay = 1.0 / fps if fps > 0 else 0
    current = board
    for gen in range(generations if generations > 0 else 10 ** 9):
        renderer.render(current, generation=gen)
        if generations > 0 and gen == generations - 1:
            break
        current = engine.step(current)
        if delay:
            time.sleep(delay)


def _run_pygame(
    board: Board,
    engine: Engine,
    fps: int,
    cell_size: int,
    title: str,
) -> None:
    try:
        from render_pygame import PygameRenderer
    except ImportError:
        print("pygame is not installed. Install it with: pip install pygame")
        sys.exit(1)
    renderer = PygameRenderer(cell_size=cell_size, fps=fps, title=title)
    renderer.run(board, engine)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cellular-automata",
        description="Cellular Automata Engine – Game of Life, Langton's Loops, and more.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    p.add_argument("--list", action="store_true", help="List available presets and exit.")

    p.add_argument("--preset", metavar="NAME", help="Name of a built-in preset to run.")
    p.add_argument(
        "--pattern", metavar="FILE",
        help="Path to a plain-text pattern file (overrides --preset pattern).",
    )
    p.add_argument(
        "--rule", metavar="NAME|FILE",
        default="life",
        help="Rule to use: 'life' or path to a table rule file. Default: life.",
    )

    p.add_argument(
        "--renderer", choices=["terminal", "pygame"], default="terminal",
        help="Renderer to use. Default: terminal.",
    )
    p.add_argument(
        "--boundary", choices=["fixed", "wrap"], default="wrap",
        help="Boundary condition. Default: wrap.",
    )
    p.add_argument(
        "--generations", type=int, default=0,
        help="Number of generations to run (0 = unlimited). Default: 0.",
    )
    p.add_argument("--fps", type=float, default=5.0, help="Frames per second. Default: 5.")
    p.add_argument(
        "--cell-size", type=int, default=12, dest="cell_size",
        help="Pixel size of each cell (pygame only). Default: 12.",
    )
    p.add_argument(
        "--no-clear", action="store_true", dest="no_clear",
        help="Don't clear the terminal between frames.",
    )
    p.add_argument(
        "--symbols", metavar="CHARS",
        help="Symbol alphabet override (e.g. '.#' maps state 0→'.', 1→'#').",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        print(describe_presets())
        return 0

    # ---- Resolve preset / board / rule ----
    boundary = args.boundary

    if args.preset:
        try:
            preset = get_preset(args.preset)
        except KeyError as exc:
            print(f"Error: {exc}")
            print(f"Available presets: {', '.join(list_presets())}")
            return 1
        board = preset.make_board()
        board.boundary = boundary  # allow CLI override
        rule = preset.make_rule()
        n_states = preset.n_states
        title = f"Cellular Automata – {args.preset}"

    elif args.pattern:
        from pattern_loader import load_pattern
        sym = None
        if args.symbols:
            sym = SymbolTable({i: c for i, c in enumerate(args.symbols)})
        board = load_pattern(args.pattern, symbol_table=sym, boundary=boundary)
        rule = _resolve_rule(args.rule)
        n_states = 2
        title = f"Cellular Automata – {os.path.basename(args.pattern)}"

    else:
        # Default: glider
        preset = get_preset("glider")
        board = preset.make_board()
        board.boundary = boundary
        rule = preset.make_rule()
        n_states = preset.n_states
        title = "Cellular Automata – glider (default)"

    # ---- Symbol table ----
    if args.symbols:
        sym_table = SymbolTable({i: c for i, c in enumerate(args.symbols)})
    elif n_states == 2:
        sym_table = _build_life_symbol_table()
    else:
        sym_table = _symbol_table_for_n(n_states)

    engine = Engine(rule)

    # ---- Run ----
    if args.renderer == "pygame":
        _run_pygame(board, engine, fps=int(args.fps), cell_size=args.cell_size, title=title)
    else:
        _run_terminal(
            board, engine, sym_table,
            generations=args.generations,
            fps=args.fps,
            clear=not args.no_clear,
        )

    return 0


def _resolve_rule(rule_arg: str):
    if rule_arg.lower() == "life":
        return LifeRule()
    # Treat as a file path
    if os.path.isfile(rule_arg):
        from rule_loader import load_table_rule
        return load_table_rule(rule_arg)
    raise ValueError(f"Unknown rule {rule_arg!r}. Use 'life' or a path to a rule file.")


if __name__ == "__main__":
    sys.exit(main())
