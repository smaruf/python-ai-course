"""
Banking Models

Data models for banking operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class AccountType(str, Enum):
    """Account type enumeration"""
    SAVINGS = "savings"
    CHECKING = "checking"
    BUSINESS = "business"
    INVESTMENT = "investment"


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"


class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Account(BaseModel):
    """Bank account model"""
    id: Optional[int] = None
    account_number: str = Field(..., min_length=10, max_length=20)
    account_type: AccountType
    customer_name: str
    balance: Decimal = Field(default=Decimal("0.0"), ge=0)
    currency: str = Field(default="USD", max_length=3)
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class AccountCreate(BaseModel):
    """Account creation model"""
    account_number: str = Field(..., min_length=10, max_length=20)
    account_type: AccountType
    customer_name: str
    initial_balance: Decimal = Field(default=Decimal("0.0"), ge=0)
    currency: str = Field(default="USD", max_length=3)


class AccountUpdate(BaseModel):
    """Account update model"""
    customer_name: Optional[str] = None
    is_active: Optional[bool] = None


class Transaction(BaseModel):
    """Transaction model"""
    id: Optional[int] = None
    transaction_id: str
    transaction_type: TransactionType
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    status: TransactionStatus = TransactionStatus.PENDING
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class TransactionCreate(BaseModel):
    """Transaction creation model"""
    transaction_type: TransactionType
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    description: Optional[str] = None


class BalanceInquiry(BaseModel):
    """Balance inquiry response"""
    account_number: str
    balance: Decimal
    currency: str
    available_balance: Decimal
    as_of_date: datetime
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class TransactionHistory(BaseModel):
    """Transaction history response"""
    account_number: str
    transactions: List[Transaction]
    total_count: int
    page: int
    page_size: int
