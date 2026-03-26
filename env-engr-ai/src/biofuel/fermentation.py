"""
Fermentation process monitoring and control.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from src.models.neural_network import AdaptiveNeuralNetwork
from src.models.schemas import BiofuelMetrics, FermentationStage


class FermentationMonitor:
    """
    Monitors bioethanol/biogas fermentation process.
    Tracks: temperature, pH, sugar content, CO2 rate, ethanol yield.
    Stages: INOCULATION -> EXPONENTIAL -> STATIONARY -> DECLINE
    """

    OPTIMAL_RANGES: dict[FermentationStage, dict[str, tuple[float, float]]] = {
        FermentationStage.INOCULATION: {
            "temperature": (28.0, 32.0),
            "ph": (4.5, 5.5),
            "sugar_content": (15.0, 20.0),
            "co2_rate": (0.0, 5.0),
        },
        FermentationStage.EXPONENTIAL: {
            "temperature": (30.0, 35.0),
            "ph": (4.0, 5.0),
            "sugar_content": (5.0, 15.0),
            "co2_rate": (10.0, 50.0),
        },
        FermentationStage.STATIONARY: {
            "temperature": (28.0, 33.0),
            "ph": (3.8, 4.8),
            "sugar_content": (1.0, 5.0),
            "co2_rate": (2.0, 10.0),
        },
        FermentationStage.DECLINE: {
            "temperature": (25.0, 32.0),
            "ph": (3.5, 4.5),
            "sugar_content": (0.0, 1.0),
            "co2_rate": (0.0, 2.0),
        },
    }

    def __init__(self, batch_id: str) -> None:
        self.batch_id = batch_id
        self._history: list[BiofuelMetrics] = []
        self._current_stage = FermentationStage.INOCULATION
        # NN for yield prediction: [temp, ph, sugar, co2_rate, ethanol, time_h] -> [yield]
        self._yield_predictor = AdaptiveNeuralNetwork(
            layer_sizes=[6, 12, 6, 1],
            activations=["relu", "relu", "sigmoid"],
            learning_rate=0.005,
        )
        self._pretrain_yield_predictor()

    def _pretrain_yield_predictor(self) -> None:
        rng = np.random.default_rng(1)
        X, y = [], []
        for _ in range(300):
            temp = rng.uniform(25, 40)
            ph = rng.uniform(3.5, 6.0)
            sugar = rng.uniform(0, 20)
            co2 = rng.uniform(0, 50)
            ethanol = rng.uniform(0, 15)
            time_h = rng.uniform(0, 72)
            # Empirical yield: best around temp=32, ph=4.5, decreases with distance
            theoretical_yield = (
                0.511 * (20.0 - sugar) * 0.85
                * np.exp(-0.001 * (temp - 32) ** 2)
                * np.exp(-0.5 * (ph - 4.5) ** 2)
            )
            theoretical_yield = max(0.0, min(15.0, theoretical_yield))
            features = np.array([temp / 40, ph / 14, sugar / 20,
                                   co2 / 50, ethanol / 15, time_h / 72])
            X.append(features)
            y.append([theoretical_yield / 15.0])
        self._yield_predictor.train(np.array(X), np.array(y), epochs=30, verbose=False)

    def update(self, metrics: BiofuelMetrics) -> dict[str, Any]:
        """Process new metrics reading, return status dict."""
        self._history.append(metrics)
        self._current_stage = self.detect_stage(metrics)

        deviations = {}
        ranges = self.OPTIMAL_RANGES[self._current_stage]
        for param, (lo, hi) in ranges.items():
            val = getattr(metrics, param, None)
            if val is not None and not (lo <= val <= hi):
                deviations[param] = {
                    "value": val,
                    "optimal_range": (lo, hi),
                    "deviation": min(abs(val - lo), abs(val - hi)),
                }

        return {
            "batch_id": self.batch_id,
            "stage": self._current_stage.value,
            "deviations": deviations,
            "predicted_yield": self.predict_yield(metrics),
            "recommendations": self.get_recommendations(),
            "history_length": len(self._history),
        }

    def detect_stage(self, metrics: BiofuelMetrics) -> FermentationStage:
        """Automatically detect fermentation stage from metrics."""
        sugar = metrics.sugar_content
        co2 = metrics.co2_rate
        ethanol = metrics.ethanol_yield

        if sugar >= 14.0 and co2 < 5.0:
            return FermentationStage.INOCULATION
        elif co2 >= 10.0 and sugar > 3.0:
            return FermentationStage.EXPONENTIAL
        if sugar < 1.0 and co2 < 2.0:
            return FermentationStage.DECLINE
        elif co2 < 10.0 and sugar <= 3.0 and ethanol > 3.0:
            return FermentationStage.STATIONARY
        return self._current_stage

    def predict_yield(self, current_metrics: BiofuelMetrics) -> float:
        """Predict final ethanol yield using neural network."""
        time_h = len(self._history) * 0.5  # Assume 30-min sampling
        features = np.array([[
            current_metrics.temperature / 40,
            current_metrics.ph / 14,
            current_metrics.sugar_content / 20,
            current_metrics.co2_rate / 50,
            current_metrics.ethanol_yield / 15,
            min(time_h / 72, 1.0),
        ]])
        raw = float(self._yield_predictor.predict(features)[0, 0])
        return round(raw * 15.0, 3)  # De-normalise

    def get_recommendations(self) -> list[str]:
        """Get process optimisation recommendations."""
        if not self._history:
            return ["Awaiting first reading"]
        latest = self._history[-1]
        recs: list[str] = []
        ranges = self.OPTIMAL_RANGES[self._current_stage]

        temp_lo, temp_hi = ranges["temperature"]
        if latest.temperature < temp_lo:
            recs.append(f"Increase temperature to {temp_lo}–{temp_hi} °C (currently {latest.temperature:.1f} °C)")
        elif latest.temperature > temp_hi:
            recs.append(f"Decrease temperature to {temp_lo}–{temp_hi} °C (currently {latest.temperature:.1f} °C)")

        ph_lo, ph_hi = ranges["ph"]
        if latest.ph < ph_lo:
            recs.append(f"Increase pH to {ph_lo}–{ph_hi} (currently {latest.ph:.2f}) – add buffer")
        elif latest.ph > ph_hi:
            recs.append(f"Decrease pH to {ph_lo}–{ph_hi} (currently {latest.ph:.2f}) – add acid")

        sugar_lo, sugar_hi = ranges["sugar_content"]
        if latest.sugar_content < sugar_lo:
            recs.append(f"Consider adding substrate; sugar content low ({latest.sugar_content:.1f} g/L)")

        if not recs:
            recs.append("All parameters within optimal range – process running well")
        return recs

    @property
    def current_stage(self) -> FermentationStage:
        return self._current_stage


class FermentationController:
    """PID-based control of temperature and pH during fermentation."""

    def __init__(
        self,
        batch_id: str,
        target_temperature: float = 30.0,
        target_ph: float = 5.0,
    ) -> None:
        self.batch_id = batch_id
        self.target_temperature = target_temperature
        self.target_ph = target_ph

        # PID state for temperature
        self._temp_integral = 0.0
        self._temp_prev_error = 0.0
        # PID state for pH
        self._ph_integral = 0.0
        self._ph_prev_error = 0.0

        # PID tuning constants
        self._temp_Kp, self._temp_Ki, self._temp_Kd = 2.0, 0.1, 0.5
        self._ph_Kp, self._ph_Ki, self._ph_Kd = 5.0, 0.2, 1.0

    def _pid(
        self,
        error: float,
        integral: float,
        prev_error: float,
        Kp: float,
        Ki: float,
        Kd: float,
        dt: float = 1.0,
        integral_limit: float = 50.0,
    ) -> tuple[float, float, float]:
        """Compute PID output. Returns (output, new_integral, new_prev_error)."""
        integral = max(-integral_limit, min(integral_limit, integral + error * dt))
        derivative = (error - prev_error) / dt
        output = Kp * error + Ki * integral + Kd * derivative
        return output, integral, error

    def compute_control_actions(
        self, current_metrics: BiofuelMetrics
    ) -> dict[str, float]:
        """
        Return control outputs:
        - heater_power (%): positive = heat, 0 = off
        - acid_pump_rate (%): pump speed to lower pH
        - base_pump_rate (%): pump speed to raise pH
        """
        # Temperature PID
        temp_error = self.target_temperature - current_metrics.temperature
        temp_out, self._temp_integral, self._temp_prev_error = self._pid(
            temp_error, self._temp_integral, self._temp_prev_error,
            self._temp_Kp, self._temp_Ki, self._temp_Kd,
        )
        heater_power = max(0.0, min(100.0, temp_out))

        # pH PID
        ph_error = self.target_ph - current_metrics.ph
        ph_out, self._ph_integral, self._ph_prev_error = self._pid(
            ph_error, self._ph_integral, self._ph_prev_error,
            self._ph_Kp, self._ph_Ki, self._ph_Kd,
        )
        # Positive output → need to raise pH (base pump); negative → lower pH (acid pump)
        base_pump_rate = max(0.0, min(100.0, ph_out))
        acid_pump_rate = max(0.0, min(100.0, -ph_out))

        return {
            "heater_power": round(heater_power, 2),
            "acid_pump_rate": round(acid_pump_rate, 2),
            "base_pump_rate": round(base_pump_rate, 2),
        }
