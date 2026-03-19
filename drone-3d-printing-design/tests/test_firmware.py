"""
Tests for phase_firmware modules: simple, medium, and advanced firmware.
"""

import math
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from phase_firmware.simple_firmware import (
    PWM_MIN, PWM_MAX, PWM_MID,
    RCInput, ESCOutput,
    normalise_channel, mix_quad_x, mix_fixed_wing, run_simple_loop,
)
from phase_firmware.medium_firmware import (
    PIDState, ComplementaryFilter, IMUData,
    MediumFlightController,
)
from phase_firmware.advanced_firmware import (
    GPSPosition, MissionManager, Waypoint, WaypointType,
    TaskScheduler, SystemHealth, HealthStatus,
    AdvancedFlightController,
)


# ===========================================================================
# simple_firmware
# ===========================================================================

class TestNormaliseChannel:
    def test_throttle_min(self):
        assert normalise_channel(PWM_MIN, centre=PWM_MIN) == pytest.approx(0.0)

    def test_throttle_max(self):
        assert normalise_channel(PWM_MAX, centre=PWM_MIN) == pytest.approx(1.0)

    def test_throttle_half(self):
        assert normalise_channel(1500, centre=PWM_MIN) == pytest.approx(0.5)

    def test_control_neutral_in_deadband(self):
        assert normalise_channel(PWM_MID) == 0.0

    def test_control_max(self):
        assert normalise_channel(PWM_MAX) == pytest.approx(1.0)

    def test_control_min(self):
        assert normalise_channel(PWM_MIN) == pytest.approx(-1.0)


class TestMixQuadX:
    def test_hover_equal_motors(self):
        """Pure throttle should produce equal motor outputs."""
        motors = mix_quad_x(0.5, 0.0, 0.0, 0.0)
        assert len(motors) == 4
        assert motors[0] == motors[1] == motors[2] == motors[3]

    def test_values_within_range(self):
        motors = mix_quad_x(0.5, 0.3, 0.2, -0.1)
        for m in motors:
            assert PWM_MIN <= m <= PWM_MAX

    def test_roll_right_differential(self):
        """Rolling right: FL/RL > FR/RR (simplified check on FL vs FR)."""
        motors = mix_quad_x(0.5, 0.0, 0.5, 0.0)
        # FL (index 0) > FR (index 1)
        assert motors[0] > motors[1]


class TestMixFixedWing:
    def test_keys_present(self):
        result = mix_fixed_wing(0.5, 0.3, 0.2, 0.1)
        assert "throttle_pwm" in result
        assert "aileron_left_pwm" in result
        assert "aileron_right_pwm" in result
        assert "elevator_pwm" in result
        assert "rudder_pwm" in result

    def test_ailerons_opposite(self):
        result = mix_fixed_wing(0.5, 0.5, 0.0, 0.0)
        # Aileron left and right must be on opposite sides of mid
        assert result["aileron_left_pwm"] > PWM_MID
        assert result["aileron_right_pwm"] < PWM_MID


class TestRunSimpleLoop:
    def test_disarmed_kills_motors(self):
        rc  = RCInput(channels=[PWM_MIN, PWM_MID, PWM_MID, PWM_MID, PWM_MIN])
        esc = ESCOutput(motor_count=4)
        esc.set(0, PWM_MAX)
        result = run_simple_loop(rc, esc)
        assert all(v == PWM_MIN for v in result.values)

    def test_armed_quad_sets_motors(self):
        rc  = RCInput(channels=[1600, 1500, 1500, 1500, 1700])
        esc = ESCOutput(motor_count=4)
        result = run_simple_loop(rc, esc, aircraft="quad")
        assert any(v > PWM_MIN for v in result.values)


# ===========================================================================
# medium_firmware
# ===========================================================================

class TestPIDState:
    def test_proportional_only(self):
        pid = PIDState(kp=2.0, ki=0.0, kd=0.0)
        out = pid.compute(setpoint=10.0, measured=5.0, dt=0.01)
        assert out == pytest.approx(10.0)  # 2.0 * 5.0

    def test_integral_accumulates(self):
        pid = PIDState(kp=0.0, ki=1.0, kd=0.0)
        for _ in range(10):
            pid.compute(setpoint=1.0, measured=0.0, dt=0.1)
        # After 10 steps at dt=0.1, integral ≈ 1.0 (capped at i_limit=400)
        out = pid.compute(setpoint=1.0, measured=0.0, dt=0.1)
        assert out > 0

    def test_reset_clears_state(self):
        pid = PIDState(kp=1.0, ki=1.0, kd=0.0)
        pid.compute(10.0, 0.0, 0.01)
        pid.reset()
        out = pid.compute(0.0, 0.0, 0.01)
        assert out == pytest.approx(0.0)

    def test_zero_dt_returns_zero(self):
        pid = PIDState(kp=1.0, ki=1.0, kd=1.0)
        assert pid.compute(1.0, 0.0, 0.0) == 0.0

    def test_output_clamped(self):
        pid = PIDState(kp=1000.0, ki=0.0, kd=0.0, output_limit=100.0)
        out = pid.compute(100.0, 0.0, 0.01)
        assert out == pytest.approx(100.0)


class TestComplementaryFilter:
    def test_initial_state(self):
        filt = ComplementaryFilter()
        assert filt.roll  == 0.0
        assert filt.pitch == 0.0

    def test_update_returns_tuple(self):
        filt = ComplementaryFilter()
        imu  = IMUData(gyro_x=10.0, gyro_y=5.0, accel_z=-9.81)
        roll, pitch = filt.update(imu, dt=0.002)
        assert isinstance(roll,  float)
        assert isinstance(pitch, float)

    def test_gyro_only_integration(self):
        """With alpha=1.0, only gyro is integrated."""
        filt = ComplementaryFilter(alpha=1.0)
        imu  = IMUData(gyro_x=90.0, accel_z=-9.81)
        roll, _ = filt.update(imu, dt=1.0)
        assert roll == pytest.approx(90.0, abs=1.0)


