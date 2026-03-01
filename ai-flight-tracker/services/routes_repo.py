import json
import os
from typing import Dict, Optional

_ROUTES_FILE = os.path.join(os.path.dirname(__file__), "..", "routes.json")
_routes_cache: Optional[Dict] = None


def _load() -> Dict:
    global _routes_cache
    if _routes_cache is None:
        with open(_ROUTES_FILE, encoding="utf-8") as f:
            _routes_cache = json.load(f)
    return _routes_cache


def get_all() -> Dict:
    return _load()


def get_by_code(route_code: str) -> Optional[Dict]:
    return _load().get(route_code)


def search(origin: str = "", destination: str = "", max_stops: Optional[int] = None, max_price: Optional[float] = None) -> list:
    results = []
    for code, route in _load().items():
        if origin and origin.upper() not in route["origin"].upper():
            continue
        if destination and destination.upper() not in route["destination"].upper():
            continue
        if max_stops is not None and len(route["stoppages"]) > max_stops:
            continue
        if max_price is not None and route["base_price"] > max_price:
            continue
        results.append((code, route))
    results.sort(key=lambda x: (x[1]["priority"], x[0]))
    return results
