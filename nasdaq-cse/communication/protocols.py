"""
FIX/FAST protocol simulation for market connectivity
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class MessageType(str, Enum):
    NEW_ORDER_SINGLE = "D"
    EXECUTION_REPORT = "8"
    MARKET_DATA_SNAPSHOT = "W"
    MARKET_DATA_INCREMENTAL = "X"
    HEARTBEAT = "0"
    LOGON = "A"
    LOGOUT = "5"


class FIXMessage:
    """
    Simple FIX message implementation
    """
    
    def __init__(self, msg_type: MessageType, fields: Dict[str, str]):
        self.msg_type = msg_type
        self.fields = fields
        self.fields["35"] = msg_type.value  # MsgType
        self.fields["52"] = datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")  # SendingTime
        
    def to_fix_string(self) -> str:
        """Convert message to FIX format string"""
        fix_parts = []
        
        # Always start with BeginString and BodyLength (calculated later)
        fix_parts.append("8=FIX.4.4")
        
        # Add all fields
        for tag, value in sorted(self.fields.items()):
            fix_parts.append(f"{tag}={value}")
        
        # Calculate body length (everything after the BodyLength field)
        body = "|".join(fix_parts[1:])
        fix_parts.insert(1, f"9={len(body)}")
        
        # Add checksum (simplified)
        checksum = sum(ord(c) for c in "|".join(fix_parts)) % 256
        fix_parts.append(f"10={checksum:03d}")
        
        return "|".join(fix_parts)
    
    @classmethod
    def from_fix_string(cls, fix_string: str) -> 'FIXMessage':
        """Parse FIX message from string"""
        parts = fix_string.split("|")
        fields = {}
        
        for part in parts:
            if "=" in part:
                tag, value = part.split("=", 1)
                fields[tag] = value
        
        msg_type = MessageType(fields.get("35", ""))
        return cls(msg_type, fields)


class FIXEngine:
    """
    FIX engine for handling protocol communication
    """
    
    def __init__(self, sender_comp_id: str = "CSE_TRADING"):
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = "EXCHANGE"
        self.seq_num = 1
        self.sessions = {}
        self.message_handlers = {}
        self.is_logged_in = False
        
    async def logon(self, username: str, password: str) -> bool:
        """
        Simulate FIX logon process
        """
        logon_msg = FIXMessage(MessageType.LOGON, {
            "49": self.sender_comp_id,  # SenderCompID
            "56": self.target_comp_id,  # TargetCompID
            "34": str(self.seq_num),    # MsgSeqNum
            "553": username,            # Username
            "554": password,            # Password
            "98": "0",                  # EncryptMethod (None)
            "108": "30"                 # HeartBtInt
        })
        
        self.seq_num += 1
        
        # Simulate successful logon
        await asyncio.sleep(0.1)
        self.is_logged_in = True
        
        print(f"FIX Logon: {logon_msg.to_fix_string()}")
        return True
    
    async def send_new_order(self, order_data: Dict) -> str:
        """
        Send new order via FIX protocol
        """
        if not self.is_logged_in:
            raise Exception("Not logged in to FIX session")
        
        cl_ord_id = str(uuid.uuid4())[:8]
        
        order_msg = FIXMessage(MessageType.NEW_ORDER_SINGLE, {
            "49": self.sender_comp_id,
            "56": self.target_comp_id,
            "34": str(self.seq_num),
            "11": cl_ord_id,                                    # ClOrdID
            "55": order_data["symbol"],                         # Symbol
            "54": "1" if order_data["side"] == "BUY" else "2", # Side
            "38": str(order_data["quantity"]),                 # OrderQty
            "40": "1" if order_data["order_type"] == "MARKET" else "2",  # OrdType
            "44": str(order_data.get("price", 0)),             # Price (if limit)
            "59": "0",                                          # TimeInForce (DAY)
            "1": str(order_data.get("account", "DEMO001"))     # Account
        })
        
        self.seq_num += 1
        
        # Simulate sending message
        fix_string = order_msg.to_fix_string()
        print(f"FIX Order: {fix_string}")
        
        # Simulate execution report response
        await asyncio.sleep(0.1)
        await self._simulate_execution_report(cl_ord_id, order_data)
        
        return cl_ord_id
    
    async def _simulate_execution_report(self, cl_ord_id: str, order_data: Dict):
        """
        Simulate execution report from exchange
        """
        exec_id = str(uuid.uuid4())[:8]
        
        # Simulate market execution
        fill_price = order_data.get("price", 2050.0)
        if order_data["order_type"] == "MARKET":
            # Add small slippage for market orders
            slippage = 0.1 if order_data["side"] == "BUY" else -0.1
            fill_price = 2050.0 + slippage
        
        exec_report = FIXMessage(MessageType.EXECUTION_REPORT, {
            "49": self.target_comp_id,
            "56": self.sender_comp_id,
            "34": str(self.seq_num),
            "11": cl_ord_id,                    # ClOrdID
            "17": exec_id,                      # ExecID
            "150": "F",                         # ExecType (Trade)
            "39": "2",                          # OrdStatus (Filled)
            "55": order_data["symbol"],         # Symbol
            "54": "1" if order_data["side"] == "BUY" else "2",
            "38": str(order_data["quantity"]), # OrderQty
            "32": str(order_data["quantity"]), # LastQty
            "31": str(fill_price),              # LastPx
            "14": str(order_data["quantity"]), # CumQty
            "6": str(fill_price)                # AvgPx
        })
        
        print(f"FIX Execution: {exec_report.to_fix_string()}")
        
        # Call execution handler if registered
        if "execution" in self.message_handlers:
            await self.message_handlers["execution"](exec_report)
    
    async def subscribe_market_data(self, symbols: List[str]) -> bool:
        """
        Subscribe to market data feeds
        """
        if not self.is_logged_in:
            raise Exception("Not logged in to FIX session")
        
        for symbol in symbols:
            req_id = str(uuid.uuid4())[:8]
            
            md_request = FIXMessage(MessageType.MARKET_DATA_SNAPSHOT, {
                "49": self.sender_comp_id,
                "56": self.target_comp_id,
                "34": str(self.seq_num),
                "262": req_id,          # MDReqID
                "263": "1",             # SubscriptionRequestType (Snapshot + Updates)
                "264": "1",             # MarketDepth
                "267": "2",             # NoMDEntryTypes
                "269": "0|1",           # MDEntryType (Bid|Offer)
                "146": "1",             # NoRelatedSym
                "55": symbol            # Symbol
            })
            
            self.seq_num += 1
            print(f"FIX Market Data Request: {md_request.to_fix_string()}")
        
        # Start market data simulation
        asyncio.create_task(self._simulate_market_data(symbols))
        return True
    
    async def _simulate_market_data(self, symbols: List[str]):
        """
        Simulate market data updates
        """
        import random
        
        while self.is_logged_in:
            for symbol in symbols:
                # Generate random price movements
                base_price = 2050.0
                price_change = random.uniform(-2.0, 2.0)
                bid_price = base_price + price_change - 0.5
                ask_price = base_price + price_change + 0.5
                
                md_update = FIXMessage(MessageType.MARKET_DATA_INCREMENTAL, {
                    "49": self.target_comp_id,
                    "56": self.sender_comp_id,
                    "34": str(self.seq_num),
                    "55": symbol,           # Symbol
                    "268": "2",             # NoMDEntries
                    "269": "0",             # MDEntryType (Bid)
                    "270": str(bid_price),  # MDEntryPx
                    "271": "100"            # MDEntrySize
                })
                
                # Call market data handler if registered
                if "market_data" in self.message_handlers:
                    await self.message_handlers["market_data"](md_update)
            
            await asyncio.sleep(5)  # Update every 5 seconds
    
    def register_handler(self, handler_type: str, handler_func):
        """
        Register message handler
        """
        self.message_handlers[handler_type] = handler_func
    
    async def logout(self):
        """
        FIX logout
        """
        if self.is_logged_in:
            logout_msg = FIXMessage(MessageType.LOGOUT, {
                "49": self.sender_comp_id,
                "56": self.target_comp_id,
                "34": str(self.seq_num)
            })
            
            print(f"FIX Logout: {logout_msg.to_fix_string()}")
            self.is_logged_in = False


class FASTDecoder:
    """
    Simplified FAST (FIX Adapted for STreaming) decoder
    """
    
    def __init__(self):
        self.templates = {
            "MarketData": {
                "id": 1,
                "fields": ["Symbol", "BidPrice", "AskPrice", "LastPrice", "Volume"]
            },
            "Trade": {
                "id": 2,
                "fields": ["Symbol", "Price", "Quantity", "Timestamp"]
            }
        }
    
    def decode_message(self, fast_data: bytes) -> Dict:
        """
        Decode FAST message (simplified implementation)
        """
        # This is a simplified decoder - real FAST is much more complex
        try:
            # For demonstration, assume JSON-like structure
            data_str = fast_data.decode('utf-8')
            return json.loads(data_str)
        except:
            return {"error": "Failed to decode FAST message"}
    
    def encode_message(self, template_name: str, data: Dict) -> bytes:
        """
        Encode message to FAST format (simplified)
        """
        template = self.templates.get(template_name, {})
        
        # Simplified encoding - just return JSON bytes
        message = {
            "template": template_name,
            "template_id": template.get("id", 0),
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return json.dumps(message).encode('utf-8')


class CommunicationManager:
    """
    Manager for FIX/FAST communication protocols
    """
    
    def __init__(self):
        self.fix_engine = FIXEngine()
        self.fast_decoder = FASTDecoder()
        self.is_connected = False
        
    async def connect(self, username: str = "demo_trader", password: str = "demo123") -> bool:
        """
        Connect to exchange via FIX protocol
        """
        try:
            success = await self.fix_engine.logon(username, password)
            if success:
                self.is_connected = True
                
                # Subscribe to market data
                await self.fix_engine.subscribe_market_data(["GOLD2024DEC", "GOLD2025MAR"])
                
                print("✅ Connected to exchange via FIX protocol")
                return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    async def send_order(self, order_data: Dict) -> str:
        """
        Send order via FIX protocol
        """
        if not self.is_connected:
            raise Exception("Not connected to exchange")
        
        return await self.fix_engine.send_new_order(order_data)
    
    async def disconnect(self):
        """
        Disconnect from exchange
        """
        if self.is_connected:
            await self.fix_engine.logout()
            self.is_connected = False
            print("🔌 Disconnected from exchange")
    
    def register_execution_handler(self, handler_func):
        """
        Register handler for execution reports
        """
        self.fix_engine.register_handler("execution", handler_func)
    
    def register_market_data_handler(self, handler_func):
        """
        Register handler for market data updates
        """
        self.fix_engine.register_handler("market_data", handler_func)


# Global instance
communication_manager = CommunicationManager()