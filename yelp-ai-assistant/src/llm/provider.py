"""
LLM Provider Abstraction
========================

Supports four backends, selectable at runtime:

  * **mock**   — deterministic keyword-based answers; no auth required.
  * **guest**  — same deterministic logic as mock but prepends an upgrade prompt.
  * **llama**  — local Llama model via a running Ollama server
                 (``OLLAMA_HOST``, default ``http://localhost:11434``).
                 Enriches the prompt with web-scraped context when a
                 ``WebScraper`` is attached.
  * **openai** — OpenAI Chat Completions (``OPENAI_API_KEY``).
  * **copilot**— GitHub Copilot (``GITHUB_TOKEN``), routed through the
                 OpenAI-compatible ``https://api.githubcopilot.com`` endpoint.

If the required credentials are absent the factory falls back to **guest** mode
and returns a clear message asking the user to authenticate.

Usage::

    from src.llm.provider import create_backend, LLMProvider

    backend = create_backend(LLMProvider.LLAMA)          # local Ollama
    backend = create_backend(LLMProvider.OPENAI, api_key="sk-...")
    backend = create_backend(LLMProvider.COPILOT, api_key="ghp_...")

    answer = await backend.generate(context, query)
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Optional


class LLMProvider(str, Enum):
    MOCK = "mock"
    GUEST = "guest"
    LLAMA = "llama"
    OPENAI = "openai"
    COPILOT = "copilot"


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class LLMBackend:
    """Abstract base for all LLM backends."""

    provider: LLMProvider = LLMProvider.MOCK

    async def generate(self, context: str, query: str) -> str:  # pragma: no cover
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Mock / Guest
# ---------------------------------------------------------------------------

_GUEST_HEADER = (
    "\n\n---\n"
    "💡 *You are using guest mode. "
    "Authenticate with OpenAI, GitHub Copilot, or a local Llama model "
    "for richer, real-time answers.*\n---\n"
)


class MockBackend(LLMBackend):
    """Deterministic mock — no network, no credentials required."""

    provider = LLMProvider.MOCK

    async def generate(self, context: str, query: str) -> str:
        return f"[Mock] Based on available data: {query.strip('?')}."


class GuestBackend(LLMBackend):
    """Same as MockBackend but appends an authentication upgrade notice."""

    provider = LLMProvider.GUEST

    async def generate(self, context: str, query: str) -> str:
        base = f"[Guest] Based on available data: {query.strip('?')}."
        return base + _GUEST_HEADER


# ---------------------------------------------------------------------------
# Llama (via Ollama)
# ---------------------------------------------------------------------------

_LLAMA_SYSTEM_PROMPT = (
    "You are a helpful business information assistant. "
    "Answer ONLY using the context provided. "
    "Never fabricate information. "
    "If the context does not contain the answer, say so clearly."
)


class LlamaBackend(LLMBackend):
    """
    Calls a locally running Ollama server.

    The model is configurable via ``OLLAMA_MODEL`` (default ``llama3``).
    The host is configurable via ``OLLAMA_HOST``
    (default ``http://localhost:11434``).

    Optionally enriches the context with web-scraped snippets when
    ``web_snippets`` are passed to ``generate``.
    """

    provider = LLMProvider.LLAMA

    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
    ) -> None:
        self._model = model or os.environ.get("OLLAMA_MODEL", "llama3")
        self._host = host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    async def generate(
        self,
        context: str,
        query: str,
        web_snippets: str | None = None,
    ) -> str:
        enriched = context
        if web_snippets:
            enriched = f"{context}\n\nWeb-scraped context:\n{web_snippets}"

        prompt = (
            f"Context:\n{enriched}\n\n"
            f"Question: {query}\n\n"
            "Answer (use context only, never fabricate):"
        )
        try:
            import ollama  # type: ignore

            client = ollama.AsyncClient(host=self._host)
            response = await client.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": _LLAMA_SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
            )
            return response["message"]["content"].strip()
        except Exception as exc:  # noqa: BLE001
            return (
                f"[Llama/{self._model}] Offline or unavailable "
                f"({exc}). Falling back to structured data."
            )


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------

_OPENAI_SYSTEM_PROMPT = (
    "You are a helpful business information assistant. "
    "Answer questions using ONLY the provided context. "
    "Never fabricate information."
)


class OpenAIBackend(LLMBackend):
    """
    Calls the OpenAI Chat Completions API.

    Requires ``api_key`` or the ``OPENAI_API_KEY`` environment variable.
    """

    provider = LLMProvider.OPENAI

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._model = model

    async def generate(self, context: str, query: str) -> str:
        if not self._api_key:
            return (
                "[OpenAI] No API key provided. "
                "Set OPENAI_API_KEY or pass --api-key to authenticate."
            )
        try:
            import openai  # type: ignore

            client = openai.AsyncOpenAI(api_key=self._api_key)
            rsp = await client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _OPENAI_SYSTEM_PROMPT},
                    {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {query}"},
                ],
                temperature=0.2,
                max_tokens=512,
            )
            return rsp.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001
            return f"[OpenAI] Error: {exc}. Falling back to structured data."


# ---------------------------------------------------------------------------
# GitHub Copilot
# ---------------------------------------------------------------------------

_COPILOT_BASE_URL = "https://api.githubcopilot.com"
_COPILOT_MODEL = "gpt-4o"


class CopilotBackend(LLMBackend):
    """
    Calls the GitHub Copilot chat API (OpenAI-compatible endpoint).

    Requires ``api_key`` (a GitHub personal-access token with ``copilot`` scope)
    or the ``GITHUB_TOKEN`` environment variable.
    """

    provider = LLMProvider.COPILOT

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("GITHUB_TOKEN", "")

    async def generate(self, context: str, query: str) -> str:
        if not self._api_key:
            return (
                "[GitHub Copilot] No token provided. "
                "Set GITHUB_TOKEN or pass --api-key to authenticate."
            )
        try:
            import openai  # type: ignore

            client = openai.AsyncOpenAI(
                api_key=self._api_key,
                base_url=_COPILOT_BASE_URL,
            )
            rsp = await client.chat.completions.create(
                model=_COPILOT_MODEL,
                messages=[
                    {"role": "system", "content": _OPENAI_SYSTEM_PROMPT},
                    {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {query}"},
                ],
                temperature=0.2,
                max_tokens=512,
            )
            return rsp.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001
            return f"[Copilot] Error: {exc}. Falling back to structured data."


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_backend(
    provider: LLMProvider | str,
    api_key: str | None = None,
    llama_model: str | None = None,
    llama_host: str | None = None,
) -> LLMBackend:
    """
    Return the appropriate ``LLMBackend`` for *provider*.

    If required credentials are missing the factory degrades gracefully:
    - openai/copilot with no key → GuestBackend (with upgrade notice)
    - llama → LlamaBackend (failure is handled inside the backend itself)

    Parameters
    ----------
    provider:
        One of ``LLMProvider`` enum values or the string equivalents
        ("mock", "guest", "llama", "openai", "copilot").
    api_key:
        API key / token for OpenAI or GitHub Copilot.  Falls back to
        ``OPENAI_API_KEY`` / ``GITHUB_TOKEN`` environment variables.
    llama_model:
        Ollama model name (default ``llama3``).
    llama_host:
        Ollama server URL (default ``http://localhost:11434``).
    """
    p = LLMProvider(provider) if isinstance(provider, str) else provider

    if p == LLMProvider.MOCK:
        return MockBackend()

    if p == LLMProvider.GUEST:
        return GuestBackend()

    if p == LLMProvider.LLAMA:
        return LlamaBackend(model=llama_model, host=llama_host)

    if p == LLMProvider.OPENAI:
        key = api_key or os.environ.get("OPENAI_API_KEY", "")
        if not key:
            return GuestBackend()
        return OpenAIBackend(api_key=key)

    if p == LLMProvider.COPILOT:
        key = api_key or os.environ.get("GITHUB_TOKEN", "")
        if not key:
            return GuestBackend()
        return CopilotBackend(api_key=key)

    return MockBackend()
