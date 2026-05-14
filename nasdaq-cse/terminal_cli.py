#!/usr/bin/env python3
"""
OMS Terminal CLI — Ultra-Fast Order Entry (standalone)

Launch with::

    python terminal_cli.py

or::

    python terminal_cli.py --user-id 2 --host http://localhost:8000

Type ``help`` or ``?`` inside the terminal for command syntax.

Dependencies: only the standard library + the local terminal package.
Optional: ``requests`` for live OMS integration (falls back to simulation).
"""
from __future__ import annotations

import argparse
import asyncio
import cmd
import sys
import os
import textwrap
from typing import List, Optional

# ── allow running from the nasdaq-cse directory or from the repo root ──────────
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from terminal.parser import TerminalParser, Action, HELP_TEXT
from terminal.symbols import autocomplete, is_valid_symbol
from terminal.commands import TerminalCommandExecutor, CommandResult


# ──────────────────────────────────────────────────────────────────────────────
# Simulated OMS  (used when no live server is available)
# ──────────────────────────────────────────────────────────────────────────────

class _SimulatedOMS:
    """
    Minimal in-memory OMS simulation for offline / demo use.
    """

    def __init__(self) -> None:
        self._orders: dict = {}
        self._next_id: int = 100001

    async def submit_order(self, user_id: int, order_request: dict) -> dict:
        import random
        order_id = str(self._next_id)
        self._next_id += 1
        is_market = order_request.get("order_type") == "MARKET"
        status = "FILLED" if is_market else "PENDING"
        # Use provided limit price or simulate a market execution price
        limit_price = order_request.get("price")
        exec_price = limit_price if limit_price else round(100.0 * (1 + random.uniform(-0.005, 0.005)), 2)
        self._orders[order_id] = {**order_request, "status": status, "user_id": user_id}
        trades = []
        if status == "FILLED":
            trades = [{"trade_id": f"T{order_id}", "price": exec_price, "quantity": order_request.get("quantity", 0)}]
        return {
            "success": True,
            "order_id": order_id,
            "status": status,
            "trades": trades,
        }

    async def cancel_order(self, order_id: str, user_id: int) -> dict:
        if order_id in self._orders:
            self._orders[order_id]["status"] = "CANCELLED"
            return {"success": True}
        return {"success": False, "error": "Order not found"}

    async def get_user_orders(self, user_id: int, limit: int = 20) -> list:
        return [
            {"order_id": oid, **data}
            for oid, data in list(self._orders.items())[-limit:]
            if data.get("user_id") == user_id
        ]


# ──────────────────────────────────────────────────────────────────────────────
# HTTP OMS client (optional live integration)
# ──────────────────────────────────────────────────────────────────────────────

class _HttpOMS:
    """
    Thin async wrapper around the REST API exposed by ``main.py``.
    Requires the ``requests`` package.
    """

    def __init__(self, base_url: str) -> None:
        self._base = base_url.rstrip("/")
        try:
            import requests
            self._requests = requests
        except ImportError:
            print("⚠  'requests' not installed — falling back to simulation mode.")
            raise

    async def submit_order(self, user_id: int, order_request: dict) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._requests.post(
                f"{self._base}/api/orders",
                json=order_request,
                params={"user_id": user_id},
                timeout=5,
            ).json(),
        )

    async def cancel_order(self, order_id: str, user_id: int) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._requests.delete(
                f"{self._base}/api/orders/{order_id}",
                params={"user_id": user_id},
                timeout=5,
            ).json(),
        )

    async def get_user_orders(self, user_id: int, limit: int = 20) -> list:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._requests.get(
                f"{self._base}/api/orders",
                params={"user_id": user_id, "limit": limit},
                timeout=5,
            ).json(),
        )


# ──────────────────────────────────────────────────────────────────────────────
# Interactive terminal (cmd.Cmd)
# ──────────────────────────────────────────────────────────────────────────────

BANNER = r"""
  ___  __  __ ____    _____                   _             _
 / _ \|  \/  / ___|  |_   _|__ _ __ _ __ ___ (_)_ __   __ _| |
| | | | |\/| \___ \    | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | |
| |_| | |  | |___) |   | |  __/ |  | | | | | | | | | | (_| | |
 \___/|_|  |_|____/    |_|\___|_|  |_| |_| |_|_|_| |_|\__,_|_|

  Ultra-Fast Order Entry   •   Type 'help' or '?' for commands
  Ctrl-D / 'exit' / 'quit' to leave
"""

PROMPT = "⚡ > "


