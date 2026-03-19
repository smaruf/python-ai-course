"""
GPS Navigation & Return-to-Home Module

Provides:
  • GPSNavigator  — waypoint sequencing, heading/distance computation
  • ReturnToHome  — battery/signal-loss triggered auto-RTH
  • Geofence      — circular and polygon keep-in / keep-out zones

Coordinate system: WGS-84 decimal degrees.
All distances in metres, bearings in degrees (0 = North, CW positive).
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EARTH_RADIUS_M = 6_371_000.0
LOW_BATTERY_PCT = 20.0     # trigger RTH below this battery %
CRITICAL_BATTERY_PCT = 10.0  # force-land immediately
RC_LOSS_TIMEOUT_S = 3.0    # seconds without RC signal before RTH
RTH_SAFE_ALTITUDE_M = 30.0  # minimum altitude during RTH
WAYPOINT_ACCEPT_RADIUS_M = 3.0  # metres — "close enough" to waypoint


# ---------------------------------------------------------------------------
# GPS helpers
# ---------------------------------------------------------------------------

@dataclass
class LatLon:
    """WGS-84 geographic point."""
    lat: float  # degrees
    lon: float  # degrees
    alt: float = 0.0  # metres above sea level

    def distance_to(self, other: "LatLon") -> float:
        """Haversine distance in metres."""
        phi1 = math.radians(self.lat)
        phi2 = math.radians(other.lat)
        dphi = math.radians(other.lat - self.lat)
        dlam = math.radians(other.lon - self.lon)
        a = (math.sin(dphi / 2) ** 2
             + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2)
        return EARTH_RADIUS_M * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def bearing_to(self, other: "LatLon") -> float:
        """Initial bearing in degrees (0 = North, CW)."""
        phi1 = math.radians(self.lat)
        phi2 = math.radians(other.lat)
        dlam = math.radians(other.lon - self.lon)
        x = math.sin(dlam) * math.cos(phi2)
        y = (math.cos(phi1) * math.sin(phi2)
             - math.sin(phi1) * math.cos(phi2) * math.cos(dlam))
        return (math.degrees(math.atan2(x, y)) + 360) % 360

    def move_by(self, north_m: float, east_m: float) -> "LatLon":
        """Offset this point by north_m / east_m and return a new LatLon."""
        dlat = math.degrees(north_m / EARTH_RADIUS_M)
        dlon = math.degrees(east_m /
                            (EARTH_RADIUS_M * math.cos(math.radians(self.lat))))
        return LatLon(self.lat + dlat, self.lon + dlon, self.alt)


# ---------------------------------------------------------------------------
# Navigator
# ---------------------------------------------------------------------------

class WaypointStatus(Enum):
    APPROACHING  = "APPROACHING"
    REACHED      = "REACHED"
    MISSION_DONE = "MISSION_DONE"


class GPSNavigator:
    """
    Sequences GPS waypoints and reports bearing/distance to the active one.

    Example
    -------
    >>> nav = GPSNavigator()
    >>> nav.add_waypoint(LatLon(51.478, -0.001))
    >>> nav.add_waypoint(LatLon(51.479, -0.000))
    >>> status, bearing, dist = nav.update(current_pos)
    """

    def __init__(self) -> None:
        self._waypoints: List[LatLon] = []
        self._index: int = 0

    def add_waypoint(self, wp: LatLon) -> None:
        self._waypoints.append(wp)

    def clear(self) -> None:
        self._waypoints.clear()
        self._index = 0

    @property
    def active_waypoint(self) -> Optional[LatLon]:
        if self._index < len(self._waypoints):
            return self._waypoints[self._index]
        return None

    @property
    def remaining(self) -> int:
        return max(0, len(self._waypoints) - self._index)

    def update(self, position: LatLon,
               accept_radius: float = WAYPOINT_ACCEPT_RADIUS_M
               ) -> Tuple[WaypointStatus, float, float]:
        """
        Call each navigation loop iteration.

        Returns
        -------
        (status, bearing_deg, distance_m)
        """
        wp = self.active_waypoint
        if wp is None:
            return WaypointStatus.MISSION_DONE, 0.0, 0.0

        dist    = position.distance_to(wp)
        bearing = position.bearing_to(wp)

        if dist <= accept_radius:
            self._index += 1
            if self._index >= len(self._waypoints):
                return WaypointStatus.MISSION_DONE, bearing, dist
            return WaypointStatus.REACHED, bearing, dist

        return WaypointStatus.APPROACHING, bearing, dist


# ---------------------------------------------------------------------------
# Return-to-Home
# ---------------------------------------------------------------------------

class RTHPhase(Enum):
    IDLE     = "IDLE"
    CLIMB    = "CLIMB"       # ascend to safe altitude
    NAVIGATE = "NAVIGATE"    # fly toward home
    DESCEND  = "DESCEND"     # descend over home
    LAND     = "LAND"        # final landing
    COMPLETE = "COMPLETE"


@dataclass
class RTHState:
    phase:            RTHPhase = RTHPhase.IDLE
    safe_altitude_m:  float    = RTH_SAFE_ALTITUDE_M
    descent_rate_ms:  float    = 0.5   # m/s
    accept_radius_m:  float    = 2.0


class ReturnToHome:
    """
    State machine for Return-to-Home behaviour.

    Usage
    -----
    >>> rth = ReturnToHome(home=LatLon(51.478, -0.001, 0))
    >>> rth.trigger()
    >>> while not rth.is_complete():
    ...     cmd = rth.update(current_pos)
    ...     send_to_autopilot(cmd)
    """

    def __init__(self, home: LatLon,
                 safe_altitude: float = RTH_SAFE_ALTITUDE_M) -> None:
        self.home  = home
        self.state = RTHState(safe_altitude_m=safe_altitude)
        self._active = False

    def trigger(self) -> None:
        """Activate RTH."""
        self._active = True
        self.state.phase = RTHPhase.CLIMB

    def cancel(self) -> None:
        """Pilot takes back control."""
        self._active = False
        self.state.phase = RTHPhase.IDLE

    def is_active(self) -> bool:
        return self._active

    def is_complete(self) -> bool:
        return self.state.phase == RTHPhase.COMPLETE

    def update(self, position: LatLon) -> dict:
        """
        Compute RTH command for current position.

        Returns a dict with keys:
          target_lat, target_lon, target_alt,
          phase (str), distance_to_home_m
        """
        dist = position.distance_to(self.home)

        if self.state.phase == RTHPhase.CLIMB:
            if position.alt < self.state.safe_altitude_m - 1.0:
                cmd_alt = self.state.safe_altitude_m
            else:
                self.state.phase = RTHPhase.NAVIGATE
                cmd_alt = self.state.safe_altitude_m

        elif self.state.phase == RTHPhase.NAVIGATE:
            if dist > self.state.accept_radius_m:
                cmd_alt = self.state.safe_altitude_m
            else:
                self.state.phase = RTHPhase.DESCEND
                cmd_alt = 5.0  # start descending to 5 m

        elif self.state.phase == RTHPhase.DESCEND:
            cmd_alt = max(0.0, position.alt - self.state.descent_rate_ms)
            if position.alt < 0.5:
                self.state.phase = RTHPhase.LAND

        elif self.state.phase == RTHPhase.LAND:
            cmd_alt = 0.0
            if position.alt < 0.1:
                self.state.phase = RTHPhase.COMPLETE
                self._active = False

        else:
            cmd_alt = position.alt

        return {
            "target_lat": self.home.lat,
            "target_lon": self.home.lon,
            "target_alt": cmd_alt,
            "phase":      self.state.phase.value,
            "distance_to_home_m": round(dist, 2),
        }


# ---------------------------------------------------------------------------
# Geofencing
# ---------------------------------------------------------------------------

class GeofenceViolation(Exception):
    """Raised when a position is outside the allowed geofence."""


class CircularGeofence:
    """
    Keep-in circular geofence centred on a home point.

    If the drone exits the radius, `check()` raises GeofenceViolation.
    """

    def __init__(self, centre: LatLon, radius_m: float) -> None:
        self.centre   = centre
        self.radius_m = radius_m

    def check(self, position: LatLon) -> None:
        dist = position.distance_to(self.centre)
        if dist > self.radius_m:
            raise GeofenceViolation(
                f"Outside geofence: {dist:.1f} m from centre "
                f"(limit {self.radius_m} m)"
            )

    def distance_to_boundary(self, position: LatLon) -> float:
        """Positive = inside, negative = outside."""
        return self.radius_m - position.distance_to(self.centre)


class AltitudeGeofence:
    """Keep altitude within [min_alt, max_alt] metres AGL."""

    def __init__(self, min_alt: float = 0.0, max_alt: float = 120.0) -> None:
        self.min_alt = min_alt
        self.max_alt = max_alt

    def check(self, altitude_m: float) -> None:
        if altitude_m > self.max_alt:
            raise GeofenceViolation(
                f"Altitude {altitude_m:.1f} m exceeds maximum {self.max_alt} m"
            )
        if altitude_m < self.min_alt:
            raise GeofenceViolation(
                f"Altitude {altitude_m:.1f} m below minimum {self.min_alt} m"
            )


# ---------------------------------------------------------------------------
# Failsafe trigger logic
# ---------------------------------------------------------------------------

def check_failsafe(battery_pct: float,
                   rc_last_seen_s: float,
                   elapsed_s: float) -> Optional[str]:
    """
    Determine if a failsafe action should trigger.

    Parameters
    ----------
    battery_pct      : float  — current battery percentage
    rc_last_seen_s   : float  — timestamp of last RC packet (seconds)
    elapsed_s        : float  — current time (seconds)

    Returns
    -------
    "RTH"       — initiate return-to-home
    "LAND"      — land immediately (critical)
    None        — no failsafe needed
    """
    rc_lost = (elapsed_s - rc_last_seen_s) > RC_LOSS_TIMEOUT_S

    if battery_pct <= CRITICAL_BATTERY_PCT or (rc_lost and battery_pct < 30):
        return "LAND"

    if battery_pct <= LOW_BATTERY_PCT or rc_lost:
        return "RTH"

    return None


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== GPS Navigation & RTH Demo ===\n")

    home = LatLon(51.4778, -0.0015, 0.0)

    # --- Navigator ---
    nav = GPSNavigator()
    nav.add_waypoint(LatLon(51.4782, -0.0010, 50.0))
    nav.add_waypoint(LatLon(51.4787, -0.0005, 50.0))
    nav.add_waypoint(home)

    print("Waypoint mission:")
    current = LatLon(51.4778, -0.0015, 50.0)
    for _ in range(3):
        status, bearing, dist = nav.update(current, accept_radius=200.0)
        wp = nav.active_waypoint
        if wp:
            print(f"  → WP{nav._index}: bearing={bearing:.1f}°  dist={dist:.0f} m  status={status.value}")
            current = wp  # jump to waypoint for demo

    print()

    # --- RTH ---
    print("Return-to-Home simulation:")
    rth      = ReturnToHome(home, safe_altitude=40.0)
    position = LatLon(51.4790, -0.0000, 10.0)  # away from home, low altitude

    rth.trigger()
    phases_seen = set()
    for step in range(200):
        cmd = rth.update(position)
        phase = cmd["phase"]
        if phase not in phases_seen:
            print(f"  Phase: {phase:10s}  dist={cmd['distance_to_home_m']:6.1f} m"
                  f"  target_alt={cmd['target_alt']:.1f} m")
            phases_seen.add(phase)
        # Simulate movement
        position = LatLon(
            position.lat + (home.lat - position.lat) * 0.15,
            position.lon + (home.lon - position.lon) * 0.15,
            cmd["target_alt"],
        )
        if rth.is_complete():
            break

    print()

    # --- Failsafe check ---
    print("Failsafe checks:")
    cases = [
        (50.0, 0.0, 1.0, "normal"),
        (15.0, 0.0, 1.0, "low battery"),
        (50.0, 0.0, 5.0, "RC lost"),
        (8.0,  0.0, 1.0, "critical battery"),
    ]
    for batt, rc_ts, now, desc in cases:
        action = check_failsafe(batt, rc_ts, now)
        print(f"  {desc:20s}: {action or 'OK'}")

    print()

    # --- Geofence ---
    print("Geofence check:")
    fence = CircularGeofence(home, radius_m=500.0)
    alt_fence = AltitudeGeofence(min_alt=0.0, max_alt=120.0)

    test_positions = [
        LatLon(51.4780, -0.0012, 50.0),   # inside
        LatLon(51.4900, 0.0100,  50.0),   # outside
    ]
    for pos in test_positions:
        dist = pos.distance_to(home)
        try:
            fence.check(pos)
            print(f"  ({pos.lat:.4f}, {pos.lon:.4f})  dist={dist:.0f} m  → OK")
        except GeofenceViolation as e:
            print(f"  ({pos.lat:.4f}, {pos.lon:.4f})  dist={dist:.0f} m  → VIOLATION: {e}")
