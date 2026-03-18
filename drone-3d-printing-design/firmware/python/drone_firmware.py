"""
Python Drone Firmware — MicroPython / CircuitPython compatible

Targets:
  • Raspberry Pi Pico (RP2040) with MicroPython
  • Adafruit Feather M4 with CircuitPython
  • Any Linux SBC (full CPython) for SITL

Usage (MicroPython on Pico):
  Copy this file to the Pico as main.py.
  Wire MPU-6050 to I2C0 (SDA=GP0, SCL=GP1).
  Wire 4 ESCs to GP2, GP3, GP4, GP5.

The module is structured to work both as a standalone firmware
(if __name__ == "__main__") and as an importable library for testing.
"""

# ---------------------------------------------------------------------------
# MicroPython / CircuitPython compatibility shim
# Try real hardware modules; fall back to simulation stubs when not available.
# ---------------------------------------------------------------------------

try:
    import machine          # type: ignore  # MicroPython hardware
    import time
    _ON_HARDWARE = True
except ImportError:
    import time
    _ON_HARDWARE = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PWM_FREQ_HZ  = 50    # standard servo/ESC PWM frequency
PWM_MIN_US   = 1000  # motor stopped
PWM_MAX_US   = 2000  # full throttle
LOOP_RATE_HZ = 200   # control loop frequency


# ---------------------------------------------------------------------------
# Hardware abstraction layer (HAL)
# ---------------------------------------------------------------------------

class PWMOutput:
    """
    Thin wrapper around machine.PWM (MicroPython) or a simulation stub.
    """

    def __init__(self, pin_number: int) -> None:
        self.pin_number = pin_number
        self._us = PWM_MIN_US

        if _ON_HARDWARE:
            pin = machine.Pin(pin_number)
            self._pwm = machine.PWM(pin)
            self._pwm.freq(PWM_FREQ_HZ)
            self._set_us(PWM_MIN_US)

    def _set_us(self, microseconds: int) -> None:
        """Convert µs pulse width to PWM duty cycle."""
        self._us = microseconds
        if _ON_HARDWARE:
            # MicroPython: duty_ns or duty_u16
            period_ns = 1_000_000_000 // PWM_FREQ_HZ   # 20 ms = 20,000,000 ns
            duty_ns   = microseconds * 1000
            self._pwm.duty_ns(min(duty_ns, period_ns - 1))

    def write(self, microseconds: int) -> None:
        us = max(PWM_MIN_US, min(PWM_MAX_US, microseconds))
        self._set_us(us)

    @property
    def current_us(self) -> int:
        return self._us

    def deinit(self) -> None:
        if _ON_HARDWARE:
            self._pwm.deinit()


class I2CDevice:
    """Stub wrapper for I2C peripheral (MPU-6050, BMP388, etc.)."""

    def __init__(self, address: int, i2c_id: int = 0) -> None:
        self.address = address
        self._i2c = None
        if _ON_HARDWARE:
            sda = machine.Pin(0)
            scl = machine.Pin(1)
            self._i2c = machine.I2C(i2c_id, sda=sda, scl=scl, freq=400_000)

    def read_register(self, reg: int, length: int = 1) -> bytes:
        if _ON_HARDWARE and self._i2c:
            return self._i2c.readfrom_mem(self.address, reg, length)
        # Simulation: return zeroed bytes
        return bytes(length)

    def write_register(self, reg: int, data: bytes) -> None:
        if _ON_HARDWARE and self._i2c:
            self._i2c.writeto_mem(self.address, reg, data)


# ---------------------------------------------------------------------------
# MPU-6050 driver (simplified)
# ---------------------------------------------------------------------------

MPU6050_ADDR      = 0x68
MPU6050_PWR_MGMT  = 0x6B
MPU6050_ACCEL_OUT = 0x3B
MPU6050_GYRO_OUT  = 0x43
ACCEL_SCALE       = 16384.0   # ±2g → LSB/g
GYRO_SCALE        = 131.0     # ±250 °/s → LSB/(°/s)


class MPU6050:
    """Minimal MPU-6050 driver for MicroPython."""

    def __init__(self) -> None:
        self._dev = I2CDevice(MPU6050_ADDR)
        # Wake up device
        self._dev.write_register(MPU6050_PWR_MGMT, b'\x00')

    def _to_signed(self, high: int, low: int) -> int:
        val = (high << 8) | low
        return val - 65536 if val > 32767 else val

    def read_accel_gyro(self):
        """
        Returns (ax, ay, az, gx, gy, gz).
        Accelerometer in m/s², gyro in deg/s.
        """
        raw = self._dev.read_register(MPU6050_ACCEL_OUT, 14)
        if len(raw) < 14:
            return (0.0,) * 6

        ax = self._to_signed(raw[0],  raw[1])  / ACCEL_SCALE * 9.81
        ay = self._to_signed(raw[2],  raw[3])  / ACCEL_SCALE * 9.81
        az = self._to_signed(raw[4],  raw[5])  / ACCEL_SCALE * 9.81
        gx = self._to_signed(raw[8],  raw[9])  / GYRO_SCALE
        gy = self._to_signed(raw[10], raw[11]) / GYRO_SCALE
        gz = self._to_signed(raw[12], raw[13]) / GYRO_SCALE

        return ax, ay, az, gx, gy, gz