class TestMediumFlightController:
    def test_disarmed_returns_min_pwm(self):
        fc  = MediumFlightController()
        imu = IMUData()
        motors = fc.update(imu, 0, 0, 0, 0.5)
        assert all(v == 1000 for v in motors)

    def test_armed_produces_nonzero_throttle(self):
        fc  = MediumFlightController()
        fc.arm()
        imu    = IMUData()
        motors = fc.update(imu, 0, 0, 0, 0.5)
        assert all(v >= 1000 for v in motors)
        assert any(v > 1000 for v in motors)

    def test_telemetry_keys(self):
        fc = MediumFlightController()
        t  = fc.get_telemetry()
        assert "roll_deg" in t and "pitch_deg" in t and "yaw_deg" in t


# ===========================================================================
# advanced_firmware
# ===========================================================================

class TestGPSPosition:
    def test_distance_to_self(self):
        pos = GPSPosition(51.0, 0.0, 0.0)
        assert pos.distance_to(pos) == pytest.approx(0.0, abs=1e-3)

    def test_distance_approximate(self):
        a = GPSPosition(0.0, 0.0, 0.0)
        b = GPSPosition(0.0, 1.0, 0.0)  # ~111 km
        assert 100_000 < a.distance_to(b) < 120_000

    def test_bearing_north(self):
        a = GPSPosition(0.0, 0.0, 0.0)
        b = GPSPosition(1.0, 0.0, 0.0)  # due North
        assert a.bearing_to(b) == pytest.approx(0.0, abs=0.5)

    def test_bearing_east(self):
        a = GPSPosition(0.0, 0.0,  0.0)
        b = GPSPosition(0.0, 1.0,  0.0)  # due East
        assert a.bearing_to(b) == pytest.approx(90.0, abs=0.5)


class TestMissionManager:
    def _home(self):
        return GPSPosition(51.4778, -0.0015, 0.0)

    def test_empty_mission(self):
        mgr = MissionManager(self._home())
        assert mgr.current_waypoint() is None
        assert mgr.is_complete()

    def test_advance_through_waypoints(self):
        mgr = MissionManager(self._home())
        mgr.add_waypoint(Waypoint(GPSPosition(51.479, 0.0, 50.0)))
        mgr.add_waypoint(Waypoint(GPSPosition(51.480, 0.0, 50.0)))
        assert mgr.remaining() == 2
        mgr.advance()
        assert mgr.remaining() == 1
        mgr.advance()
        assert mgr.is_complete()

    def test_insert_rth(self):
        mgr = MissionManager(self._home())
        mgr.add_waypoint(Waypoint(GPSPosition(51.480, 0.0, 50.0)))
        mgr.insert_rth()
        wp = mgr.current_waypoint()
        assert wp is not None
        assert wp.wp_type == WaypointType.RTH


class TestTaskScheduler:
    def test_task_runs_when_due(self):
        calls = []
        sched = TaskScheduler()
        sched.register("test_task", lambda: calls.append(1), period_ms=100)
        sched.tick(now_ms=0.0)    # _last_run_ms=0, (0-0)=0 < 100 → no run
        sched.tick(now_ms=50.0)   # (50-0)=50 < 100 → no run
        sched.tick(now_ms=101.0)  # (101-0)=101 >= 100 → runs once
        assert len(calls) == 1

    def test_task_not_overrun(self):
        calls = []
        sched = TaskScheduler()
        sched.register("slow_task", lambda: calls.append(1), period_ms=1000)
        for t in range(0, 500, 10):        # ticks at 0,10,...,490 ms
            sched.tick(now_ms=float(t))    # max elapsed = 490 ms < 1000 ms
        assert len(calls) == 0   # period not yet reached


class TestSystemHealth:
    def test_ok_status(self):
        h = SystemHealth(battery_percent=80, gps_fix=True, gps_sats=10,
                         imu_ok=True, rc_signal=True)
        assert h.overall_status() == HealthStatus.OK

    def test_critical_without_imu(self):
        h = SystemHealth(battery_percent=80, imu_ok=False, rc_signal=True)
        assert h.overall_status() == HealthStatus.CRITICAL

    def test_failsafe_low_battery(self):
        h = SystemHealth(battery_percent=5)
        assert h.failsafe_needed()

    def test_no_failsafe_normal(self):
        h = SystemHealth(battery_percent=80, rc_signal=True, imu_ok=True)
        assert not h.failsafe_needed()


class TestAdvancedFlightController:
    def _make_fc(self):
        home = GPSPosition(51.4778, -0.0015, 0.0)
        return AdvancedFlightController(home)

    def test_tick_generates_telemetry(self):
        fc = self._make_fc()
        fc.health.gps_fix = True
        fc.health.battery_percent = 80
        fc.arm()
        # Tick past the 200 ms telemetry period
        fc.tick(now_ms=0.0)
        fc.tick(now_ms=201.0)
        telem = fc.get_last_telemetry()
        assert telem is not None
        assert "mode" in telem

    def test_failsafe_inserts_rth(self):
        fc = self._make_fc()
        fc.arm()
        fc.health.rc_signal = False   # simulate RC loss
        fc.health.battery_percent = 5  # critical
        fc._task_health()
        assert fc.mode in ("AUTO_RTH", "AUTO") or not fc.armed
