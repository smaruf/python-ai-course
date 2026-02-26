#!/usr/bin/env python3
"""
GitHub Copilot Client
=====================

Handles communication with the GitHub Copilot chat completions API.
Used as the **primary** AI backend (highest priority tier).

Authentication:
  The client looks for a token in this order:
    1. ``GITHUB_COPILOT_TOKEN`` environment variable  (recommended)
    2. VS Code Copilot extension config  (~/.config/github-copilot/hosts.json)

  To obtain a token for use outside VS Code, authenticate via the GitHub CLI:
    gh auth login --scopes copilot
    gh auth token

Setup in VS Code / GitHub Copilot IDE:
  Install the GitHub Copilot extension; the token is stored automatically.
  Set GITHUB_COPILOT_TOKEN to the stored OAuth token for use by this gateway.
"""

import json
import os
import requests
from typing import Optional

_COPILOT_API_URL = "https://api.githubcopilot.com/chat/completions"

# Paths where VS Code / GitHub CLI store the Copilot OAuth token
_TOKEN_CONFIG_PATHS = [
    os.path.expanduser("~/.config/github-copilot/hosts.json"),                           # Linux
    os.path.expanduser("~/Library/Application Support/github-copilot/hosts.json"),        # macOS
    os.path.expanduser("~/AppData/Roaming/GitHub Copilot/hosts.json"),                   # Windows
]


class CopilotClient:
    """Client for the GitHub Copilot chat API (primary AI backend)."""

    # IDE version headers required by the Copilot API.
    # Override GITHUB_COPILOT_EDITOR_VERSION / GITHUB_COPILOT_PLUGIN_VERSION
    # env vars to update these without changing code.
    _DEFAULT_EDITOR_VERSION = "vscode/1.85.0"
    _DEFAULT_PLUGIN_VERSION = "copilot-chat/0.12.0"

    def __init__(
        self,
        model: str = "gpt-4o",
        timeout: int = 15,
    ):
        self.model = model
        self.timeout = timeout
        self._editor_version = os.getenv("GITHUB_COPILOT_EDITOR_VERSION", self._DEFAULT_EDITOR_VERSION)
        self._plugin_version = os.getenv("GITHUB_COPILOT_PLUGIN_VERSION", self._DEFAULT_PLUGIN_VERSION)

    def _get_token(self) -> str:
        """
        Resolve the Copilot OAuth token.

        Checks (in order):
          1. ``GITHUB_COPILOT_TOKEN`` env var
          2. VS Code Copilot extension hosts.json config file

        Raises:
            ValueError: When no token can be found.
        """
        token = os.getenv("GITHUB_COPILOT_TOKEN")
        if token:
            return token

        for path in _TOKEN_CONFIG_PATHS:
            if os.path.exists(path):
                with open(path) as fh:
                    hosts = json.load(fh)
                token = hosts.get("github.com", {}).get("oauth_token")
                if token:
                    return token

        raise ValueError(
            "GitHub Copilot token not found. "
            "Set the GITHUB_COPILOT_TOKEN environment variable, or authenticate "
            "with: gh auth login --scopes copilot"
        )

    def query(self, prompt: str) -> str:
        """
        Send a prompt to the GitHub Copilot chat API.

        Args:
            prompt: The user prompt to send.

        Returns:
            The model's text response.

        Raises:
            requests.exceptions.RequestException: On network or HTTP errors.
            ValueError: When the Copilot token cannot be resolved.
        """
        token = self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Editor-Version": self._editor_version,
            "Editor-Plugin-Version": self._plugin_version,
            "Copilot-Integration-Id": "vscode-chat",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        response = requests.post(
            _COPILOT_API_URL,
            headers=headers,
            json=data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def health_check(self) -> bool:
        """
        Check whether the GitHub Copilot API endpoint is reachable.

        Returns:
            True if a quick connectivity probe succeeds, False otherwise.
        """
        try:
            requests.get("https://api.githubcopilot.com", timeout=3)
            return True
        except Exception:
            return False