# ---------------------------------------------------------------------------
# Minimal PID
# ---------------------------------------------------------------------------

class PID:
    def __init__(self, kp: float, ki: float, kd: float,
                 limit: float = 400.0) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.limit = limit
        self._integral  = 0.0
        self._prev_error = 0.0

    def compute(self, setpoint: float, measured: float, dt: float) -> float:
        err = setpoint - measured
        self._integral = max(-self.limit,
                             min(self.limit, self._integral + err * dt))
        d_term = (err - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = err
        out = self.kp * err + self.ki * self._integral + self.kd * d_term
        return max(-self.limit, min(self.limit, out))

    def reset(self) -> None:
        self._integral   = 0.0
        self._prev_error = 0.0


# ---------------------------------------------------------------------------
# Complementary filter
# ---------------------------------------------------------------------------

import math as _math


class CompFilter:
    def __init__(self, alpha: float = 0.98) -> None:
        self.alpha = alpha
        self.roll  = 0.0
        self.pitch = 0.0

    def update(self, ax, ay, az, gx, gy, dt):
        self.roll  = self.alpha * (self.roll  + gx * dt)
        self.pitch = self.alpha * (self.pitch + gy * dt)
        if az != 0:
            ar = _math.degrees(_math.atan2(ay, az))
            ap = _math.degrees(_math.atan2(-ax, _math.sqrt(ay**2 + az**2)))
            self.roll  += (1 - self.alpha) * ar
            self.pitch += (1 - self.alpha) * ap
        return self.roll, self.pitch


# ---------------------------------------------------------------------------
# Firmware main loop
# ---------------------------------------------------------------------------

def run_firmware(loop_count: int = 100) -> None:
    """
    Main firmware loop.

    Parameters
    ----------
    loop_count : int
        Number of iterations to run.  Pass -1 for infinite (hardware use).
    """
    # Initialise hardware
    motors = [PWMOutput(2), PWMOutput(3), PWMOutput(4), PWMOutput(5)]
    imu    = MPU6050()
    filt   = CompFilter(alpha=0.98)
    pids   = {
        "roll":  PID(4.5, 0.04, 0.40),
        "pitch": PID(4.5, 0.04, 0.40),
        "yaw":   PID(6.0, 0.10, 0.20),
    }

    dt = 1.0 / LOOP_RATE_HZ
    armed = False
    throttle_pct = 0.0

    iteration = 0
    while loop_count < 0 or iteration < loop_count:
        t_start = time.time()

        # --- Sensor read ---
        ax, ay, az, gx, gy, gz = imu.read_accel_gyro()

        # --- Attitude estimate ---
        roll, pitch = filt.update(ax, ay, az, gx, gy, dt)

        # --- PID (setpoints = 0 → auto-level) ---
        roll_cmd  = pids["roll"].compute(0.0, roll,  dt)
        pitch_cmd = pids["pitch"].compute(0.0, pitch, dt)
        yaw_cmd   = pids["yaw"].compute(0.0, gz,     dt)

        # --- Motor mix (quad-X) ---
        norm = 500.0
        raw = [
            throttle_pct + pitch_cmd / norm + roll_cmd / norm - yaw_cmd / norm,
            throttle_pct + pitch_cmd / norm - roll_cmd / norm + yaw_cmd / norm,
            throttle_pct - pitch_cmd / norm - roll_cmd / norm - yaw_cmd / norm,
            throttle_pct - pitch_cmd / norm + roll_cmd / norm + yaw_cmd / norm,
        ]

        if armed:
            for motor, v in zip(motors, raw):
                motor.write(int(PWM_MIN_US + max(0.0, min(1.0, v))
                                * (PWM_MAX_US - PWM_MIN_US)))
        else:
            for motor in motors:
                motor.write(PWM_MIN_US)

        iteration += 1

        # Rate limiting (simulation only — on hardware use timer interrupts)
        elapsed = time.time() - t_start
        if elapsed < dt:
            time.sleep(dt - elapsed)

    # Cleanup
    for motor in motors:
        motor.write(PWM_MIN_US)
        motor.deinit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Python Drone Firmware — simulation mode")
    print(f"Running {LOOP_RATE_HZ} Hz control loop for 50 iterations...\n")
    run_firmware(loop_count=50)
    print("Done.")
