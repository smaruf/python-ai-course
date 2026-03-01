import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Server
    PORT = int(os.getenv("PORT", 8080))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # OpenSky
    OPENSKY_URL = os.getenv("OPENSKY_URL", "https://opensky-network.org/api")
    OPENSKY_USERNAME = os.getenv("OPENSKY_USERNAME", "")
    OPENSKY_PASSWORD = os.getenv("OPENSKY_PASSWORD", "")
    OPENSKY_TIMEOUT = int(os.getenv("OPENSKY_TIMEOUT", 10))

    # Ollama / AI
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", 30))

    # Cache
    CACHE_TTL = int(os.getenv("CACHE_TTL", 300))

    # Rate limiting (requests per minute)
    RATE_LIMIT_ASK = os.getenv("RATE_LIMIT_ASK", "10 per minute")
    RATE_LIMIT_FLIGHTS = os.getenv("RATE_LIMIT_FLIGHTS", "30 per minute")

    # Pricing
    LIVE_PRICING_ENABLED = os.getenv("LIVE_PRICING_ENABLED", "false").lower() == "true"
    PRICING_API_KEY = os.getenv("PRICING_API_KEY", "")
