import requests
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# -------------------- Flight Route Database --------------------
# Sample flight routes with stoppage, duration, and pricing information
FLIGHT_ROUTES = {
    # Prioritized routes: Dhaka <--> Gdansk/Warsaw
    "DAC-GDN": {
        "origin": "Dhaka (DAC)",
        "destination": "Gdansk (GDN)",
        "base_price": 850,
        "currency": "USD",
        "duration_hours": 12.5,
        "stoppages": ["Dubai (DXB)"],
        "priority": 1,
        "airlines": ["Emirates", "Qatar Airways"]
    },
    "GDN-DAC": {
        "origin": "Gdansk (GDN)",
        "destination": "Dhaka (DAC)",
        "base_price": 820,
        "currency": "USD",
        "duration_hours": 13.0,
        "stoppages": ["Istanbul (IST)"],
        "priority": 1,
        "airlines": ["Turkish Airlines", "LOT Polish Airlines"]
    },
    "DAC-WAW": {
        "origin": "Dhaka (DAC)",
        "destination": "Warsaw (WAW)",
        "base_price": 780,
        "currency": "USD",
        "duration_hours": 11.5,
        "stoppages": ["Doha (DOH)"],
        "priority": 1,
        "airlines": ["Qatar Airways", "LOT Polish Airlines"]
    },
    "WAW-DAC": {
        "origin": "Warsaw (WAW)",
        "destination": "Dhaka (DAC)",
        "base_price": 760,
        "currency": "USD",
        "duration_hours": 12.0,
        "stoppages": ["Abu Dhabi (AUH)"],
        "priority": 1,
        "airlines": ["Etihad Airways", "LOT Polish Airlines"]
    },
    # Additional routes
    "DAC-LHR": {
        "origin": "Dhaka (DAC)",
        "destination": "London (LHR)",
        "base_price": 650,
        "currency": "USD",
        "duration_hours": 10.5,
        "stoppages": ["Dubai (DXB)"],
        "priority": 2,
        "airlines": ["British Airways", "Emirates"]
    },
    "DAC-DXB": {
        "origin": "Dhaka (DAC)",
        "destination": "Dubai (DXB)",
        "base_price": 420,
        "currency": "USD",
        "duration_hours": 5.5,
        "stoppages": [],
        "priority": 3,
        "airlines": ["Emirates", "flydubai"]
    },
    "WAW-LHR": {
        "origin": "Warsaw (WAW)",
        "destination": "London (LHR)",
        "base_price": 180,
        "currency": "USD",
        "duration_hours": 2.5,
        "stoppages": [],
        "priority": 2,
        "airlines": ["British Airways", "LOT Polish Airlines"]
    }
}

def calculate_ticket_price(route_code, departure_date=None):
    """Calculate ticket price with dynamic adjustments based on date and demand"""
    if route_code not in FLIGHT_ROUTES:
        return None
    
    route = FLIGHT_ROUTES[route_code]
    base_price = route["base_price"]
    
    # Add price variation based on departure date
    if departure_date:
        days_until_departure = (departure_date - datetime.now()).days
        if days_until_departure < 7:
            # Last minute booking - higher price
            base_price *= 1.4
        elif days_until_departure < 14:
            base_price *= 1.2
        elif days_until_departure > 60:
            # Early bird discount
            base_price *= 0.85
    
    # Add some random variation for market dynamics
    price_variation = random.uniform(0.95, 1.05)
    final_price = round(base_price * price_variation, 2)
    
    return {
        "price": final_price,
        "currency": route["currency"],
        "route": route_code,
        "origin": route["origin"],
        "destination": route["destination"]
    }

# -------------------- Flight Data Fetching --------------------
def fetch_flights(bbox=None):
    url = "https://opensky-network.org/api/states/all"
    params = {}
    if bbox:
        params["lamin"], params["lamax"], params["lomin"], params["lomax"] = bbox
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


# -------------------- AI Assistant via Ollama --------------------
def ask_ollama(question, context):
    prompt = f"Flight data:\n{context}\n\nQuestion: {question}\nAnswer:"
    resp = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    })
    return resp.json().get("response", "No answer.")


# -------------------- REST API Endpoints --------------------
@app.route("/api/routes", methods=["GET"])
def get_routes():
    """Get all available flight routes, prioritizing Dhaka<-->Gdansk/Warsaw"""
    # Sort routes by priority (1 = highest priority)
    sorted_routes = sorted(
        FLIGHT_ROUTES.items(),
        key=lambda x: (x[1]["priority"], x[0])
    )
    
    routes_data = []
    for route_code, route in sorted_routes:
        routes_data.append({
            "route_code": route_code,
            "origin": route["origin"],
            "destination": route["destination"],
            "duration_hours": route["duration_hours"],
            "stoppages": route["stoppages"],
            "num_stops": len(route["stoppages"]),
            "airlines": route["airlines"],
            "base_price": route["base_price"],
            "currency": route["currency"],
            "is_priority": route["priority"] == 1
        })
    
    return jsonify({"routes": routes_data})


