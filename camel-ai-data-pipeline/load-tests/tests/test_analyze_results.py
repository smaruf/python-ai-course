"""
Smoke/unit tests for the load test analysis module.
Runs without a live server — uses synthesised CSV data.
"""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pytest

# Ensure the parent package is importable from this test file
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.analyze_results import (
    AnalysisResult,
    EndpointStats,
    SLO_P95_MS,
    SLO_ERROR_RATE_PCT,
    parse_stats_csv,
    parse_failures_csv,
    generate_markdown_report,
    generate_html_report,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_STATS_FIELDNAMES = [
    "Type", "Name", "Request Count", "Failure Count",
    "Median Response Time", "Average Response Time",
    "Min Response Time", "Max Response Time",
    "Average Content Size", "Requests/s", "Failures/s",
    "50%", "66%", "75%", "80%", "90%", "95%", "98%", "99%", "99.9%", "99.99%", "100%",
]


def _make_stats_csv(rows: list, *, include_aggregated: bool = True) -> Path:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_STATS_FIELDNAMES)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    if include_aggregated:
        agg = {f: "" for f in _STATS_FIELDNAMES}
        agg.update({"Type": "Aggregated", "Name": "Aggregated",
                     "Request Count": "500", "Failure Count": "2",
                     "Requests/s": "8.5", "95%": "450"})
        writer.writerow(agg)

    tmp = Path("/tmp/test_stats.csv")
    tmp.write_text(buf.getvalue(), encoding="utf-8")
    return tmp


