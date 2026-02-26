// AI Gateway — Go client example
// =================================
//
// Shows how to call the AI Gateway REST API from Go.
// Uses only the standard library — no external packages needed.
//
// Requires Go 1.18+.
//
// Run:
//   go run client.go

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

const gatewayURL = "http://localhost:8000"

// GatewayResponse maps the JSON returned by /ai/query and /ai/query/rag.
type GatewayResponse struct {
	Response string `json:"response"`
	Backend  string `json:"backend"`
	State    string `json:"state"`
}

// HealthResponse maps the JSON returned by /health.
type HealthResponse struct {
	Status           string `json:"status"`
	CopilotAvailable bool   `json:"copilot_available"`
	CloudAvailable   bool   `json:"cloud_available"`
	LocalAvailable   bool   `json:"local_available"`
	CircuitState     string `json:"circuit_state"`
}

// Query sends a plain prompt to the gateway.
func Query(prompt string) (*GatewayResponse, error) {
	body := map[string]string{"prompt": prompt}
	return postJSON[GatewayResponse]("/ai/query", body)
}

// QueryRAG sends a RAG-augmented prompt to the gateway.
func QueryRAG(prompt string, documents []string) (*GatewayResponse, error) {
	body := map[string]any{
		"prompt":    prompt,
		"documents": documents,
	}
	return postJSON[GatewayResponse]("/ai/query/rag", body)
}

// Health fetches the gateway health / circuit-breaker status.
func Health() (*HealthResponse, error) {
	resp, err := http.Get(gatewayURL + "/health")
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	var h HealthResponse
	return &h, json.Unmarshal(raw, &h)
}

// ---------------------------------------------------------------------------

func postJSON[T any](path string, payload any) (*T, error) {
	data, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}
	resp, err := http.Post(gatewayURL+path, "application/json", bytes.NewReader(data))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	var result T
	return &result, json.Unmarshal(raw, &result)
}

func main() {
	// --- plain query ---
	result, err := Query("Explain a circuit breaker pattern in two sentences.")
	if err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Printf("[%s] %s\n\n", result.Backend, result.Response)
	}

	// --- RAG query ---
	docs := []string{
		"A circuit breaker monitors calls to a remote service.",
		"When failures exceed a threshold the circuit 'opens' and further calls are blocked.",
		"After a timeout the circuit moves to 'half-open' and allows a trial call.",
	}
	ragResult, err := QueryRAG("When does a circuit breaker open?", docs)
	if err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Printf("[%s] %s\n\n", ragResult.Backend, ragResult.Response)
	}

	// --- health ---
	h, err := Health()
	if err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Printf("Gateway: %s | circuit: %s\n", h.Status, h.CircuitState)
	}
}
