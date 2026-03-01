"""
Test Suite for the Cellular Automata Engine
============================================

Tests cover:
  1. Symbol alphabet auto-detection
  2. Symbol mapping round-trips
  3. Life oscillator / still-life behaviour
  4. Table-rule missing-transition error
  5. Board boundary conditions
  6. Engine step correctness
  7. Pattern loading
  8. Rule loader (table rule files)
"""

from __future__ import annotations
import os
import sys
import tempfile

# ---------------------------------------------------------------------------
# Path setup – make sure the module is importable regardless of cwd
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from board import Board
from engine import Engine
from rules import LifeRule, TableRule, VonNeumannTableRule
from symbol_table import SymbolTable
from alphabet_detect import detect_alphabet, detect_alphabet_from_lines
from pattern_loader import load_pattern, pattern_from_rows
from rule_loader import load_table_rule
from neighborhood import moore_key, von_neumann_key


# ===========================================================================
# 1. Symbol alphabet auto-detection
# ===========================================================================

def test_detect_digit_only():
    print("Testing digit-only alphabet detection...", end=' ')
    sym = detect_alphabet("0 1 0\n1 0 1\n0 1 0")
    assert sym.symbol_to_state('0') == 0
    assert sym.symbol_to_state('1') == 1
    print("✓ PASSED")


def test_detect_dot_digit():
    print("Testing dot+digit alphabet detection...", end=' ')
    sym = detect_alphabet("....\n.##.\n.##.\n....")
    # '#' is a custom character – falls into the custom branch
    assert sym.has_symbol('.')
    assert sym.has_symbol('#')
    assert sym.symbol_to_state('.') == 0
    assert sym.symbol_to_state('#') == 1
    print("✓ PASSED")


def test_detect_pure_dot_digit():
    print("Testing pure dot+digit (no custom chars)...", end=' ')
    sym = detect_alphabet("0012\n1020\n0000")
    # All digits → digit-only branch
    assert sym.symbol_to_state('0') == 0
    assert sym.symbol_to_state('1') == 1
    assert sym.symbol_to_state('2') == 2
    print("✓ PASSED")


def test_detect_dot_and_digit():
    print("Testing dot+digit branch...", end=' ')
    sym = detect_alphabet(".12.\n.21.\n....")
    # dot + digits → dot-digit branch: '.' → 0, '1' → 1, '2' → 2
    assert sym.symbol_to_state('.') == 0
    assert sym.symbol_to_state('1') == 1
    assert sym.symbol_to_state('2') == 2
    print("✓ PASSED")


def test_detect_custom_symbols():
    print("Testing custom symbol alphabet detection...", end=' ')
    sym = detect_alphabet("AB\nBA\nAA")
    # First appearance: A=0, B=1
    assert sym.symbol_to_state('A') == 0
    assert sym.symbol_to_state('B') == 1
    print("✓ PASSED")


# ===========================================================================
# 2. Symbol mapping round-trips
# ===========================================================================

def test_symbol_roundtrip():
    print("Testing symbol table round-trip...", end=' ')
    st = SymbolTable({0: '.', 1: '#', 2: 'O'})
    for state, sym in [(0, '.'), (1, '#'), (2, 'O')]:
        assert st.state_to_symbol(state) == sym
        assert st.symbol_to_state(sym) == state
    print("✓ PASSED")


def test_symbol_from_list():
    print("Testing SymbolTable.from_symbols...", end=' ')
    st = SymbolTable.from_symbols(['.', '#'])
    assert st.state_to_symbol(0) == '.'
    assert st.state_to_symbol(1) == '#'
    assert st.symbol_to_state('#') == 1
    print("✓ PASSED")


# ===========================================================================
# 3. Life oscillator / still-life behaviour
# ===========================================================================

def _make_life_engine() -> Engine:
    return Engine(LifeRule())


def test_life_block_still():
    print("Testing Life block (still life)...", end=' ')
    board = pattern_from_rows([
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
    ], boundary=Board.FIXED)
    engine = _make_life_engine()
    after = engine.step(board)
    assert after == board, "Block should be stable"
    print("✓ PASSED")


def test_life_blinker_period2():
    print("Testing Life blinker (period-2 oscillator)...", end=' ')
    board = pattern_from_rows([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ], boundary=Board.FIXED)
    engine = _make_life_engine()
    gen1 = engine.step(board)
    gen2 = engine.step(gen1)
    assert gen2 == board, "Blinker must have period 2"
    assert gen1 != board, "Gen1 must differ from gen0"
    print("✓ PASSED")


def test_life_glider_moves():
    print("Testing Life glider (moves every 4 generations)...", end=' ')
    # A glider on a toroidal board should keep its cell count
    board = pattern_from_rows([
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ], boundary=Board.WRAP)
    engine = _make_life_engine()
    alive0 = sum(board.get(r, c) for r in range(8) for c in range(8))
    after4 = engine.run(board, 4)
    alive4 = sum(after4.get(r, c) for r in range(8) for c in range(8))
    assert alive0 == alive4 == 5, "Glider should always have 5 live cells"
    assert after4 != board, "Glider should have moved after 4 steps"
    print("✓ PASSED")


