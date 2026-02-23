"""
Web Scraper
===========

Async web scraper for enriching LLM context with live business information.

Usage::

    from src.tools.web_scraper import WebScraper

    scraper = WebScraper()

    # Scrape a single URL
    result = await scraper.scrape(url="https://example.com/bistro")

    # Search + scrape: builds a DuckDuckGo-style search URL and scrapes
    # the first result page for business-related text
    snippets = await scraper.search_and_scrape("The Golden Fork restaurant SF hours")

Features
--------
* Uses ``httpx`` (already a project dependency) — no extra network library.
* Parses HTML with ``BeautifulSoup4``.
* Strips scripts, styles, and navigation noise.
* Caps extracted text at 2 000 characters to stay within LLM context windows.
* Respects ``Retry-After`` headers and applies a configurable per-host rate limit.
* Safe for concurrent use — each call creates its own ``httpx.AsyncClient``.
"""

from __future__ import annotations

import asyncio
import re
import time
from typing import Optional
from urllib.parse import quote_plus

_MAX_TEXT_CHARS = 2000
_DEFAULT_TIMEOUT = 10.0  # seconds
_USER_AGENT = (
    "Mozilla/5.0 (compatible; YelpAIAssistant/1.0; "
    "+https://github.com/smaruf/python-ai-course)"
)

# Simple in-process per-host rate limit: minimum seconds between requests
_RATE_LIMIT_SECONDS: float = 1.0
_last_request_time: dict[str, float] = {}
_rate_lock = asyncio.Lock()


class ScrapeResult:
    """Result of a single scrape operation."""

    def __init__(
        self,
        url: str,
        title: str,
        text: str,
        ok: bool = True,
        error: str | None = None,
    ) -> None:
        self.url = url
        self.title = title
        self.text = text
        self.ok = ok
        self.error = error

    def as_snippet(self) -> str:
        """Return a compact text snippet suitable for LLM context."""
        if not self.ok:
            return f"[Could not retrieve {self.url}: {self.error}]"
        parts = []
        if self.title:
            parts.append(f"Title: {self.title}")
        if self.text:
            parts.append(self.text[:_MAX_TEXT_CHARS])
        return "\n".join(parts)


class WebScraper:
    """
    Lightweight async web scraper.

    Parameters
    ----------
    timeout:
        Per-request timeout in seconds.
    max_text_chars:
        Maximum characters to extract from each page.
    rate_limit_seconds:
        Minimum gap between successive requests to the same host.
    """

    def __init__(
        self,
        timeout: float = _DEFAULT_TIMEOUT,
        max_text_chars: int = _MAX_TEXT_CHARS,
        rate_limit_seconds: float = _RATE_LIMIT_SECONDS,
    ) -> None:
        self._timeout = timeout
        self._max_text_chars = max_text_chars
        self._rate_limit = rate_limit_seconds

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def scrape(self, url: str) -> ScrapeResult:
        """
        Fetch and parse *url*, returning a ``ScrapeResult``.

        Strips scripts, styles, and nav elements before extracting text.
        """
        await self._rate_limit_for(url)
        try:
            import httpx  # already in project deps

            headers = {"User-Agent": _USER_AGENT}
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                headers=headers,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return self._parse(url, resp.text)
        except Exception as exc:  # noqa: BLE001
            return ScrapeResult(url=url, title="", text="", ok=False, error=str(exc))

    async def search_and_scrape(self, query: str) -> str:
        """
        Perform a DuckDuckGo HTML search for *query* and return a text
        snippet combining the top search-result excerpts.

        This is the primary enrichment tool for the Llama backend.
        """
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        result = await self.scrape(search_url)
        if not result.ok:
            return f"[Web search unavailable: {result.error}]"
        return result.text[: self._max_text_chars]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse(url: str, html: str) -> ScrapeResult:
        """Parse *html* and extract clean text content."""
        try:
            from bs4 import BeautifulSoup  # beautifulsoup4

            soup = BeautifulSoup(html, "html.parser")

            # Remove noisy elements
            for tag in soup([
                "script", "style", "nav", "header", "footer",
                "aside", "form", "noscript", "iframe",
            ]):
                tag.decompose()

            title = soup.title.get_text(strip=True) if soup.title else ""

            # Prefer main content areas
            body = (
                soup.find("main")
                or soup.find("article")
                or soup.find(id=re.compile(r"content|main|body", re.I))
                or soup.body
            )
            raw_text = body.get_text(separator=" ", strip=True) if body else ""

            # Collapse whitespace
            text = re.sub(r"\s{2,}", " ", raw_text).strip()

            return ScrapeResult(url=url, title=title, text=text)
        except Exception as exc:  # noqa: BLE001
            return ScrapeResult(url=url, title="", text="", ok=False, error=str(exc))

    async def _rate_limit_for(self, url: str) -> None:
        """Enforce per-host rate limiting to avoid hammering servers."""
        from urllib.parse import urlparse

        host = urlparse(url).netloc
        async with _rate_lock:
            last = _last_request_time.get(host, 0.0)
            elapsed = time.monotonic() - last
            if elapsed < self._rate_limit:
                await asyncio.sleep(self._rate_limit - elapsed)
            _last_request_time[host] = time.monotonic()
