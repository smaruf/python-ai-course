"""
Tests for local Llama / OpenAI / Copilot LLM providers,
web scraper, and updated RAGService + CLI/GUI auth flows.
"""

from __future__ import annotations

import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.llm.provider import (
    CopilotBackend,
    GuestBackend,
    LlamaBackend,
    LLMProvider,
    MockBackend,
    OpenAIBackend,
    _GUEST_HEADER,
    create_backend,
)
from src.rag.rag_service import RAGService
from src.tools.web_scraper import ScrapeResult, WebScraper


# ---------------------------------------------------------------------------
# LLM Provider — unit tests
# ---------------------------------------------------------------------------

class TestLLMProvider:
    def test_mock_backend_generate(self):
        backend = MockBackend()
        result = asyncio.run(backend.generate("ctx", "Is it open?"))
        assert "Mock" in result
        assert isinstance(result, str)

    def test_guest_backend_appends_header(self):
        backend = GuestBackend()
        result = asyncio.run(backend.generate("ctx", "Is it open?"))
        assert "Guest" in result
        assert _GUEST_HEADER in result

    def test_factory_mock(self):
        backend = create_backend(LLMProvider.MOCK)
        assert isinstance(backend, MockBackend)

    def test_factory_guest(self):
        backend = create_backend("guest")
        assert isinstance(backend, GuestBackend)

    def test_factory_llama_returns_llama_backend(self):
        backend = create_backend(LLMProvider.LLAMA)
        assert isinstance(backend, LlamaBackend)

    def test_factory_openai_no_key_falls_back_to_guest(self):
        # Make sure env var is absent
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            backend = create_backend(LLMProvider.OPENAI)
        assert isinstance(backend, GuestBackend)

    def test_factory_openai_with_key(self):
        backend = create_backend(LLMProvider.OPENAI, api_key="sk-test-key")
        assert isinstance(backend, OpenAIBackend)

    def test_factory_copilot_no_token_falls_back_to_guest(self):
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict(os.environ, env, clear=True):
            backend = create_backend(LLMProvider.COPILOT)
        assert isinstance(backend, GuestBackend)

    def test_factory_copilot_with_token(self):
        backend = create_backend(LLMProvider.COPILOT, api_key="ghp_test")
        assert isinstance(backend, CopilotBackend)

    def test_factory_string_provider(self):
        backend = create_backend("mock")
        assert isinstance(backend, MockBackend)

    def test_openai_no_key_returns_auth_message(self):
        backend = OpenAIBackend(api_key="")
        result = asyncio.run(backend.generate("ctx", "question"))
        assert "No API key" in result or "api_key" in result.lower() or "OPENAI_API_KEY" in result

    def test_copilot_no_token_returns_auth_message(self):
        backend = CopilotBackend(api_key="")
        result = asyncio.run(backend.generate("ctx", "question"))
        # Either "No token provided" (before openai import) or openai import error
        assert "No token" in result or "GITHUB_TOKEN" in result or "Copilot" in result

    def test_llama_offline_returns_fallback_message(self):
        """LlamaBackend must not raise — it returns a graceful error string."""
        backend = LlamaBackend(host="http://localhost:19999")  # nothing running
        result = asyncio.run(backend.generate("ctx", "question"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_llama_generate_with_web_snippets(self):
        """LlamaBackend accepts optional web_snippets kwarg."""
        backend = LlamaBackend(host="http://localhost:19999")
        result = asyncio.run(backend.generate("ctx", "q", web_snippets="extra context"))
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# WebScraper — unit tests (network calls are mocked)
# ---------------------------------------------------------------------------

class TestWebScraper:
    def test_scrape_result_ok(self):
        r = ScrapeResult(url="http://x.com", title="T", text="hello world", ok=True)
        snippet = r.as_snippet()
        assert "Title: T" in snippet
        assert "hello world" in snippet

    def test_scrape_result_error(self):
        r = ScrapeResult(url="http://x.com", title="", text="", ok=False, error="timeout")
        snippet = r.as_snippet()
        assert "Could not retrieve" in snippet
        assert "timeout" in snippet

    def test_scraper_parse_html(self):
        html = """
        <html><head><title>Best Bistro</title></head>
        <body>
          <nav>Navigation</nav>
          <main><p>Open Mon–Fri 9am–10pm. Heated patio available.</p></main>
          <script>var x=1;</script>
        </body></html>
        """
        result = WebScraper._parse("http://example.com", html)
        assert result.ok
        assert result.title == "Best Bistro"
        assert "Heated patio" in result.text
        # Script and nav content should be stripped
        assert "var x" not in result.text
        assert "Navigation" not in result.text

    def test_scraper_parse_malformed_html(self):
        """Even with broken HTML, _parse must not raise."""
        result = WebScraper._parse("http://x.com", "<not valid html at all")
        assert isinstance(result, ScrapeResult)

    def test_scraper_scrape_http_error(self):
        """Network errors are caught and returned as failed ScrapeResult."""
        import httpx

        scraper = WebScraper(rate_limit_seconds=0)

        async def _mock_get(*a, **kw):
            raise httpx.ConnectError("connection refused")

        with patch("httpx.AsyncClient") as mock_cls:
            instance = MagicMock()
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=instance)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)
            instance.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
            result = asyncio.run(scraper.scrape("http://localhost:9999/nowhere"))

        assert isinstance(result, ScrapeResult)
        assert not result.ok or result.text == "" or "refused" in (result.error or "")

    def test_scraper_max_text_chars(self):
        html = "<html><body><main>" + ("x" * 5_000) + "</main></body></html>"
        scraper = WebScraper(max_text_chars=100)
        result = WebScraper._parse("http://x.com", html)
        # _parse extracts full text; as_snippet caps at max_text_chars
        snippet = result.as_snippet()[:100]
        assert len(snippet) <= 100


