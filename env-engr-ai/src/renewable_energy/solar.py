"""
Solar PV monitoring and MPPT control.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from src.models.schemas import EnergySource, RenewableEnergyMetrics


class SolarPanelMonitor:
    """
    Monitors solar PV system performance.
    Tracks: irradiance, panel temperature, power output, efficiency.
    Implements Perturb & Observe MPPT algorithm.
    """

    # Standard Test Conditions: 1000 W/m², 25°C
    STC_IRRADIANCE = 1000.0  # W/m²
    STC_TEMP = 25.0          # °C
    TEMP_COEFFICIENT = -0.0035  # Power loss per °C above STC (fraction/°C)

    def __init__(
        self,
        panel_id: str,
        rated_power_w: float = 400.0,
        panel_area_m2: float = 2.0,
    ) -> None:
        self.panel_id = panel_id
        self.rated_power_w = rated_power_w
        self.panel_area_m2 = panel_area_m2

        self._history: list[RenewableEnergyMetrics] = []
        self._mppt_voltage = 36.0   # Initial voltage guess (V)
        self._mppt_step = 0.5       # Perturbation step (V)
        self._prev_power = 0.0

    def update(self, metrics: RenewableEnergyMetrics) -> dict[str, Any]:
        """Update with new metrics reading."""
        self._history.append(metrics)
        irradiance = metrics.metadata.get("irradiance", 0.0)
        panel_temp = metrics.metadata.get("panel_temperature", 25.0)
        efficiency = self.calculate_efficiency(metrics.power_output_w, irradiance)
        faults = self.detect_faults(metrics)

        return {
            "panel_id": self.panel_id,
            "power_w": metrics.power_output_w,
            "efficiency": round(efficiency, 4),
            "capacity_factor": metrics.capacity_factor,
            "irradiance": irradiance,
            "panel_temperature": panel_temp,
            "faults": faults,
            "health": "OK" if not faults else "FAULT",
        }

    def mppt_algorithm(
        self, voltage: float, current: float, irradiance: float
    ) -> tuple[float, float]:
        """
        Perturb & Observe MPPT algorithm.
        Returns (optimal_voltage, optimal_current).
        """
        power = voltage * current
        # If power increased, continue in same direction; else reverse
        if power > self._prev_power:
            self._mppt_voltage += self._mppt_step
        else:
            self._mppt_step = -self._mppt_step
            self._mppt_voltage += self._mppt_step

        # Clamp to realistic range (20–50V for typical 400W panel)
        self._mppt_voltage = max(20.0, min(50.0, self._mppt_voltage))
        self._prev_power = power

        # Estimate optimal current at new voltage using simplified model
        voc = 48.0  # Open circuit voltage (V)
        isc = current * (1.0 + 0.01 * (irradiance / self.STC_IRRADIANCE - 1.0))
        optimal_current = isc * (1.0 - (self._mppt_voltage / voc) ** 20)
        optimal_current = max(0.0, optimal_current)

        return round(self._mppt_voltage, 2), round(optimal_current, 3)

    def detect_faults(self, metrics: RenewableEnergyMetrics) -> list[str]:
        """Detect: shading, hot spot, degradation, inverter fault."""
        faults: list[str] = []
        irradiance = metrics.metadata.get("irradiance", 0.0)
        panel_temp = metrics.metadata.get("panel_temperature", 25.0)

        if irradiance > 200.0:
            # Expected power with temperature correction
            temp_factor = 1.0 + self.TEMP_COEFFICIENT * (panel_temp - self.STC_TEMP)
            expected_power = self.rated_power_w * (irradiance / self.STC_IRRADIANCE) * temp_factor
            actual_power = metrics.power_output_w

            if actual_power < expected_power * 0.5:
                faults.append("SHADING: Output < 50% of expected for current irradiance")
            elif actual_power < expected_power * 0.8:
                faults.append("PARTIAL_SHADING or DEGRADATION: Output 50–80% of expected")

        if panel_temp > 70.0:
            faults.append(f"HOT_SPOT: Panel temperature {panel_temp:.1f}°C exceeds 70°C")

        if len(self._history) > 10:
            recent_powers = [m.power_output_w for m in self._history[-10:]]
            trend = np.polyfit(range(len(recent_powers)), recent_powers, 1)[0]
            if irradiance > 200.0 and trend < -5.0:
                faults.append("INVERTER_FAULT: Declining power trend detected")

        return faults

    def forecast_yield(self, forecast_irradiance: list[float]) -> list[float]:
        """Forecast hourly power output given irradiance forecast (W/m²)."""
        forecasts: list[float] = []
        for irr in forecast_irradiance:
            if irr <= 0:
                forecasts.append(0.0)
                continue
            # Simplified temperature model (panel heats up with irradiance)
            panel_temp = 25.0 + irr * 0.03
            temp_factor = 1.0 + self.TEMP_COEFFICIENT * (panel_temp - self.STC_TEMP)
            power = self.rated_power_w * (irr / self.STC_IRRADIANCE) * temp_factor
            forecasts.append(round(max(0.0, power), 1))
        return forecasts

    def calculate_efficiency(self, power_w: float, irradiance: float) -> float:
        """Calculate panel efficiency (fraction 0–1)."""
        if irradiance <= 0:
            return 0.0
        input_power = irradiance * self.panel_area_m2
        return min(1.0, max(0.0, power_w / input_power))
