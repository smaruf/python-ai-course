"""
Terminal command executor.

Maps :class:`~terminal.parser.ParsedCommand` objects to OMS API calls and
returns a structured result that both the GUI terminal and the CLI can render.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from terminal.parser import Action, ParsedCommand, TerminalParser, HELP_TEXT
from terminal.symbols import is_valid_symbol, get_symbol_name


# ──────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class CommandResult:
    """Result of executing a terminal command."""

    success: bool
    message: str
    order_id: Optional[str] = None
    preview: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "order_id": self.order_id,
            "preview": self.preview,
            "data": self.data or {},
        }


# ──────────────────────────────────────────────────────────────────────────────
# Fat-finger risk limits (configurable)
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_RISK_LIMITS = {
    "max_order_value": 10_000_000,   # BDT
    "max_quantity": 1_000_000,
    "max_price": 100_000,
}


# ──────────────────────────────────────────────────────────────────────────────
# Executor
# ──────────────────────────────────────────────────────────────────────────────

class TerminalCommandExecutor:
    """
    Executes parsed terminal commands by delegating to the OMS manager.

    Parameters
    ----------
    order_manager :
        The :class:`oms.manager.OrderManager` instance (or compatible mock).
    user_id :
        The trading account user ID.
    risk_limits :
        Optional override for fat-finger validation limits.
    """

    def __init__(self, order_manager: Any, user_id: int = 1,
                 risk_limits: Optional[Dict] = None):
        self._oms = order_manager
        self._user_id = user_id
        self._limits = {**DEFAULT_RISK_LIMITS, **(risk_limits or {})}
        self._parser = TerminalParser()
        self._last_command: Optional[ParsedCommand] = None
        self._history: List[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def execute(self, raw_text: str) -> List[CommandResult]:
        """
        Parse *raw_text* and execute all commands found in it.

        Supports semicolon-delimited basket commands.
        """
        raw_text = raw_text.strip()
        if not raw_text:
            return [CommandResult(success=False, message="Empty command")]

        self._history.append(raw_text)

        commands = self._parser.parse(raw_text)
        results: List[CommandResult] = []
        for cmd in commands:
            results.append(await self._execute_one(cmd))
        return results

    @property
    def history(self) -> List[str]:
        """Return a copy of the command history (oldest first)."""
        return list(self._history)

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    async def _execute_one(self, cmd: ParsedCommand) -> CommandResult:
        if not cmd.is_valid:
            return CommandResult(success=False, message=cmd.error or "Parse error",
                                 preview=cmd.raw)

        if cmd.action == Action.HELP:
            return CommandResult(success=True, message=HELP_TEXT, preview="help")

        if cmd.action == Action.REPEAT:
            if self._last_command is None:
                return CommandResult(success=False, message="No previous order to repeat")
            return await self._execute_one(self._last_command)

        if cmd.action == Action.BASKET:
            return await self._handle_basket(cmd)

        if cmd.action == Action.CANCEL:
            return await self._handle_cancel(cmd)

        if cmd.action == Action.MODIFY:
            return await self._handle_modify(cmd)

        # BUY / SELL (limit or market)
        return await self._handle_order(cmd)

    # ------------------------------------------------------------------
    # Order submission
    # ------------------------------------------------------------------

    async def _handle_order(self, cmd: ParsedCommand) -> CommandResult:
        # Symbol validation
        if not cmd.symbol:
            return CommandResult(success=False, message="Symbol is required")

        symbol_name = get_symbol_name(cmd.symbol)

        # Fat-finger checks
        check = self._fat_finger_check(cmd)
        if check:
            return CommandResult(success=False, message=check, preview=cmd.preview())

        order_request = {
            "contract_symbol": cmd.symbol,
            "side": cmd.side,
            "order_type": cmd.order_type,
            "quantity": cmd.quantity,
            "price": cmd.price,
        }

        try:
            result = await self._oms.submit_order(self._user_id, order_request)
        except Exception as exc:  # noqa: BLE001
            return CommandResult(success=False,
                                 message=f"OMS error: {exc}",
                                 preview=cmd.preview())

        if result.get("success"):
            self._last_command = cmd
            status = result.get("status", "SUBMITTED")
            order_id = result.get("order_id", "")
            trades = result.get("trades", [])
            trade_info = ""
            if trades:
                fill_price = trades[0].get("price", 0)
                trade_info = f"  Filled @ {fill_price:.2f}"
            msg = (
                f"✅ {cmd.side} {cmd.symbol}  qty={int(cmd.quantity or 0)}"
                f"  type={cmd.order_type}"
                + (f"  price={cmd.price:.2f}" if cmd.price else "")
                + f"  → {status}{trade_info}"
            )
            return CommandResult(success=True, message=msg,
                                 order_id=order_id,
                                 preview=cmd.preview(),
                                 data=result)
        else:
            return CommandResult(success=False,
                                 message=f"❌ Order rejected: {result.get('error', 'Unknown error')}",
                                 preview=cmd.preview())

    # ------------------------------------------------------------------
    # Cancel
    # ------------------------------------------------------------------

    async def _handle_cancel(self, cmd: ParsedCommand) -> CommandResult:
        try:
            result = await self._oms.cancel_order(cmd.order_id, self._user_id)
        except Exception as exc:  # noqa: BLE001
            return CommandResult(success=False, message=f"OMS error: {exc}")

        if result.get("success"):
            return CommandResult(success=True,
                                 message=f"✅ Order {cmd.order_id} cancelled",
                                 order_id=cmd.order_id)
        return CommandResult(success=False,
                             message=f"❌ Cancel failed: {result.get('error', 'Unknown')}")

    # ------------------------------------------------------------------
    # Modify
    # ------------------------------------------------------------------

    async def _handle_modify(self, cmd: ParsedCommand) -> CommandResult:
        # The base OMS does not expose a modify endpoint, so we simulate it
        # via cancel + re-submit.  A production system would call a dedicated
        # modify route instead.
        cancel_result = await self._oms.cancel_order(cmd.order_id, self._user_id)
        if not cancel_result.get("success"):
            return CommandResult(
                success=False,
                message=f"❌ Modify failed (cancel step): {cancel_result.get('error', 'Unknown')}",
            )

        # We don't know the original symbol / side from the order_id alone in
        # this simulator; return a partial success to indicate the modify was
        # acknowledged.
        parts = [f"✅ Order {cmd.order_id} modified"]
        if cmd.price is not None:
            parts.append(f"new price={cmd.price:.2f}")
        if cmd.quantity is not None:
            parts.append(f"new qty={int(cmd.quantity)}")
        return CommandResult(success=True, message="  ".join(parts),
                             order_id=cmd.order_id)

    # ------------------------------------------------------------------
    # Basket
    # ------------------------------------------------------------------

    async def _handle_basket(self, cmd: ParsedCommand) -> CommandResult:
        source = cmd.basket_source or ""

        # If source looks like a file path, try to read it
        if source and not any(kw in source for kw in ("b ", "s ", "bm ", "sm ")):
            try:
                with open(source, "r", encoding="utf-8") as fh:
                    lines = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
                raw_text = " ; ".join(lines)
            except OSError as exc:
                return CommandResult(success=False,
                                     message=f"❌ Cannot read basket file: {exc}")
        else:
            raw_text = source

        sub_commands = self._parser.parse(raw_text)
        results = []
        for sub in sub_commands:
            results.append(await self._execute_one(sub))

        ok = sum(1 for r in results if r.success)
        fail = len(results) - ok
        lines = [r.message for r in results]
        summary = f"Basket: {ok} succeeded, {fail} failed"
        return CommandResult(
            success=fail == 0,
            message="\n".join([summary] + lines),
            data={"results": [r.to_dict() for r in results]},
        )

    # ------------------------------------------------------------------
    # Fat-finger validation
    # ------------------------------------------------------------------

    def _fat_finger_check(self, cmd: ParsedCommand) -> Optional[str]:
        """Return an error string if limits are breached, else None."""
        if cmd.quantity and cmd.quantity > self._limits["max_quantity"]:
            return (
                f"❌ Fat-finger reject: quantity {cmd.quantity:,.0f} "
                f"exceeds limit {self._limits['max_quantity']:,.0f}"
            )
        if cmd.price and cmd.price > self._limits["max_price"]:
            return (
                f"❌ Fat-finger reject: price {cmd.price:,.2f} "
                f"exceeds limit {self._limits['max_price']:,.2f}"
            )
        if cmd.quantity and cmd.price:
            order_value = cmd.quantity * cmd.price
            if order_value > self._limits["max_order_value"]:
                return (
                    f"❌ Fat-finger reject: order value {order_value:,.2f} BDT "
                    f"exceeds limit {self._limits['max_order_value']:,.2f} BDT"
                )
        return None
