import logging
import re
from typing import Dict, Any

import requests

from config import Config
from services import routes_repo, opensky

logger = logging.getLogger(__name__)


# ---------- Tool definitions ----------

def tool_list_routes() -> Dict:
    routes = routes_repo.get_all()
    return {
        code: {
            "origin": r["origin"],
            "destination": r["destination"],
            "duration_hours": r["duration_hours"],
            "base_price": r["base_price"],
            "currency": r["currency"],
            "stops": len(r["stoppages"]),
        }
        for code, r in routes.items()
    }


def tool_route_details(route_code: str) -> Dict:
    r = routes_repo.get_by_code(route_code.upper())
    if not r:
        return {"error": f"Route {route_code} not found"}
    return r


def tool_search_routes(origin: str = "", destination: str = "") -> list:
    results = routes_repo.search(origin=origin, destination=destination)
    return [
        {
            "route_code": code,
            "origin": r["origin"],
            "destination": r["destination"],
            "base_price": r["base_price"],
            "duration_hours": r["duration_hours"],
            "stops": len(r["stoppages"]),
            "airlines": r["airlines"],
        }
        for code, r in results
    ]


def tool_flights_in_bbox(lamin: float, lamax: float, lomin: float, lomax: float) -> list:
    flights = opensky.fetch_flights(lamin=lamin, lamax=lamax, lomin=lomin, lomax=lomax)
    return flights[:20]


def tool_lookup_flight(identifier: str) -> Dict:
    flight = opensky.fetch_flight_detail(identifier)
    if flight:
        return flight
    # Try by callsign from a broad search
    flights = opensky.fetch_flights()
    for f in flights:
        if f.get("callsign", "").upper() == identifier.upper():
            return f
    return {"error": f"Flight {identifier} not found"}


# ---------- Intent routing ----------

def _route_intent(question: str) -> Dict[str, Any]:
    q = question.lower()
    # Flight lookup
    icao_match = re.search(r'\b([a-f0-9]{6})\b', q)
    callsign_match = re.search(r'\b([a-z]{2,3}\d{1,4}[a-z]?)\b', q)

    if any(kw in q for kw in ["flight ", "aircraft ", "plane "]) and (icao_match or callsign_match):
        ident = icao_match.group(1) if icao_match else callsign_match.group(1)
        return {"tool": "lookup_flight", "result": tool_lookup_flight(ident)}

    # Bbox
    bbox_match = re.search(
        r'(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)', q
    )
    if bbox_match and any(kw in q for kw in ["area", "region", "bbox", "over", "around"]):
        lamin, lamax, lomin, lomax = [float(x) for x in bbox_match.groups()]
        return {"tool": "flights_in_bbox", "result": tool_flights_in_bbox(lamin, lamax, lomin, lomax)}

    # Route search
    if any(kw in q for kw in ["route", "flight from", "fly from", "ticket", "price", "cheapest", "cost"]):
        known = ["dhaka", "dac", "gdansk", "gdn", "warsaw", "waw", "london", "lhr", "dubai", "dxb"]
        # Find all city/code mentions in order of appearance in the question
        found = [o for o in known if o in q]
        origin_found = found[0].upper() if len(found) > 0 else ""
        dest_found = found[1].upper() if len(found) > 1 else ""
        if origin_found or dest_found:
            return {"tool": "search_routes", "result": tool_search_routes(origin=origin_found, destination=dest_found)}
        return {"tool": "list_routes", "result": tool_list_routes()}

    # Default: list routes
    return {"tool": "list_routes", "result": tool_list_routes()}


def _build_context(tool_name: str, tool_result: Any) -> str:
    if tool_name == "list_routes":
        lines = ["Available routes:"]
        for code, r in tool_result.items():
            lines.append(
                f"  {code}: {r['origin']} -> {r['destination']}, "
                f"{r['duration_hours']}h, {r['stops']} stop(s), ~${r['base_price']} {r['currency']}"
            )
        return "\n".join(lines)
    if tool_name == "search_routes":
        if not tool_result:
            return "No matching routes found."
        lines = ["Matching routes:"]
        for r in tool_result:
            lines.append(
                f"  {r['route_code']}: {r['origin']} -> {r['destination']}, "
                f"{r['duration_hours']}h, {r['stops']} stop(s), ~${r['base_price']}, "
                f"Airlines: {', '.join(r['airlines'])}"
            )
        return "\n".join(lines)
    if tool_name == "route_details":
        if "error" in tool_result:
            return tool_result["error"]
        r = tool_result
        return (
            f"Route details: {r['origin']} -> {r['destination']}, "
            f"Duration: {r['duration_hours']}h, Stops: {r['stoppages']}, "
            f"Airlines: {r['airlines']}, Base price: ${r['base_price']} {r['currency']}"
        )
    if tool_name == "flights_in_bbox":
        if not tool_result:
            return "No flights found in that area."
        lines = [f"Flights in area ({len(tool_result)} shown):"]
        for f in tool_result[:10]:
            lines.append(
                f"  {f['icao24']} {f['callsign']} from {f['origin_country']} "
                f"at lat={f['lat']}, lon={f['lon']}, alt={f['altitude']}m"
            )
        return "\n".join(lines)
    if tool_name == "lookup_flight":
        if "error" in tool_result:
            return tool_result["error"]
        f = tool_result
        return (
            f"Flight {f['icao24']} ({f['callsign']}): from {f['origin_country']}, "
            f"lat={f['lat']}, lon={f['lon']}, altitude={f['altitude']}m, "
            f"speed={f['velocity']}m/s, heading={f['heading']}°"
        )
    return str(tool_result)[:1000]


def ask(question: str, session_context: str = "") -> str:
    intent = _route_intent(question)
    tool_name = intent["tool"]
    tool_result = intent["result"]
    context = _build_context(tool_name, tool_result)
    if session_context:
        context = session_context + "\n\n" + context

    prompt = (
        f"You are a helpful flight assistant. Use the following data to answer the question.\n\n"
        f"{context}\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )
    try:
        resp = requests.post(
            Config.OLLAMA_URL,
            json={"model": Config.OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=Config.OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json().get("response", "No answer.")
    except requests.RequestException as exc:
        logger.warning("Ollama request failed: %s", exc)
        return f"AI unavailable. Based on available data: {context}"
