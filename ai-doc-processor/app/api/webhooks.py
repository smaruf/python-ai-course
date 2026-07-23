import hashlib
import hmac
from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings

router = APIRouter()


def _verify_signature(payload: bytes, header_sig: str) -> bool:
    expected = hmac.new(
        settings.LEMONSQUEEZY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, header_sig)


@router.post("/lemonsqueezy")
async def lemonsqueezy_webhook(request: Request):
    """Handle Lemon Squeezy subscription lifecycle events."""
    payload = await request.body()
    sig = request.headers.get("X-Signature", "")

    if not _verify_signature(payload, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = await request.json()
    event_name = event.get("meta", {}).get("event_name")

    if event_name == "subscription_created":
        # TODO: update user subscription_status = 'active' in DB
        pass
    elif event_name == "subscription_cancelled":
        # TODO: update user subscription_status = 'cancelled' in DB
        pass

    return {"received": True}