@app.route("/api/route/<route_code>", methods=["GET"])
def get_route_details(route_code):
    """Get detailed information about a specific route including pricing"""
    if route_code not in FLIGHT_ROUTES:
        return jsonify({"error": "Route not found"}), 404
    
    route = FLIGHT_ROUTES[route_code]
    
    # Calculate price for different booking windows
    now = datetime.now()
    pricing = {
        "last_minute": calculate_ticket_price(route_code, now + timedelta(days=5)),
        "two_weeks": calculate_ticket_price(route_code, now + timedelta(days=14)),
        "one_month": calculate_ticket_price(route_code, now + timedelta(days=30)),
        "early_bird": calculate_ticket_price(route_code, now + timedelta(days=90))
    }
    
    return jsonify({
        "route_code": route_code,
        "origin": route["origin"],
        "destination": route["destination"],
        "duration_hours": route["duration_hours"],
        "stoppages": route["stoppages"],
        "num_stops": len(route["stoppages"]),
        "airlines": route["airlines"],
        "pricing": pricing,
        "is_priority": route["priority"] == 1
    })


@app.route("/api/search", methods=["GET"])
def search_routes():
    """Search routes with filters for origin, destination, max stops, etc."""
    origin = request.args.get("origin", "").upper()
    destination = request.args.get("destination", "").upper()
    max_stops = request.args.get("max_stops", type=int)
    max_price = request.args.get("max_price", type=float)
    
    results = []
    for route_code, route in FLIGHT_ROUTES.items():
        # Filter by origin
        if origin and origin not in route["origin"].upper():
            continue
        
        # Filter by destination
        if destination and destination not in route["destination"].upper():
            continue
        
        # Filter by max stops
        if max_stops is not None and len(route["stoppages"]) > max_stops:
            continue
        
        # Filter by max price
        if max_price is not None and route["base_price"] > max_price:
            continue
        
        price_info = calculate_ticket_price(route_code)
        if price_info is None:
            continue
        
        results.append({
            "route_code": route_code,
            "origin": route["origin"],
            "destination": route["destination"],
            "duration_hours": route["duration_hours"],
            "stoppages": route["stoppages"],
            "num_stops": len(route["stoppages"]),
            "airlines": route["airlines"],
            "estimated_price": price_info["price"],
            "currency": route["currency"],
            "is_priority": route["priority"] == 1
        })
    
    # Sort by priority first, then by price
    results.sort(key=lambda x: (0 if x["is_priority"] else 1, x["estimated_price"]))
    
    return jsonify({"results": results, "count": len(results)})


@app.route("/api/aviation/ask", methods=["POST"])
def aviation_ask():
    if request.is_json:
        data = request.get_json()
        question = data.get("question", "")
    else:
        question = request.data.decode() or ""
    
    # Include flight routes information in context
    flights = fetch_flights()
    routes_context = "\n\nAvailable Routes (Prioritized - Dhaka<-->Gdansk/Warsaw):\n"
    for route_code, route in sorted(FLIGHT_ROUTES.items(), key=lambda x: x[1]["priority"]):
        routes_context += f"{route_code}: {route['origin']} -> {route['destination']}, "
        routes_context += f"Duration: {route['duration_hours']}h, "
        routes_context += f"Stops: {len(route['stoppages'])}, "
        routes_context += f"Price: ~${route['base_price']}\n"
    
    # You can format/truncate context as needed; here we use all
    context = str(flights)[:1500] + routes_context
    answer = ask_ollama(question, context)
    return jsonify({"answer": answer})


