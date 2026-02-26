#!/usr/bin/env python3
"""
AI Gateway — Python client example
====================================

Shows how to call the AI Gateway REST API from Python using only
the standard library (no extra packages required).

Usage:
    python client.py
"""

import json
import urllib.request

GATEWAY_URL = "http://localhost:8000"


def query(prompt: str) -> dict:
    """Send a plain prompt to the gateway and return the parsed response."""
    payload = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(
        f"{GATEWAY_URL}/ai/query",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def query_rag(prompt: str, documents: list[str]) -> dict:
    """Send a RAG-augmented prompt (question + context docs) to the gateway."""
    payload = json.dumps({"prompt": prompt, "documents": documents}).encode()
    req = urllib.request.Request(
        f"{GATEWAY_URL}/ai/query/rag",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def health() -> dict:
    """Fetch the gateway health / circuit-breaker status."""
    with urllib.request.urlopen(f"{GATEWAY_URL}/health") as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    # --- plain query ---
    result = query("Explain a circuit breaker pattern in two sentences.")
    print(f"[{result['backend']}] {result['response']}\n")

    # --- RAG query ---
    docs = [
        "A circuit breaker monitors calls to a remote service.",
        "When failures exceed a threshold the circuit 'opens' and further calls are blocked.",
        "After a timeout the circuit moves to 'half-open' and allows a trial call.",
    ]
    rag_result = query_rag("When does a circuit breaker open?", docs)
    print(f"[{rag_result['backend']}] {rag_result['response']}\n")

    # --- health ---
    h = health()
    print(f"Gateway health: {h['status']} | circuit: {h['circuit_state']}")
