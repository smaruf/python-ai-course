"""
Data persistence: file-based (CSV/JSON) and in-memory circular buffer.
"""
from __future__ import annotations

import abc
import csv
import json
import os
from collections import deque
from datetime import datetime
from typing import Optional

from src.models.schemas import SensorReading


class DataStore(abc.ABC):
    """Abstract base class for sensor data stores."""

    @abc.abstractmethod
    def store_reading(self, reading: SensorReading) -> None: ...

    @abc.abstractmethod
    def get_readings(
        self, sensor_id: str, limit: int = 100
    ) -> list[SensorReading]: ...

    @abc.abstractmethod
    def export_csv(self, filepath: str, sensor_id: Optional[str] = None) -> None: ...

    @abc.abstractmethod
    def export_json(self, filepath: str, sensor_id: Optional[str] = None) -> None: ...


class LocalDataStore(DataStore):
    """File-based data persistence using CSV files per sensor."""

    def __init__(self, data_dir: str = "data") -> None:
        self._data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _filepath(self, sensor_id: str) -> str:
        safe_id = sensor_id.replace("/", "_").replace("\\", "_")
        return os.path.join(self._data_dir, f"{safe_id}.csv")

    def store_reading(self, reading: SensorReading) -> None:
        filepath = self._filepath(reading.sensor_id)
        file_exists = os.path.isfile(filepath)
        with open(filepath, "a", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["reading_id", "sensor_id", "timestamp",
                               "value", "unit", "quality"]
            )
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "reading_id": reading.reading_id,
                "sensor_id": reading.sensor_id,
                "timestamp": reading.timestamp.isoformat(),
                "value": reading.value,
                "unit": reading.unit,
                "quality": reading.quality,
            })

    def get_readings(
        self, sensor_id: str, limit: int = 100
    ) -> list[SensorReading]:
        filepath = self._filepath(sensor_id)
        if not os.path.isfile(filepath):
            return []
        readings: list[SensorReading] = []
        with open(filepath, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                readings.append(SensorReading(
                    reading_id=row["reading_id"],
                    sensor_id=row["sensor_id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    value=float(row["value"]),
                    unit=row["unit"],
                    quality=float(row["quality"]),
                ))
        return readings[-limit:]

    def export_csv(self, filepath: str, sensor_id: Optional[str] = None) -> None:
        all_readings = self._collect_all(sensor_id)
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["reading_id", "sensor_id", "timestamp",
                               "value", "unit", "quality"]
            )
            writer.writeheader()
            for r in all_readings:
                writer.writerow({
                    "reading_id": r.reading_id,
                    "sensor_id": r.sensor_id,
                    "timestamp": r.timestamp.isoformat(),
                    "value": r.value,
                    "unit": r.unit,
                    "quality": r.quality,
                })

    def export_json(self, filepath: str, sensor_id: Optional[str] = None) -> None:
        all_readings = self._collect_all(sensor_id)
        data = [
            {
                "reading_id": r.reading_id,
                "sensor_id": r.sensor_id,
                "timestamp": r.timestamp.isoformat(),
                "value": r.value,
                "unit": r.unit,
                "quality": r.quality,
            }
            for r in all_readings
        ]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def _collect_all(self, sensor_id: Optional[str]) -> list[SensorReading]:
        if sensor_id:
            return self.get_readings(sensor_id, limit=10000)
        readings: list[SensorReading] = []
        for fname in os.listdir(self._data_dir):
            if fname.endswith(".csv"):
                sid = fname[:-4]
                readings.extend(self.get_readings(sid, limit=10000))
        readings.sort(key=lambda r: r.timestamp)
        return readings


class TimeSeriesBuffer(DataStore):
    """In-memory circular buffer for recent sensor readings."""

    def __init__(self, max_size: int = 1000) -> None:
        self._buffer: deque[SensorReading] = deque(maxlen=max_size)
        self._by_sensor: dict[str, deque[SensorReading]] = {}
        self._max_size = max_size

    def store_reading(self, reading: SensorReading) -> None:
        self._buffer.append(reading)
        if reading.sensor_id not in self._by_sensor:
            self._by_sensor[reading.sensor_id] = deque(maxlen=self._max_size)
        self._by_sensor[reading.sensor_id].append(reading)

    def get_readings(
        self, sensor_id: str, limit: int = 100
    ) -> list[SensorReading]:
        sensor_readings = self._by_sensor.get(sensor_id, deque())
        return list(sensor_readings)[-limit:]

    def get_all_recent(self, limit: int = 100) -> list[SensorReading]:
        return list(self._buffer)[-limit:]

    def export_csv(self, filepath: str, sensor_id: Optional[str] = None) -> None:
        readings = (
            self.get_readings(sensor_id, limit=10000) if sensor_id
            else list(self._buffer)
        )
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["reading_id", "sensor_id", "timestamp",
                               "value", "unit", "quality"]
            )
            writer.writeheader()
            for r in readings:
                writer.writerow({
                    "reading_id": r.reading_id,
                    "sensor_id": r.sensor_id,
                    "timestamp": r.timestamp.isoformat(),
                    "value": r.value,
                    "unit": r.unit,
                    "quality": r.quality,
                })

    def export_json(self, filepath: str, sensor_id: Optional[str] = None) -> None:
        readings = (
            self.get_readings(sensor_id, limit=10000) if sensor_id
            else list(self._buffer)
        )
        data = [
            {
                "reading_id": r.reading_id,
                "sensor_id": r.sensor_id,
                "timestamp": r.timestamp.isoformat(),
                "value": r.value,
                "unit": r.unit,
                "quality": r.quality,
            }
            for r in readings
        ]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def __len__(self) -> int:
        return len(self._buffer)
