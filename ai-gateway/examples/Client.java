// AI Gateway — Java client example
// ===================================
//
// Shows how to call the AI Gateway REST API from Java.
// Uses only the standard library (java.net.http) — no Maven dependencies needed.
//
// Requires Java 11+ for HttpClient.
//
// Compile & run:
//   javac Client.java
//   java Client

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class Client {

    private static final String GATEWAY_URL = "http://localhost:8000";
    private static final HttpClient HTTP = HttpClient.newHttpClient();

    /** Send a plain prompt to the gateway. */
    public static String query(String prompt) throws IOException, InterruptedException {
        String body = "{\"prompt\": " + jsonString(prompt) + "}";
        return post("/ai/query", body);
    }

    /** Send a RAG-augmented prompt to the gateway. */
    public static String queryRag(String prompt, String[] documents)
            throws IOException, InterruptedException {
        StringBuilder docs = new StringBuilder("[");
        for (int i = 0; i < documents.length; i++) {
            if (i > 0) docs.append(",");
            docs.append(jsonString(documents[i]));
        }
        docs.append("]");
        String body = "{\"prompt\": " + jsonString(prompt) + ", \"documents\": " + docs + "}";
        return post("/ai/query/rag", body);
    }

    /** Fetch the gateway health status. */
    public static String health() throws IOException, InterruptedException {
        HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create(GATEWAY_URL + "/health"))
                .GET()
                .build();
        return HTTP.send(req, HttpResponse.BodyHandlers.ofString()).body();
    }

    // -----------------------------------------------------------------------

    private static String post(String path, String jsonBody)
            throws IOException, InterruptedException {
        HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create(GATEWAY_URL + path))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();
        return HTTP.send(req, HttpResponse.BodyHandlers.ofString()).body();
    }

    /** Minimal JSON string escaping (sufficient for plain ASCII prompts). */
    private static String jsonString(String s) {
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"")
                        .replace("\n", "\\n").replace("\r", "\\r") + "\"";
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        // --- plain query ---
        String result = query("Explain a circuit breaker pattern in two sentences.");
        System.out.println("Query response: " + result);

        // --- RAG query ---
        String[] docs = {
            "A circuit breaker monitors calls to a remote service.",
            "When failures exceed a threshold the circuit 'opens' and further calls are blocked.",
            "After a timeout the circuit moves to 'half-open' and allows a trial call.",
        };
        String ragResult = queryRag("When does a circuit breaker open?", docs);
        System.out.println("RAG response: " + ragResult);

        // --- health ---
        System.out.println("Health: " + health());
    }
}
