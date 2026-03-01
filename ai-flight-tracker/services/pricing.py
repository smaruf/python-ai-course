import random
from datetime import datetime, timedelta
from typing import Optional, Dict

from config import Config

_cache: Dict = {}


def _get_cached(key: str) -> Optional[Dict]:
    if key in _cache:
        data, ts = _cache[key]
        if (datetime.now() - ts).total_seconds() < Config.CACHE_TTL:
            return data
    return None


def _set_cached(key: str, data: Dict) -> None:
    _cache[key] = (data, datetime.now())


def _fetch_live_price(origin: str, destination: str, departure_date: datetime) -> Optional[Dict]:
    if not Config.LIVE_PRICING_ENABLED or not Config.PRICING_API_KEY:
        return None
    try:
        import requests
        params = {
            "access_key": Config.PRICING_API_KEY,
            "dep_iata": origin,
            "arr_iata": destination,
            "date": departure_date.strftime("%Y-%m-%d"),
        }
        resp = requests.get(
            "https://api.aviationstack.com/v1/flights",
            params=params,
            timeout=3,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("data") and data["data"][0].get("price"):
                fd = data["data"][0]
                return {
                    "price": float(fd["price"]),
                    "currency": fd.get("currency", "USD"),
                    "is_live": True,
                    "source": "live_api",
                }
    except Exception:
        pass
    return None


def calculate(route_code: str, route: Dict, departure_date: Optional[datetime] = None) -> Dict:
    if not departure_date:
        departure_date = datetime.now() + timedelta(days=30)
    cache_key = f"{route_code}_{departure_date.strftime('%Y-%m-%d')}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    codes = route_code.split("-")
    if len(codes) == 2:
        live = _fetch_live_price(codes[0], codes[1], departure_date)
        if live:
            result = {**live, "route": route_code, "origin": route["origin"], "destination": route["destination"]}
            _set_cached(cache_key, result)
            return result

    base = route["base_price"]
    days = (departure_date - datetime.now()).days
    if days < 7:
        base *= 1.4
    elif days < 14:
        base *= 1.2
    elif days > 60:
        base *= 0.85
    price = round(base * random.uniform(0.95, 1.05), 2)
    result = {
        "price": price,
        "currency": route["currency"],
        "route": route_code,
        "origin": route["origin"],
        "destination": route["destination"],
        "is_live": False,
        "source": "simulated",
    }
    _set_cached(cache_key, result)
    return result