# -------------------- Web UI --------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Flight Tracker AI - Enhanced</title>
<style>
body { 
    font-family: Arial, sans-serif; 
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2em;
}
h1 { 
    color: white;
    text-align: center;
    margin-bottom: 0.5em;
}
.subtitle {
    color: #f0f0f0;
    text-align: center;
    font-size: 1.1em;
    margin-bottom: 2em;
}
.priority-badge {
    background: #ff6b6b;
    color: white;
    padding: 0.3em 0.8em;
    border-radius: 15px;
    font-size: 0.8em;
    font-weight: bold;
}
.section {
    background: white;
    border-radius: 10px;
    padding: 1.5em;
    margin-bottom: 1.5em;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.ai-section {
    background: #f8f9fa;
}
input, button { 
    font-size: 1.1em; 
    padding: 0.6em;
    border-radius: 5px;
    border: 1px solid #ddd;
}
button {
    background: #667eea;
    color: white;
    border: none;
    cursor: pointer;
    transition: background 0.3s;
}
button:hover {
    background: #5568d3;
}
pre { 
    background: #f4f4f4; 
    padding: 1em; 
    border-radius: 5px;
    overflow-x: auto;
}
.route-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1em;
    margin-bottom: 1em;
    background: #fafafa;
    transition: transform 0.2s, box-shadow 0.2s;
}
.route-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
.route-card.priority {
    border-left: 4px solid #ff6b6b;
    background: #fff5f5;
}
.route-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8em;
}
.route-path {
    font-size: 1.2em;
    font-weight: bold;
    color: #333;
}
.route-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.8em;
}
.detail-item {
    display: flex;
    flex-direction: column;
}
.detail-label {
    font-size: 0.85em;
    color: #666;
    margin-bottom: 0.2em;
}
.detail-value {
    font-weight: bold;
    color: #333;
}
.price-highlight {
    color: #27ae60;
    font-size: 1.3em;
}
.stops-info {
    color: #666;
    font-size: 0.9em;
    margin-top: 0.5em;
}
.search-form {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1em;
    margin-bottom: 1em;
}
#loading {
    display: none;
    text-align: center;
    padding: 1em;
    color: #667eea;
}
</style>
</head>
<body>
<div class="container">
    <h1>✈️ Flight Tracker AI Assistant</h1>
    <p class="subtitle">Enhanced with Route Search, Pricing & Priority Routes (Dhaka ↔ Gdansk/Warsaw)</p>
    
    <div class="section">
        <h2>🔍 Search Flight Routes</h2>
        <div class="search-form">
            <div>
                <label>Origin:</label>
                <input id="searchOrigin" type="text" placeholder="e.g., Dhaka, DAC"/>
            </div>
            <div>
                <label>Destination:</label>
                <input id="searchDest" type="text" placeholder="e.g., Warsaw, WAW"/>
            </div>
            <div>
                <label>Max Stops:</label>
                <input id="maxStops" type="number" placeholder="Any" min="0"/>
            </div>
            <div>
                <label>Max Price (USD):</label>
                <input id="maxPrice" type="number" placeholder="Any" min="0"/>
            </div>
        </div>
        <button onclick="searchRoutes()">Search Routes</button>
        <button onclick="loadAllRoutes()" style="background: #48bb78;">Show All Routes</button>
        <div id="loading">⏳ Loading...</div>
        <div id="routes"></div>
    </div>
    
    <div class="section ai-section">
        <h2>🤖 AI Assistant</h2>
        <input id="question" type="text" placeholder="Ask about flights..." size="50"/>
        <button onclick="ask()">Ask AI</button>
        <pre id="answer"></pre>
    </div>
</div>

<script>
function searchRoutes() {
    const origin = document.getElementById('searchOrigin').value;
    const dest = document.getElementById('searchDest').value;
    const maxStops = document.getElementById('maxStops').value;
    const maxPrice = document.getElementById('maxPrice').value;
    
    let url = "/api/search?";
    if (origin) url += `origin=${encodeURIComponent(origin)}&`;
    if (dest) url += `destination=${encodeURIComponent(dest)}&`;
    if (maxStops) url += `max_stops=${maxStops}&`;
    if (maxPrice) url += `max_price=${maxPrice}&`;
    
    document.getElementById('loading').style.display = 'block';
    
    fetch(url)
        .then(r => r.json())
        .then(data => {
            document.getElementById('loading').style.display = 'none';
            displayRoutes(data.results);
        });
}

function loadAllRoutes() {
    document.getElementById('loading').style.display = 'block';
    fetch("/api/routes")
        .then(r => r.json())
        .then(data => {
            document.getElementById('loading').style.display = 'none';
            displayRoutes(data.routes);
        });
}

function displayRoutes(routes) {
    const container = document.getElementById('routes');
    if (routes.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#666; margin-top:1em;">No routes found matching your criteria.</p>';
        return;
    }
    
    container.innerHTML = routes.map(route => `
        <div class="route-card ${route.is_priority ? 'priority' : ''}">
            <div class="route-header">
                <div class="route-path">${route.origin} → ${route.destination}</div>
                ${route.is_priority ? '<span class="priority-badge">PRIORITY ROUTE</span>' : ''}
            </div>
            <div class="route-details">
                <div class="detail-item">
                    <span class="detail-label">Duration</span>
                    <span class="detail-value">${route.duration_hours} hours</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Stops</span>
                    <span class="detail-value">${route.num_stops} stop${route.num_stops !== 1 ? 's' : ''}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Base Price</span>
                    <span class="detail-value price-highlight">$${route.base_price || route.estimated_price}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Airlines</span>
                    <span class="detail-value">${route.airlines.join(', ')}</span>
                </div>
            </div>
            ${route.stoppages && route.stoppages.length > 0 ? 
                `<div class="stops-info">Via: ${route.stoppages.join(', ')}</div>` : 
                '<div class="stops-info">Direct Flight</div>'}
        </div>
    `).join('');
}

function ask() {
    fetch("/api/aviation/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: document.getElementById('question').value})
    })
    .then(r => r.json()).then(data => {
        document.getElementById('answer').innerText = data.answer
    });
}

// Load all routes on page load
window.onload = function() {
    loadAllRoutes();
};
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

# -------------------- (Optional) Rate Limiting --------------------
# from flask_limiter import Limiter
# limiter = Limiter(app, key_func=lambda: request.remote_addr)
# @app.route("/api/aviation/ask", methods=["POST"])
# @limiter.limit("5 per minute")
# def aviation_ask():
#     ...

# -------------------- Main Entry --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