def test_life_death_by_isolation():
    print("Testing Life death by isolation...", end=' ')
    board = pattern_from_rows([[0, 0, 0], [0, 1, 0], [0, 0, 0]], boundary=Board.FIXED)
    engine = _make_life_engine()
    after = engine.step(board)
    assert after.get(1, 1) == 0, "Isolated cell should die"
    print("✓ PASSED")


def test_life_birth():
    print("Testing Life birth rule...", end=' ')
    board = pattern_from_rows([
        [0, 1, 0],
        [1, 0, 1],
        [0, 0, 0],
    ], boundary=Board.FIXED)
    engine = _make_life_engine()
    after = engine.step(board)
    assert after.get(1, 1) == 1, "Dead cell with 3 neighbors should be born"
    print("✓ PASSED")


# ===========================================================================
# 4. Table-rule missing-transition error
# ===========================================================================

def test_table_rule_missing_key_raises():
    print("Testing TableRule missing key raises KeyError...", end=' ')
    # Minimal table: only covers all-zero neighborhood
    table = {(0,) * 9: 0}
    rule = TableRule(table, name="MinimalTable")
    board = pattern_from_rows([[1, 0], [0, 0]])
    engine = Engine(rule)
    try:
        engine.step(board)
        assert False, "Should have raised KeyError"
    except KeyError as exc:
        assert "MinimalTable" in str(exc), "Error message should name the rule"
        assert "No transition" in str(exc)
    print("✓ PASSED")


def test_vn_table_rule_missing_key_raises():
    print("Testing VonNeumannTableRule missing key raises KeyError...", end=' ')
    table = {(0, 0, 0, 0, 0): 0}
    rule = VonNeumannTableRule(table, name="MinimalVN")
    board = pattern_from_rows([[1, 0], [0, 0]])
    engine = Engine(rule)
    try:
        engine.step(board)
        assert False, "Should have raised KeyError"
    except KeyError as exc:
        assert "MinimalVN" in str(exc)
    print("✓ PASSED")


# ===========================================================================
# 5. Board boundary conditions
# ===========================================================================

def test_board_fixed_oob():
    print("Testing Board fixed boundary (out-of-bounds returns 0)...", end=' ')
    board = Board(3, 3, boundary=Board.FIXED)
    board.set(0, 0, 1)
    assert board.get(-1, 0) == 0
    assert board.get(0, -1) == 0
    assert board.get(3, 3) == 0
    print("✓ PASSED")


def test_board_wrap_oob():
    print("Testing Board wrap boundary...", end=' ')
    board = Board(3, 3, boundary=Board.WRAP)
    board.set(0, 0, 7)
    # (3,0) wraps to (0,0): 3 % 3 == 0 → should return 7
    assert board.get(3, 0) == 7
    # (0,3) wraps to (0,0): 3 % 3 == 0 → should return 7
    assert board.get(0, 3) == 7
    # (-1,0) wraps to (2,0) in Python (-1 % 3 == 2) → should return 0
    assert board.get(-1, 0) == 0
    print("✓ PASSED")


def test_board_copy():
    print("Testing Board.copy is independent...", end=' ')
    board = Board(3, 3)
    board.set(1, 1, 5)
    copy = board.copy()
    copy.set(1, 1, 9)
    assert board.get(1, 1) == 5, "Original must not change"
    assert copy.get(1, 1) == 9
    print("✓ PASSED")


# ===========================================================================
# 6. Engine step correctness
# ===========================================================================

def test_engine_no_mutation():
    print("Testing Engine does not mutate original board...", end=' ')
    board = pattern_from_rows([[1, 1, 1], [0, 0, 0], [0, 0, 0]], boundary=Board.FIXED)
    original = board.copy()
    engine = _make_life_engine()
    engine.step(board)
    assert board == original, "Engine.step must not mutate the input board"
    print("✓ PASSED")


