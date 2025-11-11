"""
Fintech Tools - Main FastAPI Application

A comprehensive fintech toolkit for banking, payments, protocols, and account management.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
from contextlib import asynccontextmanager

# Import routers (will be created)
from src.auth.security import get_current_user
from src.auth.models import User

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Fintech Tools API...")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("🔐 Security: JWT Authentication enabled")
    yield
    # Shutdown
    print("👋 Shutting down Fintech Tools API...")

# Initialize FastAPI application
app = FastAPI(
    title="Fintech Tools API",
    description="""
    A comprehensive fintech toolkit providing:
    * 🏦 Banking operations
    * 💳 Payment processing
    * 📡 Financial protocols (FIX, FAST, ITCH)
    * 👤 Account management (BO and Client)
    * 🏢 Back-office operations
    * 🔐 Secure authentication and authorization
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()


# Root endpoint
@app.get("/", tags=["Root"])
@limiter.limit("10/minute")
async def root():
    """
    Welcome endpoint with API information
    """
    return {
        "message": "Welcome to Fintech Tools API",
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Banking Operations",
            "Payment Processing",
            "FIX/FAST/ITCH Protocols",
            "Account Management",
            "Back Office Operations",
            "Secure Authentication"
        ]
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "fintech-tools",
        "version": "1.0.0"
    }


# Protected endpoint example
@app.get("/protected", tags=["Security"])
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    Example protected endpoint requiring authentication
    """
    return {
        "message": "This is a protected endpoint",
        "user": current_user.username,
        "role": current_user.role
    }


# Banking endpoints group
@app.get("/bank/status", tags=["Banking"])
async def bank_status():
    """
    Get banking module status
    """
    return {
        "module": "banking",
        "status": "operational",
        "features": ["accounts", "transactions", "balance_inquiry"]
    }


# Payment endpoints group
@app.get("/payment/status", tags=["Payment"])
async def payment_status():
    """
    Get payment module status
    """
    return {
        "module": "payment",
        "status": "operational",
        "features": ["process_payment", "refunds", "gateway_integration"]
    }


# Protocols endpoints group
@app.get("/protocols/status", tags=["Protocols"])
async def protocols_status():
    """
    Get protocols module status
    """
    return {
        "module": "protocols",
        "status": "operational",
        "supported_protocols": ["FIX", "FAST", "ITCH"],
        "features": ["message_parsing", "encoding", "decoding"]
    }


# Account management endpoints group
@app.get("/accounts/status", tags=["Account Management"])
async def accounts_status():
    """
    Get account management module status
    """
    return {
        "module": "account_management",
        "status": "operational",
        "account_types": ["client_accounts", "backoffice_accounts"],
        "features": ["portfolio_management", "position_tracking"]
    }


# Back office endpoints group
@app.get("/backoffice/status", tags=["Back Office"])
async def backoffice_status():
    """
    Get back office module status
    """
    return {
        "module": "backoffice",
        "status": "operational",
        "features": ["reconciliation", "settlement", "reporting"]
    }


# Authentication endpoints group
@app.get("/auth/status", tags=["Authentication"])
async def auth_status():
    """
    Get authentication module status
    """
    return {
        "module": "authentication",
        "status": "operational",
        "features": ["jwt_tokens", "rbac", "password_hashing"],
        "supported_roles": ["admin", "backoffice", "trader", "client"]
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
