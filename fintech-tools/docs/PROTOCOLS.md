# Financial Protocols Documentation

## Overview

The protocols module implements three major financial messaging protocols used in trading systems:

1. **FIX (Financial Information eXchange)** - Standard for trade-related messages
2. **FAST (FIX Adapted for STreaming)** - Optimized encoding for market data
3. **ITCH (NASDAQ TotalView-ITCH)** - NASDAQ's market data protocol

## FIX Protocol

### Overview

FIX is the industry-standard protocol for real-time electronic exchange of securities transactions. It's used for order entry, execution reports, trade confirmations, and more.

### Key Features

- Tag-value pair format
- Human-readable (can be inspected)
- Widely adopted across financial institutions
- Session-level and application-level messages

### Message Structure

```
8=FIX.4.2|9=65|35=A|49=SENDER|56=TARGET|34=1|52=20231111-10:30:00.123|10=123|
```

Components:
- `8` - BeginString (protocol version)
- `9` - BodyLength
- `35` - MsgType
- `49` - SenderCompID
- `56` - TargetCompID
- `34` - MsgSeqNum
- `52` - SendingTime
- `10` - CheckSum

### Usage Examples

#### Creating a New Order

```python
from src.protocols import FIXProtocol, FIXSide, FIXOrderType

fix = FIXProtocol()

# Create a buy order
order_message = fix.create_new_order(
    symbol="AAPL",
    side=FIXSide.BUY,
    quantity=100,
    price=150.50,
    order_type=FIXOrderType.LIMIT,
    client_order_id="ORD123456"
)

print(order_message)
```

#### Parsing a FIX Message

```python
# Parse received message
parsed = fix.parse_message(order_message)

print(f"Symbol: {parsed[55]}")      # Tag 55 = Symbol
print(f"Side: {parsed[54]}")        # Tag 54 = Side
print(f"Quantity: {parsed[38]}")    # Tag 38 = OrderQty
print(f"Price: {parsed[44]}")       # Tag 44 = Price
```

#### Creating an Execution Report

```python
exec_report = fix.create_execution_report(
    order_id="ORD123456",
    exec_id="EXEC789",
    exec_type="0",  # New
    order_status="0",  # New
    symbol="AAPL",
    side=FIXSide.BUY,
    quantity=100,
    price=150.50
)
```

### Common FIX Tags

| Tag | Field Name | Description |
|-----|------------|-------------|
| 11  | ClOrdID    | Client Order ID |
| 35  | MsgType    | Message Type |
| 38  | OrderQty   | Order Quantity |
| 40  | OrdType    | Order Type |
| 44  | Price      | Price |
| 54  | Side       | Buy/Sell |
| 55  | Symbol     | Trading Symbol |
| 150 | ExecType   | Execution Type |

### Message Types

- `A` - Logon
- `D` - New Order Single
- `F` - Order Cancel Request
- `8` - Execution Report
- `0` - Heartbeat
- `5` - Logout

## FAST Protocol

### Overview

FAST (FIX Adapted for STreaming) is a compression technique for FIX messages, designed for high-frequency market data distribution. It significantly reduces bandwidth and latency.

### Key Features

- Binary encoding (not human-readable)
- Template-based compression
- Delta encoding support
- Stop-bit encoding for variable-length fields

### Usage Examples

#### Register a Template

```python
from src.protocols import FASTProtocol

fast = FASTProtocol()

# Create market data template
fast.create_market_data_template()

# Or register custom template
fast.register_template(
    template_id=2,
    template_name="OrderBook",
    fields=[
        {"name": "symbol", "type": "string"},
        {"name": "level", "type": "uint32"},
        {"name": "price", "type": "decimal"},
        {"name": "size", "type": "uint32"},
    ]
)
```

#### Encode a Message

```python
# Prepare market data
market_data = {
    "symbol": "AAPL",
    "bid_price": 150.25,
    "ask_price": 150.50,
    "bid_size": 100,
    "ask_size": 200,
    "last_price": 150.35,
    "volume": 1000000
}

# Encode using template ID 1 (MarketData)
encoded = fast.encode_message(
    template_id=1,
    fields=market_data,
    use_delta=True
)

print(f"Encoded bytes: {encoded.hex()}")
print(f"Size: {len(encoded)} bytes")
```

#### Decode a Message

```python
# Decode received message
decoded = fast.decode_message(encoded)

print(f"Template: {decoded['_template_name']}")
print(f"Symbol: {decoded['symbol']}")
print(f"Bid: {decoded['bid_price']} x {decoded['bid_size']}")
print(f"Ask: {decoded['ask_price']} x {decoded['ask_size']}")
```

### Compression Benefits

Original FIX message size: ~200 bytes
FAST encoded message size: ~20-50 bytes
Compression ratio: 75-90%

### When to Use FAST

- ✅ High-frequency market data feeds
- ✅ Low-latency requirements
- ✅ Bandwidth-constrained networks
- ❌ Human inspection needed
- ❌ Simple, low-volume applications

## ITCH Protocol

### Overview

ITCH is NASDAQ's proprietary protocol for disseminating real-time market data. It provides a complete view of the order book.

### Key Features

- Binary format
- Fixed-length messages
- Nanosecond timestamps
- Complete order book visibility

### Message Types

| Type | Name | Description |
|------|------|-------------|
| S | System Event | System status |
| R | Stock Directory | Stock information |
| A | Add Order | New order added |
| E | Order Executed | Order execution |
| X | Order Cancel | Order cancelled |
| D | Order Delete | Order deleted |
| P | Trade | Non-displayed trade |

