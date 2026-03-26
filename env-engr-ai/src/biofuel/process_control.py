"""
PID controller and biofuel process controller with safety interlocks.
"""
from __future__ import annotations

from typing import Any

from src.models.schemas import BiofuelMetrics


class PIDController:
    """Generic PID controller with anti-windup and output clamping."""

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        setpoint: float,
        output_min: float = 0.0,
        output_max: float = 100.0,
    ) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.output_min = output_min
        self.output_max = output_max

        self._integral = 0.0
        self._prev_error = 0.0
        self._initialized = False

    def compute(self, measured_value: float, dt: float = 1.0) -> float:
        """Compute PID output. Returns clamped output."""
        error = self.setpoint - measured_value

        # Anti-windup: only integrate when output not saturated
        proposed_output = self.kp * error
        if self.output_min < proposed_output < self.output_max:
            self._integral += error * dt

        # Derivative (avoid derivative kick on setpoint change)
        if self._initialized:
            derivative = (error - self._prev_error) / max(dt, 1e-6)
        else:
            derivative = 0.0
            self._initialized = True

        output = self.kp * error + self.ki * self._integral + self.kd * derivative
        self._prev_error = error

        return max(self.output_min, min(self.output_max, output))

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0
        self._initialized = False

    def set_setpoint(self, setpoint: float) -> None:
        self.setpoint = setpoint


class BiofuelProcessController:
    """
    Manages multiple PIDs for biofuel production.
    Controls: temperature, pH, feed rate.
    Implements safety interlocks.
    """

    SAFETY_LIMITS: dict[str, tuple[float, float]] = {
        "temperature": (10.0, 55.0),
        "ph": (2.0, 12.0),
        "pressure": (0.0, 5.0),
    }

    def __init__(self) -> None:
        self._temperature_pid = PIDController(
            kp=2.0, ki=0.05, kd=0.5,
            setpoint=32.0,
            output_min=0.0, output_max=100.0,
        )
        self._ph_pid = PIDController(
            kp=5.0, ki=0.1, kd=1.0,
            setpoint=4.8,
            output_min=-100.0, output_max=100.0,
        )
        self._feed_rate_pid = PIDController(
            kp=1.0, ki=0.02, kd=0.1,
            setpoint=10.0,  # g/L target sugar
            output_min=0.0, output_max=100.0,
        )
        self._emergency_stopped = False
        self._dt = 1.0

    def update(self, metrics: BiofuelMetrics) -> dict[str, float]:
        """Compute all control outputs."""
        if self._emergency_stopped:
            return {"heater_power": 0.0, "acid_pump": 0.0, "base_pump": 0.0,
                    "feed_rate": 0.0, "emergency_stop": 1.0}

        violations = self.check_safety_interlocks(metrics)
        if violations:
            self.emergency_stop()
            return {"heater_power": 0.0, "acid_pump": 0.0, "base_pump": 0.0,
                    "feed_rate": 0.0, "emergency_stop": 1.0,
                    "violations": len(violations)}

        temp_out = self._temperature_pid.compute(metrics.temperature, self._dt)
        ph_out = self._ph_pid.compute(metrics.ph, self._dt)
        feed_out = self._feed_rate_pid.compute(metrics.sugar_content, self._dt)

        heater_power = max(0.0, temp_out)
        cooler_power = max(0.0, -temp_out)
        acid_pump = max(0.0, -ph_out)
        base_pump = max(0.0, ph_out)

        return {
            "heater_power": round(heater_power, 2),
            "cooler_power": round(cooler_power, 2),
            "acid_pump": round(acid_pump, 2),
            "base_pump": round(base_pump, 2),
            "feed_rate": round(feed_out, 2),
            "emergency_stop": 0.0,
        }

    def check_safety_interlocks(self, metrics: BiofuelMetrics) -> list[str]:
        """Return list of violated safety conditions."""
        violations: list[str] = []
        checks = {
            "temperature": metrics.temperature,
            "ph": metrics.ph,
        }
        for param, value in checks.items():
            lo, hi = self.SAFETY_LIMITS[param]
            if not (lo <= value <= hi):
                violations.append(
                    f"{param}={value:.2f} outside safety range [{lo}, {hi}]"
                )
        return violations

    def emergency_stop(self) -> None:
        """Activate emergency stop: cut all outputs."""
        self._emergency_stopped = True
        self._temperature_pid.reset()
        self._ph_pid.reset()
        self._feed_rate_pid.reset()

    def reset_emergency_stop(self) -> None:
        self._emergency_stopped = False

    def set_temperature_setpoint(self, sp: float) -> None:
        self._temperature_pid.set_setpoint(sp)

    def set_ph_setpoint(self, sp: float) -> None:
        self._ph_pid.set_setpoint(sp)

    def is_emergency_stopped(self) -> bool:
        return self._emergency_stopped
