"""
Advanced Firmware Module — Level 3

RTOS-style cooperative task scheduler with MAVLink telemetry,
GPS waypoint navigation, and health monitoring.

Equivalent to a simplified PX4/ArduPilot custom module running on:
  • NuttX RTOS (Pixhawk hardware)
  • FreeRTOS (STM32H7 / F7)
  • Linux (Raspberry Pi, Jetson Nano — via Python simulation)

This module can run in simulation (pure Python) or be ported to
MicroPython on capable hardware.
"""

import math
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# GPS / coordinate utilities
# ---------------------------------------------------------------------------

EARTH_RADIUS_M = 6_371_000.0


@dataclass
class GPSPosition:
    """WGS-84 geographic coordinate."""
    latitude:  float  # decimal degrees, -90 to +90
    longitude: float  # decimal degrees, -180 to +180
    altitude:  float  # metres above sea level

    def distance_to(self, other: "GPSPosition") -> float:
        """Haversine distance in metres."""
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        dlat = math.radians(other.latitude  - self.latitude)
        dlon = math.radians(other.longitude - self.longitude)

        a = (math.sin(dlat / 2) ** 2
             + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        return EARTH_RADIUS_M * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def bearing_to(self, other: "GPSPosition") -> float:
        """Initial bearing from self → other, in degrees (0 = North)."""
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        dlon = math.radians(other.longitude - self.longitude)

        x = math.sin(dlon) * math.cos(lat2)
        y = (math.cos(lat1) * math.sin(lat2)
             - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
        return (math.degrees(math.atan2(x, y)) + 360) % 360


# ---------------------------------------------------------------------------
# MAVLink-style message structures
# ---------------------------------------------------------------------------

@dataclass
class HeartbeatMsg:
    system_id:    int
    component_id: int
    flight_mode:  str
    armed:        bool
    timestamp_ms: int = 0


@dataclass
class AttitudeMsg:
    roll:  float   # radians
    pitch: float
    yaw:   float
    rollspeed:  float = 0.0
    pitchspeed: float = 0.0
    yawspeed:   float = 0.0


@dataclass
class GlobalPositionMsg:
    lat:     float   # deg × 1e7
    lon:     float
    alt:     float   # mm above MSL
    vel_n:   float = 0.0  # m/s North
    vel_e:   float = 0.0
    vel_d:   float = 0.0


def build_heartbeat(mode: str, armed: bool, sysid: int = 1) -> HeartbeatMsg:
    return HeartbeatMsg(
        system_id=sysid,
        component_id=1,
        flight_mode=mode,
        armed=armed,
        timestamp_ms=int(time.time() * 1000) % (2 ** 31),
    )


# ---------------------------------------------------------------------------
# Mission management
# ---------------------------------------------------------------------------

class WaypointType(Enum):
    TAKEOFF     = "TAKEOFF"
    WAYPOINT    = "WAYPOINT"
    LOITER      = "LOITER"
    RTH         = "RETURN_TO_HOME"
    LAND        = "LAND"


@dataclass
class Waypoint:
    position:    GPSPosition
    wp_type:     WaypointType = WaypointType.WAYPOINT
    acceptance_radius: float = 3.0   # metres
    hold_time_s: float = 0.0         # loiter duration


class MissionManager:
    """
    Stores and sequences a list of GPS waypoints.

    Usage
    -----
    >>> mgr = MissionManager(home)
    >>> mgr.add_waypoint(Waypoint(pos1))
    >>> mgr.add_waypoint(Waypoint(pos2))
    >>> wp = mgr.current_waypoint()
    >>> if close_enough:
    ...     mgr.advance()
    """

    def __init__(self, home: GPSPosition) -> None:
        self.home      = home
        self._waypoints: List[Waypoint] = []
        self._index     = 0

    def add_waypoint(self, wp: Waypoint) -> None:
        self._waypoints.append(wp)

    def current_waypoint(self) -> Optional[Waypoint]:
        if self._index < len(self._waypoints):
            return self._waypoints[self._index]
        return None

    def advance(self) -> bool:
        """Move to next waypoint. Returns True if more waypoints remain."""
        self._index += 1
        return self._index < len(self._waypoints)

    def remaining(self) -> int:
        return max(0, len(self._waypoints) - self._index)

    def is_complete(self) -> bool:
        return self._index >= len(self._waypoints)

    def insert_rth(self) -> None:
        """Prepend a return-to-home waypoint at the current position."""
        rth = Waypoint(
            position=self.home,
            wp_type=WaypointType.RTH,
            acceptance_radius=2.0,
        )
        self._waypoints.insert(self._index, rth)


# ---------------------------------------------------------------------------
# RTOS-style cooperative task scheduler
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name:            str
    callback:        Callable[[], None]
    period_ms:       float          # how often to run (milliseconds)
    _last_run_ms:    float = field(default=0.0, init=False, repr=False)

    def is_due(self, now_ms: float) -> bool:
        return (now_ms - self._last_run_ms) >= self.period_ms

    def run(self, now_ms: float) -> None:
        self._last_run_ms = now_ms
        self.callback()


class TaskScheduler:
    """
    Lightweight cooperative (non-preemptive) scheduler.

    Tasks are registered with a period; the scheduler calls each task
    when its deadline is due.  This mirrors the NuttX px4_task approach
    but runs in pure Python for simulation and unit-testing.
    """

    def __init__(self) -> None:
        self._tasks: List[Task] = []

    def register(self, name: str, callback: Callable,
                 period_ms: float) -> None:
        self._tasks.append(Task(name=name, callback=callback,
                                period_ms=period_ms))

    def tick(self, now_ms: Optional[float] = None) -> None:
        """Run all tasks that are due."""
        t = now_ms if now_ms is not None else time.monotonic() * 1000
        for task in self._tasks:
            if task.is_due(t):
                task.run(t)


# ---------------------------------------------------------------------------
# Health monitor
# ---------------------------------------------------------------------------

class HealthStatus(Enum):
    OK       = "OK"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


@dataclass
class SystemHealth:
    """Aggregated health snapshot."""
    battery_voltage: float  = 0.0   # V
    battery_percent: float  = 0.0   # %
    gps_fix:         bool   = False
    gps_sats:        int    = 0
    imu_ok:          bool   = True
    baro_ok:         bool   = True
    rc_signal:       bool   = True
    cpu_load:        float  = 0.0   # 0–100 %

    def overall_status(self) -> HealthStatus:
        if not self.imu_ok or not self.rc_signal:
            return HealthStatus.CRITICAL
        if not self.gps_fix or self.battery_percent < 15:
            return HealthStatus.DEGRADED
        return HealthStatus.OK

    def failsafe_needed(self) -> bool:
        """Return True if an automatic failsafe action should trigger."""
        return (not self.rc_signal
                or not self.imu_ok
                or self.battery_percent < 10)


# ---------------------------------------------------------------------------
# Advanced flight controller façade
# ---------------------------------------------------------------------------

class AdvancedFlightController:
    """
    Integrates scheduler, mission manager, health monitor, and telemetry.

    Designed to be subclassed or instantiated directly for SITL testing.
    """

    def __init__(self, home: GPSPosition) -> None:
        self.home     = home
        self.position = GPSPosition(home.latitude, home.longitude, home.altitude)
        self.health   = SystemHealth()
        self.mission  = MissionManager(home)
        self.scheduler = TaskScheduler()
        self.armed    = False
        self.mode     = "STABILISE"
        self._telemetry_log: List[Dict] = []

        # Register default tasks (periods are simulated, not real-time)
        self.scheduler.register("imu_update",    self._task_imu,       period_ms=2)
        self.scheduler.register("attitude_ctrl", self._task_attitude,  period_ms=2)
        self.scheduler.register("nav_update",    self._task_navigation, period_ms=100)
        self.scheduler.register("health_check",  self._task_health,    period_ms=500)
        self.scheduler.register("telemetry",     self._task_telemetry, period_ms=200)

    # ------------------------------------------------------------------
    # Task callbacks (override in subclass for real hardware)
    # ------------------------------------------------------------------

    def _task_imu(self) -> None:
        """Read IMU — override with real SPI/I2C call."""

    def _task_attitude(self) -> None:
        """Run PID control loop — override with real PID instance."""

    def _task_navigation(self) -> None:
        """Advance mission if waypoint reached."""
        wp = self.mission.current_waypoint()
        if wp is None:
            return
        dist = self.position.distance_to(wp.position)
        if dist <= wp.acceptance_radius:
            advanced = self.mission.advance()
            if not advanced:
                self.mode = "LAND"

    def _task_health(self) -> None:
        """Check health and trigger failsafe if needed."""
        if self.health.failsafe_needed() and self.armed:
            self._trigger_failsafe()

    def _task_telemetry(self) -> None:
        """Build and store a telemetry snapshot."""
        hb = build_heartbeat(self.mode, self.armed)
        self._telemetry_log.append({
            "ts":   hb.timestamp_ms,
            "mode": hb.flight_mode,
            "armed": hb.armed,
            "lat":   self.position.latitude,
            "lon":   self.position.longitude,
            "alt":   self.position.altitude,
            "health": self.health.overall_status().value,
            "wp_remaining": self.mission.remaining(),
        })

    def _trigger_failsafe(self) -> None:
        """Insert RTH waypoint and switch to auto mode."""
        self.mission.insert_rth()
        self.mode = "AUTO_RTH"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tick(self, now_ms: Optional[float] = None) -> None:
        self.scheduler.tick(now_ms)

    def upload_mission(self, waypoints: List[Waypoint]) -> None:
        for wp in waypoints:
            self.mission.add_waypoint(wp)

    def arm(self) -> None:
        self.armed = True
        self.mode  = "AUTO"

    def disarm(self) -> None:
        self.armed = False

    def get_last_telemetry(self) -> Optional[Dict]:
        return self._telemetry_log[-1] if self._telemetry_log else None


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Advanced Firmware Demo (Level 3 — RTOS scheduler + GPS mission) ===\n")

    home = GPSPosition(latitude=51.4778, longitude=-0.0015, altitude=30.0)
    fc   = AdvancedFlightController(home)

    # Upload a 3-waypoint survey mission
    waypoints = [
        Waypoint(GPSPosition(51.4780, -0.0010, 50.0), WaypointType.WAYPOINT),
        Waypoint(GPSPosition(51.4785, -0.0005, 50.0), WaypointType.WAYPOINT),
        Waypoint(GPSPosition(51.4778, -0.0015, 30.0), WaypointType.LAND),
    ]
    fc.upload_mission(waypoints)
    fc.health.gps_fix  = True
    fc.health.gps_sats = 12
    fc.health.battery_percent = 85.0
    fc.arm()

    print(f"Mission loaded: {fc.mission.remaining()} waypoints")
    print(f"Home: {home.latitude:.4f}, {home.longitude:.4f}")
    print()

    # Simulate 5 scheduler ticks (each 200 ms apart)
    for i in range(5):
        fc.tick(now_ms=i * 200.0)

    telem = fc.get_last_telemetry()
    if telem:
        print("Last telemetry snapshot:")
        for k, v in telem.items():
            print(f"  {k:16s}: {v}")
