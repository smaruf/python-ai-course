#!/usr/bin/env python3
"""
Local LLM Client
================

Handles communication with a locally-running Ollama instance.
Used as the fallback AI backend when cloud connectivity is unavailable.

Setup:
    curl -fsSL https://ollama.com/install.sh | sh
    ollama run llama3          # or mistral, phi3, qwen, etc.
"""

import requests
from typing import Optional


class LocalClient:
    """Client for a locally-running Ollama LLM (fallback AI backend)."""

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 60,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def query(self, prompt: str) -> str:
        """
        Send a prompt to the local Ollama instance and return the response.

        Args:
            prompt: The user prompt to send.

        Returns:
            The model's text response.

        Raises:
            requests.exceptions.RequestException: On network or HTTP errors.
        """
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["response"]

    def health_check(self) -> bool:
        """
        Check whether the local Ollama service is reachable.

        Returns:
            True if Ollama is running and responsive, False otherwise.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=3,
            )
            return response.status_code == 200
        except Exception:
            return False
