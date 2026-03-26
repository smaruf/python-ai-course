"""Tests for monitoring: alerting, data stores, and dashboard."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import tempfile
import csv
import json

from src.models.schemas import Alert, AlertSeverity, SensorReading, SensorType, SystemStatus
from src.monitoring.alerting import AlertManager
from src.monitoring.data_store import LocalDataStore, TimeSeriesBuffer
from src.monitoring.dashboard import DashboardConfig, MonitoringDashboard


def make_reading(sensor_id="temp_01", value=25.0, unit="°C") -> SensorReading:
    return SensorReading(sensor_id=sensor_id, value=value, unit=unit)


# ---------------------------------------------------------------------------
# AlertManager tests
# ---------------------------------------------------------------------------

def test_alert_manager_create_alert(tmp_path):
    mgr = AlertManager(log_file=str(tmp_path / "alerts.log"))
    alert = mgr.create_alert(AlertSeverity.WARNING, "biofuel", "Test warning")
    assert isinstance(alert, Alert)
    assert alert.severity == AlertSeverity.WARNING
    assert not alert.resolved
    assert not alert.acknowledged


def test_alert_manager_active_alerts(tmp_path):
    mgr = AlertManager(log_file=str(tmp_path / "alerts.log"))
    a1 = mgr.create_alert(AlertSeverity.INFO, "module_a", "Info alert")
    a2 = mgr.create_alert(AlertSeverity.CRITICAL, "module_b", "Critical alert")
    active = mgr.get_active_alerts()
    assert len(active) == 2


def test_alert_manager_resolve_alert(tmp_path):
    mgr = AlertManager(log_file=str(tmp_path / "alerts.log"))
    alert = mgr.create_alert(AlertSeverity.WARNING, "test", "Resolving test")
    result = mgr.resolve_alert(alert.alert_id)
    assert result is True
    active = mgr.get_active_alerts()
    assert all(a.alert_id != alert.alert_id for a in active)


def test_alert_manager_resolve_nonexistent(tmp_path):
    mgr = AlertManager(log_file=str(tmp_path / "alerts.log"))
    assert not mgr.resolve_alert("nonexistent-id")


def test_alert_manager_acknowledge(tmp_path):
    mgr = AlertManager(log_file=str(tmp_path / "alerts.log"))
    alert = mgr.create_alert(AlertSeverity.CRITICAL, "solar", "Solar fault")
    result = mgr.acknowledge_alert(alert.alert_id)
    assert result is True
    active = mgr.get_active_alerts()
    matching = [a for a in active if a.alert_id == alert.alert_id]
    assert matching[0].acknowledged is True


def test_alert_manager_history(tmp_path):
    mgr = AlertManager(log_file=str(tmp_path / "alerts.log"))
    for i in range(5):
        mgr.create_alert(AlertSeverity.INFO, "sensor", f"Alert {i}")
    history = mgr.get_history(limit=10)
    assert len(history) == 5


def test_alert_manager_process_reading_triggers_rule(tmp_path):
    mgr = AlertManager(log_file=str(tmp_path / "alerts.log"))

    def high_temp_rule(reading: SensorReading):
        if reading.value > 40.0:
            return AlertSeverity.WARNING, f"High temperature: {reading.value}"
        return None

    mgr.add_rule(high_temp_rule)
    normal = make_reading(value=25.0)
    hot = make_reading(value=45.0)

    alerts_normal = mgr.process_reading(normal)
    assert len(alerts_normal) == 0

    alerts_hot = mgr.process_reading(hot)
    assert len(alerts_hot) == 1
    assert alerts_hot[0].severity == AlertSeverity.WARNING


# ---------------------------------------------------------------------------
# TimeSeriesBuffer tests
# ---------------------------------------------------------------------------

def test_time_series_buffer_store_and_retrieve():
    buf = TimeSeriesBuffer(max_size=100)
    for i in range(10):
        buf.store_reading(make_reading(value=float(i)))
    readings = buf.get_readings("temp_01", limit=5)
    assert len(readings) == 5


def test_time_series_buffer_max_size():
    buf = TimeSeriesBuffer(max_size=5)
    for i in range(10):
        buf.store_reading(make_reading(value=float(i)))
    # Buffer should only hold last 5
    assert len(buf) <= 5


def test_time_series_buffer_multiple_sensors():
    buf = TimeSeriesBuffer()
    buf.store_reading(make_reading("sensor_a", 1.0))
    buf.store_reading(make_reading("sensor_b", 2.0))
    buf.store_reading(make_reading("sensor_a", 3.0))
    a_readings = buf.get_readings("sensor_a")
    b_readings = buf.get_readings("sensor_b")
    assert len(a_readings) == 2
    assert len(b_readings) == 1


def test_time_series_buffer_export_csv(tmp_path):
    buf = TimeSeriesBuffer()
    for i in range(5):
        buf.store_reading(make_reading(value=float(i)))
    filepath = str(tmp_path / "export.csv")
    buf.export_csv(filepath)
    assert os.path.exists(filepath)
    with open(filepath) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5


# ---------------------------------------------------------------------------
# LocalDataStore tests
# ---------------------------------------------------------------------------

def test_local_data_store_store_and_retrieve(tmp_path):
    store = LocalDataStore(data_dir=str(tmp_path))
    reading = make_reading("ph_01", value=7.2, unit="pH")
    store.store_reading(reading)
    retrieved = store.get_readings("ph_01")
    assert len(retrieved) == 1
    assert abs(retrieved[0].value - 7.2) < 0.001


def test_local_data_store_export_csv(tmp_path):
    store = LocalDataStore(data_dir=str(tmp_path / "data"))
    for i in range(3):
        store.store_reading(make_reading("co2_01", value=400.0 + i))
    export_path = str(tmp_path / "export.csv")
    store.export_csv(export_path, sensor_id="co2_01")
    assert os.path.exists(export_path)
    with open(export_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3


def test_local_data_store_export_json(tmp_path):
    store = LocalDataStore(data_dir=str(tmp_path / "data2"))
    for i in range(3):
        store.store_reading(make_reading("temp_02", value=20.0 + i))
    export_path = str(tmp_path / "export.json")
    store.export_json(export_path, sensor_id="temp_02")
    assert os.path.exists(export_path)
    with open(export_path) as f:
        data = json.load(f)
    assert len(data) == 3


# ---------------------------------------------------------------------------
# DashboardConfig tests
# ---------------------------------------------------------------------------

def test_dashboard_config_defaults():
    config = DashboardConfig()
    assert config.refresh_interval_s == 2.0
    assert config.show_sensors is True
    assert config.show_alerts is True
    assert len(config.show_modules) == 4
    assert config.max_history_display == 10


def test_dashboard_config_custom():
    config = DashboardConfig(refresh_interval_s=5.0, max_history_display=20)
    assert config.refresh_interval_s == 5.0
    assert config.max_history_display == 20


def test_monitoring_dashboard_display_snapshot(capsys, tmp_path):
    """Smoke test: display_snapshot should not raise."""
    dashboard = MonitoringDashboard()
    status = SystemStatus(
        active_sensors=["temp_01"],
        alerts=[],
        module_statuses={"biofuel": "OK"},
    )
    readings = [make_reading("temp_01", 25.0)]
    dashboard.display_snapshot(status, readings)  # Should not raise
