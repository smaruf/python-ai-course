"""
Abstract base classes and implementations for environmental sensors.
"""
import abc
import math
import random
import time
from datetime import datetime
from typing import Optional

from src.models.schemas import SensorConfig, SensorReading, SensorType


class AbstractSensor(abc.ABC):
    """Abstract base class for all environmental sensors."""

    def __init__(self, config: SensorConfig) -> None:
        self.config = config
        self._initialized = False
        self._last_reading: Optional[SensorReading] = None

    @abc.abstractmethod
    def initialize(self) -> bool:
        """Initialize hardware and return True on success."""
        ...

    @abc.abstractmethod
    def read(self) -> SensorReading:
        """Read sensor value and return a SensorReading."""
        ...

    @abc.abstractmethod
    def calibrate(self, reference_value: float) -> None:
        """Calibrate sensor against a known reference value."""
        ...

    @abc.abstractmethod
    def shutdown(self) -> None:
        """Cleanly release sensor resources."""
        ...

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def last_reading(self) -> Optional[SensorReading]:
        return self._last_reading


# ---------------------------------------------------------------------------
# Sensor Registry
# ---------------------------------------------------------------------------

class SensorRegistry:
    """Manages a collection of sensors."""

    def __init__(self) -> None:
        self._sensors: dict[str, AbstractSensor] = {}

    def register(self, sensor: AbstractSensor) -> None:
        self._sensors[sensor.config.sensor_id] = sensor

    def unregister(self, sensor_id: str) -> None:
        self._sensors.pop(sensor_id, None)

    def get(self, sensor_id: str) -> Optional[AbstractSensor]:
        return self._sensors.get(sensor_id)

    def read_all(self) -> list[SensorReading]:
        readings: list[SensorReading] = []
        for sensor in self._sensors.values():
            if sensor.is_initialized:
                try:
                    readings.append(sensor.read())
                except Exception:
                    pass
        return readings

    def initialize_all(self) -> dict[str, bool]:
        return {
            sid: sensor.initialize()
            for sid, sensor in self._sensors.items()
        }

    def shutdown_all(self) -> None:
        for sensor in self._sensors.values():
            try:
                sensor.shutdown()
            except Exception:
                pass

    def list_sensors(self) -> list[str]:
        return list(self._sensors.keys())


# ---------------------------------------------------------------------------
# Mock Sensor
# ---------------------------------------------------------------------------

class MockSensor(AbstractSensor):
    """Mock sensor that generates realistic synthetic data using sine waves + noise."""

    # (min, max, unit, noise_std)
    MOCK_RANGES: dict[SensorType, tuple[float, float, str, float]] = {
        SensorType.TEMPERATURE:      (15.0,   35.0,   "°C",   0.5),
        SensorType.HUMIDITY:         (30.0,   90.0,   "%RH",  1.0),
        SensorType.PH:               (4.0,    9.0,    "pH",   0.05),
        SensorType.DISSOLVED_OXYGEN: (2.0,    12.0,   "mg/L", 0.1),
        SensorType.TURBIDITY:        (0.0,    100.0,  "NTU",  2.0),
        SensorType.CO2:              (300.0,  2000.0, "ppm",  10.0),
        SensorType.METHANE:          (0.0,    50.0,   "ppm",  0.5),
        SensorType.FLOW_RATE:        (0.0,    100.0,  "L/min",0.5),
        SensorType.PRESSURE:         (0.9,    1.2,    "atm",  0.01),
        SensorType.MOISTURE:         (5.0,    80.0,   "%",    1.0),
        SensorType.SOLAR_IRRADIANCE: (0.0,    1200.0, "W/m²", 10.0),
        SensorType.WIND_SPEED:       (0.0,    30.0,   "m/s",  0.1),
        SensorType.POWER_OUTPUT:     (0.0,    5000.0, "W",    50.0),
    }

    def __init__(self, config: SensorConfig, seed: int = None) -> None:
        super().__init__(config)
        self._rng = random.Random(seed)
        self._start_time: float = time.time()
        self._period_s: float = 120.0  # sine wave period

    def initialize(self) -> bool:
        self._initialized = True
        self._start_time = time.time()
        return True

    def read(self) -> SensorReading:
        sensor_type = self.config.sensor_type
        lo, hi, unit, noise_std = self.MOCK_RANGES.get(
            sensor_type,
            (0.0, 100.0, "units", 1.0),
        )

        # Sine-wave base value oscillating across the full range
        elapsed = time.time() - self._start_time
        phase = (2.0 * math.pi * elapsed) / self._period_s
        mid = (lo + hi) / 2.0
        amplitude = (hi - lo) / 2.0
        base_value = mid + amplitude * 0.6 * math.sin(phase)

        # Gaussian noise
        noise = self._rng.gauss(0.0, noise_std)
        raw_value = base_value + noise + self.config.calibration_offset

        # Clamp to valid range
        value = max(lo, min(hi, raw_value))

        # Quality varies slightly
        quality = max(0.8, min(1.0, 1.0 - abs(self._rng.gauss(0.0, 0.05))))

        reading = SensorReading(
            sensor_id=self.config.sensor_id,
            timestamp=datetime.now(),
            value=round(value, 4),
            unit=unit,
            quality=round(quality, 3),
        )
        self._last_reading = reading
        return reading

    def calibrate(self, reference_value: float) -> None:
        if self._last_reading is not None:
            self.config.calibration_offset += reference_value - self._last_reading.value

    def shutdown(self) -> None:
        self._initialized = False
