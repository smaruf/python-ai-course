# Authentication and Security Documentation

## Overview

The authentication module provides JWT-based authentication and role-based access control (RBAC) for the Fintech Tools API.

## Features

- **JWT Token Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt-based password hashing
- **Role-Based Access Control (RBAC)**: Multiple user roles with different permissions
- **Token Management**: Token creation, validation, and refresh

## User Roles

### Available Roles

1. **Admin** (`admin`)
   - Full system access
   - Can manage all resources
   - Can access all endpoints

2. **Back Office** (`backoffice`)
   - Access to back-office operations
   - Can view and manage settlements and reconciliations
   - Limited trading access

3. **Trader** (`trader`)
   - Can create and manage orders
   - Access to trading endpoints
   - Portfolio management

4. **Client** (`client`)
   - Limited access to own accounts
   - Can view portfolio and transactions
   - Cannot access administrative functions

## Authentication Flow

### 1. User Registration

```bash
POST /auth/register
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "role": "client"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "user@example.com",
  "full_name": "John Doe",
  "role": "client",
  "is_active": true
}
```

### 2. User Login

```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePassword123!
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Using the Token

Include the token in the Authorization header for protected endpoints:

```bash
GET /protected-endpoint
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Security Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Generating a Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Code Examples

### Using Authentication in Endpoints

```python
from fastapi import Depends
from src.auth import get_current_user, User, require_role, UserRole

@app.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}

@app.get("/admin-only")
async def admin_endpoint(current_user: User = Depends(require_role(UserRole.ADMIN))):
    return {"message": "Admin access granted"}
```

### Checking Multiple Roles

```python
from src.auth import require_any_role, UserRole

@app.get("/trading")
async def trading_endpoint(
    current_user: User = Depends(require_any_role(UserRole.TRADER, UserRole.ADMIN))
):
    return {"message": "Trading access granted"}
```

### Manual Token Creation

```python
from src.auth.jwt_handler import create_token_response

token_data = create_token_response(
    username="user@example.com",
    role="trader"
)
# Returns: {"access_token": "...", "token_type": "bearer", "expires_in": 1800}
```

### Password Hashing

```python
from src.auth.jwt_handler import get_password_hash, verify_password

# Hash a password
hashed = get_password_hash("mypassword")

# Verify a password
is_valid = verify_password("mypassword", hashed)
```

## Security Best Practices

### 1. Strong Secret Keys

- Use a cryptographically secure random string
- Never commit secret keys to version control
- Rotate keys periodically

### 2. Password Requirements

- Minimum 8 characters
- Mix of uppercase, lowercase, numbers, and special characters
- Consider implementing password strength meter

### 3. Token Expiration

- Set appropriate expiration times (default: 30 minutes)
- Implement token refresh mechanism
- Invalidate tokens on logout

### 4. HTTPS Only

In production, always use HTTPS:

```python
# Force HTTPS redirect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)
```

### 5. Rate Limiting

Protect against brute force attacks:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login():
    pass
```

## Common Issues and Solutions

### Issue: "Could not validate credentials"

**Causes:**
- Expired token
- Invalid token format
- Wrong secret key

**Solution:**
- Request a new token
- Check token format
- Verify SECRET_KEY environment variable

### Issue: "403 Forbidden"

**Cause:** User doesn't have required role

**Solution:** Check user role and endpoint requirements

### Issue: Token not being accepted

**Cause:** Missing "Bearer" prefix

**Solution:** Ensure Authorization header is formatted correctly:
```
Authorization: Bearer <token>
```

## Advanced Topics

### Custom User Storage

Replace the mock database with a real database:

```python
from sqlalchemy.orm import Session

def get_user(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()
```

### Token Refresh

Implement token refresh endpoint:

```python
@app.post("/auth/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    return create_token_response(current_user.username, current_user.role)
```

### Logout (Token Blacklisting)

Implement token blacklisting for logout:

```python
# Store blacklisted tokens in Redis or database
blacklist = set()

@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    blacklist.add(credentials.credentials)
    return {"message": "Logged out successfully"}
```

## API Reference

### Models

- `User`: User information model
- `UserCreate`: User registration model
- `UserLogin`: Login credentials model
- `Token`: Token response model
- `TokenData`: Decoded token data

### Functions

- `create_access_token()`: Create JWT token
- `decode_access_token()`: Decode and validate JWT
- `verify_password()`: Verify password hash
- `get_password_hash()`: Hash a password
- `get_current_user()`: Dependency to get authenticated user
- `require_role()`: Dependency factory for role checking

## Testing Authentication

```python
import pytest
from fastapi.testclient import TestClient

def test_login():
    client = TestClient(app)
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint():
    client = TestClient(app)
    # Login first
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```
