"""
Tests for Protocols Module
"""

import pytest
from src.protocols import FIXProtocol, FIXSide, FIXOrderType
from src.protocols import FASTProtocol
from src.protocols import ITCHProtocol, ITCHSide


class TestFIXProtocol:
    """Tests for FIX Protocol"""
    
    def test_create_new_order(self):
        """Test FIX new order creation"""
        fix = FIXProtocol()
        
        message = fix.create_new_order(
            symbol="AAPL",
            side=FIXSide.BUY,
            quantity=100,
            price=150.0
        )
        
        assert message is not None
        assert "35=D" in message  # MsgType = NewOrderSingle
        assert "55=AAPL" in message  # Symbol
        assert "54=1" in message  # Side = Buy
    
    def test_parse_message(self):
        """Test FIX message parsing"""
        fix = FIXProtocol()
        
        message = fix.create_new_order(
            symbol="AAPL",
            side=FIXSide.BUY,
            quantity=100,
            price=150.0
        )
        
        parsed = fix.parse_message(message)
        
        assert 55 in parsed  # Symbol tag
        assert parsed[55] == "AAPL"
        assert parsed[54] == "1"  # Buy side


class TestFASTProtocol:
    """Tests for FAST Protocol"""
    
    def test_encode_uint32(self):
        """Test unsigned integer encoding"""
        fast = FASTProtocol()
        
        # Test encoding small number
        encoded = fast.encode_uint32(127)
        assert len(encoded) == 1
        
        # Test encoding larger number
        encoded = fast.encode_uint32(1000)
        assert len(encoded) > 1
    
    def test_decode_uint32(self):
        """Test unsigned integer decoding"""
        fast = FASTProtocol()
        
        # Encode and decode
        original = 1234
        encoded = fast.encode_uint32(original)
        decoded, bytes_consumed = fast.decode_uint32(encoded)
        
        assert decoded == original
        assert bytes_consumed == len(encoded)
    
    def test_encode_string(self):
        """Test string encoding"""
        fast = FASTProtocol()
        
        encoded = fast.encode_string("AAPL")
        assert len(encoded) == 4
        assert encoded[-1] & 0x80  # Stop bit set on last byte
    
    def test_decode_string(self):
        """Test string decoding"""
        fast = FASTProtocol()
        
        # Encode and decode
        original = "AAPL"
        encoded = fast.encode_string(original)
        decoded, bytes_consumed = fast.decode_string(encoded)
        
        assert decoded == original
        assert bytes_consumed == len(encoded)
    
    def test_market_data_encoding(self):
        """Test market data message encoding"""
        fast = FASTProtocol()
        fast.create_market_data_template()
        
        market_data = {
            "symbol": "AAPL",
            "bid_price": 150.25,
            "ask_price": 150.50,
            "bid_size": 100,
            "ask_size": 200,
            "last_price": 150.35,
            "volume": 1000000
        }
        
        encoded = fast.encode_message(1, market_data)
        assert len(encoded) > 0
        
        # Decode and verify
        decoded = fast.decode_message(encoded)
        assert decoded["symbol"] == "AAPL"


class TestITCHProtocol:
    """Tests for ITCH Protocol"""
    
    def test_create_add_order(self):
        """Test ITCH add order creation"""
        itch = ITCHProtocol()
        
        message = itch.create_add_order(
            stock="AAPL",
            side=ITCHSide.BUY,
            shares=100,
            price=150.50
        )
        
        assert len(message) == 36  # Add Order is 36 bytes
        assert message[0:1] == b'A'  # Message type
    
    def test_parse_add_order(self):
        """Test ITCH add order parsing"""
        itch = ITCHProtocol()
        
        # Create and parse
        message = itch.create_add_order(
            stock="AAPL",
            side=ITCHSide.BUY,
            shares=100,
            price=150.50,
            order_reference=12345
        )
        
        parsed = itch.parse_add_order(message)
        
        assert parsed["message_type"] == "A"
        assert parsed["stock"] == "AAPL"
        assert parsed["side"] == "B"
        assert parsed["shares"] == 100
        assert parsed["price"] == 150.50
        assert parsed["order_reference"] == 12345
    
    def test_create_order_executed(self):
        """Test ITCH order executed message"""
        itch = ITCHProtocol()
        
        message = itch.create_order_executed(
            order_reference=12345,
            executed_shares=50,
            match_number=67890
        )
        
        assert message[0:1] == b'E'  # Message type
        assert len(message) > 0
    
    def test_create_trade_message(self):
        """Test ITCH trade message"""
        itch = ITCHProtocol()
        
        message = itch.create_trade_message(
            stock="AAPL",
            side=ITCHSide.BUY,
            shares=100,
            price=150.50,
            match_number=67890
        )
        
        assert message[0:1] == b'P'  # Message type
        assert len(message) > 0
