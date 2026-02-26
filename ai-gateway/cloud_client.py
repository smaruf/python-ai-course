#!/usr/bin/env python3
"""
Cloud LLM Client
================

Handles communication with cloud-based AI providers (OpenAI, Anthropic, etc.).
Used as the **secondary** AI backend when GitHub Copilot (primary) is unavailable.
"""

import os
import requests
from typing import Optional


class CloudClient:
    """Client for cloud-based LLM APIs (secondary AI backend)."""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
        timeout: int = 15,
    ):
        self.provider = provider
        self.model = model
        self.timeout = timeout

    def _openai_query(self, prompt: str) -> str:
        """Call the OpenAI Chat Completions API."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.7,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def query(self, prompt: str) -> str:
        """
        Send a prompt to the cloud LLM and return the response.

        Args:
            prompt: The user prompt to send.

        Returns:
            The model's text response.

        Raises:
            requests.exceptions.RequestException: On network or HTTP errors.
            ValueError: When required configuration is missing.
        """
        if self.provider == "openai":
            return self._openai_query(prompt)
        raise ValueError(f"Unsupported cloud provider: {self.provider}")

    def health_check(self) -> bool:
        """
        Check whether the cloud API endpoint is reachable.

        Returns:
            True if a quick connectivity probe succeeds, False otherwise.
        """
        try:
            requests.get(
                "https://api.openai.com",
                timeout=3,
            )
            return True
        except Exception:
            return False
