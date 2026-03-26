"""Smart irrigation system with AI-optimized scheduling."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

try:
    import numpy as np
    _NP = True
except ImportError:
    _NP = False


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SoilMoistureZone:
    """A single irrigation zone with soil moisture state."""
    zone_id: str
    crop_type: str
    area_m2: float
    current_moisture_pct: float
    target_moisture_pct: float
    last_irrigated: datetime = field(default_factory=datetime.now)


@dataclass
class IrrigationSchedule:
    """A single irrigation event for one zone."""
    zone_id: str
    start_time: datetime
    duration_minutes: float
    water_volume_liters: float


@dataclass
class WeatherForecast:
    """Weather forecast data used for ET0 calculations."""
    temperature_c: float
    rainfall_mm: float
    humidity_pct: float
    wind_speed_ms: float
    solar_radiation_wm2: float
    forecast_date: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# IrrigationController
# ---------------------------------------------------------------------------

class IrrigationController:
    """Manages multiple irrigation zones and schedules watering events."""

    def __init__(self) -> None:
        """Initialise controller with an empty zones registry."""
        self._zones: dict[str, SoilMoistureZone] = {}
        self._schedule_history: list[IrrigationSchedule] = []
        self._total_water_applied_l: float = 0.0

    def add_zone(self, zone: SoilMoistureZone) -> None:
        """Register a new irrigation zone."""
        self._zones[zone.zone_id] = zone

    def update_soil_moisture(self, zone_id: str, moisture_pct: float) -> None:
        """Update the current soil moisture reading for a zone."""
        if zone_id in self._zones:
            self._zones[zone_id].current_moisture_pct = moisture_pct

    def calculate_water_need(
        self, zone_id: str, forecast: WeatherForecast
    ) -> float:
        """Estimate litres of water needed for a zone using a simplified
        Penman-Monteith ET0 formula.

        Returns 0.0 if the zone already meets or exceeds its target moisture
        or if expected rainfall is sufficient.
        """
        if zone_id not in self._zones:
            return 0.0

        zone = self._zones[zone_id]
        moisture_deficit = max(0.0, zone.target_moisture_pct - zone.current_moisture_pct)

        T = forecast.temperature_c
        u2 = forecast.wind_speed_ms
        RH = forecast.humidity_pct / 100.0
        Rn = forecast.solar_radiation_wm2 * 0.0864  # W/m² → MJ/m²/day

        # Saturation vapour pressure (kPa)
        es = 0.6108 * math.exp(17.27 * T / (T + 237.3))
        ea = es * RH
        delta = 4098.0 * es / ((T + 237.3) ** 2)
        gamma = 0.0665  # psychrometric constant kPa/°C

        denom = delta + gamma * (1 + 0.34 * u2)
        if denom == 0:
            et0 = 0.0
        else:
            et0 = (0.408 * delta * Rn + gamma * (900.0 / (T + 273.0)) * u2 * (es - ea)) / denom

        et0 = max(0.0, et0)  # mm/day

        # Effective rainfall reduces irrigation need
        effective_rain = forecast.rainfall_mm * 0.8
        net_need_mm = max(0.0, et0 - effective_rain)

        # Scale by moisture deficit (0 = fully irrigated, 1 = dry)
        deficit_factor = moisture_deficit / 100.0

        water_need_liters = net_need_mm * zone.area_m2 * deficit_factor
        return round(water_need_liters, 2)

    def generate_schedule(
        self, forecast: WeatherForecast
    ) -> list[IrrigationSchedule]:
        """Generate an AI-optimised irrigation schedule for all zones.

        Zones with greater water need are scheduled first.  Returns a list
        of IrrigationSchedule events.
        """
        schedules: list[IrrigationSchedule] = []
        start = datetime.now().replace(hour=5, minute=0, second=0, microsecond=0)
        offset_minutes = 0.0

        # Sort by water need descending
        needs = [
            (zid, self.calculate_water_need(zid, forecast))
            for zid in self._zones
        ]
        needs.sort(key=lambda x: x[1], reverse=True)

        for zone_id, liters in needs:
            if liters <= 0.0:
                continue
            flow_rate_lpm = 10.0  # 10 litres per minute
            duration = liters / flow_rate_lpm
            schedule = IrrigationSchedule(
                zone_id=zone_id,
                start_time=start + timedelta(minutes=offset_minutes),
                duration_minutes=round(duration, 2),
                water_volume_liters=round(liters, 2),
            )
            schedules.append(schedule)
            self._schedule_history.append(schedule)
            self._total_water_applied_l += liters
            offset_minutes += duration + 5.0  # 5-min gap between zones

        return schedules

    def estimate_water_savings(
        self, traditional_l: float, smart_l: float
    ) -> dict[str, float]:
        """Compare smart irrigation water use against traditional scheduling.

        Returns a dict with savings metrics.
        """
        saved = max(0.0, traditional_l - smart_l)
        pct = (saved / traditional_l * 100.0) if traditional_l > 0 else 0.0
        return {
            "traditional_liters": traditional_l,
            "smart_liters": smart_l,
            "saved_liters": round(saved, 2),
            "savings_percent": round(pct, 2),
            "cost_saved_usd": round(saved * 0.001, 4),  # ~$0.001/L
        }

    def monthly_water_report(self) -> dict[str, Any]:
        """Generate a monthly water usage summary.

        Returns a dict with total events, total water applied, and zone summary.
        """
        zone_totals: dict[str, float] = {}
        for sch in self._schedule_history:
            zone_totals[sch.zone_id] = (
                zone_totals.get(sch.zone_id, 0.0) + sch.water_volume_liters
            )
        return {
            "total_events": len(self._schedule_history),
            "total_water_applied_liters": round(self._total_water_applied_l, 2),
            "water_per_zone": zone_totals,
            "active_zones": len(self._zones),
        }
