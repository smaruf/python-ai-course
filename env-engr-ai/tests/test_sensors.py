"""Tests for sensor base classes and MockSensor."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime

from src.models.schemas import SensorConfig, SensorReading, SensorType
from src.sensors.base import MockSensor, SensorRegistry


def make_config(sensor_type: SensorType, sensor_id: str = "test_01") -> SensorConfig:
    return SensorConfig(sensor_id=sensor_id, sensor_type=sensor_type, location="lab")


def test_mock_sensor_initialize():
    sensor = MockSensor(make_config(SensorType.TEMPERATURE))
    assert not sensor.is_initialized
    result = sensor.initialize()
    assert result is True
    assert sensor.is_initialized


def test_mock_sensor_read_returns_reading():
    sensor = MockSensor(make_config(SensorType.TEMPERATURE))
    sensor.initialize()
    reading = sensor.read()
    assert isinstance(reading, SensorReading)
    assert reading.sensor_id == "test_01"
    assert reading.unit == "°C"
    assert isinstance(reading.timestamp, datetime)
    assert isinstance(reading.value, float)


def test_mock_sensor_calibrate():
    sensor = MockSensor(make_config(SensorType.TEMPERATURE, "cal_01"))
    sensor.initialize()
    reading = sensor.read()
    original_value = reading.value
    reference = original_value + 5.0
    sensor.calibrate(reference)
    # Offset should shift subsequent readings
    assert abs(sensor.config.calibration_offset - 5.0) < 0.1


def test_mock_sensor_shutdown():
    sensor = MockSensor(make_config(SensorType.HUMIDITY, "shut_01"))
    sensor.initialize()
    assert sensor.is_initialized
    sensor.shutdown()
    assert not sensor.is_initialized


def test_sensor_registry_register_and_read_all():
    registry = SensorRegistry()
    for stype, sid in [(SensorType.TEMPERATURE, "t1"), (SensorType.PH, "ph1")]:
        s = MockSensor(make_config(stype, sid))
        registry.register(s)
    results = registry.initialize_all()
    assert all(results.values())
    readings = registry.read_all()
    assert len(readings) == 2
    sensor_ids = {r.sensor_id for r in readings}
    assert "t1" in sensor_ids
    assert "ph1" in sensor_ids


def test_sensor_registry_list_and_unregister():
    registry = SensorRegistry()
    s = MockSensor(make_config(SensorType.CO2, "co2_01"))
    registry.register(s)
    assert "co2_01" in registry.list_sensors()
    registry.unregister("co2_01")
    assert "co2_01" not in registry.list_sensors()


def test_sensor_reading_schema_validation():
    reading = SensorReading(
        sensor_id="s1", value=23.5, unit="°C", quality=0.95
    )
    assert reading.sensor_id == "s1"
    assert reading.value == 23.5
    assert reading.quality == 0.95
    assert reading.reading_id is not None


def test_sensor_reading_quality_clamped():
    r = SensorReading(sensor_id="s1", value=10.0, unit="°C", quality=1.5)
    assert r.quality <= 1.0
    r2 = SensorReading(sensor_id="s1", value=10.0, unit="°C", quality=-0.1)
    assert r2.quality >= 0.0


def test_mock_sensor_generates_realistic_data():
    """Verify MockSensor values stay within expected physical ranges."""
    checks = [
        (SensorType.TEMPERATURE, 10.0, 40.0),
        (SensorType.PH, 3.5, 9.5),
        (SensorType.CO2, 280.0, 2100.0),
        (SensorType.HUMIDITY, 25.0, 95.0),
    ]
    for stype, lo, hi in checks:
        sensor = MockSensor(make_config(stype, f"rng_{stype.value}"), seed=42)
        sensor.initialize()
        for _ in range(20):
            r = sensor.read()
            assert lo <= r.value <= hi, (
                f"{stype.value}: value {r.value} outside [{lo}, {hi}]"
            )


def test_mock_sensor_last_reading():
    sensor = MockSensor(make_config(SensorType.WIND_SPEED, "wind_01"))
    sensor.initialize()
    assert sensor.last_reading is None
    reading = sensor.read()
    assert sensor.last_reading is not None
    assert sensor.last_reading.sensor_id == "wind_01"
