"""
Tests for the OMS Terminal / Command Mode feature.
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from terminal.parser import TerminalParser, Action, ParsedCommand, HELP_TEXT
from terminal.symbols import autocomplete, is_valid_symbol, get_symbol_name
from terminal.commands import TerminalCommandExecutor, CommandResult


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

def _make_oms(submit_ok: bool = True, cancel_ok: bool = True) -> MagicMock:
    """Return a mock OMS with configurable success flags."""
    oms = MagicMock()
    oms.submit_order = AsyncMock(return_value={
        "success": submit_ok,
        "order_id": "ORD-001",
        "status": "FILLED",
        "trades": [{"trade_id": "TRD-001", "price": 25.40, "quantity": 100}],
        "error": None if submit_ok else "Insufficient balance",
    })
    oms.cancel_order = AsyncMock(return_value={
        "success": cancel_ok,
        "error": None if cancel_ok else "Order not found",
    })
    oms.get_user_orders = AsyncMock(return_value=[])
    return oms


# ──────────────────────────────────────────────────────────────────────────────
# Parser tests
# ──────────────────────────────────────────────────────────────────────────────

class TestTerminalParser:
    """Unit tests for TerminalParser."""

    def setup_method(self):
        self.parser = TerminalParser()

    def _single(self, text: str) -> ParsedCommand:
        cmds = self.parser.parse(text)
        assert len(cmds) == 1
        return cmds[0]

    # ── buy ──────────────────────────────────────────────────────────────────

    def test_buy_limit(self):
        cmd = self._single("b BATBC 100 25.40")
        assert cmd.action == Action.BUY
        assert cmd.symbol == "BATBC"
        assert cmd.quantity == 100.0
        assert cmd.price == 25.40
        assert cmd.order_type == "LIMIT"
        assert cmd.side == "BUY"
        assert cmd.is_valid

    def test_buy_market(self):
        cmd = self._single("bm GP 200")
        assert cmd.action == Action.BUY_MARKET
        assert cmd.symbol == "GP"
        assert cmd.quantity == 200.0
        assert cmd.price is None
        assert cmd.order_type == "MARKET"

    def test_buy_alias(self):
        cmd = self._single("buy BATBC 50 25.00")
        assert cmd.action == Action.BUY

    # ── sell ─────────────────────────────────────────────────────────────────

    def test_sell_limit(self):
        cmd = self._single("s GP 500 350")
        assert cmd.action == Action.SELL
        assert cmd.symbol == "GP"
        assert cmd.quantity == 500.0
        assert cmd.price == 350.0
        assert cmd.side == "SELL"

    def test_sell_market(self):
        cmd = self._single("sm BATBC 300")
        assert cmd.action == Action.SELL_MARKET
        assert cmd.quantity == 300.0

    # ── cancel ───────────────────────────────────────────────────────────────

    def test_cancel(self):
        cmd = self._single("c 982734")
        assert cmd.action == Action.CANCEL
        assert cmd.order_id == "982734"
        assert cmd.is_valid

    def test_cancel_no_id(self):
        cmd = self._single("c")
        assert not cmd.is_valid
        assert "order ID" in (cmd.error or "")

    # ── modify ───────────────────────────────────────────────────────────────

    def test_modify_price_and_qty(self):
        cmd = self._single("m 982734 25.60 200")
        assert cmd.action == Action.MODIFY
        assert cmd.order_id == "982734"
        assert cmd.price == 25.60
        assert cmd.quantity == 200.0

    def test_modify_price_only(self):
        cmd = self._single("m 982734 25.60")
        assert cmd.action == Action.MODIFY
        assert cmd.price == 25.60
        assert cmd.quantity is None

    # ── quantity shorthands ───────────────────────────────────────────────────

    def test_quantity_5k(self):
        cmd = self._single("b BATBC 5k 25.40")
        assert cmd.quantity == 5000.0
        assert not cmd.quantity_is_pct

    def test_quantity_2_5k(self):
        cmd = self._single("b BATBC 2.5k 25.40")
        assert cmd.quantity == 2500.0

    def test_quantity_percentage(self):
        cmd = self._single("s BATBC 50%")
        # percentage with no price — missing price token → parse error for limit
        # but the qty_is_pct flag should be set if we get that far
        # Because "s BATBC 50%" only has 3 tokens → error (missing price)
        assert not cmd.is_valid

    def test_quantity_percentage_with_market(self):
        # Market sell: sm BATBC 50%
        cmd = self._single("sm BATBC 50%")
        assert cmd.is_valid
        assert cmd.quantity_is_pct is True
        assert cmd.quantity == 50.0

    # ── repeat / help ─────────────────────────────────────────────────────────

    def test_repeat(self):
        cmd = self._single("rr")
        assert cmd.action == Action.REPEAT
        assert cmd.is_valid

    def test_help(self):
        cmd = self._single("help")
        assert cmd.action == Action.HELP

    def test_help_question_mark(self):
        cmd = self._single("?")
        assert cmd.action == Action.HELP

    # ── basket (semicolons) ───────────────────────────────────────────────────

    def test_basket_semicolon(self):
        cmds = self.parser.parse("b GP 100 350 ; s BATBC 200 25.4")
        assert len(cmds) == 2
        assert cmds[0].action == Action.BUY
        assert cmds[1].action == Action.SELL

    # ── unknown / error ───────────────────────────────────────────────────────

    def test_unknown_action(self):
        cmd = self._single("xyz GP 100 350")
        assert cmd.action == Action.UNKNOWN
        assert not cmd.is_valid

    def test_empty(self):
        cmds = self.parser.parse("")
        assert all(not c.is_valid for c in cmds)

    def test_buy_missing_price(self):
        cmd = self._single("b BATBC 100")
        assert not cmd.is_valid

    # ── symbol normalisation ──────────────────────────────────────────────────

    def test_symbol_uppercased(self):
        cmd = self._single("b batbc 100 25.40")
        assert cmd.symbol == "BATBC"

    # ── preview string ────────────────────────────────────────────────────────

    def test_preview_buy_limit(self):
        cmd = self._single("b BATBC 100 25.40")
        preview = cmd.preview()
        assert "Buy" in preview
        assert "BATBC" in preview
        assert "25.40" in preview

    def test_preview_cancel(self):
        cmd = self._single("c 982734")
        assert "982734" in cmd.preview()


# ──────────────────────────────────────────────────────────────────────────────
# Symbol registry tests
# ──────────────────────────────────────────────────────────────────────────────

class TestSymbolRegistry:
    def test_known_symbol(self):
        assert is_valid_symbol("BATBC")
        assert is_valid_symbol("GP")

    def test_case_insensitive(self):
        assert is_valid_symbol("batbc")
        assert is_valid_symbol("Gp")

    def test_unknown_symbol(self):
        assert not is_valid_symbol("XYZNOTREAL")

    def test_get_name(self):
        name = get_symbol_name("GP")
        assert "Grameenphone" in name

    def test_autocomplete_prefix(self):
        results = autocomplete("BAT")
        symbols = [r["symbol"] for r in results]
        assert "BATBC" in symbols

    def test_autocomplete_case_insensitive(self):
        results = autocomplete("bat")
        symbols = [r["symbol"] for r in results]
        assert "BATBC" in symbols

    def test_autocomplete_no_match(self):
        results = autocomplete("ZZZZZ")
        assert results == []

    def test_autocomplete_max_results(self):
        results = autocomplete("B", max_results=3)
        assert len(results) <= 3

    def test_autocomplete_returns_dict(self):
        results = autocomplete("GP")
        assert all("symbol" in r and "name" in r for r in results)


# ──────────────────────────────────────────────────────────────────────────────
# Executor tests
# ──────────────────────────────────────────────────────────────────────────────

class TestTerminalCommandExecutor:
    def _executor(self, **oms_kwargs) -> TerminalCommandExecutor:
        return TerminalCommandExecutor(
            order_manager=_make_oms(**oms_kwargs),
            user_id=1,
        )

    @pytest.mark.asyncio
    async def test_execute_buy_limit(self):
        ex = self._executor()
        results = await ex.execute("b BATBC 100 25.40")
        assert len(results) == 1
        assert results[0].success
        assert results[0].order_id == "ORD-001"

    @pytest.mark.asyncio
    async def test_execute_buy_market(self):
        ex = self._executor()
        results = await ex.execute("bm GP 200")
        assert results[0].success

    @pytest.mark.asyncio
    async def test_execute_sell_limit(self):
        ex = self._executor()
        results = await ex.execute("s GP 500 350")
        assert results[0].success

    @pytest.mark.asyncio
    async def test_execute_cancel(self):
        ex = self._executor()
        results = await ex.execute("c ORDER-123")
        assert results[0].success

    @pytest.mark.asyncio
    async def test_execute_cancel_not_found(self):
        ex = self._executor(cancel_ok=False)
        results = await ex.execute("c ORDER-999")
        assert not results[0].success
        assert "Cancel failed" in results[0].message

    @pytest.mark.asyncio
    async def test_execute_help(self):
        ex = self._executor()
        results = await ex.execute("help")
        assert results[0].success
        assert "OMS Terminal" in results[0].message

    @pytest.mark.asyncio
    async def test_execute_repeat_no_history(self):
        ex = self._executor()
        results = await ex.execute("rr")
        assert not results[0].success
        assert "No previous" in results[0].message

    @pytest.mark.asyncio
    async def test_execute_repeat_after_order(self):
        ex = self._executor()
        await ex.execute("b BATBC 100 25.40")
        results = await ex.execute("rr")
        assert results[0].success

    @pytest.mark.asyncio
    async def test_basket_semicolons(self):
        ex = self._executor()
        results = await ex.execute("b GP 100 350 ; s BATBC 200 25.4")
        assert len(results) == 2
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_fat_finger_qty(self):
        ex = self._executor()
        ex._limits["max_quantity"] = 500
        results = await ex.execute("b BATBC 1000 25.40")
        assert not results[0].success
        assert "Fat-finger" in results[0].message

    @pytest.mark.asyncio
    async def test_fat_finger_value(self):
        ex = self._executor()
        ex._limits["max_order_value"] = 1000
        results = await ex.execute("b BATBC 100 25.40")  # 100 * 25.40 = 2540 > 1000
        assert not results[0].success
        assert "Fat-finger" in results[0].message

    @pytest.mark.asyncio
    async def test_command_history_stored(self):
        ex = self._executor()
        await ex.execute("b BATBC 100 25.40")
        await ex.execute("s GP 50 350")
        hist = ex.history
        assert "b BATBC 100 25.40" in hist
        assert "s GP 50 350" in hist

    @pytest.mark.asyncio
    async def test_oms_submit_failure(self):
        ex = self._executor(submit_ok=False)
        results = await ex.execute("b BATBC 100 25.40")
        assert not results[0].success

    @pytest.mark.asyncio
    async def test_unknown_command(self):
        ex = self._executor()
        results = await ex.execute("xyz BATBC 100 25.40")
        assert not results[0].success

    @pytest.mark.asyncio
    async def test_modify_order(self):
        ex = self._executor()
        results = await ex.execute("m ORDER-001 26.00 150")
        assert results[0].success
        assert "modified" in results[0].message.lower()

    @pytest.mark.asyncio
    async def test_result_to_dict(self):
        ex = self._executor()
        results = await ex.execute("b BATBC 100 25.40")
        d = results[0].to_dict()
        assert "success" in d
        assert "message" in d
        assert "order_id" in d
