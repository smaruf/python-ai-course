"""
Authentication Models

User and authentication-related data models
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    BACKOFFICE = "backoffice"
    TRADER = "trader"
    CLIENT = "client"


class User(BaseModel):
    """User model"""
    id: Optional[int] = None
    username: EmailStr
    full_name: str
    role: UserRole = UserRole.CLIENT
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password"""
    hashed_password: str


class UserCreate(BaseModel):
    """User creation model"""
    username: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str
    role: UserRole = UserRole.CLIENT


class UserLogin(BaseModel):
    """User login model"""
    username: EmailStr
    password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data extracted from JWT"""
    username: Optional[str] = None
    role: Optional[str] = None