def _make_failures_csv(rows: list) -> Path:
    tmp = Path("/tmp/test_failures.csv")
    buf = io.StringIO()
    fieldnames = ["Method", "Name", "Error", "Occurrences"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    tmp.write_text(buf.getvalue(), encoding="utf-8")
    return tmp


def _sample_endpoint_row(
    name: str = "POST /api/message",
    method: str = "POST",
    req: int = 200,
    fail: int = 1,
    p95: float = 300.0,
) -> dict:
    row = {f: "" for f in _STATS_FIELDNAMES}
    row.update({
        "Type": method,
        "Name": name,
        "Request Count": str(req),
        "Failure Count": str(fail),
        "Median Response Time": "100",
        "Average Response Time": "120",
        "Min Response Time": "20",
        "Max Response Time": "800",
        "Requests/s": "10.0",
        "95%": str(p95),
        "99%": str(p95 * 1.5),
    })
    return row


# ---------------------------------------------------------------------------
# Tests: EndpointStats
# ---------------------------------------------------------------------------
class TestEndpointStats:
    def test_error_rate_zero_requests(self):
        ep = EndpointStats(
            name="x", method="GET", request_count=0, failure_count=0,
            median_ms=0, p95_ms=0, p99_ms=0, avg_ms=0, min_ms=0, max_ms=0, rps=0,
        )
        assert ep.error_rate_pct == 0.0

    def test_error_rate_calculated(self):
        ep = EndpointStats(
            name="x", method="GET", request_count=100, failure_count=5,
            median_ms=50, p95_ms=200, p99_ms=400, avg_ms=60, min_ms=10, max_ms=500, rps=5.0,
        )
        assert ep.error_rate_pct == pytest.approx(5.0)

    def test_p95_slo_pass(self):
        ep = EndpointStats(
            name="x", method="GET", request_count=100, failure_count=0,
            median_ms=50, p95_ms=SLO_P95_MS - 1, p99_ms=400, avg_ms=60,
            min_ms=10, max_ms=500, rps=5.0,
        )
        assert ep.p95_slo_pass is True

    def test_p95_slo_fail(self):
        ep = EndpointStats(
            name="x", method="GET", request_count=100, failure_count=0,
            median_ms=50, p95_ms=SLO_P95_MS + 1, p99_ms=400, avg_ms=60,
            min_ms=10, max_ms=500, rps=5.0,
        )
        assert ep.p95_slo_pass is False

    def test_error_slo_boundary(self):
        ep_ok = EndpointStats(
            name="x", method="GET", request_count=1000,
            failure_count=int(SLO_ERROR_RATE_PCT * 10),
            median_ms=50, p95_ms=200, p99_ms=400, avg_ms=60, min_ms=10, max_ms=500, rps=5.0,
        )
        assert ep_ok.error_slo_pass is True

        ep_fail = EndpointStats(
            name="x", method="GET", request_count=100, failure_count=20,
            median_ms=50, p95_ms=200, p99_ms=400, avg_ms=60, min_ms=10, max_ms=500, rps=5.0,
        )
        assert ep_fail.error_slo_pass is False


# ---------------------------------------------------------------------------
# Tests: parse_stats_csv
# ---------------------------------------------------------------------------
class TestParseStatsCsv:
    def test_parses_rows(self):
        csv_path = _make_stats_csv([_sample_endpoint_row()])
        endpoints = parse_stats_csv(csv_path)
        assert len(endpoints) == 1
        ep = endpoints[0]
        assert ep.name == "POST /api/message"
        assert ep.request_count == 200
        assert ep.p95_ms == pytest.approx(300.0)

    def test_excludes_aggregated_row(self):
        rows = [_sample_endpoint_row("POST /api/ask"), _sample_endpoint_row("GET /api/health")]
        csv_path = _make_stats_csv(rows, include_aggregated=True)
        endpoints = parse_stats_csv(csv_path)
        names = [e.name for e in endpoints]
        assert "Aggregated" not in names
        assert len(endpoints) == 2

    def test_missing_file_returns_empty(self):
        result = parse_stats_csv(Path("/tmp/nonexistent_xyz.csv"))
        assert result == []


# ---------------------------------------------------------------------------
# Tests: parse_failures_csv
# ---------------------------------------------------------------------------
class TestParseFailuresCsv:
    def test_parses_failures(self):
        path = _make_failures_csv([
            {"Method": "POST", "Name": "/api/message",
             "Error": "Connection refused", "Occurrences": "3"},
        ])
        failures = parse_failures_csv(path)
        assert len(failures) == 1
        assert failures[0]["Error"] == "Connection refused"

    def test_missing_file_returns_empty(self):
        result = parse_failures_csv(Path("/tmp/nonexistent_failures.csv"))
        assert result == []


# ---------------------------------------------------------------------------
# Tests: AnalysisResult
# ---------------------------------------------------------------------------
class TestAnalysisResult:
    def _build_result(
        self, p95: float = 300.0, fail_count: int = 0, rps: float = 10.0
    ) -> AnalysisResult:
        ep = EndpointStats(
            name="POST /api/message", method="POST",
            request_count=100, failure_count=fail_count,
            median_ms=50, p95_ms=p95, p99_ms=400, avg_ms=60,
            min_ms=10, max_ms=500, rps=rps,
        )
        return AnalysisResult(
            endpoints=[ep],
            total_requests=100,
            total_failures=fail_count,
            overall_rps=rps,
        )

    def test_slo_passed_all_ok(self):
        result = self._build_result(p95=300.0, fail_count=0, rps=10.0)
        assert result.slo_passed is True

    def test_slo_fails_on_high_p95(self):
        result = self._build_result(p95=SLO_P95_MS + 1.0)
        assert result.slo_passed is False

    def test_slo_fails_on_high_error_rate(self):
        result = self._build_result(fail_count=50)  # 50% error rate
        assert result.slo_passed is False

    def test_overall_error_rate(self):
        result = self._build_result(fail_count=10)
        assert result.overall_error_rate_pct == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Tests: report generation (smoke — just check file is created & non-empty)
# ---------------------------------------------------------------------------
class TestReportGeneration:
    def _minimal_result(self) -> AnalysisResult:
        ep = EndpointStats(
            name="POST /api/ask", method="POST",
            request_count=50, failure_count=1,
            median_ms=120, p95_ms=450, p99_ms=800, avg_ms=150,
            min_ms=30, max_ms=1200, rps=8.0,
        )
        return AnalysisResult(
            endpoints=[ep], total_requests=50,
            total_failures=1, overall_rps=8.0,
        )

    def test_markdown_report_created(self, tmp_path):
        result = self._minimal_result()
        out = tmp_path / "analysis_report.md"
        generate_markdown_report(result, out)
        assert out.exists()
        content = out.read_text()
        assert "POST /api/ask" in content
        assert "SLO" in content

    def test_html_report_created(self, tmp_path):
        result = self._minimal_result()
        out = tmp_path / "analysis_report.html"
        generate_html_report(result, out)
        assert out.exists()
        content = out.read_text()
        assert "<!DOCTYPE html>" in content
        assert "POST /api/ask" in content
