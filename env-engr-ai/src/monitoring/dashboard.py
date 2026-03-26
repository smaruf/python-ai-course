"""
Rich-based terminal monitoring dashboard.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.models.schemas import Alert, AlertSeverity, SensorReading, SystemStatus


@dataclass
class DashboardConfig:
    refresh_interval_s: float = 2.0
    show_sensors: bool = True
    show_alerts: bool = True
    show_modules: list[str] = field(
        default_factory=lambda: [
            "waste_management", "biofuel", "edible_oil", "renewable_energy"
        ]
    )
    max_history_display: int = 10


SEVERITY_STYLE = {
    AlertSeverity.INFO:      "blue",
    AlertSeverity.WARNING:   "yellow",
    AlertSeverity.CRITICAL:  "bold red",
    AlertSeverity.EMERGENCY: "bold white on red",
}


class MonitoringDashboard:
    """
    Rich-based terminal monitoring dashboard.
    Shows: live sensor readings, module statuses, alerts, system status.
    """

    def __init__(self, config: DashboardConfig = None) -> None:
        self.config = config or DashboardConfig()
        self._console = Console()
        self._last_status: SystemStatus = SystemStatus()
        self._recent_readings: list[SensorReading] = []

    def update(
        self,
        status: SystemStatus,
        recent_readings: list[SensorReading],
    ) -> None:
        """Update internal state with new data."""
        self._last_status = status
        self._recent_readings = recent_readings[-self.config.max_history_display:]

    def _build_sensor_table(self) -> Table:
        table = Table(title="Sensor Readings", show_lines=True)
        table.add_column("Sensor ID", style="cyan")
        table.add_column("Value", justify="right")
        table.add_column("Unit", style="green")
        table.add_column("Quality", justify="right")
        table.add_column("Timestamp", style="dim")

        for r in self._recent_readings:
            quality_style = "green" if r.quality > 0.9 else "yellow" if r.quality > 0.7 else "red"
            table.add_row(
                r.sensor_id,
                f"{r.value:.3f}",
                r.unit,
                Text(f"{r.quality:.2f}", style=quality_style),
                r.timestamp.strftime("%H:%M:%S"),
            )
        return table

    def _build_alert_table(self) -> Table:
        table = Table(title="Active Alerts", show_lines=True)
        table.add_column("Severity", style="bold")
        table.add_column("Source")
        table.add_column("Message")
        table.add_column("Time", style="dim")

        for alert in self._last_status.alerts:
            if alert.resolved:
                continue
            style = SEVERITY_STYLE.get(alert.severity, "white")
            table.add_row(
                Text(alert.severity.value, style=style),
                alert.source_module,
                alert.message[:60],
                alert.timestamp.strftime("%H:%M:%S"),
            )
        if not any(not a.resolved for a in self._last_status.alerts):
            table.add_row("–", "–", "No active alerts", "–")
        return table

    def _build_module_panel(self) -> Panel:
        lines: list[Text] = []
        for module in self.config.show_modules:
            status_str = self._last_status.module_statuses.get(module, "UNKNOWN")
            style = "green" if status_str == "OK" else "yellow" if status_str == "WARNING" else "red"
            line = Text()
            line.append(f"  {module:<25}", style="white")
            line.append(status_str, style=style)
            lines.append(line)

        # Build single Text object by appending each line with newlines
        if lines:
            content = Text()
            for i, line in enumerate(lines):
                content.append_text(line)
                if i < len(lines) - 1:
                    content.append("\n")
        else:
            content = Text("No modules configured")
        return Panel(content, title="Module Statuses", border_style="blue")

    def _build_header(self) -> Panel:
        ts = self._last_status.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        n_sensors = len(self._last_status.active_sensors)
        n_alerts = sum(1 for a in self._last_status.alerts if not a.resolved)
        text = Text()
        text.append("🌱 Environmental Engineering AI Platform  ", style="bold green")
        text.append(f"[{ts}]  ", style="dim")
        text.append(f"Sensors: {n_sensors}  ", style="cyan")
        alert_style = "red" if n_alerts > 0 else "green"
        text.append(f"Alerts: {n_alerts}", style=alert_style)
        return Panel(text, style="green")

    def render(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(self._build_header(), name="header", size=3),
            Layout(name="body"),
        )
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )
        layout["left"].update(self._build_sensor_table())
        layout["right"].split_column(
            Layout(self._build_module_panel(), name="modules"),
            Layout(self._build_alert_table(), name="alerts"),
        )
        return layout

    def run_live(
        self,
        data_source: Callable,
        duration_s: float = 60.0,
    ) -> None:
        """Run live dashboard, calling data_source() each refresh."""
        start = time.time()
        with Live(
            self.render(),
            console=self._console,
            refresh_per_second=1.0 / self.config.refresh_interval_s,
        ) as live:
            while time.time() - start < duration_s:
                result = data_source()
                if isinstance(result, tuple):
                    status, readings = result
                    self.update(status, readings)
                live.update(self.render())
                time.sleep(self.config.refresh_interval_s)

    def display_snapshot(
        self,
        status: SystemStatus,
        readings: list[SensorReading],
    ) -> None:
        """Display a single snapshot (non-live mode)."""
        self.update(status, readings)
        self._console.print(self._build_header())
        self._console.print(self._build_sensor_table())
        self._console.print(self._build_module_panel())
        self._console.print(self._build_alert_table())
