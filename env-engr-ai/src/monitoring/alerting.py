"""
Alert management with severity levels, history, and acknowledgment.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Callable, Optional

from src.models.schemas import Alert, AlertSeverity, SensorReading


class AlertManager:
    """
    Manages alerts with severity levels, history, acknowledgment.
    Notification channels: console, file, optional webhook.
    """

    SEVERITY_COLORS = {
        AlertSeverity.INFO:      "blue",
        AlertSeverity.WARNING:   "yellow",
        AlertSeverity.CRITICAL:  "red",
        AlertSeverity.EMERGENCY: "bold red",
    }

    def __init__(
        self,
        log_file: str = "alerts.log",
        webhook_url: Optional[str] = None,
    ) -> None:
        self._log_file = log_file
        self._webhook_url = webhook_url
        self._active_alerts: dict[str, Alert] = {}
        self._history: list[Alert] = []
        self._rules: list[Callable[[SensorReading], Optional[tuple[AlertSeverity, str]]]] = []

    def create_alert(
        self,
        severity: AlertSeverity,
        source_module: str,
        message: str,
    ) -> Alert:
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            severity=severity,
            source_module=source_module,
            message=message,
            timestamp=datetime.now(),
        )
        self._active_alerts[alert.alert_id] = alert
        self._history.append(alert)
        self._notify_console(alert)
        self._notify_file(alert)
        return alert

    def resolve_alert(self, alert_id: str) -> bool:
        if alert_id in self._active_alerts:
            self._active_alerts[alert_id].resolved = True
            alert = self._active_alerts.pop(alert_id)
            # Update in history
            for a in self._history:
                if a.alert_id == alert_id:
                    a.resolved = True
            return True
        return False

    def acknowledge_alert(self, alert_id: str) -> bool:
        if alert_id in self._active_alerts:
            self._active_alerts[alert_id].acknowledged = True
            for a in self._history:
                if a.alert_id == alert_id:
                    a.acknowledged = True
            return True
        return False

    def get_active_alerts(self) -> list[Alert]:
        return list(self._active_alerts.values())

    def get_history(self, limit: int = 100) -> list[Alert]:
        return self._history[-limit:]

    def add_rule(
        self,
        rule: Callable[[SensorReading], Optional[tuple[AlertSeverity, str]]],
    ) -> None:
        """Add a function that checks a reading and optionally returns (severity, message)."""
        self._rules.append(rule)

    def process_reading(self, reading: SensorReading) -> list[Alert]:
        """Run all rules against a new reading. Returns list of triggered alerts."""
        triggered: list[Alert] = []
        for rule in self._rules:
            try:
                result = rule(reading)
                if result is not None:
                    severity, message = result
                    alert = self.create_alert(severity, reading.sensor_id, message)
                    triggered.append(alert)
            except Exception:
                pass
        return triggered

    def _notify_console(self, alert: Alert) -> None:
        severity_symbols = {
            AlertSeverity.INFO:      "[INFO]",
            AlertSeverity.WARNING:   "[WARN]",
            AlertSeverity.CRITICAL:  "[CRIT]",
            AlertSeverity.EMERGENCY: "[EMER]",
        }
        symbol = severity_symbols.get(alert.severity, "[????]")
        ts = alert.timestamp.strftime("%H:%M:%S")
        print(f"{symbol} {ts} [{alert.source_module}] {alert.message}")

    def _notify_file(self, alert: Alert) -> None:
        try:
            with open(self._log_file, "a") as f:
                f.write(
                    f"{alert.timestamp.isoformat()} | {alert.severity.value} | "
                    f"{alert.source_module} | {alert.message}\n"
                )
        except OSError:
            pass

    def get_alert_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {sev.value: 0 for sev in AlertSeverity}
        for alert in self._active_alerts.values():
            counts[alert.severity.value] += 1
        return counts
