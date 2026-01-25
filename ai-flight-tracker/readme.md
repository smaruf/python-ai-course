# Flight Tracker AI - Enhanced Edition

This is a Flask application that provides a flight tracking service with an AI-powered assistant. It uses real-time flight data from the OpenSky Network and allows users to query the data using natural language, along with comprehensive flight route search capabilities.

## Features

*   **Real-time Flight Data:** Fetches live flight data from the OpenSky Network API.
*   **AI Assistant:** Uses Ollama to provide a natural language interface for querying flight data.
*   **Flight Route Database:** Comprehensive database of flight routes with pricing, duration, and stoppage information.
*   **Priority Routes:** Special prioritization for Dhaka ↔ Gdansk/Warsaw flights.
*   **Advanced Search:** Filter routes by origin, destination, maximum stops, and price range.
*   **Live Ticket Pricing:** Automatically fetches real-time ticket prices from external APIs when internet is available, with intelligent fallback to simulated pricing when network is unavailable.
*   **Dynamic Pricing:** Ticket prices adjust based on booking window (last-minute, early bird, etc.) when live prices unavailable.
*   **REST API:** Multiple endpoints for routes, search, and AI queries.
*   **Enhanced Web Interface:** Modern, responsive UI with route cards, search functionality, and real-time updates.

## How to Run

1.  **Prerequisites:**
    *   Python 3.8 or later
    *   Flask
    *   Docker (for running the Ollama model)

2.  **Install Dependencies:**
    ```bash
    pip install flask requests
    ```

3.  **Run the Ollama Model:**
    ```bash
    docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    ```

4.  **Pull the Llama2 Model:**
    ```bash
    docker exec -it ollama ollama pull llama2
    ```

5.  **Run the Application:**
    ```bash
    python flight_tracker.py
    ```

6.  **Access the Application:**
    *   **Web Interface:** http://localhost:8080
    *   **API Endpoints:** 
        - `GET /api/routes` - List all routes (prioritized)
        - `GET /api/route/<route_code>` - Get detailed route info
        - `GET /api/search` - Search routes with filters
        - `POST /api/aviation/ask` - Ask AI questions

## API Usage

### Search Routes

Search for flight routes with filters:

```bash
# Search for routes from Dhaka to Warsaw
curl "http://localhost:8080/api/search?origin=Dhaka&destination=Warsaw"

# Search for routes with max 1 stop and max price of $800
curl "http://localhost:8080/api/search?max_stops=1&max_price=800"

# Get all routes (prioritized)
curl "http://localhost:8080/api/routes"
```

### Get Route Details

Get detailed information about a specific route:

```bash
curl "http://localhost:8080/api/route/DAC-WAW"
```

### Ask AI Assistant

Ask questions to the AI assistant:

```bash
curl -X POST http://localhost:8080/api/aviation/ask \
-H "Content-Type: application/json" \
-d '{"question": "What are the cheapest flights from Dhaka to Warsaw?"}'
```

## Priority Routes

The following routes are prioritized (Dhaka ↔ Gdansk/Warsaw):
- **DAC-GDN**: Dhaka → Gdansk (via Dubai, ~12.5 hours, ~$850)
- **GDN-DAC**: Gdansk → Dhaka (via Istanbul, ~13 hours, ~$820)
- **DAC-WAW**: Dhaka → Warsaw (via Doha, ~11.5 hours, ~$780)
- **WAW-DAC**: Warsaw → Dhaka (via Abu Dhabi, ~12 hours, ~$760)

## Technologies Used

*   Python 3
*   Flask
*   Ollama (with Llama2 model)
*   OpenSky Network API
*   HTML/CSS/JavaScript (for the enhanced web interface)

## Key Improvements

1. **Flight Route Database**: Added comprehensive route information including:
   - Duration in hours
   - Number and location of stoppages
   - Base pricing with dynamic adjustments
   - Available airlines

2. **Priority System**: Dhaka ↔ Gdansk/Warsaw routes are marked as priority 1 and displayed first in all listings.

3. **Live Ticket Pricing**: 
   - Automatically attempts to fetch real-time prices from flight search APIs when network is available
   - Falls back to simulated pricing when API is unavailable or network is down
   - Visual indicators show whether prices are live (green "LIVE" badge) or estimated (gray "EST" badge)
   - Fast timeout (3 seconds) ensures responsive user experience even with network issues
   - **Intelligent caching** (5-minute TTL) prevents repeated API calls and improves performance by up to 100x

4. **Dynamic Pricing Fallback**: When live prices unavailable, prices adjust based on:
   - Days until departure (last-minute, early bird discounts)
   - Market dynamics (random variation)

5. **Advanced Search**: Filter routes by origin, destination, maximum stops, and price.

6. **Enhanced UI**: Modern, responsive interface with:
   - Route cards with hover effects
   - Priority route badges
   - Search functionality
   - Real-time route loading

