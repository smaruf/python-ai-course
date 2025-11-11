"""
Protocol Examples

Demonstrates FIX, FAST, and ITCH protocol usage
"""

from src.protocols import FIXProtocol, FIXSide, FIXOrderType
from src.protocols import FASTProtocol
from src.protocols import ITCHProtocol, ITCHSide


def fix_protocol_example():
    """Demonstrate FIX protocol usage"""
    print("=" * 60)
    print("FIX PROTOCOL EXAMPLE")
    print("=" * 60)
    print()
    
    fix = FIXProtocol()
    
    # Create a new order
    print("1. Creating a New Order (Buy 100 AAPL @ $150.50)")
    print("-" * 60)
    
    order_message = fix.create_new_order(
        symbol="AAPL",
        side=FIXSide.BUY,
        quantity=100,
        price=150.50,
        order_type=FIXOrderType.LIMIT
    )
    
    print(f"FIX Message (human-readable):")
    # Replace SOH with | for display
    display_message = order_message.replace("\x01", "|")
    print(f"  {display_message}")
    print()
    
    # Parse the message
    print("2. Parsing FIX Message")
    print("-" * 60)
    parsed = fix.parse_message(order_message)
    
    print(f"Message Type (35): {parsed.get(35)}")
    print(f"Symbol (55): {parsed.get(55)}")
    print(f"Side (54): {parsed.get(54)} (1=Buy, 2=Sell)")
    print(f"Quantity (38): {parsed.get(38)}")
    print(f"Price (44): {parsed.get(44)}")
    print(f"Order Type (40): {parsed.get(40)}")
    print()
    
    # Create execution report
    print("3. Creating Execution Report")
    print("-" * 60)
    
    exec_report = fix.create_execution_report(
        order_id="ORD12345",
        exec_id="EXEC67890",
        exec_type="F",  # Fill
        order_status="2",  # Filled
        symbol="AAPL",
        side=FIXSide.BUY,
        quantity=100,
        price=150.50
    )
    
    display_exec = exec_report.replace("\x01", "|")
    print(f"Execution Report:")
    print(f"  {display_exec[:200]}...")
    print()


def fast_protocol_example():
    """Demonstrate FAST protocol usage"""
    print("=" * 60)
    print("FAST PROTOCOL EXAMPLE")
    print("=" * 60)
    print()
    
    fast = FASTProtocol()
    
    # Create market data template
    fast.create_market_data_template()
    
    print("1. Encoding Market Data")
    print("-" * 60)
    
    market_data = {
        "symbol": "AAPL",
        "bid_price": 150.25,
        "ask_price": 150.50,
        "bid_size": 1000,
        "ask_size": 1500,
        "last_price": 150.35,
        "volume": 1000000
    }
    
    print(f"Original Data:")
    for key, value in market_data.items():
        print(f"  {key}: {value}")
    print()
    
    # Encode
    encoded = fast.encode_message(1, market_data)
    
    print(f"Encoded Size: {len(encoded)} bytes")
    print(f"Encoded Data (hex): {encoded.hex()}")
    print()
    
    # Decode
    print("2. Decoding FAST Message")
    print("-" * 60)
    
    decoded = fast.decode_message(encoded)
    
    print(f"Template: {decoded['_template_name']}")
    print(f"Symbol: {decoded['symbol']}")
    print(f"Bid: ${decoded['bid_price']} x {decoded['bid_size']}")
    print(f"Ask: ${decoded['ask_price']} x {decoded['ask_size']}")
    print(f"Last: ${decoded['last_price']}")
    print(f"Volume: {decoded['volume']:,}")
    print()


def itch_protocol_example():
    """Demonstrate ITCH protocol usage"""
    print("=" * 60)
    print("ITCH PROTOCOL EXAMPLE")
    print("=" * 60)
    print()
    
    itch = ITCHProtocol()
    
    # Create add order message
    print("1. Creating Add Order Message")
    print("-" * 60)
    
    order_msg = itch.create_add_order(
        stock="AAPL",
        side=ITCHSide.BUY,
        shares=100,
        price=150.50,
        order_reference=12345
    )
    
    print(f"Message Size: {len(order_msg)} bytes")
    print(f"Message Type: Add Order (A)")
    print(f"Message Hex: {order_msg.hex()}")
    print()
    
    # Parse the message
    print("2. Parsing Add Order Message")
    print("-" * 60)
    
    parsed = itch.parse_add_order(order_msg)
    
    print(f"Stock: {parsed['stock']}")
    print(f"Side: {parsed['side']} (B=Buy, S=Sell)")
    print(f"Shares: {parsed['shares']}")
    print(f"Price: ${parsed['price']}")
    print(f"Order Reference: {parsed['order_reference']}")
    print(f"Timestamp (ns): {parsed['timestamp']}")
    print()
    
    # Create order executed message
    print("3. Creating Order Executed Message")
    print("-" * 60)
    
    exec_msg = itch.create_order_executed(
        order_reference=12345,
        executed_shares=100,
        match_number=67890
    )
    
    print(f"Message Size: {len(exec_msg)} bytes")
    print(f"Message Type: Order Executed (E)")
    print(f"Message Hex: {exec_msg.hex()}")
    print()
    
    # Create trade message
    print("4. Creating Trade Message")
    print("-" * 60)
    
    trade_msg = itch.create_trade_message(
        stock="AAPL",
        side=ITCHSide.BUY,
        shares=100,
        price=150.50,
        match_number=67890
    )
    
    print(f"Message Size: {len(trade_msg)} bytes")
    print(f"Message Type: Trade (P)")
    print(f"Message Hex: {trade_msg.hex()}")
    print()


def main():
    """Run all protocol examples"""
    fix_protocol_example()
    fast_protocol_example()
    itch_protocol_example()
    
    print("=" * 60)
    print("All protocol examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
