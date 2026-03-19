"""
Tests for phase_ai_flight modules: flight_path, gps_navigation, ai_controller.
"""

import math
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from phase_ai_flight.flight_path import (
    OccupancyGrid, astar, rrt_star, smooth_path,
)
from phase_ai_flight.gps_navigation import (
    LatLon, GPSNavigator, ReturnToHome, RTHPhase,
    CircularGeofence, AltitudeGeofence, GeofenceViolation,
    check_failsafe,
)
from phase_ai_flight.ai_controller import (
    DroneContext, DroneState, RuleEngine,
    Agent, BoidAgent,
    compute_desired_velocity, velocity_obstacle_avoid, boids_update,
    AIController,
)


# ===========================================================================
# OccupancyGrid
# ===========================================================================

class TestOccupancyGrid:
    def test_default_free(self):
        g = OccupancyGrid(10, 10)
        assert g.is_free(5, 5)

    def test_set_occupied(self):
        g = OccupancyGrid(10, 10)
        g.set(3, 3, OccupancyGrid.OCCUPIED)
        assert not g.is_free(3, 3)

    def test_out_of_bounds_treated_as_occupied(self):
        g = OccupancyGrid(5, 5)
        assert not g.is_free(10, 10)

    def test_add_obstacle_rect(self):
        g = OccupancyGrid(10, 10)
        g.add_obstacle_rect(2, 2, 4, 4)
        assert not g.is_free(3, 3)
        assert g.is_free(5, 5)

    def test_neighbours_count(self):
        g = OccupancyGrid(10, 10)
        nbrs = g.neighbours((5, 5), allow_diagonal=False)
        assert len(nbrs) == 4

    def test_coord_conversion_roundtrip(self):
        g = OccupancyGrid(20, 20, cell_size_m=1.0)
        pos = (7, 12)
        n, e = g.to_metric(pos)
        assert g.to_grid(n, e) == pos


# ===========================================================================
# A* planner
# ===========================================================================

class TestAStar:
    def test_straight_path(self):
        g = OccupancyGrid(5, 5)
        path = astar(g, (0, 0), (4, 4))
        assert path is not None
        assert path[0]  == (0, 0)
        assert path[-1] == (4, 4)

    def test_blocked_goal_returns_none(self):
        g = OccupancyGrid(5, 5)
        g.set(4, 4, OccupancyGrid.OCCUPIED)
        assert astar(g, (0, 0), (4, 4)) is None

    def test_path_navigates_around_wall(self):
        g = OccupancyGrid(10, 10)
        g.add_obstacle_rect(0, 5, 8, 5)   # vertical wall, gap at row 9
        path = astar(g, (0, 0), (0, 9))
        assert path is not None
        assert path[-1] == (0, 9)


# ===========================================================================
# RRT* planner
# ===========================================================================

class TestRRTStar:
    def test_finds_path_simple(self):
        g = OccupancyGrid(20, 20)
        path = rrt_star(g, (0, 0), (18, 18),
                        max_iter=3000, seed=42)
        assert path is not None
        assert path[0]  == (0, 0)
        assert path[-1][0] >= 15 and path[-1][1] >= 15

    def test_returns_none_when_blocked(self):
        """Goal completely surrounded — no path possible."""
        g = OccupancyGrid(10, 10)
        # Build a tight wall around cell (5,5), leaving no gap within goal_radius=1
        for r in range(3, 8):
            for c in range(3, 8):
                g.set(r, c, OccupancyGrid.OCCUPIED)
        path = rrt_star(g, (0, 0), (5, 5),
                        max_iter=500, seed=0, goal_radius=1.0)
        assert path is None


# ===========================================================================
# Path smoother
# ===========================================================================

class TestSmoothPath:
    def test_straight_line_unchanged(self):
        g    = OccupancyGrid(10, 10)
        path = [(0, 0), (5, 5), (9, 9)]
        s    = smooth_path(path, g)
        # All three visible from (0,0) → should collapse to 2 or 3 points
        assert s[0] == (0, 0)
        assert s[-1] == (9, 9)

    def test_no_crash_on_short_path(self):
        g = OccupancyGrid(5, 5)
        assert smooth_path([], g) == []
        assert smooth_path([(0, 0)], g) == [(0, 0)]


# ===========================================================================
# LatLon
# ===========================================================================

class TestLatLon:
    def test_distance_self(self):
        p = LatLon(51.0, 0.0)
        assert p.distance_to(p) == pytest.approx(0.0, abs=1e-3)

    def test_distance_one_degree_lat(self):
        a = LatLon(0.0, 0.0)
        b = LatLon(1.0, 0.0)
        d = a.distance_to(b)
        assert 111_000 < d < 112_000   # ≈ 111 km

    def test_bearing_north(self):
        a = LatLon(0.0, 0.0)
        b = LatLon(1.0, 0.0)
        assert a.bearing_to(b) == pytest.approx(0.0, abs=0.5)

    def test_bearing_east(self):
        a = LatLon(0.0, 0.0)
        b = LatLon(0.0, 1.0)
        assert a.bearing_to(b) == pytest.approx(90.0, abs=0.5)

    def test_move_by(self):
        p   = LatLon(0.0, 0.0)
        p2  = p.move_by(north_m=0, east_m=111_320)  # ≈ 1° East at equator
        assert abs(p2.lon - 1.0) < 0.01


# ===========================================================================
# GPSNavigator
# ===========================================================================

