"""
ITCH Protocol Implementation

NASDAQ TotalView-ITCH Protocol for market data feed
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import struct


class ITCHMessageType(str, Enum):
    """ITCH message types"""
    SYSTEM_EVENT = "S"
    STOCK_DIRECTORY = "R"
    STOCK_TRADING_ACTION = "H"
    REG_SHO_RESTRICTION = "Y"
    MARKET_PARTICIPANT_POSITION = "L"
    ADD_ORDER = "A"
    ADD_ORDER_MPID = "F"
    ORDER_EXECUTED = "E"
    ORDER_EXECUTED_WITH_PRICE = "C"
    ORDER_CANCEL = "X"
    ORDER_DELETE = "D"
    ORDER_REPLACE = "U"
    TRADE = "P"
    CROSS_TRADE = "Q"
    BROKEN_TRADE = "B"


class ITCHSide(str, Enum):
    """Order side"""
    BUY = "B"
    SELL = "S"


class ITCHProtocol:
    """ITCH Protocol message handler"""
    
    def __init__(self):
        self.sequence_number = 0
    
    def _pack_timestamp(self) -> bytes:
        """
        Pack timestamp as nanoseconds since midnight
        
        Returns:
            bytes: 6-byte timestamp
        """
        now = datetime.utcnow()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        nanoseconds = int((now - midnight).total_seconds() * 1_000_000_000)
        
        # Pack as 48-bit (6 bytes) big-endian
        return struct.pack(">Q", nanoseconds)[-6:]
    
    def _pack_price(self, price: float) -> bytes:
        """
        Pack price as 4-byte integer (price * 10000)
        
        Args:
            price: Price as float
            
        Returns:
            bytes: Packed price
        """
        price_int = int(price * 10000)
        return struct.pack(">I", price_int)
    
    def _unpack_price(self, data: bytes) -> float:
        """
        Unpack price from bytes
        
        Args:
            data: 4-byte price data
            
        Returns:
            float: Price value
        """
        price_int = struct.unpack(">I", data)[0]
        return price_int / 10000.0
    
    def create_add_order(
        self,
        stock: str,
        side: ITCHSide,
        shares: int,
        price: float,
        order_reference: Optional[int] = None
    ) -> bytes:
        """
        Create Add Order message (Type A)
        
        Args:
            stock: Stock symbol (up to 8 characters)
            side: Buy or Sell
            shares: Number of shares
            price: Order price
            order_reference: Optional order reference number
            
        Returns:
            bytes: ITCH Add Order message
        """
        if order_reference is None:
            self.sequence_number += 1
            order_reference = self.sequence_number
        
        message = bytearray()
        
        # Message Type (1 byte)
        message.extend(ITCHMessageType.ADD_ORDER.value.encode('ascii'))
        
        # Stock Locate (2 bytes) - simplified as 0
        message.extend(struct.pack(">H", 0))
        
        # Tracking Number (2 bytes) - simplified as 0
        message.extend(struct.pack(">H", 0))
        
        # Timestamp (6 bytes)
        message.extend(self._pack_timestamp())
        
        # Order Reference Number (8 bytes)
        message.extend(struct.pack(">Q", order_reference))
        
        # Buy/Sell Indicator (1 byte)
        message.extend(side.value.encode('ascii'))
        
        # Shares (4 bytes)
        message.extend(struct.pack(">I", shares))
        
        # Stock (8 bytes, space-padded)
        stock_padded = stock.ljust(8)[:8]
        message.extend(stock_padded.encode('ascii'))
        
        # Price (4 bytes)
        message.extend(self._pack_price(price))
        
        return bytes(message)
    
    def parse_add_order(self, data: bytes) -> Dict[str, Any]:
        """
        Parse Add Order message
        
        Args:
            data: ITCH message bytes
            
        Returns:
            Dict: Parsed message fields
        """
        if len(data) < 36:
            raise ValueError("Invalid message length for Add Order")
        
        offset = 0
        
        # Message Type
        msg_type = data[offset:offset+1].decode('ascii')
        offset += 1
        
        # Stock Locate
        stock_locate = struct.unpack(">H", data[offset:offset+2])[0]
        offset += 2
        
        # Tracking Number
        tracking_number = struct.unpack(">H", data[offset:offset+2])[0]
        offset += 2
        
        # Timestamp
        timestamp = struct.unpack(">Q", b'\x00\x00' + data[offset:offset+6])[0]
        offset += 6
        
        # Order Reference Number
        order_ref = struct.unpack(">Q", data[offset:offset+8])[0]
        offset += 8
        
        # Buy/Sell Indicator
        side = data[offset:offset+1].decode('ascii')
        offset += 1
        
        # Shares
        shares = struct.unpack(">I", data[offset:offset+4])[0]
        offset += 4
        
        # Stock
        stock = data[offset:offset+8].decode('ascii').strip()
        offset += 8
        
        # Price
        price = self._unpack_price(data[offset:offset+4])
        
        return {
            "message_type": msg_type,
            "stock_locate": stock_locate,
            "tracking_number": tracking_number,
            "timestamp": timestamp,
            "order_reference": order_ref,
            "side": side,
            "shares": shares,
            "stock": stock,
            "price": price
        }
    
    def create_order_executed(
        self,
        order_reference: int,
        executed_shares: int,
        match_number: int
    ) -> bytes:
        """
        Create Order Executed message (Type E)
        
        Args:
            order_reference: Order reference number
            executed_shares: Number of shares executed
            match_number: Match number
            
        Returns:
            bytes: ITCH Order Executed message
        """
        message = bytearray()
        
        # Message Type
        message.extend(ITCHMessageType.ORDER_EXECUTED.value.encode('ascii'))
        
        # Stock Locate
        message.extend(struct.pack(">H", 0))
        
        # Tracking Number
        message.extend(struct.pack(">H", 0))
        
        # Timestamp
        message.extend(self._pack_timestamp())
        
        # Order Reference Number
        message.extend(struct.pack(">Q", order_reference))
        
        # Executed Shares
        message.extend(struct.pack(">I", executed_shares))
        
        # Match Number
        message.extend(struct.pack(">Q", match_number))
        
        return bytes(message)
    
    def create_trade_message(
        self,
        stock: str,
        side: ITCHSide,
        shares: int,
        price: float,
        match_number: int
    ) -> bytes:
        """
        Create Trade message (Type P)
        
        Args:
            stock: Stock symbol
            side: Buy or Sell
            shares: Number of shares
            price: Trade price
            match_number: Match number
            
        Returns:
            bytes: ITCH Trade message
        """
        message = bytearray()
        
        # Message Type
        message.extend(ITCHMessageType.TRADE.value.encode('ascii'))
        
        # Stock Locate
        message.extend(struct.pack(">H", 0))
        
        # Tracking Number
        message.extend(struct.pack(">H", 0))
        
        # Timestamp
        message.extend(self._pack_timestamp())
        
        # Order Reference Number (for trade, use match number)
        message.extend(struct.pack(">Q", match_number))
        
        # Buy/Sell Indicator
        message.extend(side.value.encode('ascii'))
        
        # Shares
        message.extend(struct.pack(">I", shares))
        
        # Stock
        stock_padded = stock.ljust(8)[:8]
        message.extend(stock_padded.encode('ascii'))
        
        # Price
        message.extend(self._pack_price(price))
        
        # Match Number
        message.extend(struct.pack(">Q", match_number))
        
        return bytes(message)
    
    def parse_message(self, data: bytes) -> Dict[str, Any]:
        """
        Parse any ITCH message
        
        Args:
            data: ITCH message bytes
            
        Returns:
            Dict: Parsed message
        """
        if len(data) < 1:
            raise ValueError("Empty message")
        
        msg_type = data[0:1].decode('ascii')
        
        if msg_type == ITCHMessageType.ADD_ORDER.value:
            return self.parse_add_order(data)
        else:
            return {
                "message_type": msg_type,
                "raw_data": data.hex()
            }
