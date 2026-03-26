# Cellular Automata Engine

> **Part of [Philomath AI](../README.md)** | [Python AI Course](../../README.md)  
> See also: [2D Lists](../2d-lists/) | [Genome Algorithms](../genome_algorithms/) | [Monte Carlo Simulation](../monte-carlo/) | [Election Simulation](../election-simulation/)

A self-contained Python engine for running **Conway's Game of Life** and
**Langton's Loops**, with terminal and pygame renderers, a preset gallery,
and flexible alphabet auto-detection.

---

## 📁 Module Structure

```
cellular-automata/
├── main.py              # CLI entry point
├── README.md            # This file
│
├── board.py             # Integer-state 2-D grid (fixed/wrap boundary)
├── engine.py            # Synchronous single-step engine
├── neighborhood.py      # Moore & von Neumann neighborhood keys
│
├── rules.py             # LifeRule, TableRule, VonNeumannTableRule
├── rule_loader.py       # Load table-driven rules from files
│
├── symbol_table.py      # Bidirectional state ↔ symbol mapping
├── alphabet_detect.py   # Auto-detect symbol alphabets
├── pattern_loader.py    # Load board patterns from plain-text files
│
├── render_terminal.py   # Terminal renderer
├── render_pygame.py     # Pygame renderer (circles, colour palette)
│
├── presets.py           # Built-in preset/gallery system
│
├── assets/
│   ├── rules/
│   │   └── langton_loops.txt    # Langton's Loops rule table (von Neumann, 8 states)
│   └── patterns/
│       ├── blinker.txt
│       ├── block.txt
│       ├── glider.txt
│       └── langton_seed.txt     # Classic 15×15 Langton loop seed
│
└── test_all.py          # Test suite (26 tests)
```

---

## 🚀 Quick Start

```bash
# Run from this directory:
python main.py --list                         # list presets
python main.py --preset glider                # glider in terminal
python main.py --preset blinker --no-clear    # blinker without screen clearing
python main.py --preset glider --renderer pygame --cell-size 16
python main.py --preset langton-loops --renderer pygame
python main.py --pattern assets/patterns/glider.txt --rule life
```

---

## ⌨️ CLI Reference

| Option | Default | Description |
|---|---|---|
| `--list` | — | Print preset gallery and exit |
| `--preset NAME` | `glider` | Use a built-in preset |
| `--pattern FILE` | — | Load initial board from a pattern file |
| `--rule life\|FILE` | `life` | Rule: `life` or path to a table rule file |
| `--renderer terminal\|pygame` | `terminal` | Renderer to use |
| `--boundary fixed\|wrap` | `wrap` | Boundary condition |
| `--generations N` | `0` (∞) | Generations to run (0 = unlimited) |
| `--fps N` | `5` | Frames per second |
| `--cell-size N` | `12` | Cell pixel size (pygame only) |
| `--no-clear` | — | Don't clear terminal between frames |
| `--symbols CHARS` | auto | Override symbol alphabet (e.g. `.#`) |

### Pygame key bindings
| Key | Action |
|---|---|
| `SPACE` | Pause / resume |
| `Q` / `ESC` | Quit |

---

## 🎮 Built-in Presets

| Name | Rule | Description |
|---|---|---|
| `blinker` | Life | Period-2 oscillator |
| `block` | Life | 2×2 still life |
| `glider` | Life | Diagonal spaceship |
| `toad` | Life | Period-2 oscillator |
| `beacon` | Life | Period-2 oscillator |
| `pulsar` | Life | Period-3 oscillator |
| `r-pentomino` | Life | Methuselah (1103 generations) |
| `langton-loops` | Table (VN) | Langton's self-replicating loops |

---

## 🔩 Architecture

### Board
`Board` stores states as Python `int` in a 2-D list.  Supports `fixed`
(out-of-bounds returns 0) and `wrap` (toroidal) boundary modes.

### Rules
- **`LifeRule`** – algorithmic B3/S23 rule, requires no table.
- **`TableRule`** – Moore (8-neighbour) table; key is a 9-`int` tuple.
- **`VonNeumannTableRule`** – von Neumann (4-neighbour) table; key is a
  5-`int` tuple. Used by Langton's Loops.

Strict validation: a `KeyError` is raised (with the rule name and missing
key) whenever a transition is not found.

### Alphabet Detection
`alphabet_detect.detect_alphabet(text)` inspects raw file content and
returns a `SymbolTable`:
1. **Digit-only** (`0`–`9` only) → digit = state.
2. **Dot+digit** (`.` and digits) → `.` = 0, digit = itself.
3. **Custom** (anything else) → first-appearance order.

### Pattern / Rule Files
Plain text, one row per line, characters mapped via the `SymbolTable`.
Comment lines start with `#`.

Rule files support two formats (auto-detected by token count):
- **10 tokens** – Moore: `center n0 n1 n2 n3 n4 n5 n6 n7 next`
- **6 tokens** – von Neumann: `center north west east south next`

---

## 🧪 Running Tests

```bash
python test_all.py
```

Expected: **26 tests, 0 failures**.

---

## 📦 Dependencies

| Package | Required for |
|---|---|
| (none) | core engine, terminal renderer, tests |
| `pygame` | `--renderer pygame` |

Install pygame:
```bash
pip install pygame
```