class TestGPSNavigator:
    def test_empty_returns_done(self):
        from phase_ai_flight.gps_navigation import WaypointStatus
        nav = GPSNavigator()
        status, _, _ = nav.update(LatLon(0, 0))
        assert status == WaypointStatus.MISSION_DONE

    def test_reaches_waypoint(self):
        from phase_ai_flight.gps_navigation import WaypointStatus
        nav = GPSNavigator()
        wp  = LatLon(51.4778, -0.0015)
        nav.add_waypoint(wp)
        status, _, _ = nav.update(wp, accept_radius=10.0)
        assert status in (WaypointStatus.REACHED, WaypointStatus.MISSION_DONE)


# ===========================================================================
# ReturnToHome
# ===========================================================================

class TestReturnToHome:
    def test_trigger_enters_climb(self):
        home = LatLon(51.4778, -0.0015, 0.0)
        rth  = ReturnToHome(home)
        rth.trigger()
        assert rth.is_active()
        assert rth.state.phase == RTHPhase.CLIMB

    def test_cancel_deactivates(self):
        home = LatLon(51.4778, -0.0015, 0.0)
        rth  = ReturnToHome(home)
        rth.trigger()
        rth.cancel()
        assert not rth.is_active()

    def test_update_returns_dict_keys(self):
        home = LatLon(51.4778, -0.0015, 30.0)
        rth  = ReturnToHome(home)
        rth.trigger()
        cmd  = rth.update(LatLon(51.479, 0.0, 50.0))
        assert "phase" in cmd
        assert "target_alt" in cmd
        assert "distance_to_home_m" in cmd


# ===========================================================================
# Geofence
# ===========================================================================

class TestGeofences:
    def test_inside_circular(self):
        home  = LatLon(0.0, 0.0)
        fence = CircularGeofence(home, radius_m=500)
        fence.check(LatLon(0.001, 0.0))  # ~111 m — should not raise

    def test_outside_circular(self):
        home  = LatLon(0.0, 0.0)
        fence = CircularGeofence(home, radius_m=100)
        with pytest.raises(GeofenceViolation):
            fence.check(LatLon(0.01, 0.0))  # ~1111 m

    def test_altitude_ok(self):
        fence = AltitudeGeofence(0.0, 120.0)
        fence.check(60.0)  # no exception

    def test_altitude_too_high(self):
        fence = AltitudeGeofence(0.0, 120.0)
        with pytest.raises(GeofenceViolation):
            fence.check(150.0)


# ===========================================================================
# Failsafe checks
# ===========================================================================

class TestCheckFailsafe:
    def test_normal_no_failsafe(self):
        assert check_failsafe(80.0, 0.0, 1.0) is None

    def test_low_battery_rth(self):
        assert check_failsafe(15.0, 0.0, 1.0) == "RTH"

    def test_rc_loss_rth(self):
        assert check_failsafe(80.0, 0.0, 10.0) == "RTH"

    def test_critical_battery_land(self):
        assert check_failsafe(5.0, 0.0, 1.0) == "LAND"


# ===========================================================================
# RuleEngine
# ===========================================================================

class TestRuleEngine:
    def test_normal_mission(self):
        ctx = DroneContext(battery_pct=80, rc_signal=True, gps_fix=True)
        assert RuleEngine().evaluate(ctx) == DroneState.MISSION

    def test_low_battery_rth(self):
        ctx = DroneContext(battery_pct=15, rc_signal=True)
        assert RuleEngine().evaluate(ctx) == DroneState.RTH

    def test_rc_lost_rth(self):
        ctx = DroneContext(battery_pct=80, rc_signal=False)
        assert RuleEngine().evaluate(ctx) == DroneState.RTH

    def test_critical_land(self):
        ctx = DroneContext(battery_pct=5, rc_signal=True)
        assert RuleEngine().evaluate(ctx) == DroneState.LAND


# ===========================================================================
# Velocity obstacle avoidance
# ===========================================================================

class TestVelocityObstacle:
    def test_no_obstacle_unchanged(self):
        me      = Agent(position=(0.0, 0.0), velocity=(3.0, 0.0))
        desired = compute_desired_velocity(me, (20.0, 0.0))
        safe    = velocity_obstacle_avoid(me, [], desired)
        assert safe == desired

    def test_obstacle_triggers_avoidance(self):
        me      = Agent(position=(0.0, 0.0), velocity=(5.0, 0.0))
        blocker = Agent(position=(8.0,  0.0), velocity=(-1.0, 0.0), radius=3.0)
        desired = compute_desired_velocity(me, (20.0, 0.0))
        safe    = velocity_obstacle_avoid(me, [blocker], desired, time_horizon=4.0)
        assert safe != desired


# ===========================================================================
# Boids swarm
# ===========================================================================

class TestBoids:
    def test_returns_same_count(self):
        agents = [BoidAgent(position=(i*5.0, 0.0), velocity=(0.5, 0.5), id=i)
                  for i in range(5)]
        updated = boids_update(agents)
        assert len(updated) == 5

    def test_max_speed_respected(self):
        agents = [BoidAgent(position=(float(i), 0.0),
                            velocity=(10.0, 10.0),
                            max_speed=5.0, id=i)
                  for i in range(3)]
        updated = boids_update(agents)
        for a in updated:
            speed = math.sqrt(a.velocity[0]**2 + a.velocity[1]**2)
            assert speed <= a.max_speed + 1e-6
