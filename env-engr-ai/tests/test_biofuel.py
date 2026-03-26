"""Tests for biofuel fermentation monitoring and process control."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.models.schemas import BiofuelMetrics, FermentationStage
from src.biofuel.fermentation import FermentationController, FermentationMonitor
from src.biofuel.process_control import BiofuelProcessController, PIDController


def make_metrics(stage: str = "INOCULATION", temp=30.0, ph=5.0,
                 sugar=18.0, ethanol=0.5, co2=2.0) -> BiofuelMetrics:
    return BiofuelMetrics(
        batch_id="batch_test",
        temperature=temp,
        ph=ph,
        sugar_content=sugar,
        ethanol_yield=ethanol,
        stage=FermentationStage(stage),
        co2_rate=co2,
    )


def test_fermentation_monitor_stage_detection():
    monitor = FermentationMonitor("test_batch")
    # Inoculation: high sugar, low CO2
    m = make_metrics(sugar=18.0, co2=1.0, ethanol=0.0)
    stage = monitor.detect_stage(m)
    assert stage == FermentationStage.INOCULATION

    # Exponential: high CO2, medium sugar
    m2 = make_metrics(sugar=8.0, co2=25.0, ethanol=2.0)
    stage2 = monitor.detect_stage(m2)
    assert stage2 == FermentationStage.EXPONENTIAL

    # Decline: very low sugar and CO2
    m3 = make_metrics(sugar=0.3, co2=0.5, ethanol=10.0)
    stage3 = monitor.detect_stage(m3)
    assert stage3 == FermentationStage.DECLINE


def test_fermentation_monitor_update_returns_status():
    monitor = FermentationMonitor("batch_02")
    m = make_metrics()
    status = monitor.update(m)
    assert "batch_id" in status
    assert "stage" in status
    assert "predicted_yield" in status
    assert "recommendations" in status


def test_fermentation_monitor_yield_prediction():
    monitor = FermentationMonitor("batch_03")
    m = make_metrics(temp=32.0, ph=4.5, sugar=12.0, co2=20.0, ethanol=3.0)
    predicted = monitor.predict_yield(m)
    assert isinstance(predicted, float)
    assert 0.0 <= predicted <= 15.0


def test_fermentation_monitor_recommendations_in_range():
    monitor = FermentationMonitor("batch_04")
    m = make_metrics(temp=30.0, ph=5.0, sugar=18.0)
    monitor.update(m)
    recs = monitor.get_recommendations()
    assert isinstance(recs, list)
    assert len(recs) > 0
    # When in range, should say all OK
    assert any("optimal" in r.lower() or "well" in r.lower() for r in recs)


def test_fermentation_monitor_recommendations_out_of_range():
    monitor = FermentationMonitor("batch_05")
    # Very cold – should recommend heating
    m = make_metrics(temp=10.0, ph=5.0, sugar=18.0)
    monitor.update(m)
    recs = monitor.get_recommendations()
    assert any("temperature" in r.lower() or "heat" in r.lower() for r in recs)


# ---------------------------------------------------------------------------
# PIDController tests
# ---------------------------------------------------------------------------

def test_pid_controller_basic():
    pid = PIDController(kp=2.0, ki=0.1, kd=0.5, setpoint=30.0)
    # Simulate: measured = 25.0, error = +5.0 → output > 0
    output = pid.compute(25.0, dt=1.0)
    assert output > 0.0


def test_pid_controller_output_clamping():
    pid = PIDController(kp=100.0, ki=10.0, kd=5.0, setpoint=100.0,
                        output_min=0.0, output_max=50.0)
    output = pid.compute(0.0)
    assert 0.0 <= output <= 50.0


def test_pid_controller_zero_error():
    pid = PIDController(kp=2.0, ki=0.1, kd=0.5, setpoint=30.0)
    # Zero error → near-zero output (some integral may be there)
    output = pid.compute(30.0, dt=1.0)
    assert abs(output) < 5.0


def test_pid_controller_reset():
    pid = PIDController(kp=2.0, ki=0.5, kd=0.1, setpoint=50.0)
    for _ in range(10):
        pid.compute(0.0)
    pid.reset()
    # After reset, integral should be zero
    assert pid._integral == 0.0
    assert not pid._initialized


def test_pid_setpoint_change():
    pid = PIDController(kp=1.0, ki=0.0, kd=0.0, setpoint=20.0)
    pid.set_setpoint(30.0)
    assert pid.setpoint == 30.0


# ---------------------------------------------------------------------------
# BiofuelProcessController tests
# ---------------------------------------------------------------------------

def test_biofuel_process_controller_safety_interlocks():
    ctrl = BiofuelProcessController()
    # Extreme temperature – should trigger interlock
    m = make_metrics(temp=70.0, ph=5.0)
    violations = ctrl.check_safety_interlocks(m)
    assert len(violations) > 0


def test_biofuel_process_controller_normal_operation():
    ctrl = BiofuelProcessController()
    m = make_metrics(temp=32.0, ph=4.8, sugar=10.0)
    outputs = ctrl.update(m)
    assert "heater_power" in outputs
    assert "acid_pump" in outputs
    assert "base_pump" in outputs
    assert outputs["emergency_stop"] == 0.0


def test_biofuel_process_controller_emergency_stop():
    ctrl = BiofuelProcessController()
    ctrl.emergency_stop()
    m = make_metrics()
    outputs = ctrl.update(m)
    assert outputs["emergency_stop"] == 1.0
    assert outputs["heater_power"] == 0.0


def test_fermentation_controller_compute_actions():
    ctrl = FermentationController("test_batch", target_temperature=30.0,
                                  target_ph=5.0)
    m = make_metrics(temp=25.0, ph=4.0)
    actions = ctrl.compute_control_actions(m)
    assert "heater_power" in actions
    assert "acid_pump_rate" in actions
    assert "base_pump_rate" in actions
    # Temperature below target → heater should be on
    assert actions["heater_power"] > 0.0
    # pH below target → base pump to raise it
    assert actions["base_pump_rate"] > 0.0
