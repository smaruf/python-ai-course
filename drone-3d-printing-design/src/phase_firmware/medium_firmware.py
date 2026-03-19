"""
Medium Firmware Module — Level 2

PID-based stabilisation flight controller with sensor fusion.
Equivalent to what ArduPilot / iNAV run on an F4/F7 flight controller.

This Python implementation is suitable for:
  • Raspberry Pi / Jetson Nano (Linux)
  • MicroPython on RP2040 / ESP32
  • Software-in-the-loop (SITL) simulation

Real hardware layer (not simulated here):
  • IMU : MPU-6000 / ICM-42688 via SPI
  • Baro : MS5611 / BMP388 via I2C
  • GPS  : u-blox M8N / M9N via UART
  • ESC  : DShot / PWM via hardware timer
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


# ---------------------------------------------------------------------------
# Data classes — sensor readings
# ---------------------------------------------------------------------------

@dataclass
class IMUData:
    """6-axis IMU reading (gyro + accelerometer)."""
    gyro_x: float = 0.0   # deg/s
    gyro_y: float = 0.0
    gyro_z: float = 0.0
    accel_x: float = 0.0  # m/s²
    accel_y: float = 0.0
    accel_z: float = -9.81  # gravity at rest


@dataclass
class AttitudeEstimate:
    """Estimated vehicle attitude after sensor fusion."""
    roll: float  = 0.0   # degrees, + = right bank
    pitch: float = 0.0   # degrees, + = nose up
    yaw: float   = 0.0   # degrees, 0 = North, 0–360


@dataclass
class PIDState:
    """Running state for a single PID controller axis."""
    kp: float
    ki: float
    kd: float
    i_limit: float = 400.0      # anti-windup clamp
    output_limit: float = 500.0 # maximum output (µs offset or %)

    _integral: float = field(default=0.0, init=False, repr=False)
    _prev_error: float = field(default=0.0, init=False, repr=False)

    def compute(self, setpoint: float, measured: float, dt: float) -> float:
        """
        Compute PID output.

        Parameters
        ----------
        setpoint : float  — desired value
        measured : float  — current measured value
        dt       : float  — loop time in seconds

        Returns
        -------
        float  — PID output (clamped to ±output_limit)
        """
        if dt <= 0:
            return 0.0

        error = setpoint - measured

        # Proportional
        p_term = self.kp * error

        # Integral with anti-windup
        self._integral += error * dt
        self._integral = max(-self.i_limit, min(self.i_limit, self._integral))
        i_term = self.ki * self._integral

        # Derivative (on measurement to avoid derivative kick on setpoint change)
        d_term = self.kd * (error - self._prev_error) / dt
        self._prev_error = error

        output = p_term + i_term + d_term
        return max(-self.output_limit, min(self.output_limit, output))

    def reset(self) -> None:
        """Reset integrator and derivative state (e.g., on disarm)."""
        self._integral = 0.0
        self._prev_error = 0.0


# ---------------------------------------------------------------------------
# Complementary filter — simple sensor fusion
# ---------------------------------------------------------------------------

class ComplementaryFilter:
    """
    Fuse gyroscope and accelerometer to estimate roll & pitch.

    alpha close to 1.0 → trust gyro (fast response, drifts over time)
    alpha close to 0.0 → trust accel (slow, noisy, but no drift)
    Typical alpha: 0.96–0.98 at 250 Hz loop rate.
    """

    def __init__(self, alpha: float = 0.98) -> None:
        self.alpha = alpha
        self.roll  = 0.0
        self.pitch = 0.0

    def update(self, imu: IMUData, dt: float) -> Tuple[float, float]:
        """
        Update attitude estimate.

        Returns
        -------
        (roll_deg, pitch_deg)
        """
        # Gyro integration (degrees)
        self.roll  += imu.gyro_x * dt
        self.pitch += imu.gyro_y * dt

        # Accelerometer angle
        if imu.accel_z != 0:
            accel_roll  = math.degrees(math.atan2(imu.accel_y, imu.accel_z))
            accel_pitch = math.degrees(math.atan2(-imu.accel_x,
                                                   math.sqrt(imu.accel_y ** 2
                                                             + imu.accel_z ** 2)))
        else:
            accel_roll  = self.roll
            accel_pitch = self.pitch

        # Fuse
        self.roll  = self.alpha * self.roll  + (1 - self.alpha) * accel_roll
        self.pitch = self.alpha * self.pitch + (1 - self.alpha) * accel_pitch

        return self.roll, self.pitch


# ---------------------------------------------------------------------------
# Flight modes
# ---------------------------------------------------------------------------

class FlightMode:
    ACRO     = "acro"      # rate control only (no auto-level)
    STABILISE = "stabilise" # auto-level (angle control)
    ALT_HOLD  = "alt_hold"  # stabilise + barometer altitude hold
    GPS_HOLD  = "gps_hold"  # stabilise + GPS position hold


# ---------------------------------------------------------------------------
# Medium-level flight controller
# ---------------------------------------------------------------------------

class MediumFlightController:
    """
    PID stabilisation controller with sensor fusion.

    Loop order (typical 500 Hz):
      1. Read IMU
      2. Update attitude estimate (complementary filter)
      3. Compute PID outputs for roll, pitch, yaw
      4. Mix + send to ESCs
    """

    # Default PID gains (tune for your aircraft)
    DEFAULT_GAINS: Dict[str, Dict[str, float]] = {
        "roll":  {"kp": 4.5, "ki": 0.04, "kd": 0.40},
        "pitch": {"kp": 4.5, "ki": 0.04, "kd": 0.40},
        "yaw":   {"kp": 6.0, "ki": 0.10, "kd": 0.20},
    }

    def __init__(self, motor_count: int = 4,
                 gains: Optional[Dict] = None,
                 loop_rate_hz: float = 500.0) -> None:
        g = gains or self.DEFAULT_GAINS
        self.roll_pid  = PIDState(**g["roll"])
        self.pitch_pid = PIDState(**g["pitch"])
        self.yaw_pid   = PIDState(**g["yaw"])

        self.filter    = ComplementaryFilter()
        self.attitude  = AttitudeEstimate()
        self.mode      = FlightMode.STABILISE
        self.motor_count = motor_count
        self.dt = 1.0 / loop_rate_hz
        self.armed = False

    def arm(self) -> None:
        self.armed = True
        self.roll_pid.reset()
        self.pitch_pid.reset()
        self.yaw_pid.reset()

    def disarm(self) -> None:
        self.armed = False

    def update(self, imu: IMUData,
               roll_sp: float, pitch_sp: float, yaw_rate_sp: float,
               throttle: float) -> List[int]:
        """
        Run one control loop.

        Parameters
        ----------
        imu          : IMUData  — latest sensor reading
        roll_sp      : float    — roll setpoint (degrees, Stabilise mode)
        pitch_sp     : float    — pitch setpoint (degrees)
        yaw_rate_sp  : float    — yaw rate setpoint (deg/s)
        throttle     : float    — 0.0–1.0

        Returns
        -------
        List[int]  — ESC PWM values in µs for each motor
        """
        if not self.armed:
            return [1000] * self.motor_count

        # 1. Sensor fusion
        roll_est, pitch_est = self.filter.update(imu, self.dt)
        self.attitude.roll  = roll_est
        self.attitude.pitch = pitch_est
        self.attitude.yaw  += imu.gyro_z * self.dt  # gyro-only yaw

        # 2. PID
        roll_out  = self.roll_pid.compute(roll_sp,        roll_est,          self.dt)
        pitch_out = self.pitch_pid.compute(pitch_sp,      pitch_est,         self.dt)
        yaw_out   = self.yaw_pid.compute(yaw_rate_sp,     imu.gyro_z,        self.dt)

        # 3. Normalise PID outputs to [-1, 1]
        max_out = 500.0
        roll_n  = roll_out  / max_out
        pitch_n = pitch_out / max_out
        yaw_n   = yaw_out   / max_out

        # 4. Quad-X motor mix (same as simple_firmware)
        raw = [
            throttle + pitch_n + roll_n - yaw_n,   # FL
            throttle + pitch_n - roll_n + yaw_n,   # FR
            throttle - pitch_n - roll_n - yaw_n,   # RR
            throttle - pitch_n + roll_n + yaw_n,   # RL
        ]

        return [
            int(1000 + max(0.0, min(1.0, v)) * 1000)
            for v in raw
        ]

    def get_telemetry(self) -> Dict[str, float]:
        """Return current attitude and PID state for logging / display."""
        return {
            "roll_deg":  round(self.attitude.roll,  2),
            "pitch_deg": round(self.attitude.pitch, 2),
            "yaw_deg":   round(self.attitude.yaw,   2),
        }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Medium Firmware Demo (Level 2 — PID stabilisation) ===\n")

    fc = MediumFlightController(motor_count=4)
    fc.arm()

    # Simulate: aircraft tilted 5° right, pilot asking for level flight
    imu = IMUData(
        gyro_x=2.0, gyro_y=0.5, gyro_z=0.0,
        accel_x=0.0, accel_y=0.85, accel_z=-9.77  # ~5° roll tilt
    )

    motors = fc.update(imu,
                       roll_sp=0.0,      # level
                       pitch_sp=0.0,     # level
                       yaw_rate_sp=0.0,  # no yaw
                       throttle=0.5)

    print(f"Attitude estimate: {fc.get_telemetry()}")
    print()
    labels = ["Front-Left", "Front-Right", "Rear-Right", "Rear-Left"]
    for label, pwm in zip(labels, motors):
        print(f"  {label:12s}: {pwm} µs")
