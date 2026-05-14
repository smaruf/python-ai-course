"""
Terminal command parser.

Supported grammar::

    [action] [symbol] [qty] [price] [flags]

Actions
-------
b   / buy   — limit buy
bm          — market buy
s   / sell  — limit sell
sm          — sell market
c   / cancel — cancel order by ID
m   / modify — modify order: m <id> <new_price> [new_qty]
rr           — repeat last order
help / ?     — show help text
basket       — execute a basket file or semicolon-separated commands

Quantity notation
-----------------
100    → 100
5k     → 5000
2.5k   → 2500
50%    → percentage of portfolio (resolved later by command executor)

Examples::

    b BATBC 100 25.40
    s GP 500 350
    bm BATBC 100
    sm GP 500
    c 982734
    m 982734 25.60 200
    b BATBC 5k 25.40
    rr
    b GP 100 350 ; b BATBC 200 25.4
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUY_MARKET = "BUY_MARKET"
    SELL_MARKET = "SELL_MARKET"
    CANCEL = "CANCEL"
    MODIFY = "MODIFY"
    REPEAT = "REPEAT"
    HELP = "HELP"
    BASKET = "BASKET"
    UNKNOWN = "UNKNOWN"


@dataclass
class ParsedCommand:
    """Result of parsing a single terminal command token."""

    raw: str
    action: Action = Action.UNKNOWN
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    quantity_is_pct: bool = False   # True when qty was expressed as "50%"
    price: Optional[float] = None
    order_id: Optional[str] = None  # for cancel / modify
    basket_source: Optional[str] = None  # for basket command
    error: Optional[str] = None     # populated when parsing fails

    # ---------- helpers ----------

    @property
    def is_valid(self) -> bool:
        return self.error is None

    @property
    def order_type(self) -> str:
        if self.action in (Action.BUY_MARKET, Action.SELL_MARKET):
            return "MARKET"
        return "LIMIT"

    @property
    def side(self) -> Optional[str]:
        if self.action in (Action.BUY, Action.BUY_MARKET):
            return "BUY"
        if self.action in (Action.SELL, Action.SELL_MARKET):
            return "SELL"
        return None

    def preview(self) -> str:
        """Human-readable one-line preview of the order."""
        if self.action == Action.CANCEL:
            return f"Cancel order {self.order_id}"
        if self.action == Action.MODIFY:
            parts = [f"Modify order {self.order_id}"]
            if self.price is not None:
                parts.append(f"price → {self.price:.2f}")
            if self.quantity is not None:
                parts.append(f"qty → {int(self.quantity)}")
            return "  ".join(parts)
        if self.action == Action.REPEAT:
            return "Repeat last order"
        if self.action == Action.HELP:
            return "Show help"
        if self.action == Action.BASKET:
            return f"Basket: {self.basket_source}"
        if self.action == Action.UNKNOWN:
            return f"Unknown command: {self.raw!r}"
        side_label = "Buy" if self.side == "BUY" else "Sell"
        qty_str = (
            f"{self.quantity:.0f}" if self.quantity and not self.quantity_is_pct
            else f"{self.quantity:.0f}%" if self.quantity_is_pct
            else "?"
        )
        type_label: str
        if self.order_type == "MARKET":
            type_label = "Market"
        elif self.price:
            type_label = f"@ {self.price:.2f}"
        else:
            type_label = "Limit"
        if self.quantity and self.price:
            value = self.quantity * self.price
            return f"{side_label} {self.symbol}  qty {qty_str}  {type_label}  value ≈ {value:,.2f} BDT"
        return f"{side_label} {self.symbol}  qty {qty_str}  {type_label}"


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

_ACTION_MAP = {
    "b": Action.BUY,
    "buy": Action.BUY,
    "bm": Action.BUY_MARKET,
    "s": Action.SELL,
    "sell": Action.SELL,
    "sm": Action.SELL_MARKET,
    "c": Action.CANCEL,
    "cancel": Action.CANCEL,
    "m": Action.MODIFY,
    "modify": Action.MODIFY,
    "rr": Action.REPEAT,
    "help": Action.HELP,
    "?": Action.HELP,
    "h": Action.HELP,
    "basket": Action.BASKET,
}


def _parse_quantity(token: str) -> tuple[Optional[float], bool]:
    """
    Parse a quantity token.  Returns ``(value, is_percentage)``.

    Accepted forms:
    - ``100``     → (100.0, False)
    - ``5k``      → (5000.0, False)
    - ``2.5k``    → (2500.0, False)
    - ``50%``     → (50.0, True)
    """
    token = token.strip().lower()
    pct = token.endswith("%")
    if pct:
        token = token[:-1]

    multiplier = 1.0
    if token.endswith("k"):
        multiplier = 1000.0
        token = token[:-1]
    elif token.endswith("m"):
        multiplier = 1_000_000.0
        token = token[:-1]

    try:
        value = float(token) * multiplier
        return value, pct
    except ValueError:
        return None, False


def _parse_price(token: str) -> Optional[float]:
    try:
        return float(token)
    except ValueError:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Main parser
# ──────────────────────────────────────────────────────────────────────────────

class TerminalParser:
    """
    Stateless command parser.

    Usage::

        parser = TerminalParser()
        cmd = parser.parse("b BATBC 100 25.40")
        print(cmd.preview())
    """

    def parse(self, text: str) -> list[ParsedCommand]:
        """
        Parse *text* into one or more :class:`ParsedCommand` objects.

        Semicolons split the input into multiple commands.
        """
        parts = [p.strip() for p in text.split(";") if p.strip()]
        return [self._parse_single(p) for p in parts]

    def _parse_single(self, text: str) -> ParsedCommand:
        tokens = text.split()
        if not tokens:
            return ParsedCommand(raw=text, action=Action.UNKNOWN, error="Empty command")

        verb = tokens[0].lower()
        action = _ACTION_MAP.get(verb, Action.UNKNOWN)

        if action == Action.UNKNOWN:
            return ParsedCommand(raw=text, action=Action.UNKNOWN,
                                 error=f"Unknown action '{tokens[0]}'. Type 'help' for usage.")

        if action == Action.HELP:
            return ParsedCommand(raw=text, action=Action.HELP)

        if action == Action.REPEAT:
            return ParsedCommand(raw=text, action=Action.REPEAT)

        if action == Action.BASKET:
            source = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            return ParsedCommand(raw=text, action=Action.BASKET,
                                 basket_source=source or None,
                                 error=None if source else "basket requires a file path or command list")

        if action == Action.CANCEL:
            if len(tokens) < 2:
                return ParsedCommand(raw=text, action=action,
                                     error="cancel requires an order ID: c <order_id>")
            return ParsedCommand(raw=text, action=action, order_id=tokens[1])

        if action == Action.MODIFY:
            # m <order_id> <new_price> [new_qty]
            if len(tokens) < 3:
                return ParsedCommand(raw=text, action=action,
                                     error="modify requires: m <order_id> <new_price> [new_qty]")
            order_id = tokens[1]
            new_price = _parse_price(tokens[2])
            if new_price is None:
                return ParsedCommand(raw=text, action=action,
                                     error=f"Invalid price '{tokens[2]}'")
            new_qty: Optional[float] = None
            if len(tokens) >= 4:
                new_qty, _ = _parse_quantity(tokens[3])
                if new_qty is None:
                    return ParsedCommand(raw=text, action=action,
                                         error=f"Invalid quantity '{tokens[3]}'")
            return ParsedCommand(raw=text, action=action,
                                 order_id=order_id, price=new_price, quantity=new_qty)

        # BUY / SELL (limit or market)
        if action in (Action.BUY_MARKET, Action.SELL_MARKET):
            # bm / sm  SYMBOL  QTY
            if len(tokens) < 3:
                return ParsedCommand(raw=text, action=action,
                                     error=f"Market order requires: {verb} <symbol> <qty>")
            symbol = tokens[1].upper()
            qty, is_pct = _parse_quantity(tokens[2])
            if qty is None:
                return ParsedCommand(raw=text, action=action,
                                     error=f"Invalid quantity '{tokens[2]}'")
            return ParsedCommand(raw=text, action=action,
                                 symbol=symbol, quantity=qty, quantity_is_pct=is_pct)

        # BUY / SELL limit
        if len(tokens) < 4:
            return ParsedCommand(raw=text, action=action,
                                 error=f"Limit order requires: {verb} <symbol> <qty> <price>")
        symbol = tokens[1].upper()
        qty, is_pct = _parse_quantity(tokens[2])
        if qty is None:
            return ParsedCommand(raw=text, action=action,
                                 error=f"Invalid quantity '{tokens[2]}'")
        price = _parse_price(tokens[3])
        if price is None:
            return ParsedCommand(raw=text, action=action,
                                 error=f"Invalid price '{tokens[3]}'")
        return ParsedCommand(raw=text, action=action,
                             symbol=symbol, quantity=qty,
                             quantity_is_pct=is_pct, price=price)


HELP_TEXT = """\
┌──────────────────────────────────────────────────────────────────────┐
│  OMS Terminal  –  Ultra-Fast Order Entry                             │
│  Hotkey: Ctrl+Space  or  Alt+T                                       │
├──────────────────────────────────────────────────────────────────────┤
│  COMMAND              MEANING                                        │
│  b  SYMBOL QTY PRICE  Limit Buy                                     │
│  bm SYMBOL QTY        Market Buy                                    │
│  s  SYMBOL QTY PRICE  Limit Sell                                    │
│  sm SYMBOL QTY        Market Sell                                   │
│  c  ORDER_ID          Cancel Order                                  │
│  m  ORDER_ID PR [QTY] Modify Order                                  │
│  rr                   Repeat Last Order                             │
│  b GP 100 350 ; s BATBC 50 25  Basket (semicolons)                 │
├──────────────────────────────────────────────────────────────────────┤
│  QUANTITY SHORTCUTS                                                  │
│  5k  → 5000    2.5k → 2500    50% → 50 pct of position             │
├──────────────────────────────────────────────────────────────────────┤
│  help  or  ?  — show this screen                                     │
└──────────────────────────────────────────────────────────────────────┘"""