class OMSTerminalShell(cmd.Cmd):
    """Interactive OMS terminal built on top of Python's cmd.Cmd."""

    intro = BANNER
    prompt = PROMPT

    def __init__(self, executor: TerminalCommandExecutor) -> None:
        super().__init__()
        self._executor = executor
        self._loop = asyncio.new_event_loop()

    # ------------------------------------------------------------------
    # Core command dispatch
    # ------------------------------------------------------------------

    def default(self, line: str) -> None:
        """Handle any line that isn't a built-in Cmd command."""
        line = line.strip()
        if not line:
            return
        results: List[CommandResult] = self._loop.run_until_complete(
            self._executor.execute(line)
        )
        for result in results:
            self._print_result(result)

    def do_exit(self, _: str) -> bool:
        """Exit the terminal."""
        print("\n👋  Goodbye!")
        return True

    def do_quit(self, _: str) -> bool:
        """Exit the terminal."""
        return self.do_exit(_)

    def do_EOF(self, _: str) -> bool:  # noqa: N802
        """Handle Ctrl-D."""
        print()
        return self.do_exit(_)

    # ------------------------------------------------------------------
    # Built-in convenience commands
    # ------------------------------------------------------------------

    def do_orders(self, _: str) -> None:
        """List your recent orders."""
        orders = self._loop.run_until_complete(
            self._executor._oms.get_user_orders(self._executor._user_id, 10)
        )
        if not orders:
            print("  (no orders)")
            return
        print(f"  {'ORDER ID':<36} {'SIDE':<5} {'SYMBOL':<12} {'QTY':>8} {'PRICE':>10} {'STATUS':<14}")
        print("  " + "─" * 88)
        for o in orders:
            print(
                f"  {o.get('order_id',''):<36} "
                f"{o.get('side',''):<5} "
                f"{o.get('contract_symbol', o.get('symbol', '')):<12} "
                f"{o.get('quantity', 0):>8.0f} "
                f"{(o.get('price') or 0):>10.2f} "
                f"{o.get('status',''):<14}"
            )

    def do_history(self, _: str) -> None:
        """Show command history."""
        hist = self._executor.history
        if not hist:
            print("  (no history)")
            return
        for i, entry in enumerate(hist[-20:], 1):
            print(f"  {i:3d}  {entry}")

    def do_clearhistory(self, _: str) -> None:
        """Clear command history: clearhistory"""
        self._executor.clear_history()
        if sys.stdout.isatty():
            # Also clear the terminal screen
            print("\033[2J\033[H", end="")
        print("  History cleared.")

    def do_cls(self, _: str) -> None:
        """Clear screen and command history: cls"""
        self.do_clearhistory(_)

    def do_complete(self, symbol_prefix: str) -> None:
        """Autocomplete symbol: complete <prefix>"""
        matches = autocomplete(symbol_prefix.strip(), max_results=15)
        if not matches:
            print("  (no matches)")
            return
        for m in matches:
            print(f"  {m['symbol']:<16} {m['name']}")

    # ------------------------------------------------------------------
    # Tab completion for symbols (after b / s / bm / sm)
    # ------------------------------------------------------------------

    def completedefault(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        tokens = line.split()
        if len(tokens) >= 2:
            prefix = tokens[-1] if not line.endswith(" ") else ""
            return [m["symbol"] for m in autocomplete(prefix)]
        return []

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _print_result(self, result: CommandResult) -> None:
        colour = "\033[92m" if result.success else "\033[91m"
        reset = "\033[0m"
        if sys.stdout.isatty():
            print(f"{colour}{result.message}{reset}")
        else:
            print(result.message)

        if result.preview and result.preview not in ("help", "Show help"):
            print(f"  Preview: {result.preview}")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def _build_oms(host: Optional[str]) -> object:
    if host:
        try:
            return _HttpOMS(host)
        except ImportError:
            pass
    return _SimulatedOMS()


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="OMS Terminal — Ultra-Fast Order Entry CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python terminal_cli.py
              python terminal_cli.py --host http://localhost:8000
              python terminal_cli.py --user-id 2
              echo "b BATBC 100 25.40" | python terminal_cli.py --batch
        """),
    )
    parser.add_argument("--host", default=None,
                        help="OMS server base URL (e.g. http://localhost:8000). "
                             "Omit to use offline simulation mode.")
    parser.add_argument("--user-id", type=int, default=1,
                        help="Trading account user ID (default: 1)")
    parser.add_argument("--batch", action="store_true",
                        help="Read commands from stdin (one per line) and exit.")
    parser.add_argument("--risk-max-value", type=float, default=10_000_000,
                        help="Fat-finger: max order value in BDT (default: 10,000,000)")
    args = parser.parse_args(argv)

    oms = _build_oms(args.host)
    executor = TerminalCommandExecutor(
        order_manager=oms,
        user_id=args.user_id,
        risk_limits={"max_order_value": args.risk_max_value},
    )

    if args.batch:
        # Non-interactive: read from stdin
        loop = asyncio.new_event_loop()
        for line in sys.stdin:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            results = loop.run_until_complete(executor.execute(line))
            for r in results:
                status = "OK" if r.success else "FAIL"
                print(f"[{status}] {r.message}")
        return

    shell = OMSTerminalShell(executor)
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\n👋  Interrupted. Goodbye!")


if __name__ == "__main__":
    main()
