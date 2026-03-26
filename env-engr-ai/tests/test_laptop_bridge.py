"""Tests for SimulatedLaptopBridge and IoTSensorHub."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.sensors.laptop_bridge import (
    SimulatedLaptopBridge,
    IoTSensorHub,
    ConnectionType,
)
from src.models.schemas import SensorReading


# ---------------------------------------------------------------------------
# SimulatedLaptopBridge tests
# ---------------------------------------------------------------------------

def test_simulated_bridge_connect_returns_true():
    bridge = SimulatedLaptopBridge()
    assert bridge.connect() is True


def test_simulated_bridge_is_connected_after_connect():
    bridge = SimulatedLaptopBridge()
    bridge.connect()
    assert bridge.is_connected is True


def test_simulated_bridge_is_disconnected_after_disconnect():
    bridge = SimulatedLaptopBridge()
    bridge.connect()
    bridge.disconnect()
    assert bridge.is_connected is False


def test_simulated_bridge_read_sensor_data_returns_list():
    bridge = SimulatedLaptopBridge()
    bridge.connect()
    readings = bridge.read_sensor_data()
    assert isinstance(readings, list)


def test_simulated_bridge_read_sensor_data_correct_count():
    bridge = SimulatedLaptopBridge(num_sensors=3, seed=0)
    bridge.connect()
    readings = bridge.read_sensor_data()
    assert len(readings) == 3


def test_simulated_bridge_readings_are_sensor_reading_instances():
    bridge = SimulatedLaptopBridge(num_sensors=2, seed=7)
    bridge.connect()
    readings = bridge.read_sensor_data()
    for r in readings:
        assert isinstance(r, SensorReading)


def test_simulated_bridge_reading_units():
    bridge = SimulatedLaptopBridge(num_sensors=3, seed=1)
    bridge.connect()
    readings = bridge.read_sensor_data()
    units = {r.unit for r in readings}
    assert len(units) >= 1


def test_simulated_bridge_write_command_returns_true():
    bridge = SimulatedLaptopBridge()
    bridge.connect()
    assert bridge.write_command("STATUS") is True


def test_simulated_bridge_is_connected_initial_false():
    bridge = SimulatedLaptopBridge()
    assert bridge.is_connected is False


# ---------------------------------------------------------------------------
# IoTSensorHub tests
# ---------------------------------------------------------------------------

def test_hub_add_and_connect_all():
    hub = IoTSensorHub()
    hub.add_bridge("sim1", SimulatedLaptopBridge(seed=10))
    results = hub.connect_all()
    assert "sim1" in results
    assert results["sim1"] is True


def test_hub_read_all_sensors_returns_list():
    hub = IoTSensorHub()
    hub.add_bridge("sim1", SimulatedLaptopBridge(num_sensors=3, seed=20))
    hub.connect_all()
    readings = hub.read_all_sensors()
    assert isinstance(readings, list)
    assert len(readings) == 3


def test_hub_read_all_sensors_multiple_bridges():
    hub = IoTSensorHub()
    hub.add_bridge("a", SimulatedLaptopBridge(num_sensors=2, seed=1))
    hub.add_bridge("b", SimulatedLaptopBridge(num_sensors=2, seed=2))
    hub.connect_all()
    readings = hub.read_all_sensors()
    assert len(readings) == 4


def test_hub_disconnect_all():
    hub = IoTSensorHub()
    b1 = SimulatedLaptopBridge(seed=30)
    hub.add_bridge("x", b1)
    hub.connect_all()
    hub.disconnect_all()
    assert b1.is_connected is False


def test_hub_get_status():
    hub = IoTSensorHub()
    hub.add_bridge("sim_a", SimulatedLaptopBridge(seed=40))
    hub.connect_all()
    status = hub.get_status()
    assert "bridges" in status
    assert "total_bridges" in status
    assert status["total_bridges"] == 1
    assert status["connected_bridges"] == 1


def test_hub_get_status_before_connect():
    hub = IoTSensorHub()
    hub.add_bridge("sim_b", SimulatedLaptopBridge(seed=50))
    status = hub.get_status()
    assert status["connected_bridges"] == 0
