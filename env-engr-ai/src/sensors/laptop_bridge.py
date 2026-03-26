"""Direct laptop/USB/IoT sensor bridge as alternative to RPi GPIO."""
from __future__ import annotations

import json
import random
from datetime import datetime
from enum import Enum
from typing import Any

try:
    import serial  # type: ignore[import-untyped]
    import serial.tools.list_ports  # type: ignore[import-untyped]
    _SERIAL_AVAILABLE = True
except ImportError:
    _SERIAL_AVAILABLE = False

try:
    import paho.mqtt.client as mqtt  # type: ignore[import-untyped]
    _MQTT_AVAILABLE = True
except ImportError:
    _MQTT_AVAILABLE = False

from src.models.schemas import SensorReading


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ConnectionType(str, Enum):
    """Supported connection types for sensor bridges."""
    USB_SERIAL = "USB_SERIAL"
    BLUETOOTH = "BLUETOOTH"
    WIFI_MQTT = "WIFI_MQTT"
    REST_API = "REST_API"
    MODBUS_RTU = "MODBUS_RTU"
    I2C_USB = "I2C_USB"


# ---------------------------------------------------------------------------
# LaptopSensorBridge
# ---------------------------------------------------------------------------

class LaptopSensorBridge:
    """Reads sensor data from an Arduino/microcontroller over USB serial."""

    # Keywords indicating a known sensor/microcontroller device on serial ports
    _DEVICE_KEYWORDS = ("arduino", "ch340", "cp210", "ftdi", "uart")

    def __init__(
        self,
        port: str | None = None,
        baud_rate: int = 9600,
        connection_type: ConnectionType = ConnectionType.USB_SERIAL,
    ) -> None:
        """Initialise the bridge.

        Args:
            port: Serial port path (e.g. '/dev/ttyACM0', 'COM3'). If None,
                auto-detection will be attempted on connect().
            baud_rate: Serial baud rate.
            connection_type: Type of connection being used.
        """
        self._port = port
        self._baud_rate = baud_rate
        self._connection_type = connection_type
        self._serial: Any = None
        self._connected = False

    def auto_detect_port(self) -> str | None:
        """Scan serial ports and return the first likely sensor device port.

        Returns None if pyserial is unavailable or no device found.
        """
        if not _SERIAL_AVAILABLE:
            return None
        try:
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                desc = (p.description or "").lower()
                if any(kw in desc for kw in self._DEVICE_KEYWORDS):
                    return p.device
            if ports:
                return ports[0].device
        except Exception:
            pass
        return None

    def connect(self) -> bool:
        """Open the serial connection.

        Returns True on success, False otherwise.
        """
        if not _SERIAL_AVAILABLE:
            return False
        if self._port is None:
            self._port = self.auto_detect_port()
        if self._port is None:
            return False
        try:
            self._serial = serial.Serial(self._port, self._baud_rate, timeout=2.0)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    def read_sensor_data(self) -> list[SensorReading]:
        """Read a line of JSON sensor data from the connected device.

        Expected JSON format from the microcontroller:
            {"sensor_id": "temp_01", "value": 23.5, "unit": "C", "quality": 1.0}

        Returns a list of SensorReading (may be empty on parse failure).
        """
        if not self._connected or self._serial is None:
            return []
        try:
            raw = self._serial.readline().decode("utf-8", errors="ignore").strip()
            if not raw:
                return []
            packet = json.loads(raw)
            if isinstance(packet, list):
                packets = packet
            else:
                packets = [packet]
            readings: list[SensorReading] = []
            for pkt in packets:
                readings.append(SensorReading(
                    sensor_id=str(pkt.get("sensor_id", "unknown")),
                    value=float(pkt.get("value", 0.0)),
                    unit=str(pkt.get("unit", "")),
                    quality=float(pkt.get("quality", 1.0)),
                    timestamp=datetime.now(),
                ))
            return readings
        except Exception:
            return []

    def write_command(self, command: str) -> bool:
        """Send a text command to the connected microcontroller.

        Returns True if the write succeeded.
        """
        if not self._connected or self._serial is None:
            return False
        try:
            self._serial.write((command + "\n").encode("utf-8"))
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        """Close the serial connection."""
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
        self._serial = None
        self._connected = False


# ---------------------------------------------------------------------------
# MQTTSensorBridge
# ---------------------------------------------------------------------------

