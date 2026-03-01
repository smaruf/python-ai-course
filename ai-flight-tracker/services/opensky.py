import logging
from typing import Dict, List, Optional

import requests

from config import Config

logger = logging.getLogger(__name__)

_FIELDS = ["icao24", "callsign", "origin_country", "time_position", "last_contact",
           "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
           "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
           "spi", "position_source"]


def _parse_state(state: list) -> Dict:
    d = dict(zip(_FIELDS, state))
    return {
        "icao24": d.get("icao24", ""),
        "callsign": (d.get("callsign") or "").strip(),
        "origin_country": d.get("origin_country", ""),
        "lat": d.get("latitude"),
        "lon": d.get("longitude"),
        "altitude": d.get("baro_altitude"),
        "velocity": d.get("velocity"),
        "heading": d.get("true_track"),
        "on_ground": d.get("on_ground", False),
        "last_contact": d.get("last_contact"),
    }


def fetch_flights(lamin: Optional[float] = None, lamax: Optional[float] = None,
                  lomin: Optional[float] = None, lomax: Optional[float] = None) -> List[Dict]:
    params: Dict = {}
    if all(v is not None for v in [lamin, lamax, lomin, lomax]):
        params = {"lamin": lamin, "lamax": lamax, "lomin": lomin, "lomax": lomax}
    auth = None
    if Config.OPENSKY_USERNAME and Config.OPENSKY_PASSWORD:
        auth = (Config.OPENSKY_USERNAME, Config.OPENSKY_PASSWORD)
    try:
        resp = requests.get(
            f"{Config.OPENSKY_URL}/states/all",
            params=params,
            auth=auth,
            timeout=Config.OPENSKY_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        states = data.get("states") or []
        return [_parse_state(s) for s in states if s[5] is not None and s[6] is not None]
    except requests.RequestException as exc:
        logger.warning("OpenSky fetch failed: %s", exc)
        return []


def fetch_flight_detail(icao24: str) -> Optional[Dict]:
    try:
        resp = requests.get(
            f"{Config.OPENSKY_URL}/states/all",
            params={"icao24": icao24.lower()},
            timeout=Config.OPENSKY_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        states = data.get("states") or []
        if states:
            return _parse_state(states[0])
    except requests.RequestException as exc:
        logger.warning("OpenSky detail fetch failed: %s", exc)
    return None
