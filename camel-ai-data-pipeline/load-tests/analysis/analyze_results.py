"""
Camel AI Pipeline — Load Test Result Analyser
==============================================
Parses the CSV files produced by Locust (--csv flag) and generates:

  1. Console summary table (always)
  2. Markdown report  → results/analysis_report.md
  3. HTML report      → results/analysis_report.html

Usage
-----
    python analysis/analyze_results.py --csv-prefix results/load_test

The script expects two Locust CSV files:
  <prefix>_stats.csv       — per-endpoint request statistics
  <prefix>_stats_history.csv — time-series RPS / response-time data
  <prefix>_failures.csv    — failure details  (optional)

Exit codes
----------
  0 — all SLOs passed
  1 — one or more SLOs violated (useful for CI gate)
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# SLO thresholds — adjust to match your pipeline SLAs
# ---------------------------------------------------------------------------
SLO_P95_MS: float = 2000.0    # 95th-percentile latency must be below 2 s
SLO_ERROR_RATE_PCT: float = 1.0  # error rate must be below 1 %
SLO_RPS_MIN: float = 5.0       # minimum sustained RPS across the run


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class EndpointStats:
    name: str
    method: str
    request_count: int
    failure_count: int
    median_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    min_ms: float
    max_ms: float
    rps: float

    @property
    def error_rate_pct(self) -> float:
        if self.request_count == 0:
            return 0.0
        return 100.0 * self.failure_count / self.request_count

    @property
    def p95_slo_pass(self) -> bool:
        return self.p95_ms <= SLO_P95_MS

    @property
    def error_slo_pass(self) -> bool:
        return self.error_rate_pct <= SLO_ERROR_RATE_PCT


@dataclass
class AnalysisResult:
    endpoints: List[EndpointStats] = field(default_factory=list)
    failures: List[dict] = field(default_factory=list)
    run_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_requests: int = 0
    total_failures: int = 0
    overall_rps: float = 0.0
    duration_s: float = 0.0

    @property
    def overall_error_rate_pct(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return 100.0 * self.total_failures / self.total_requests

    @property
    def slo_passed(self) -> bool:
        endpoint_slos = all(e.p95_slo_pass and e.error_slo_pass for e in self.endpoints)
        rps_slo = self.overall_rps >= SLO_RPS_MIN
        return endpoint_slos and rps_slo


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------
def _safe_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value) if value.strip() not in ("", "N/A") else default
    except (ValueError, AttributeError):
        return default


def _safe_int(value: str, default: int = 0) -> int:
    try:
        return int(value) if value.strip() not in ("", "N/A") else default
    except (ValueError, AttributeError):
        return default


def parse_stats_csv(path: Path) -> List[EndpointStats]:
    """Parse Locust *_stats.csv into a list of EndpointStats (skips Aggregated row)."""
    endpoints: List[EndpointStats] = []
    if not path.exists():
        print(f"[WARN] Stats file not found: {path}")
        return endpoints

    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = row.get("Name", "")
            if name == "Aggregated":
                continue
            endpoints.append(EndpointStats(
                name=name,
                method=row.get("Type", ""),
                request_count=_safe_int(row.get("Request Count", "0")),
                failure_count=_safe_int(row.get("Failure Count", "0")),
                median_ms=_safe_float(row.get("Median Response Time", "0")),
                p95_ms=_safe_float(row.get("95%", "0")),
                p99_ms=_safe_float(row.get("99%", "0")),
                avg_ms=_safe_float(row.get("Average Response Time", "0")),
                min_ms=_safe_float(row.get("Min Response Time", "0")),
                max_ms=_safe_float(row.get("Max Response Time", "0")),
                rps=_safe_float(row.get("Requests/s", "0")),
            ))
    return endpoints


def parse_aggregated_row(path: Path) -> tuple[int, int, float]:
    """Return (total_requests, total_failures, overall_rps) from the Aggregated row."""
    if not path.exists():
        return 0, 0, 0.0
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row.get("Name") == "Aggregated":
                return (
                    _safe_int(row.get("Request Count", "0")),
                    _safe_int(row.get("Failure Count", "0")),
                    _safe_float(row.get("Requests/s", "0")),
                )
    return 0, 0, 0.0


def parse_failures_csv(path: Path) -> List[dict]:
    """Parse Locust *_failures.csv."""
    failures: List[dict] = []
    if not path.exists():
        return failures
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        failures = list(reader)
    return failures


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
_PASS = "✅ PASS"
_FAIL = "❌ FAIL"


def _slo_badge(passed: bool) -> str:
    return _PASS if passed else _FAIL


def print_console_summary(result: AnalysisResult) -> None:
    """Print a human-readable table to stdout."""
    print("\n" + "=" * 80)
    print("  CAMEL AI PIPELINE — LOAD TEST ANALYSIS")
    print(f"  Generated: {result.run_timestamp}")
    print("=" * 80)
    print(f"\n  Total requests : {result.total_requests:,}")
    print(f"  Total failures : {result.total_failures:,}")
    print(f"  Overall RPS    : {result.overall_rps:.1f}")
    print(f"  Error rate     : {result.overall_error_rate_pct:.2f} %")
    print(f"\n  SLO thresholds : P95 < {SLO_P95_MS:.0f} ms | error rate < {SLO_ERROR_RATE_PCT:.1f} % | RPS >= {SLO_RPS_MIN:.0f}")
    print(f"\n  Overall SLO    : {_slo_badge(result.slo_passed)}\n")

    header = f"  {'Endpoint':<40} {'Method':<6} {'Req':>6} {'Fail':>5} {'Err%':>6} {'P50':>6} {'P95':>7} {'P99':>7} {'RPS':>6}  SLO"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for ep in result.endpoints:
        slo = _slo_badge(ep.p95_slo_pass and ep.error_slo_pass)
        print(
            f"  {ep.name:<40} {ep.method:<6} {ep.request_count:>6,} "
            f"{ep.failure_count:>5,} {ep.error_rate_pct:>5.1f}% "
            f"{ep.median_ms:>6.0f} {ep.p95_ms:>7.0f} {ep.p99_ms:>7.0f} "
            f"{ep.rps:>6.1f}  {slo}"
        )

    if result.failures:
        print(f"\n  Top failures ({min(len(result.failures), 10)} of {len(result.failures)}):")
        for f in result.failures[:10]:
            print(f"    [{f.get('Method','?')}] {f.get('Name','?')} — {f.get('Error','?')} (count: {f.get('Occurrences','?')})")
    print()


def generate_markdown_report(result: AnalysisResult, out_path: Path) -> None:
    """Write a Markdown analysis report."""
    lines = [
        "# Camel AI Pipeline — Load Test Analysis Report",
        "",
        f"**Generated:** {result.run_timestamp}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total requests | {result.total_requests:,} |",
        f"| Total failures | {result.total_failures:,} |",
        f"| Overall RPS | {result.overall_rps:.1f} |",
        f"| Error rate | {result.overall_error_rate_pct:.2f} % |",
        f"| Overall SLO | {_slo_badge(result.slo_passed)} |",
        "",
        f"> **SLO thresholds**: P95 < {SLO_P95_MS:.0f} ms | error rate < {SLO_ERROR_RATE_PCT:.1f} % | RPS ≥ {SLO_RPS_MIN:.0f}",
        "",
        "## Endpoint Details",
        "",
        "| Endpoint | Method | Requests | Failures | Error % | P50 (ms) | P95 (ms) | P99 (ms) | RPS | SLO |",
        "|----------|--------|----------|----------|---------|----------|----------|----------|-----|-----|",
    ]
    for ep in result.endpoints:
        slo = _slo_badge(ep.p95_slo_pass and ep.error_slo_pass)
        lines.append(
            f"| {ep.name} | {ep.method} | {ep.request_count:,} | {ep.failure_count:,} "
            f"| {ep.error_rate_pct:.1f}% | {ep.median_ms:.0f} | {ep.p95_ms:.0f} "
            f"| {ep.p99_ms:.0f} | {ep.rps:.1f} | {slo} |"
        )

    if result.failures:
        lines += [
            "",
            "## Failures",
            "",
            "| Method | Endpoint | Error | Count |",
            "|--------|----------|-------|-------|",
        ]
        for f in result.failures[:50]:
            lines.append(
                f"| {f.get('Method','?')} | {f.get('Name','?')} "
                f"| {f.get('Error','?')} | {f.get('Occurrences','?')} |"
            )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[INFO] Markdown report written to {out_path}")


def generate_html_report(result: AnalysisResult, out_path: Path) -> None:
    """Write a styled HTML analysis report."""
    def row_class(passed: bool) -> str:
        return "pass" if passed else "fail"

    endpoint_rows = ""
    for ep in result.endpoints:
        slo_ok = ep.p95_slo_pass and ep.error_slo_pass
        rc = row_class(slo_ok)
        badge = _slo_badge(slo_ok)
        endpoint_rows += (
            f'<tr class="{rc}">'
            f"<td>{ep.name}</td><td>{ep.method}</td>"
            f"<td>{ep.request_count:,}</td><td>{ep.failure_count:,}</td>"
            f"<td>{ep.error_rate_pct:.1f}%</td>"
            f"<td>{ep.median_ms:.0f}</td><td>{ep.p95_ms:.0f}</td><td>{ep.p99_ms:.0f}</td>"
            f"<td>{ep.rps:.1f}</td><td>{badge}</td>"
            f"</tr>\n"
        )

    failure_rows = ""
    for f in result.failures[:50]:
        failure_rows += (
            f'<tr><td>{f.get("Method","?")}</td><td>{f.get("Name","?")}</td>'
            f'<td>{f.get("Error","?")}</td><td>{f.get("Occurrences","?")}</td></tr>\n'
        )
    failures_section = ""
    if failure_rows:
        failures_section = f"""
        <h2>Failures (top 50)</h2>
        <table>
          <thead><tr><th>Method</th><th>Endpoint</th><th>Error</th><th>Count</th></tr></thead>
          <tbody>{failure_rows}</tbody>
        </table>"""

    overall_class = "pass" if result.slo_passed else "fail"
    overall_badge = _slo_badge(result.slo_passed)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Camel AI Pipeline — Load Test Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
           margin: 40px; background: #f9f9f9; color: #333; }}
    h1 {{ color: #1a1a2e; }}
    h2 {{ color: #16213e; margin-top: 32px; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                     gap: 16px; margin: 24px 0; }}
    .metric {{ background: white; padding: 20px; border-radius: 8px;
               box-shadow: 0 1px 4px rgba(0,0,0,.1); text-align: center; }}
    .metric .value {{ font-size: 2rem; font-weight: 700; color: #1a1a2e; }}
    .metric .label {{ font-size: 0.85rem; color: #666; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; background: white;
             border-radius: 8px; overflow: hidden;
             box-shadow: 0 1px 4px rgba(0,0,0,.1); margin-bottom: 32px; }}
    th {{ background: #1a1a2e; color: white; padding: 12px 16px; text-align: left; font-size: 0.85rem; }}
    td {{ padding: 10px 16px; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; }}
    tr:last-child td {{ border-bottom: none; }}
    tr.pass td {{ background: #f0fff4; }}
    tr.fail td {{ background: #fff5f5; }}
    .badge-pass {{ color: #16a34a; font-weight: 600; }}
    .badge-fail {{ color: #dc2626; font-weight: 600; }}
    .slo-bar {{ padding: 16px 24px; border-radius: 8px; font-size: 1.1rem; font-weight: 600;
                margin: 16px 0; }}
    .slo-bar.pass {{ background: #dcfce7; color: #16a34a; border-left: 4px solid #16a34a; }}
    .slo-bar.fail {{ background: #fee2e2; color: #dc2626; border-left: 4px solid #dc2626; }}
    .slo-note {{ color: #888; font-size: 0.85rem; margin-bottom: 24px; }}
    footer {{ color: #aaa; font-size: 0.8rem; margin-top: 48px; }}
  </style>
</head>
<body>
  <h1>🚀 Camel AI Pipeline — Load Test Analysis</h1>
  <p style="color:#666">Generated: {result.run_timestamp}</p>

  <div class="slo-bar {overall_class}">{overall_badge} Overall SLO</div>
  <p class="slo-note">
    Thresholds: P95 &lt; {SLO_P95_MS:.0f} ms &nbsp;|&nbsp;
    error rate &lt; {SLO_ERROR_RATE_PCT:.1f} % &nbsp;|&nbsp;
    RPS &ge; {SLO_RPS_MIN:.0f}
  </p>

  <div class="summary-grid">
    <div class="metric"><div class="value">{result.total_requests:,}</div><div class="label">Total Requests</div></div>
    <div class="metric"><div class="value">{result.total_failures:,}</div><div class="label">Total Failures</div></div>
    <div class="metric"><div class="value">{result.overall_rps:.1f}</div><div class="label">Overall RPS</div></div>
    <div class="metric"><div class="value">{result.overall_error_rate_pct:.2f}%</div><div class="label">Error Rate</div></div>
  </div>

  <h2>Endpoint Statistics</h2>
  <table>
    <thead>
      <tr>
        <th>Endpoint</th><th>Method</th><th>Requests</th><th>Failures</th>
        <th>Error %</th><th>P50 (ms)</th><th>P95 (ms)</th><th>P99 (ms)</th>
        <th>RPS</th><th>SLO</th>
      </tr>
    </thead>
    <tbody>{endpoint_rows}</tbody>
  </table>
  {failures_section}
  <footer>Camel AI Data Pipeline &mdash; Load Test Analysis Tool</footer>
</body>
</html>"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"[INFO] HTML report written to {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def analyse(csv_prefix: str, output_dir: str) -> int:
    """Run the full analysis pipeline. Returns exit code (0=pass, 1=fail)."""
    prefix = Path(csv_prefix)
    stats_csv = Path(f"{csv_prefix}_stats.csv")
    failures_csv = Path(f"{csv_prefix}_failures.csv")

    endpoints = parse_stats_csv(stats_csv)
    total_req, total_fail, overall_rps = parse_aggregated_row(stats_csv)
    failures = parse_failures_csv(failures_csv)

    result = AnalysisResult(
        endpoints=endpoints,
        failures=failures,
        total_requests=total_req,
        total_failures=total_fail,
        overall_rps=overall_rps,
    )

    print_console_summary(result)

    out = Path(output_dir)
    generate_markdown_report(result, out / "analysis_report.md")
    generate_html_report(result, out / "analysis_report.html")

    if not result.slo_passed:
        print("[ERROR] One or more SLOs FAILED — see report for details.")
        return 1

    print("[INFO] All SLOs PASSED.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyse Locust load test CSV results for the Camel AI Pipeline."
    )
    parser.add_argument(
        "--csv-prefix",
        default="results/load_test",
        help="Prefix of the Locust CSV files (default: results/load_test)",
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Directory to write analysis reports (default: results/)",
    )
    args = parser.parse_args()
    sys.exit(analyse(args.csv_prefix, args.output_dir))


if __name__ == "__main__":
    main()
