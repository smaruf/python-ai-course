"""
mock_fix_server.py — TCP socket server that simulates a Nasdaq FIX counterparty.

Listens on localhost:9878 (configurable via FIX_MOCK_PORT env var).
Accepts a QuickFIX/J NewOrderSingle and replies with a synthetic ExecutionReport.

Usage:
    python scripts/testing/mock_fix_server.py
    FIX_MOCK_PORT=9878 python scripts/testing/mock_fix_server.py
"""
import asyncio
import os
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MockFIX] %(message)s")
log = logging.getLogger(__name__)

HOST = "0.0.0.0"
PORT = int(os.getenv("FIX_MOCK_PORT", "9878"))

# Minimal FIX 4.4 ExecutionReport (tag=value, SOH-delimited)
def build_exec_report(cl_ord_id: str, symbol: str, qty: int) -> bytes:
    body_fields = (
        f"35=8\x01"           # MsgType = ExecutionReport
        f"49=MOCKFIX\x01"     # SenderCompID
        f"56=TRADINGAI\x01"   # TargetCompID
        f"34=1\x01"           # MsgSeqNum
        f"52={time.strftime('%Y%m%d-%H:%M:%S')}\x01"
        f"37=ORD-{cl_ord_id}\x01"  # OrderID
        f"11={cl_ord_id}\x01"       # ClOrdID (echo)
        f"17=EXEC-001\x01"          # ExecID
        f"150=2\x01"                # ExecType = Trade
        f"39=2\x01"                 # OrdStatus = Filled
        f"55={symbol}\x01"          # Symbol
        f"54=1\x01"                 # Side = Buy
        f"38={qty}\x01"             # OrderQty
        f"32={qty}\x01"             # LastQty
        f"31=100.00\x01"            # LastPx
        f"14={qty}\x01"             # CumQty
        f"6=100.00\x01"             # AvgPx
        f"151=0\x01"                # LeavesQty
    )
    header = f"8=FIX.4.4\x019={len(body_fields)}\x01"
    raw = header + body_fields
    checksum = sum(ord(c) for c in raw) % 256
    return (raw + f"10={checksum:03d}\x01").encode()


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    addr = writer.get_extra_info("peername")
    log.info("Connection from %s", addr)
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            message = data.decode(errors="replace")
            log.info("Received: %s", message.replace("\x01", "|"))

            # Parse minimal fields for the reply
            fields = dict(
                field.split("=", 1) for field in message.split("\x01") if "=" in field
            )
            msg_type  = fields.get("35", "")
            cl_ord_id = fields.get("11", "UNKNOWN")
            symbol    = fields.get("55", "AAPL")
            qty       = int(fields.get("38", "0"))

            if msg_type == "D":  # NewOrderSingle
                reply = build_exec_report(cl_ord_id, symbol, qty)
                writer.write(reply)
                await writer.drain()
                log.info("Sent ExecutionReport for ClOrdID=%s", cl_ord_id)
    except asyncio.IncompleteReadError:
        pass
    finally:
        writer.close()
        log.info("Connection closed: %s", addr)


async def main() -> None:
    server = await asyncio.start_server(handle_client, HOST, PORT)
    log.info("Mock FIX server listening on %s:%s", HOST, PORT)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
