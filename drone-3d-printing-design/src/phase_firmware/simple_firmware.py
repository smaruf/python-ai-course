"""
Simple Firmware Module — Level 1

Simulates bare-metal RC receiver input and PWM ESC output with no OS.
This is the Python equivalent of what runs on an Arduino Nano or STM32F103
in a basic RC-only aircraft.

Hardware targets (real-world):
  • Arduino Nano / Uno (ATmega328P)
  • STM32F103 "Blue Pill"
  • RP2040 (Raspberry Pi Pico)

On real hardware the PWM values are written directly to timer registers.
Here we model the same logic in pure Python for simulation and testing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PWM_MIN = 1000   # microseconds (motor stopped / servo centre-min)
PWM_MAX = 2000   # microseconds (full throttle / servo max)
PWM_MID = 1500   # microseconds (servo neutral)
PWM_DEADBAND = 20  # ±µs around mid — ignore noise

# RC channel mapping (standard Mode-2 transmitter)
CH_THROTTLE = 0
CH_AILERON  = 1   # roll
CH_ELEVATOR = 2   # pitch
CH_RUDDER   = 3   # yaw
CH_AUX1     = 4   # arm switch
CH_AUX2     = 5   # flight-mode switch

# Motor indices for a quadcopter X-frame
MOTOR_FRONT_LEFT  = 0
MOTOR_FRONT_RIGHT = 1
MOTOR_REAR_RIGHT  = 2
MOTOR_REAR_LEFT   = 3


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RCInput:
    """Raw RC receiver channel values (µs, 1000–2000)."""

    channels: List[int] = field(default_factory=lambda: [PWM_MIN] + [PWM_MID] * 7)

    def __post_init__(self) -> None:
        if len(self.channels) < 4:
            raise ValueError("Need at least 4 RC channels")

    @property
    def throttle(self) -> int:
        return self.channels[CH_THROTTLE]

    @property
    def aileron(self) -> int:
        return self.channels[CH_AILERON]

    @property
    def elevator(self) -> int:
        return self.channels[CH_ELEVATOR]

    @property
    def rudder(self) -> int:
        return self.channels[CH_RUDDER]

    @property
    def armed(self) -> bool:
        """AUX1 > 1500 µs = armed."""
        return len(self.channels) > CH_AUX1 and self.channels[CH_AUX1] > PWM_MID


@dataclass
class ESCOutput:
    """PWM values sent to each ESC (µs, 1000–2000)."""

    motor_count: int = 4
    values: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.values:
            self.values = [PWM_MIN] * self.motor_count

    def set(self, index: int, value: int) -> None:
        self.values[index] = max(PWM_MIN, min(PWM_MAX, value))

    def arm(self) -> None:
        """Send arming signal (1000 µs) to all ESCs."""
        self.values = [PWM_MIN] * self.motor_count

    def disarm(self) -> None:
        """Cut all motor signals."""
        self.values = [PWM_MIN] * self.motor_count


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def normalise_channel(raw_us: int, centre: int = PWM_MID) -> float:
    """
    Convert a raw RC channel value to a normalised float.

    Returns
    -------
    float
        Throttle channel → 0.0 … 1.0
        Control channels → -1.0 … +1.0 (with deadband applied)
    """
    half_range = PWM_MAX - PWM_MID  # 500

    if centre == PWM_MIN:
        # Throttle: map 1000–2000 → 0.0–1.0
        return max(0.0, min(1.0, (raw_us - PWM_MIN) / (PWM_MAX - PWM_MIN)))

    # Control axis: apply deadband then normalise
    offset = raw_us - centre
    if abs(offset) < PWM_DEADBAND:
        return 0.0
    return max(-1.0, min(1.0, offset / half_range))


def mix_quad_x(throttle: float, pitch: float, roll: float, yaw: float) -> List[int]:
    """
    Quad-X motor mixer.

    Motor layout (top view):
        FL(0)  FR(1)
          \\  //
           XX
          //  \\
        RL(3)  RR(2)

    FL, RR spin CW; FR, RL spin CCW.

    Parameters
    ----------
    throttle : float  0.0–1.0
    pitch    : float -1.0–+1.0  (+ = nose up)
    roll     : float -1.0–+1.0  (+ = right bank)
    yaw      : float -1.0–+1.0  (+ = nose right / CW from above)

    Returns
    -------
    List[int]  Four PWM values in µs [FL, FR, RR, RL]
    """
    raw = [
        throttle + pitch + roll - yaw,   # FL  (CW)
        throttle + pitch - roll + yaw,   # FR  (CCW)
        throttle - pitch - roll - yaw,   # RR  (CW)
        throttle - pitch + roll + yaw,   # RL  (CCW)
    ]

    # Clamp to [0, 1] then convert to µs
    return [
        int(PWM_MIN + max(0.0, min(1.0, v)) * (PWM_MAX - PWM_MIN))
        for v in raw
    ]


def mix_fixed_wing(throttle: float, aileron: float,
                   elevator: float, rudder: float) -> Dict[str, int]:
    """
    Fixed-wing surface mixer (conventional: one ESC + 4 servos).

    Returns
    -------
    dict
        throttle_pwm, aileron_left_pwm, aileron_right_pwm,
        elevator_pwm, rudder_pwm
    """
    def to_pwm(norm: float) -> int:
        return int(PWM_MID + norm * (PWM_MAX - PWM_MID))

    throttle_pwm = int(PWM_MIN + max(0.0, min(1.0, throttle)) * (PWM_MAX - PWM_MIN))

    return {
        "throttle_pwm":       throttle_pwm,
        "aileron_left_pwm":   to_pwm(aileron),
        "aileron_right_pwm":  to_pwm(-aileron),   # opposite deflection
        "elevator_pwm":       to_pwm(elevator),
        "rudder_pwm":         to_pwm(rudder),
    }


def run_simple_loop(rc: RCInput, esc: ESCOutput,
                    aircraft: str = "quad") -> ESCOutput:
    """
    Execute one firmware loop iteration (replaces the Arduino loop()).

    Parameters
    ----------
    rc       : RCInput   — latest RC receiver data
    esc      : ESCOutput — current ESC state (mutated in place)
    aircraft : str       — "quad" or "fixed_wing"

    Returns
    -------
    ESCOutput  (same object, updated)
    """
    if not rc.armed:
        esc.disarm()
        return esc

    thr  = normalise_channel(rc.throttle, centre=PWM_MIN)
    roll = normalise_channel(rc.aileron)
    pit  = normalise_channel(rc.elevator)
    yaw  = normalise_channel(rc.rudder)

    if aircraft == "quad":
        pwm_values = mix_quad_x(thr, pit, roll, yaw)
        for i, v in enumerate(pwm_values):
            esc.set(i, v)
    else:
        # Fixed-wing: only throttle ESC is motor_0
        surf = mix_fixed_wing(thr, roll, pit, yaw)
        esc.set(0, surf["throttle_pwm"])

    return esc


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Simple Firmware Demo (Level 1 — RC pass-through) ===\n")

    # Simulate: armed, 50% throttle, slight right roll, slight pitch up
    rc = RCInput(channels=[1500, 1600, 1550, 1500, 1700, 1500, 1500, 1500])
    esc = ESCOutput(motor_count=4)

    esc = run_simple_loop(rc, esc, aircraft="quad")

    print(f"Armed   : {rc.armed}")
    print(f"Throttle: {rc.throttle} µs  → {normalise_channel(rc.throttle, PWM_MIN):.2f}")
    print(f"Roll    : {rc.aileron} µs   → {normalise_channel(rc.aileron):.2f}")
    print(f"Pitch   : {rc.elevator} µs  → {normalise_channel(rc.elevator):.2f}")
    print(f"Yaw     : {rc.rudder} µs    → {normalise_channel(rc.rudder):.2f}")
    print()

    labels = ["Front-Left", "Front-Right", "Rear-Right", "Rear-Left"]
    for label, pwm in zip(labels, esc.values):
        print(f"  {label:12s}: {pwm} µs")
