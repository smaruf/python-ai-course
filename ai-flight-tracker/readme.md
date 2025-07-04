# Flight Tracker AI

This is a Spring Boot application that provides a flight tracking service with an AI-powered assistant. It uses real-time flight data from the OpenSky Network and allows users to query the data using natural language.

## Features

*   **Real-time Flight Data:** Fetches live flight data from the OpenSky Network API.
*   **AI Assistant:** Uses Langchain4j and Ollama to provide a natural language interface for querying flight data.
*   **REST API:** Exposes a simple REST API for asking questions about flights.
*   **Web Interface:** Includes a basic web interface for interacting with the AI assistant.

## How to Run

1.  **Prerequisites:**
    *   Java 21 or later
    *   Docker (for running the Ollama model)

2.  **Run the Ollama Model:**
    ```bash
    docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    ```

3.  **Pull the Llama3.1 Model:**
    ```bash
    docker exec -it ollama ollama pull llama3.1:8b
    ```

4.  **Run the Application:**
    ```bash
    ./gradlew bootRun
    ```

5.  **Access the Application:**
    *   **Web Interface:** http://localhost:8080
    *   **API Endpoint:** `POST /api/aviation/ask`

## API Usage

You can ask questions to the AI assistant by sending a POST request to the `/api/aviation/ask` endpoint with the question in the request body.

**Example:**

```bash
curl -X POST http://localhost:8080/api/aviation/ask \
-H "Content-Type: text/plain" \
-d "What aircraft are currently flying near Toronto International Airport within 15 nautical miles"
```

## Technologies Used

*   Spring Boot 3
*   Java 21
*   Langchain4j
*   Ollama
*   Bucket4j (for rate limiting)
*   HTML/CSS/JavaScript (for the web interface)

