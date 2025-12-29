"""
FIX Protocol Implementation

Financial Information eXchange (FIX) Protocol for trade messaging
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class FIXMessageType(str, Enum):
    """FIX message types"""
    LOGON = "A"
    LOGOUT = "5"
    HEARTBEAT = "0"
    TEST_REQUEST = "1"
    NEW_ORDER_SINGLE = "D"
    EXECUTION_REPORT = "8"
    ORDER_CANCEL_REQUEST = "F"
    ORDER_CANCEL_REJECT = "9"


class FIXSide(str, Enum):
    """Order side"""
    BUY = "1"
    SELL = "2"


class FIXOrderType(str, Enum):
    """Order type"""
    MARKET = "1"
    LIMIT = "2"
    STOP = "3"
    STOP_LIMIT = "4"


class FIXProtocol:
    """FIX Protocol message handler"""
    
    def __init__(self, version: str = "FIX.4.2"):
        self.version = version
        self.seq_num = 1
    
    def _format_timestamp(self, dt: Optional[datetime] = None) -> str:
        """Format timestamp for FIX message"""
        if dt is None:
            dt = datetime.utcnow()
        return dt.strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
    
    def _calculate_checksum(self, message: str) -> str:
        """Calculate FIX message checksum"""
        checksum = sum(ord(c) for c in message) % 256
        return f"{checksum:03d}"
    
    def create_message(
        self,
        msg_type: FIXMessageType,
        sender_comp_id: str,
        target_comp_id: str,
        fields: Dict[int, Any]
    ) -> str:
        """
        Create a FIX message
        
        Args:
            msg_type: Message type
            sender_comp_id: Sender company ID
            target_comp_id: Target company ID
            fields: Additional FIX fields as tag-value pairs
            
        Returns:
            str: Formatted FIX message
        """
        # Build message body
        body = []
        body.append(f"35={msg_type.value}")  # MsgType
        body.append(f"49={sender_comp_id}")  # SenderCompID
        body.append(f"56={target_comp_id}")  # TargetCompID
        body.append(f"34={self.seq_num}")    # MsgSeqNum
        body.append(f"52={self._format_timestamp()}")  # SendingTime
        
        # Add custom fields
        for tag, value in sorted(fields.items()):
            body.append(f"{tag}={value}")
        
        body_str = "\x01".join(body)
        
        # Build header
        header = []
        header.append(f"8={self.version}")  # BeginString
        header.append(f"9={len(body_str)}")  # BodyLength
        
        header_str = "\x01".join(header)
        
        # Build message without checksum
        message_without_checksum = header_str + "\x01" + body_str + "\x01"
        
        # Calculate and append checksum
        checksum = self._calculate_checksum(message_without_checksum)
        full_message = message_without_checksum + f"10={checksum}\x01"
        
        self.seq_num += 1
        return full_message
    
    def create_new_order(
        self,
        symbol: str,
        side: FIXSide,
        quantity: int,
        price: float,
        order_type: FIXOrderType = FIXOrderType.LIMIT,
        client_order_id: Optional[str] = None
    ) -> str:
        """
        Create a new order message
        
        Args:
            symbol: Trading symbol
            side: Buy or Sell
            quantity: Order quantity
            price: Order price
            order_type: Order type
            client_order_id: Client order ID
            
        Returns:
            str: FIX new order message
        """
        if client_order_id is None:
            client_order_id = f"ORD{int(datetime.utcnow().timestamp() * 1000)}"
        
        fields = {
            11: client_order_id,      # ClOrdID
            21: "1",                   # HandlInst (Automated execution)
            55: symbol,                # Symbol
            54: side.value,            # Side
            40: order_type.value,      # OrdType
            38: quantity,              # OrderQty
            44: price,                 # Price
            59: "0",                   # TimeInForce (Day)
            60: self._format_timestamp()  # TransactTime
        }
        
        return self.create_message(
            FIXMessageType.NEW_ORDER_SINGLE,
            "SENDER",
            "TARGET",
            fields
        )
    
    def parse_message(self, message: str) -> Dict[int, str]:
        """
        Parse a FIX message
        
        Args:
            message: FIX message string
            
        Returns:
            Dict: Parsed FIX fields as tag-value pairs
        """
        fields = {}
        parts = message.split("\x01")
        
        for part in parts:
            if "=" in part:
                tag, value = part.split("=", 1)
                try:
                    fields[int(tag)] = value
                except ValueError:
                    continue
        
        return fields
    
    def create_execution_report(
        self,
        order_id: str,
        exec_id: str,
        exec_type: str,
        order_status: str,
        symbol: str,
        side: FIXSide,
        quantity: int,
        price: float
    ) -> str:
        """
        Create an execution report
        
        Args:
            order_id: Order ID
            exec_id: Execution ID
            exec_type: Execution type
            order_status: Order status
            symbol: Trading symbol
            side: Buy or Sell
            quantity: Order quantity
            price: Execution price
            
        Returns:
            str: FIX execution report message
        """
        fields = {
            37: order_id,              # OrderID
            17: exec_id,               # ExecID
            150: exec_type,            # ExecType
            39: order_status,          # OrdStatus
            55: symbol,                # Symbol
            54: side.value,            # Side
            38: quantity,              # OrderQty
            44: price,                 # Price
            31: price,                 # LastPx
            32: quantity,              # LastShares
            14: quantity,              # CumQty
            151: 0,                    # LeavesQty
            60: self._format_timestamp()  # TransactTime
        }
        
        return self.create_message(
            FIXMessageType.EXECUTION_REPORT,
            "SENDER",
            "TARGET",
            fields
        )