class MQTTSensorBridge:
    """Subscribes to MQTT topics and collects sensor readings."""

    def __init__(
        self,
        broker: str,
        port: int = 1883,
        topics: list[str] | None = None,
    ) -> None:
        """Initialise the MQTT bridge.

        Args:
            broker: MQTT broker hostname or IP address.
            port: MQTT broker port.
            topics: List of MQTT topics to subscribe to.
        """
        self._broker = broker
        self._port = port
        self._topics = topics or ["sensors/#"]
        self._readings: list[SensorReading] = []
        self._client: Any = None

    def subscribe_and_read(self, timeout_s: float = 5.0) -> list[SensorReading]:
        """Connect to the MQTT broker, subscribe, collect readings, then disconnect.

        Returns a list of SensorReading gathered within *timeout_s* seconds.
        If paho-mqtt is unavailable returns an empty list.
        """
        if not _MQTT_AVAILABLE:
            return []
        self._readings = []

        def on_message(_client: Any, _userdata: Any, msg: Any) -> None:
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                self._readings.append(SensorReading(
                    sensor_id=str(payload.get("sensor_id", msg.topic)),
                    value=float(payload.get("value", 0.0)),
                    unit=str(payload.get("unit", "")),
                    quality=float(payload.get("quality", 1.0)),
                    timestamp=datetime.now(),
                ))
            except Exception:
                pass

        try:
            client = mqtt.Client()
            client.on_message = on_message
            client.connect(self._broker, self._port, keepalive=10)
            for topic in self._topics:
                client.subscribe(topic)
            client.loop_start()
            import time
            time.sleep(timeout_s)
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass

        return list(self._readings)


# ---------------------------------------------------------------------------
# SimulatedLaptopBridge
# ---------------------------------------------------------------------------

class SimulatedLaptopBridge:
    """Software-only sensor bridge that generates mock readings for testing."""

    _SENSOR_DEFS = [
        ("temperature", "C", 20.0, 5.0),
        ("pH", "pH", 7.0, 0.5),
        ("dissolved_oxygen", "mg/L", 8.0, 1.0),
    ]

    def __init__(self, num_sensors: int = 3, seed: int = 42) -> None:
        """Initialise the simulated bridge.

        Args:
            num_sensors: Number of virtual sensors to simulate.
            seed: Random seed for reproducibility.
        """
        self._num_sensors = min(num_sensors, len(self._SENSOR_DEFS))
        self._rng = random.Random(seed)
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """True if the simulated bridge is currently connected."""
        return self._connected

    def connect(self) -> bool:
        """Simulate establishing a connection.  Always returns True."""
        self._connected = True
        return True

    def read_sensor_data(self) -> list[SensorReading]:
        """Generate a fresh set of mock SensorReading objects.

        Returns one reading per virtual sensor.
        """
        readings: list[SensorReading] = []
        defs = self._SENSOR_DEFS[: self._num_sensors]
        for i, (name, unit, mean, std) in enumerate(defs):
            value = self._rng.gauss(mean, std)
            readings.append(SensorReading(
                sensor_id=f"sim_{name}_{i:02d}",
                value=round(value, 3),
                unit=unit,
                quality=round(self._rng.uniform(0.85, 1.0), 3),
                timestamp=datetime.now(),
            ))
        return readings

    def write_command(self, command: str) -> bool:
        """Simulate sending a command.  Always returns True."""
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting."""
        self._connected = False


# ---------------------------------------------------------------------------
# IoTSensorHub
# ---------------------------------------------------------------------------

class IoTSensorHub:
    """Aggregates multiple sensor bridges and provides a unified interface."""

    def __init__(self) -> None:
        """Initialise hub with an empty set of bridges."""
        self._bridges: dict[str, Any] = {}
        self._connected_flags: dict[str, bool] = {}

    def add_bridge(self, name: str, bridge: Any) -> None:
        """Register a bridge under the given name.

        Args:
            name: Unique identifier for this bridge.
            bridge: Any bridge instance (LaptopSensorBridge, SimulatedLaptopBridge, etc.).
        """
        self._bridges[name] = bridge
        self._connected_flags[name] = False

    def connect_all(self) -> dict[str, bool]:
        """Attempt to connect all registered bridges.

        Returns a dict mapping bridge name → connection success.
        """
        results: dict[str, bool] = {}
        for name, bridge in self._bridges.items():
            try:
                ok = bridge.connect()
            except Exception:
                ok = False
            self._connected_flags[name] = bool(ok)
            results[name] = bool(ok)
        return results

    def read_all_sensors(self) -> list[SensorReading]:
        """Read sensor data from every connected bridge.

        Returns a combined list of all SensorReading objects.
        """
        all_readings: list[SensorReading] = []
        for name, bridge in self._bridges.items():
            if not self._connected_flags.get(name, False):
                continue
            try:
                readings = bridge.read_sensor_data()
                if readings:
                    all_readings.extend(readings)
            except Exception:
                pass
        return all_readings

    def disconnect_all(self) -> None:
        """Disconnect all registered bridges."""
        for name, bridge in self._bridges.items():
            try:
                bridge.disconnect()
            except Exception:
                pass
            self._connected_flags[name] = False

    def get_status(self) -> dict[str, Any]:
        """Return connection status for all registered bridges.

        Returns a dict with per-bridge status and overall summary.
        """
        status: dict[str, bool] = dict(self._connected_flags)
        connected_count = sum(1 for v in status.values() if v)
        return {
            "bridges": status,
            "total_bridges": len(self._bridges),
            "connected_bridges": connected_count,
            "serial_library_available": _SERIAL_AVAILABLE,
            "mqtt_library_available": _MQTT_AVAILABLE,
        }
