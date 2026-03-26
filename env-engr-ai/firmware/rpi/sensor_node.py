#!/usr/bin/env python3
"""
Raspberry Pi sensor node firmware.
Reads sensors, sends data to PC via HTTP POST, with auto-reconnect.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime

# Allow running from firmware/rpi directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False

try:
    from rich.console import Console
    console = Console()
    def log(level: str, msg: str) -> None:
        styles = {"INFO": "green", "WARN": "yellow", "ERROR": "red"}
        style = styles.get(level, "white")
        ts = datetime.now().strftime("%H:%M:%S")
        console.print(f"[{style}][{level}][/{style}] {ts} {msg}")
except ImportError:
    def log(level: str, msg: str) -> None:  # type: ignore
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{level}] {ts} {msg}")

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------
PC_URL = os.getenv("PC_URL", "http://192.168.1.100:8000/readings")
SEND_INTERVAL = float(os.getenv("SEND_INTERVAL", "5.0"))
HEARTBEAT_INTERVAL = 30.0
NODE_ID = os.getenv("NODE_ID", "rpi_node_01")

# Sensor configs: comma-separated list of "sensor_type:gpio_pin"
SENSORS_ENV = os.getenv("SENSORS", "temperature:4,humidity:4,co2:0")


def parse_sensor_configs() -> list[dict]:
    """Parse SENSORS env variable into list of sensor configs."""
    configs: list[dict] = []
    for entry in SENSORS_ENV.split(","):
        parts = entry.strip().split(":")
        if len(parts) >= 1:
            configs.append({
                "sensor_type": parts[0].strip().upper(),
                "gpio_pin": int(parts[1]) if len(parts) > 1 else 0,
                "sensor_id": f"{parts[0].strip().lower()}_{NODE_ID}",
            })
    return configs


def create_sensors(configs: list[dict]) -> list:
    """Instantiate sensor objects based on config."""
    from src.models.schemas import SensorConfig, SensorType
    from src.sensors.rpi_sensors import DHT22Sensor, MQ135Sensor, PHSensor
    from src.sensors.base import MockSensor

    sensors = []
    for cfg in configs:
        try:
            sensor_type = SensorType(cfg["sensor_type"])
        except ValueError:
            sensor_type = SensorType.TEMPERATURE

        sc = SensorConfig(
            sensor_id=cfg["sensor_id"],
            sensor_type=sensor_type,
            location=NODE_ID,
        )
        if cfg["sensor_type"] in ("TEMPERATURE", "HUMIDITY"):
            sensor = DHT22Sensor(sc, gpio_pin=cfg.get("gpio_pin", 4))
        elif cfg["sensor_type"] == "CO2":
            sensor = MQ135Sensor(sc, adc_channel=cfg.get("gpio_pin", 0))
        elif cfg["sensor_type"] == "PH":
            sensor = PHSensor(sc)
        else:
            sensor = MockSensor(sc)
        sensors.append(sensor)
    return sensors


def send_reading(reading_data: dict, retries: int = 3) -> bool:
    """POST a reading to the PC server. Returns True on success."""
    if not _HTTPX_AVAILABLE:
        log("WARN", f"httpx not available – would send: {reading_data}")
        return True
    for attempt in range(retries):
        try:
            resp = httpx.post(PC_URL, json=reading_data, timeout=5.0)
            if resp.status_code in (200, 201):
                return True
            log("WARN", f"Server returned {resp.status_code}")
        except Exception as e:
            if attempt < retries - 1:
                log("WARN", f"Send failed (attempt {attempt+1}): {e} – retrying")
                time.sleep(1.0)
            else:
                log("ERROR", f"Send failed after {retries} attempts: {e}")
    return False


def main() -> None:
    log("INFO", f"Starting sensor node {NODE_ID}")
    log("INFO", f"PC URL: {PC_URL}")
    log("INFO", f"Send interval: {SEND_INTERVAL}s")

    sensor_configs = parse_sensor_configs()
    sensors = create_sensors(sensor_configs)

    log("INFO", f"Initializing {len(sensors)} sensors...")
    for sensor in sensors:
        ok = sensor.initialize()
        status = "OK" if ok else "MOCK fallback"
        log("INFO", f"  {sensor.config.sensor_id}: {status}")

    last_heartbeat = 0.0
    consecutive_failures = 0

    while True:
        loop_start = time.time()

        # Heartbeat
        if time.time() - last_heartbeat >= HEARTBEAT_INTERVAL:
            heartbeat = {
                "type": "heartbeat",
                "node_id": NODE_ID,
                "timestamp": datetime.now().isoformat(),
                "sensor_count": len(sensors),
            }
            send_reading(heartbeat)
            last_heartbeat = time.time()
            log("INFO", f"Heartbeat sent")

        # Read and send each sensor
        for sensor in sensors:
            try:
                reading = sensor.read()
                payload = {
                    "type": "reading",
                    "reading_id": reading.reading_id,
                    "sensor_id": reading.sensor_id,
                    "timestamp": reading.timestamp.isoformat(),
                    "value": reading.value,
                    "unit": reading.unit,
                    "quality": reading.quality,
                    "node_id": NODE_ID,
                }
                success = send_reading(payload)
                if success:
                    log("INFO", f"{reading.sensor_id}: {reading.value:.3f} {reading.unit}")
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
            except Exception as e:
                log("ERROR", f"Error reading {sensor.config.sensor_id}: {e}")
                consecutive_failures += 1

        # Exponential back-off on many failures
        if consecutive_failures > 10:
            backoff = min(60.0, 2.0 ** (consecutive_failures - 10))
            log("WARN", f"Too many failures – backing off {backoff:.1f}s")
            time.sleep(backoff)

        elapsed = time.time() - loop_start
        sleep_time = max(0.0, SEND_INTERVAL - elapsed)
        time.sleep(sleep_time)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("INFO", "Sensor node shutdown")
