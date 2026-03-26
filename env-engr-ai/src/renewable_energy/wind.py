"""
Wind turbine monitoring with power curve model and predictive maintenance.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from src.models.neural_network import AdaptiveNeuralNetwork
from src.models.schemas import RenewableEnergyMetrics


class WindTurbineMonitor:
    """
    Monitors wind turbine performance.
    Uses power curve model: P = 0.5 * rho * A * Cp * v³
    Cp_max (Betz limit) = 0.593
    Cut-in: 3 m/s, Rated: 12 m/s, Cut-out: 25 m/s
    """

    RHO_AIR = 1.225       # kg/m³ at sea level, 15°C
    CP_MAX = 0.40         # Practical Cp (below Betz 0.593)
    CUT_IN = 3.0          # m/s
    RATED_SPEED = 12.0    # m/s
    CUT_OUT = 25.0        # m/s

    def __init__(
        self,
        turbine_id: str,
        rated_power_w: float = 5000.0,
        rotor_diameter_m: float = 5.0,
        sampling_interval_s: float = 1800.0,  # Default: 30-minute intervals
    ) -> None:
        self.turbine_id = turbine_id
        self.rated_power_w = rated_power_w
        self.rotor_diameter_m = rotor_diameter_m
        self.rotor_area_m2 = math.pi * (rotor_diameter_m / 2.0) ** 2
        self.sampling_interval_s = sampling_interval_s

        self._history: list[RenewableEnergyMetrics] = []

        # Predictive maintenance NN: [power, capacity_factor, vibration, rpm, age_h] -> [fault_prob]
        self._maint_model = AdaptiveNeuralNetwork(
            layer_sizes=[5, 10, 6, 1],
            activations=["relu", "relu", "sigmoid"],
            learning_rate=0.005,
        )
        self._pretrain_maintenance_model()

    def _pretrain_maintenance_model(self) -> None:
        rng = np.random.default_rng(3)
        X, y = [], []
        for _ in range(200):
            power_ratio = rng.uniform(0, 1)
            cf = rng.uniform(0, 1)
            vibration = rng.uniform(0, 10)  # mm/s RMS
            rpm = rng.uniform(0, 200)
            age_h = rng.uniform(0, 43800)  # 0–5 years

            # Fault probability increases with age and vibration
            fault_prob = (
                0.1 * (age_h / 43800) +
                0.4 * min(1.0, vibration / 5.0) +
                0.2 * (1.0 - power_ratio) +
                rng.uniform(0, 0.1)
            )
            fault_prob = min(1.0, max(0.0, fault_prob))
            X.append([power_ratio, cf, vibration / 10, rpm / 200, age_h / 43800])
            y.append([fault_prob])

        self._maint_model.train(np.array(X), np.array(y), epochs=30, verbose=False)

    def update(self, metrics: RenewableEnergyMetrics) -> dict[str, Any]:
        """Update with new metrics reading."""
        self._history.append(metrics)
        wind_speed = metrics.metadata.get("wind_speed", 0.0)
        theoretical = self.power_curve(wind_speed)
        faults = self.detect_faults(metrics)

        return {
            "turbine_id": self.turbine_id,
            "wind_speed_ms": wind_speed,
            "power_w": metrics.power_output_w,
            "theoretical_power_w": round(theoretical, 1),
            "capacity_factor": metrics.capacity_factor,
            "efficiency_vs_curve": (
                round(metrics.power_output_w / theoretical, 3) if theoretical > 0 else 0.0
            ),
            "faults": faults,
            "health": "OK" if not faults else "FAULT",
        }

    def power_curve(self, wind_speed_ms: float) -> float:
        """
        Calculate theoretical power output from wind speed.
        Uses Betz limit (Cp_max = 0.593) with practical adjustment.
        """
        if wind_speed_ms < self.CUT_IN or wind_speed_ms > self.CUT_OUT:
            return 0.0

        # Cubic region: below rated speed
        if wind_speed_ms <= self.RATED_SPEED:
            # Smooth cubic curve capped at rated power
            cp = self.CP_MAX * min(1.0, (wind_speed_ms / self.RATED_SPEED) ** 0.5)
            power = 0.5 * self.RHO_AIR * self.rotor_area_m2 * cp * wind_speed_ms ** 3
            return min(self.rated_power_w, power)

        # Flat region: above rated speed (pitch control)
        return self.rated_power_w

    def detect_faults(self, metrics: RenewableEnergyMetrics) -> list[str]:
        """Detect: over-speed, vibration anomaly, blade imbalance, yaw error."""
        faults: list[str] = []
        wind_speed = metrics.metadata.get("wind_speed", 0.0)
        rpm = metrics.metadata.get("rpm", 0.0)
        vibration = metrics.metadata.get("vibration_mms", 0.0)

        if wind_speed > self.CUT_OUT:
            faults.append(f"OVER_SPEED: Wind {wind_speed:.1f} m/s exceeds cut-out {self.CUT_OUT} m/s")

        if vibration > 5.0:
            faults.append(f"VIBRATION_ANOMALY: {vibration:.2f} mm/s RMS exceeds 5.0 mm/s limit")

        if wind_speed >= self.CUT_IN:
            theoretical = self.power_curve(wind_speed)
            if theoretical > 0 and metrics.power_output_w < theoretical * 0.5:
                faults.append("BLADE_IMBALANCE or YAW_ERROR: Output < 50% of theoretical")

        # RPM over-speed detection
        if rpm > 0:
            rated_rpm = 150.0
            if rpm > rated_rpm * 1.2:
                faults.append(f"ROTOR_OVER_SPEED: {rpm:.0f} RPM exceeds rated {rated_rpm:.0f} RPM by >20%")

        return faults

    def predict_maintenance(
        self, history: list[RenewableEnergyMetrics]
    ) -> dict[str, Any]:
        """Predictive maintenance using neural network."""
        if not history:
            return {"fault_probability": 0.0, "recommendation": "No data available"}

        recent = history[-min(10, len(history)):]
        power_ratios = [m.power_output_w / self.rated_power_w for m in recent]
        cfs = [m.capacity_factor for m in recent]
        vibrations = [m.metadata.get("vibration_mms", 0.0) for m in recent]
        rpms = [m.metadata.get("rpm", 0.0) for m in recent]
        age_h = float(len(history) * self.sampling_interval_s / 3600.0)

        features = np.array([[
            float(np.mean(power_ratios)),
            float(np.mean(cfs)),
            min(float(np.mean(vibrations)) / 10, 1.0),
            min(float(np.mean(rpms)) / 200, 1.0),
            min(age_h / 43800, 1.0),
        ]])
        fault_prob = float(self._maint_model.predict(features)[0, 0])

        if fault_prob > 0.7:
            rec = "URGENT: Schedule maintenance within 1 week"
        elif fault_prob > 0.4:
            rec = "ADVISORY: Plan inspection within 1 month"
        else:
            rec = "Normal – next scheduled maintenance on time"

        return {
            "fault_probability": round(fault_prob, 4),
            "recommendation": rec,
            "avg_power_ratio": round(float(np.mean(power_ratios)), 3),
            "avg_vibration": round(float(np.mean(vibrations)), 3),
        }

    def calculate_capacity_factor(self, power_w: float) -> float:
        """Capacity factor = actual output / rated power."""
        return max(0.0, min(1.0, power_w / self.rated_power_w))