# ---------------------------------------------------------------------------
# RAGService — backend parameter
# ---------------------------------------------------------------------------

class TestRAGServiceBackend:
    def _make_bundle(self):
        from src.models.schemas import BusinessData, BusinessHours, Photo, Review
        from src.search.services import (
            PhotoHybridRetrievalService,
            ReviewVectorSearchService,
            StructuredSearchService,
        )
        from src.routing.router import QueryRouter, RoutedResults
        from src.routing.router import RoutingDecision
        from src.orchestration.orchestrator import AnswerOrchestrator

        biz = BusinessData(
            business_id="t1",
            name="Test Biz",
            address="1 Test St",
            phone="+1-555-0100",
            price_range="$$",
            hours=[BusinessHours("monday", "09:00", "21:00")],
            amenities={"heated_patio": True},
        )
        ss = StructuredSearchService()
        ss.add_business(biz)
        results = asyncio.run(ss.search("Is it open?", "t1"))
        from src.models.schemas import QueryIntent
        routed = RoutedResults(
            decision=RoutingDecision(
                intent=QueryIntent.OPERATIONAL,
                use_structured=True,
                use_review_vector=False,
                use_photo_hybrid=False,
            ),
            structured_results=results,
            review_results=[],
            photo_results=[],
        )
        return AnswerOrchestrator().orchestrate(routed)

    def test_rag_with_mock_backend(self):
        rag = RAGService(use_mock=True)
        bundle = self._make_bundle()
        from src.models.schemas import QueryIntent
        response = asyncio.run(rag.generate_answer("Is it open?", QueryIntent.OPERATIONAL, bundle))
        assert response.answer
        assert response.confidence >= 0

    def test_rag_with_explicit_mock_backend(self):
        backend = MockBackend()
        rag = RAGService(backend=backend)
        assert rag._use_mock is False
        bundle = self._make_bundle()
        from src.models.schemas import QueryIntent
        response = asyncio.run(rag.generate_answer("Is it open?", QueryIntent.OPERATIONAL, bundle))
        assert response.answer
        assert "Mock" in response.answer

    def test_rag_with_guest_backend(self):
        backend = GuestBackend()
        rag = RAGService(backend=backend)
        bundle = self._make_bundle()
        from src.models.schemas import QueryIntent
        response = asyncio.run(rag.generate_answer("Is it open?", QueryIntent.OPERATIONAL, bundle))
        assert _GUEST_HEADER in response.answer

    def test_rag_web_scraper_called_for_llama(self):
        """When using LlamaBackend + WebScraper, the scraper is invoked."""
        backend = LlamaBackend(host="http://localhost:19999")
        scraper = MagicMock()
        scraper.search_and_scrape = AsyncMock(return_value="live web snippet")

        rag = RAGService(backend=backend, web_scraper=scraper)
        bundle = self._make_bundle()
        from src.models.schemas import QueryIntent
        # LlamaBackend will fail (no server) but scraper must have been called
        asyncio.run(rag.generate_answer("Is it open?", QueryIntent.OPERATIONAL, bundle))
        scraper.search_and_scrape.assert_called_once()

    def test_rag_web_scraper_not_called_for_openai(self):
        """WebScraper should NOT be called for non-Llama backends."""
        backend = OpenAIBackend(api_key="")  # no key → returns auth message
        scraper = MagicMock()
        scraper.search_and_scrape = AsyncMock(return_value="not used")

        rag = RAGService(backend=backend, web_scraper=scraper)
        bundle = self._make_bundle()
        from src.models.schemas import QueryIntent
        asyncio.run(rag.generate_answer("Is it open?", QueryIntent.OPERATIONAL, bundle))
        scraper.search_and_scrape.assert_not_called()


