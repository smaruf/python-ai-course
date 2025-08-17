"""
Core data models for the trading simulator
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class ContractType(str, Enum):
    GOLD_FUTURES = "GOLD_FUTURES"
    GOLD_OPTIONS = "GOLD_OPTIONS"


# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    account_balance = Column(Float, default=100000.0)  # Starting balance $100k
    margin_available = Column(Float, default=100000.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # e.g., "GOLD2024DEC"
    contract_type = Column(SQLEnum(ContractType))
    expiry_date = Column(DateTime)
    contract_size = Column(Float)  # Troy ounces per contract
    tick_size = Column(Float, default=0.01)
    initial_margin = Column(Float)
    maintenance_margin = Column(Float)
    is_active = Column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    user_id = Column(Integer)
    contract_id = Column(Integer)
    side = Column(SQLEnum(OrderSide))
    order_type = Column(SQLEnum(OrderType))
    quantity = Column(Float)
    price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    filled_quantity = Column(Float, default=0.0)
    avg_fill_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True)
    buy_order_id = Column(String)
    sell_order_id = Column(String)
    contract_id = Column(Integer)
    quantity = Column(Float)
    price = Column(Float)
    trade_time = Column(DateTime, default=datetime.utcnow)


class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    contract_id = Column(Integer)
    quantity = Column(Float)  # Positive for long, negative for short
    avg_entry_price = Column(Float)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    margin_requirement = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)


class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer)
    price = Column(Float)
    bid_price = Column(Float, nullable=True)
    ask_price = Column(Float, nullable=True)
    volume = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    analysis_type = Column(String)  # "trade_suggestion", "risk_warning", "strategy_insight"
    content = Column(Text)
    confidence_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Pydantic Models for API
class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    account_balance: float
    margin_available: float
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    contract_symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None


class OrderResponse(BaseModel):
    id: int
    order_id: str
    user_id: int
    contract_id: int
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    status: OrderStatus
    filled_quantity: float
    avg_fill_price: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    id: int
    trade_id: str
    contract_id: int
    quantity: float
    price: float
    trade_time: datetime

    class Config:
        from_attributes = True


class PositionResponse(BaseModel):
    id: int
    user_id: int
    contract_id: int
    quantity: float
    avg_entry_price: float
    unrealized_pnl: float
    realized_pnl: float
    margin_requirement: float
    last_updated: datetime

    class Config:
        from_attributes = True


class MarketDataResponse(BaseModel):
    contract_id: int
    price: float
    bid_price: Optional[float]
    ask_price: Optional[float]
    volume: float
    timestamp: datetime

    class Config:
        from_attributes = True


class AIAnalysisResponse(BaseModel):
    id: int
    analysis_type: str
    content: str
    confidence_score: float
    timestamp: datetime

    class Config:
        from_attributes = True