def test_engine_run_n_steps():
    print("Testing Engine.run(n) consistency with n×step...", end=' ')
    board = pattern_from_rows([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    engine = _make_life_engine()
    run4 = engine.run(board, 4)
    step4 = board
    for _ in range(4):
        step4 = engine.step(step4)
    assert run4 == step4, "run(4) must match 4×step()"
    print("✓ PASSED")


# ===========================================================================
# 7. Pattern loading
# ===========================================================================

def test_pattern_load_dot_hash():
    print("Testing pattern loading (dot+hash format)...", end=' ')
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    try:
        tmp.write(".....\n.###.\n.....\n")
        tmp.close()
        board = load_pattern(tmp.name, boundary=Board.FIXED)
        # Row 1 should be [0,1,1,1,0]
        assert board.get(1, 0) == 0
        assert board.get(1, 1) == 1
        assert board.get(1, 2) == 1
        assert board.get(1, 3) == 1
        assert board.get(1, 4) == 0
    finally:
        os.unlink(tmp.name)
    print("✓ PASSED")


def test_pattern_from_rows():
    print("Testing pattern_from_rows...", end=' ')
    board = pattern_from_rows([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    assert board.rows == 3
    assert board.cols == 3
    assert board.get(0, 1) == 1
    assert board.get(0, 0) == 0
    print("✓ PASSED")


# ===========================================================================
# 8. Rule loader
# ===========================================================================

def test_rule_loader_moore():
    print("Testing rule loader (Moore / 10-token format)...", end=' ')
    # Create a tiny Moore rule table: everything → 0 except all-1 → 1
    lines = []
    # A 2-state board: center in {0,1}, each of 8 neighbors in {0,1}
    # We only need to cover what the engine will encounter
    # All-zero neighborhood → 0
    lines.append("0 0 0 0 0 0 0 0 0  0")
    # All-one neighborhood → 1
    lines.append("1 1 1 1 1 1 1 1 1  1")
    content = '\n'.join(lines)
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    try:
        tmp.write(content)
        tmp.close()
        rule = load_table_rule(tmp.name, name="TestMoore")
        # Verify keys
        assert rule.table[(0,) * 9] == 0
        assert rule.table[(1,) * 9] == 1
    finally:
        os.unlink(tmp.name)
    print("✓ PASSED")


def test_rule_loader_vn():
    print("Testing rule loader (von Neumann / 6-token format)...", end=' ')
    lines = [
        "0 0 0 0 0  0",
        "1 0 0 0 0  1",
        "0 1 0 0 0  0",
    ]
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    try:
        tmp.write('\n'.join(lines))
        tmp.close()
        rule = load_table_rule(tmp.name)
        assert isinstance(rule, VonNeumannTableRule)
        assert rule.table[(0, 0, 0, 0, 0)] == 0
        assert rule.table[(1, 0, 0, 0, 0)] == 1
    finally:
        os.unlink(tmp.name)
    print("✓ PASSED")


def test_rule_loader_bad_token_count():
    print("Testing rule loader rejects wrong token count...", end=' ')
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    try:
        tmp.write("0 1 2 3  0\n")  # only 5 tokens
        tmp.close()
        try:
            load_table_rule(tmp.name)
            assert False, "Should have raised ValueError"
        except ValueError as exc:
            assert "expected 10" in str(exc) or "expected" in str(exc).lower()
    finally:
        os.unlink(tmp.name)
    print("✓ PASSED")


# ===========================================================================
# 9. Neighborhood keys
# ===========================================================================

def test_moore_key_shape():
    print("Testing moore_key returns 9-element tuple...", end=' ')
    board = Board.from_list([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    key = moore_key(board, 1, 1)
    assert isinstance(key, tuple)
    assert len(key) == 9
    assert key[0] == board.get(1, 1)  # center
    print("✓ PASSED")


def test_von_neumann_key_shape():
    print("Testing von_neumann_key returns 5-element tuple...", end=' ')
    board = Board.from_list([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    key = von_neumann_key(board, 1, 1)
    assert isinstance(key, tuple)
    assert len(key) == 5
    assert key[0] == board.get(1, 1)  # center
    print("✓ PASSED")


# ===========================================================================
# Runner
# ===========================================================================

def run_all_tests():
    print("=" * 70)
    print("RUNNING TESTS FOR CELLULAR AUTOMATA ENGINE")
    print("=" * 70)
    print()

    tests = [
        # Alphabet detection
        test_detect_digit_only,
        test_detect_dot_digit,
        test_detect_pure_dot_digit,
        test_detect_dot_and_digit,
        test_detect_custom_symbols,
        # Symbol mapping
        test_symbol_roundtrip,
        test_symbol_from_list,
        # Life patterns
        test_life_block_still,
        test_life_blinker_period2,
        test_life_glider_moves,
        test_life_death_by_isolation,
        test_life_birth,
        # Table rule errors
        test_table_rule_missing_key_raises,
        test_vn_table_rule_missing_key_raises,
        # Board
        test_board_fixed_oob,
        test_board_wrap_oob,
        test_board_copy,
        # Engine
        test_engine_no_mutation,
        test_engine_run_n_steps,
        # Pattern loading
        test_pattern_load_dot_hash,
        test_pattern_from_rows,
        # Rule loader
        test_rule_loader_moore,
        test_rule_loader_vn,
        test_rule_loader_bad_token_count,
        # Neighborhood
        test_moore_key_shape,
        test_von_neumann_key_shape,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as exc:
            print(f"  ✗ FAILED: {exc}")
            failed += 1
        except Exception as exc:
            print(f"  ✗ ERROR: {type(exc).__name__}: {exc}")
            failed += 1

    print()
    print("=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
