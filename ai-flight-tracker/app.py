import logging
import re
import time
import uuid
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from services import ai, opensky, pricing, routes_repo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static")
    app.secret_key = Config.SECRET_KEY

    CORS(app, origins=Config.CORS_ORIGINS)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[],
        storage_uri="memory://",
    )

    @app.before_request
    def _before():
        request.request_id = str(uuid.uuid4())[:8]
        request.start_time = time.time()

    @app.after_request
    def _after(response):
        latency = round((time.time() - request.start_time) * 1000)
        logger.info(
            "req_id=%s method=%s path=%s status=%s latency_ms=%d",
            request.request_id,
            request.method,
            request.path,
            response.status_code,
            latency,
        )
        response.headers["X-Request-Id"] = request.request_id
        return response

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(429)
    def too_many(_e):
        return jsonify({"error": "Rate limit exceeded. Please slow down."}), 429

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/api/routes")
    def get_routes():
        all_routes = routes_repo.get_all()
        sorted_routes = sorted(all_routes.items(), key=lambda x: (x[1]["priority"], x[0]))
        departure = datetime.now() + timedelta(days=30)
        data = []
        for code, route in sorted_routes:
            price_info = pricing.calculate(code, route, departure)
            data.append({
                "route_code": code,
                "origin": route["origin"],
                "destination": route["destination"],
                "duration_hours": route["duration_hours"],
                "stoppages": route["stoppages"],
                "num_stops": len(route["stoppages"]),
                "airlines": route["airlines"],
                "base_price": price_info["price"],
                "currency": route["currency"],
                "is_priority": route["priority"] == 1,
                "is_live": price_info.get("is_live", False),
            })
        return jsonify({"routes": data})

    @app.route("/api/route/<route_code>")
    def get_route_details(route_code):
        route = routes_repo.get_by_code(route_code.upper())
        if not route:
            return jsonify({"error": "Route not found"}), 404
        now = datetime.now()
        pricing_windows = {
            "last_minute": pricing.calculate(route_code, route, now + timedelta(days=5)),
            "two_weeks": pricing.calculate(route_code, route, now + timedelta(days=14)),
            "one_month": pricing.calculate(route_code, route, now + timedelta(days=30)),
            "early_bird": pricing.calculate(route_code, route, now + timedelta(days=90)),
        }
        return jsonify({
            "route_code": route_code,
            "origin": route["origin"],
            "destination": route["destination"],
            "duration_hours": route["duration_hours"],
            "stoppages": route["stoppages"],
            "num_stops": len(route["stoppages"]),
            "airlines": route["airlines"],
            "pricing": pricing_windows,
            "is_priority": route["priority"] == 1,
        })

    @app.route("/api/search")
    def search_routes():
        origin = request.args.get("origin", "")
        destination = request.args.get("destination", "")
        max_stops = request.args.get("max_stops", type=int)
        max_price = request.args.get("max_price", type=float)
        results_raw = routes_repo.search(
            origin=origin, destination=destination,
            max_stops=max_stops, max_price=max_price
        )
        departure = datetime.now() + timedelta(days=30)
        results = []
        for code, route in results_raw:
            price_info = pricing.calculate(code, route, departure)
            results.append({
                "route_code": code,
                "origin": route["origin"],
                "destination": route["destination"],
                "duration_hours": route["duration_hours"],
                "stoppages": route["stoppages"],
                "num_stops": len(route["stoppages"]),
                "airlines": route["airlines"],
                "estimated_price": price_info["price"],
                "currency": route["currency"],
                "is_priority": route["priority"] == 1,
                "is_live": price_info.get("is_live", False),
            })
        results.sort(key=lambda x: (0 if x["is_priority"] else 1, x["estimated_price"]))
        return jsonify({"results": results, "count": len(results)})

    @app.route("/api/flights")
    @limiter.limit(Config.RATE_LIMIT_FLIGHTS)
    def get_flights():
        lamin = request.args.get("lamin", type=float)
        lamax = request.args.get("lamax", type=float)
        lomin = request.args.get("lomin", type=float)
        lomax = request.args.get("lomax", type=float)
        bbox_params = [lamin, lamax, lomin, lomax]
        if any(v is not None for v in bbox_params) and not all(v is not None for v in bbox_params):
            return jsonify({"error": "All bbox params required: lamin, lamax, lomin, lomax"}), 400
        if lamin is not None:
            if lamin < -90 or lamax > 90 or lomin < -180 or lomax > 180:
                return jsonify({"error": "Invalid bbox values"}), 400
            if lamin >= lamax or lomin >= lomax:
                return jsonify({"error": "lamin must be < lamax and lomin must be < lomax"}), 400
        flights = opensky.fetch_flights(lamin=lamin, lamax=lamax, lomin=lomin, lomax=lomax)
        return jsonify({"flights": flights, "count": len(flights)})

    @app.route("/api/flights/<icao24>")
    def get_flight_detail(icao24):
        if not re.match(r'^[a-fA-F0-9]{6}$', icao24):
            return jsonify({"error": "Invalid ICAO24 format (must be 6 hex chars)"}), 400
        flight = opensky.fetch_flight_detail(icao24)
        if not flight:
            return jsonify({"error": "Flight not found"}), 404
        return jsonify(flight)

    @app.route("/api/aviation/ask", methods=["POST"])
    @limiter.limit(Config.RATE_LIMIT_ASK)
    def aviation_ask():
        if not request.is_json:
            return jsonify({"error": "JSON body required"}), 400
        data = request.get_json(silent=True) or {}
        question = (data.get("question") or "").strip()
        if not question:
            return jsonify({"error": "question field is required"}), 400
        if len(question) > 500:
            return jsonify({"error": "question too long (max 500 chars)"}), 400

        if "preferences" not in session:
            session["preferences"] = {}
        q_lower = question.lower()
        for city in ["dhaka", "gdansk", "warsaw", "london", "dubai"]:
            if city in q_lower:
                session["preferences"]["last_mentioned_city"] = city
                session.modified = True
                break

        session_ctx = ""
        prefs = session.get("preferences", {})
        if prefs:
            session_ctx = "User context: " + ", ".join(f"{k}={v}" for k, v in prefs.items())

        answer = ai.ask(question, session_ctx)
        return jsonify({"answer": answer})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
