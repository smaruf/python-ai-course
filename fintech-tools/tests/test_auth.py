"""
Tests for Authentication Module
"""

import pytest
from src.auth.jwt_handler import (
    create_access_token,
    decode_access_token,
    verify_password,
    get_password_hash
)
from src.auth.models import TokenData


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Verify correct password
    assert verify_password(password, hashed) is True
    
    # Verify incorrect password
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "test@example.com", "role": "client"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    """Test JWT token decoding"""
    data = {"sub": "test@example.com", "role": "client"}
    token = create_access_token(data)
    
    decoded = decode_access_token(token)
    
    assert decoded is not None
    assert isinstance(decoded, TokenData)
    assert decoded.username == "test@example.com"
    assert decoded.role == "client"


def test_decode_invalid_token():
    """Test decoding invalid token"""
    invalid_token = "invalid.token.here"
    
    decoded = decode_access_token(invalid_token)
    
    assert decoded is None
