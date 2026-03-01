# Flight Tracker AI

> **Part of [Python AI Course](../README.md)** — A comprehensive learning repository covering AI, algorithms, and real-world applications.

A production-ready Flask application providing live flight tracking, an interactive Leaflet map, route search, dynamic pricing, and an AI assistant grounded in tool results.

## Features

- **Interactive Flight Map** — Leaflet map with bbox-based flight fetching, plane markers, and clustering.
- **Live Flight Data** — Real-time data from the [OpenSky Network](https://opensky-network.org/).
- **Route Search** — Filter by origin, destination, max stops, and max price.
- **Priority Routes** — Dhaka ↔ Gdansk/Warsaw highlighted throughout.
- **Dynamic Pricing** — Simulated pricing with booking-window adjustments; optional live API integration.
- **AI Assistant** — Intent-routing assistant backed by tool results (route search, live flights). No raw data truncation.
- **Session Memory** — Remembers user preferences (e.g. last-mentioned city) within a session.
- **Production-ready** — CORS, rate limiting, structured logging, request IDs, `/health` endpoint, Gunicorn in Docker.

## Project Structure

```
ai-flight-tracker/
├── app.py                # Flask app factory
├── config.py             # Env-based configuration
├── routes.json           # Flight routes data
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── services/
│   ├── opensky.py        # OpenSky API client
│   ├── pricing.py        # Pricing with TTL cache
│   ├── routes_repo.py    # Route data access
│   └── ai.py             # Intent-routing AI assistant
├── static/
│   ├── index.html        # UI (Leaflet map + route search + AI)
│   ├── app.js
│   └── style.css
└── tests/
    ├── test_routes.py
    ├── test_flights.py
    └── test_ai.py
```

## Running Locally

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/) (optional, for AI answers)

### Quick Start

```bash
cd ai-flight-tracker

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment variables (optional)
cp .env.example .env

# Run the app
python app.py
```

Open **http://localhost:8080**.

### Pull AI model (optional)

```bash
# Using Docker
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull llama2
```

## Running with Docker

```bash
cd ai-flight-tracker

# Start app + Ollama
docker-compose up --build
```

Open **http://localhost:8080**. Ollama runs at `http://ollama:11434` inside the compose network.

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8080` | Server port |
| `DEBUG` | `false` | Flask debug mode |
| `SECRET_KEY` | `change-me-in-production` | Session secret key |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `OPENSKY_URL` | `https://opensky-network.org/api` | OpenSky base URL |
| `OPENSKY_USERNAME` | _(empty)_ | Optional OpenSky credentials |
| `OPENSKY_PASSWORD` | _(empty)_ | Optional OpenSky credentials |
| `OPENSKY_TIMEOUT` | `10` | Timeout (seconds) for OpenSky requests |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama endpoint |
| `OLLAMA_MODEL` | `llama2` | Ollama model name |
| `OLLAMA_TIMEOUT` | `30` | Timeout (seconds) for Ollama requests |
| `CACHE_TTL` | `300` | Pricing cache TTL in seconds |
| `RATE_LIMIT_ASK` | `10 per minute` | Rate limit for `/api/aviation/ask` |
| `RATE_LIMIT_FLIGHTS` | `30 per minute` | Rate limit for `/api/flights` |
| `LIVE_PRICING_ENABLED` | `false` | Enable live ticket pricing API |
| `PRICING_API_KEY` | _(empty)_ | API key for live pricing provider |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/routes` | All routes (priority-sorted) |
| `GET` | `/api/route/<code>` | Route details + pricing windows |
| `GET` | `/api/search` | Search routes (`origin`, `destination`, `max_stops`, `max_price`) |
| `GET` | `/api/flights` | Live flights (optional bbox: `lamin`, `lamax`, `lomin`, `lomax`) |
| `GET` | `/api/flights/<icao24>` | Single flight details by ICAO24 |
| `POST` | `/api/aviation/ask` | AI assistant (`{"question": "..."}`) |

### Examples

```bash
# Health check
curl http://localhost:8080/health

# All routes
curl http://localhost:8080/api/routes

# Search from Dhaka, max 1 stop
curl "http://localhost:8080/api/search?origin=Dhaka&max_stops=1"

# Flights over Europe (bbox)
curl "http://localhost:8080/api/flights?lamin=35&lamax=70&lomin=-10&lomax=40"

# Single flight by ICAO24
curl http://localhost:8080/api/flights/3c6444

# Ask the AI
curl -X POST http://localhost:8080/api/aviation/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the cheapest flights from Dhaka to Warsaw?"}'
```

## AI Tool Routing

The AI assistant uses intent routing (no raw data truncation):

1. **Intent detection** — question keywords map to one of: `list_routes`, `search_routes`, `lookup_flight`, `flights_in_bbox`.
2. **Tool execution** — the matched tool fetches structured data (routes DB or OpenSky API).
3. **Context building** — compact, readable text is composed from tool results.
4. **Answer generation** — Ollama receives the context + question and generates a grounded answer.

If Ollama is unavailable, the tool result context is returned directly.

## Priority Routes

| Code | Route | Via | Duration | ~Price |
|---|---|---|---|---|
| DAC-GDN | Dhaka → Gdansk | Dubai | 12.5h | $850 |
| GDN-DAC | Gdansk → Dhaka | Istanbul | 13h | $820 |
| DAC-WAW | Dhaka → Warsaw | Doha | 11.5h | $780 |
| WAW-DAC | Warsaw → Dhaka | Abu Dhabi | 12h | $760 |

## Running Tests

```bash
cd ai-flight-tracker
pytest tests/ -v
```

## Technologies

- Python 3.11, Flask, Flask-CORS, Flask-Limiter
- Leaflet.js + MarkerCluster (frontend map)
- OpenSky Network API (live flights)
- Ollama / llama2 (AI assistant)
- Gunicorn (production server)
- Docker / docker-compose
- pytest (tests)
- GitHub Actions (CI)

