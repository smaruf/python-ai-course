"""
Authentication Module

Provides JWT-based authentication and authorization
"""

from .models import User, UserInDB, UserCreate, UserLogin, Token, TokenData, UserRole
from .jwt_handler import (
    create_access_token,
    decode_access_token,
    verify_password,
    get_password_hash,
    create_token_response
)
from .security import (
    get_current_user,
    get_current_active_user,
    get_user,
    require_role,
    require_any_role
)

__all__ = [
    # Models
    "User",
    "UserInDB",
    "UserCreate",
    "UserLogin",
    "Token",
    "TokenData",
    "UserRole",
    # JWT Handler
    "create_access_token",
    "decode_access_token",
    "verify_password",
    "get_password_hash",
    "create_token_response",
    # Security
    "get_current_user",
    "get_current_active_user",
    "get_user",
    "require_role",
    "require_any_role",
]