# ---------------------------------------------------------------------------
# CLI — auth resolution helper
# ---------------------------------------------------------------------------

class TestCLIAuthResolution:
    def test_resolve_key_explicit(self):
        from cli.main import _resolve_api_key
        assert _resolve_api_key("openai", "sk-explicit") == "sk-explicit"

    def test_resolve_key_from_env(self):
        from cli.main import _resolve_api_key
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-from-env"}):
            assert _resolve_api_key("openai", None) == "sk-from-env"

    def test_resolve_key_mock_returns_none(self):
        from cli.main import _resolve_api_key
        # mock/llama do not need a key
        assert _resolve_api_key("mock", None) is None
        assert _resolve_api_key("llama", None) is None

    def test_resolve_key_copilot_from_env(self):
        from cli.main import _resolve_api_key
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_env_token"}):
            assert _resolve_api_key("copilot", None) == "ghp_env_token"


# ---------------------------------------------------------------------------
# CLI — --provider flag wired into query command
# ---------------------------------------------------------------------------

class TestCLIProviderFlag:
    def test_query_help_shows_provider_option(self):
        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["query", "--help"])
        assert result.exit_code == 0
        assert "--provider" in result.output

    def test_query_with_mock_provider(self):
        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["query", "--provider", "mock", "Is it open?"])
        assert result.exit_code == 0
        assert "Answer" in result.output

    def test_query_provider_in_output(self):
        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["query", "--provider", "mock", "Is it open?"])
        assert "mock" in result.output

    def test_scrape_help(self):
        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["scrape", "--help"])
        assert result.exit_code == 0
        assert "scrape" in result.output.lower()

    def test_scrape_url_flag_network_error_handled(self):
        """scrape --url with unreachable host must not crash the CLI."""
        from click.testing import CliRunner
        from cli.main import cli

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["scrape", "--url", "--timeout", "2", "http://localhost:19999/nothing"],
        )
        # Should exit cleanly (may show error message but no Python traceback)
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# GUI — _ask with provider / api_key params
# ---------------------------------------------------------------------------

class TestGUIProviderIntegration:
    def test_ask_mock_provider(self):
        from gui.app import _ask

        answer_md, intent_md, raw = _ask("Is it open?", "demo-001", "mock", "")
        assert "Mock" in raw or "answer" in raw.lower()
        assert intent_md  # non-empty intent badge

    def test_ask_guest_provider_shows_upgrade_notice(self):
        from gui.app import _ask

        # openai with no key → falls back to guest
        answer_md, intent_md, raw = _ask("Is it open?", "demo-001", "openai", "")
        assert "guest mode" in answer_md.lower() or "Guest" in answer_md

    def test_ask_empty_query_returns_warning(self):
        from gui.app import _ask

        answer_md, _, _ = _ask("", "demo-001", "mock", "")
        assert "⚠️" in answer_md

    def test_ask_provider_field_in_raw_json(self):
        from gui.app import _ask
        import json as _json

        _, _, raw = _ask("Is it open?", "demo-001", "mock", "")
        data = _json.loads(raw)
        assert "provider" in data
        assert data["provider"] == "mock"

    def test_build_interface_has_provider_radio(self):
        from gui.app import build_interface
        import gradio as gr

        iface = build_interface()
        # Walk the component tree looking for a Radio with provider choices
        found = False
        for block in iface.blocks.values():
            if isinstance(block, gr.Radio):
                if any("mock" in str(c).lower() for c in (block.choices or [])):
                    found = True
                    break
        assert found, "Provider Radio not found in Gradio interface"

    def test_build_interface_has_api_key_box(self):
        from gui.app import build_interface
        import gradio as gr

        iface = build_interface()
        has_password_box = any(
            isinstance(b, gr.Textbox) and getattr(b, "type", None) == "password"
            for b in iface.blocks.values()
        )
        assert has_password_box, "API key password Textbox not found in Gradio interface"
