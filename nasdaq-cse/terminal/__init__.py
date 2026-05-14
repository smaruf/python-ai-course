"""
Terminal / Command Mode for Ultra-Fast Order Entry.

Provides a Bloomberg-style command interface for rapid order entry:

    b BATBC 100 25.40     → buy limit
    s GP 500 350          → sell limit
    bm BATBC 100          → buy market
    sm GP 500             → sell market
    c 982734              → cancel order
    m 982734 25.60 200    → modify order
    rr                    → repeat last order
"""
from .parser import TerminalParser, ParsedCommand
from .commands import TerminalCommandExecutor

__all__ = ["TerminalParser", "ParsedCommand", "TerminalCommandExecutor"]
