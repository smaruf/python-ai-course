"""
Webhook API endpoints for receiving WhatsApp messages.
"""

from fastapi import FastAPI, Request, Response, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..utils.config import settings

# Create FastAPI app
app = FastAPI(
    title="WhatsApp Medical Report Vault",
    description="Secure medical document storage via WhatsApp",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.environment
    }


@app.get("/webhook/whatsapp")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
):
    """
    Webhook verification endpoint for WhatsApp.
    
    Called by WhatsApp during initial webhook setup.
    """
    if mode == "subscribe" and token == settings.whatsapp_webhook_verify_token:
        return int(challenge)
    
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@app.post("/webhook/whatsapp")
@limiter.limit("60/minute")
async def webhook_handler(request: Request):
    """
    Webhook endpoint for receiving WhatsApp messages.
    
    This is the main entry point for all WhatsApp messages.
    Messages are validated and queued for asynchronous processing.
    """
    try:
        # Get request body
        body = await request.json()
        
        # TODO: Implement webhook signature verification
        # TODO: Validate payload structure
        # TODO: Publish to message queue
        # TODO: Return 200 OK within 10 seconds
        
        # For now, just acknowledge
        return Response(status_code=200)
        
    except Exception as e:
        # Log error but still return 200 to avoid WhatsApp retries
        # Actual errors should be handled in the async worker
        return Response(status_code=200)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "WhatsApp Medical Report Vault",
        "version": "0.1.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
