# Monitoring Guide

## Dashboard Usage

```bash
# Live dashboard (30 seconds)
python main.py monitor --duration 30

# Single snapshot (non-interactive)
from src.monitoring.dashboard import MonitoringDashboard, DashboardConfig
dashboard = MonitoringDashboard()
dashboard.display_snapshot(status, readings)
```

## Alert Configuration

```python
from src.monitoring.alerting import AlertManager
from src.models.schemas import AlertSeverity

mgr = AlertManager(log_file="alerts.log")

# Add custom rule
def high_temp_rule(reading):
    if reading.sensor_id == "temp_01" and reading.value > 40.0:
        return AlertSeverity.WARNING, f"High temperature: {reading.value:.1f}°C"
    return None

mgr.add_rule(high_temp_rule)
```

## Data Storage

```python
from src.monitoring.data_store import LocalDataStore, TimeSeriesBuffer

# File-based (persistent)
store = LocalDataStore(data_dir="data/")
store.store_reading(reading)
store.export_csv("export.csv", sensor_id="temp_01")

# In-memory buffer (recent 1000 readings)
buf = TimeSeriesBuffer(max_size=1000)
buf.store_reading(reading)
recent = buf.get_all_recent(limit=50)
```