### Usage Examples

#### Create Add Order Message

```python
from src.protocols import ITCHProtocol, ITCHSide

itch = ITCHProtocol()

# Create an add order message
order_msg = itch.create_add_order(
    stock="AAPL",
    side=ITCHSide.BUY,
    shares=100,
    price=150.50,
    order_reference=12345
)

print(f"Message size: {len(order_msg)} bytes")
print(f"Message hex: {order_msg.hex()}")
```

#### Parse Add Order Message

```python
# Parse received message
parsed = itch.parse_add_order(order_msg)

print(f"Stock: {parsed['stock']}")
print(f"Side: {parsed['side']}")
print(f"Shares: {parsed['shares']}")
print(f"Price: {parsed['price']}")
print(f"Order Reference: {parsed['order_reference']}")
```

#### Create Order Executed Message

```python
exec_msg = itch.create_order_executed(
    order_reference=12345,
    executed_shares=50,
    match_number=67890
)
```

#### Create Trade Message

```python
trade_msg = itch.create_trade_message(
    stock="AAPL",
    side=ITCHSide.BUY,
    shares=100,
    price=150.50,
    match_number=67890
)
```

### Message Structure

#### Add Order (Type A) - 36 bytes

```
Offset | Size | Field
-------|------|-------
0      | 1    | Message Type ('A')
1      | 2    | Stock Locate
3      | 2    | Tracking Number
5      | 6    | Timestamp (nanoseconds)
11     | 8    | Order Reference
19     | 1    | Buy/Sell
20     | 4    | Shares
24     | 8    | Stock (padded)
32     | 4    | Price (×10000)
```

### Price Encoding

ITCH prices are encoded as integers multiplied by 10,000:
- $150.50 → 1,505,000
- $0.0001 → 1

```python
# Manual price conversion
def encode_price(price: float) -> int:
    return int(price * 10000)

def decode_price(price_int: int) -> float:
    return price_int / 10000.0
```

## Protocol Comparison

| Feature | FIX | FAST | ITCH |
|---------|-----|------|------|
| **Format** | Text | Binary | Binary |
| **Readability** | Human-readable | Not readable | Not readable |
| **Size** | Large (200+ bytes) | Small (20-50 bytes) | Fixed (varies) |
| **Speed** | Moderate | Fast | Very Fast |
| **Flexibility** | High | Moderate | Low |
| **Use Case** | Order entry, execution | Market data | NASDAQ data feed |

## Best Practices

### 1. Protocol Selection

- **Order Entry/Management**: Use FIX
- **Market Data Distribution**: Use FAST
- **NASDAQ Market Data**: Use ITCH

### 2. Error Handling

```python
from src.protocols import FIXProtocol

try:
    fix = FIXProtocol()
    message = fix.create_new_order(
        symbol="INVALID_SYMBOL_TOO_LONG",
        side=FIXSide.BUY,
        quantity=100,
        price=150.0
    )
except ValueError as e:
    print(f"Invalid order: {e}")
```

### 3. Message Validation

Always validate messages before sending:

```python
def validate_order(symbol, quantity, price):
    if len(symbol) > 8:
        raise ValueError("Symbol too long")
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    if price <= 0:
        raise ValueError("Price must be positive")
```

### 4. Sequence Number Management

```python
# Track sequence numbers to detect gaps
class SequenceTracker:
    def __init__(self):
        self.expected_seq = 1
    
    def check_sequence(self, received_seq):
        if received_seq != self.expected_seq:
            print(f"Gap detected: expected {self.expected_seq}, got {received_seq}")
        self.expected_seq = received_seq + 1
```

## Integration Examples

### FIX Trading Gateway

```python
from fastapi import FastAPI
from src.protocols import FIXProtocol, FIXSide, FIXOrderType

app = FastAPI()
fix = FIXProtocol()

@app.post("/orders/fix")
async def create_fix_order(
    symbol: str,
    side: str,
    quantity: int,
    price: float
):
    fix_side = FIXSide.BUY if side.upper() == "BUY" else FIXSide.SELL
    
    message = fix.create_new_order(
        symbol=symbol,
        side=fix_side,
        quantity=quantity,
        price=price,
        order_type=FIXOrderType.LIMIT
    )
    
    # Send to exchange...
    
    return {"fix_message": message, "status": "sent"}
```

### Market Data Feed Handler

```python
import asyncio
from src.protocols import ITCHProtocol

async def process_itch_feed(data_source):
    itch = ITCHProtocol()
    
    async for message in data_source:
        try:
            parsed = itch.parse_message(message)
            
            if parsed["message_type"] == "A":
                # Process add order
                print(f"New order: {parsed['stock']} {parsed['shares']}@{parsed['price']}")
            
        except Exception as e:
            print(f"Error processing message: {e}")
```

## Testing

```python
import pytest
from src.protocols import FIXProtocol, FIXSide

def test_fix_order_creation():
    fix = FIXProtocol()
    message = fix.create_new_order(
        symbol="AAPL",
        side=FIXSide.BUY,
        quantity=100,
        price=150.0
    )
    
    assert "35=D" in message  # MsgType = NewOrderSingle
    assert "55=AAPL" in message  # Symbol
    assert "54=1" in message  # Side = Buy

def test_fix_parsing():
    fix = FIXProtocol()
    message = fix.create_new_order("AAPL", FIXSide.BUY, 100, 150.0)
    parsed = fix.parse_message(message)
    
    assert parsed[55] == "AAPL"
    assert parsed[54] == "1"
    assert parsed[38] == "100"
```
