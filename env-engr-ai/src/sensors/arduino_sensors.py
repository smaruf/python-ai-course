"""
Arduino serial bridge for sensor data acquisition.
"""
import json
import random
import math
import time
from datetime import datetime
from typing import Optional

from src.models.schemas import SensorConfig, SensorReading, SensorType

try:
    import serial  # type: ignore
    _SERIAL_AVAILABLE = True
except ImportError:
    _SERIAL_AVAILABLE = False


class ArduinoSerialBridge:
    """
    Reads JSON sensor packets from an Arduino over a serial port.
    Expected JSON format: {"sensor_id":"temp_01","value":23.5,"unit":"C","ts":12345}
    """

    def __init__(self, port: str = "/dev/ttyACM0", baud: int = 9600,
                 timeout: float = 2.0) -> None:
        self._port = port
        self._baud = baud
        self._timeout = timeout
        self._serial: Optional[object] = None
        self._connected = False

    def connect(self) -> bool:
        if not _SERIAL_AVAILABLE:
            return False
        try:
            self._serial = serial.Serial(self._port, self._baud,
                                         timeout=self._timeout)
            time.sleep(2.0)  # Allow Arduino bootloader to finish
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    def disconnect(self) -> None:
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
        self._connected = False

    def _try_reconnect(self) -> bool:
        self.disconnect()
        time.sleep(1.0)
        return self.connect()

    def read_packet(self) -> Optional[dict]:
        """Read one JSON packet from serial. Returns None on error."""
        if not self._connected:
            if not self._try_reconnect():
                return None
        try:
            raw = self._serial.readline().decode("utf-8", errors="ignore").strip()
            if not raw:
                return None
            return json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        except Exception:
            self._connected = False
            return None

    def read_reading(self) -> Optional[SensorReading]:
        """Read one packet and convert to SensorReading."""
        packet = self.read_packet()
        if not packet:
            return None
        required = {"sensor_id", "value", "unit"}
        if not required.issubset(packet.keys()):
            return None
        try:
            return SensorReading(
                sensor_id=str(packet["sensor_id"]),
                timestamp=datetime.now(),
                value=float(packet["value"]),
                unit=str(packet["unit"]),
                quality=float(packet.get("quality", 1.0)),
            )
        except (ValueError, KeyError):
            return None

    def read_all_available(self) -> list[SensorReading]:
        """Drain the serial buffer and return all valid readings."""
        readings: list[SensorReading] = []
        if not self._connected:
            return readings
        while self._serial.in_waiting > 0:
            r = self.read_reading()
            if r:
                readings.append(r)
        return readings

    def is_connected(self) -> bool:
        return self._connected


class SimulatedArduinoBridge:
    """
    Generates fake Arduino data for testing without physical hardware.
    Simulates: temperature (NTC), pH (analog), moisture (capacitive)
    """

    SENSORS = [
        {"sensor_id": "temp_01",     "type": SensorType.TEMPERATURE,  "unit": "C",   "lo": 15.0, "hi": 40.0,  "noise": 0.3},
        {"sensor_id": "ph_01",       "type": SensorType.PH,           "unit": "pH",  "lo": 4.5,  "hi": 8.5,   "noise": 0.05},
        {"sensor_id": "moisture_01", "type": SensorType.MOISTURE,     "unit": "%",   "lo": 20.0, "hi": 80.0,  "noise": 0.8},
        {"sensor_id": "co2_01",      "type": SensorType.CO2,          "unit": "ppm", "lo": 350.0,"hi": 1500.0,"noise": 8.0},
    ]

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._start = time.time()
        self._connected = False

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def _generate_value(self, sensor_def: dict) -> float:
        elapsed = time.time() - self._start
        lo, hi = sensor_def["lo"], sensor_def["hi"]
        mid = (lo + hi) / 2.0
        amp = (hi - lo) / 2.0
        period = 90.0 + self._rng.uniform(-10, 10)
        base = mid + amp * 0.7 * math.sin(2.0 * math.pi * elapsed / period)
        noise = self._rng.gauss(0.0, sensor_def["noise"])
        return max(lo, min(hi, base + noise))

    def read_reading(self) -> Optional[SensorReading]:
        if not self._connected:
            return None
        sensor_def = self._rng.choice(self.SENSORS)
        value = self._generate_value(sensor_def)
        return SensorReading(
            sensor_id=sensor_def["sensor_id"],
            timestamp=datetime.now(),
            value=round(value, 4),
            unit=sensor_def["unit"],
            quality=round(self._rng.uniform(0.85, 1.0), 3),
        )

    def read_all_available(self) -> list[SensorReading]:
        """Return one reading per sensor each call."""
        if not self._connected:
            return []
        readings: list[SensorReading] = []
        for sensor_def in self.SENSORS:
            value = self._generate_value(sensor_def)
            readings.append(SensorReading(
                sensor_id=sensor_def["sensor_id"],
                timestamp=datetime.now(),
                value=round(value, 4),
                unit=sensor_def["unit"],
                quality=round(self._rng.uniform(0.85, 1.0), 3),
            ))
        return readings
