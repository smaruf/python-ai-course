"""
Security Utilities

Provides authentication dependencies and security utilities
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from .jwt_handler import decode_access_token
from .models import User, UserInDB, UserRole

# Security scheme
security = HTTPBearer()

# Mock user database (replace with actual database in production)
fake_users_db = {
    "admin@example.com": {
        "username": "admin@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "is_active": True,
    },
    "trader@example.com": {
        "username": "trader@example.com",
        "full_name": "Trader User",
        "role": "trader",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "is_active": True,
    }
}


def get_user(username: str) -> Optional[UserInDB]:
    """
    Get user from database
    
    Args:
        username: User's username
        
    Returns:
        UserInDB: User object or None if not found
    """
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get the current authenticated user
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(
        username=user.username,
        full_name=user.full_name,
        role=UserRole(user.role),
        is_active=user.is_active
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(required_role: UserRole):
    """
    Dependency factory to check user role
    
    Args:
        required_role: Required user role
        
    Returns:
        Function: Dependency function that checks the role
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """Check if user has required role"""
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role.value}"
            )
        return current_user
    
    return role_checker


def require_any_role(*required_roles: UserRole):
    """
    Dependency factory to check if user has any of the specified roles
    
    Args:
        required_roles: List of acceptable roles
        
    Returns:
        Function: Dependency function that checks the roles
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """Check if user has any of the required roles"""
        if current_user.role not in required_roles and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required one of roles: {', '.join(r.value for r in required_roles)}"
            )
        return current_user
    
    return role_checker
