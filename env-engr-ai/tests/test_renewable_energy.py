"""Tests for solar and wind energy monitoring."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import math
from src.models.schemas import EnergySource, RenewableEnergyMetrics
from src.renewable_energy.solar import SolarPanelMonitor
from src.renewable_energy.wind import WindTurbineMonitor


def make_solar_metrics(power_w=300.0, irradiance=800.0,
                       panel_temp=35.0) -> RenewableEnergyMetrics:
    efficiency = power_w / (irradiance * 2.0) if irradiance > 0 else 0.0
    return RenewableEnergyMetrics(
        source_type=EnergySource.SOLAR,
        power_output_w=power_w,
        efficiency=min(1.0, efficiency),
        capacity_factor=power_w / 400.0,
        metadata={"irradiance": irradiance, "panel_temperature": panel_temp},
    )


def make_wind_metrics(power_w=2000.0, wind_speed=8.0,
                      vibration=1.0, rpm=80.0) -> RenewableEnergyMetrics:
    return RenewableEnergyMetrics(
        source_type=EnergySource.WIND,
        power_output_w=power_w,
        efficiency=0.85,
        capacity_factor=power_w / 5000.0,
        metadata={"wind_speed": wind_speed, "vibration_mms": vibration, "rpm": rpm},
    )


# ---------------------------------------------------------------------------
# Solar tests
# ---------------------------------------------------------------------------

def test_solar_panel_monitor_init():
    monitor = SolarPanelMonitor("panel_01", rated_power_w=400.0, panel_area_m2=2.0)
    assert monitor.panel_id == "panel_01"
    assert monitor.rated_power_w == 400.0


def test_solar_panel_monitor_efficiency():
    monitor = SolarPanelMonitor("panel_01", rated_power_w=400.0, panel_area_m2=2.0)
    # 300 W / (800 W/m² × 2 m²) = 0.1875
    eff = monitor.calculate_efficiency(300.0, 800.0)
    assert abs(eff - 0.1875) < 0.001


def test_solar_panel_monitor_zero_irradiance():
    monitor = SolarPanelMonitor("panel_01")
    eff = monitor.calculate_efficiency(0.0, 0.0)
    assert eff == 0.0


def test_solar_panel_update():
    monitor = SolarPanelMonitor("panel_01")
    m = make_solar_metrics(power_w=350.0, irradiance=900.0)
    status = monitor.update(m)
    assert "power_w" in status
    assert "efficiency" in status
    assert "faults" in status


def test_solar_panel_fault_detection_shading():
    monitor = SolarPanelMonitor("panel_02", rated_power_w=400.0, panel_area_m2=2.0)
    # Only 30% of expected output at 1000 W/m² → shading
    m = make_solar_metrics(power_w=60.0, irradiance=1000.0)
    faults = monitor.detect_faults(m)
    assert any("SHADING" in f or "PARTIAL" in f for f in faults)


def test_solar_panel_fault_detection_hotspot():
    monitor = SolarPanelMonitor("panel_03")
    m = make_solar_metrics(power_w=300.0, irradiance=800.0, panel_temp=75.0)
    faults = monitor.detect_faults(m)
    assert any("HOT_SPOT" in f for f in faults)


def test_solar_panel_no_fault_normal():
    monitor = SolarPanelMonitor("panel_04", rated_power_w=400.0, panel_area_m2=2.0)
    # Normal output at 500 W/m²
    m = make_solar_metrics(power_w=200.0, irradiance=500.0, panel_temp=35.0)
    faults = monitor.detect_faults(m)
    # At 500 W/m²: expected ≈ 200W, actual 200W → no shading
    assert not any("SHADING" in f for f in faults)


def test_solar_mppt_algorithm():
    monitor = SolarPanelMonitor("mppt_panel")
    # Simulate increasing power scenario
    v_opt, i_opt = monitor.mppt_algorithm(36.0, 5.0, 800.0)
    assert 20.0 <= v_opt <= 50.0
    assert i_opt >= 0.0


def test_solar_forecast_yield():
    monitor = SolarPanelMonitor("panel_05", rated_power_w=400.0)
    irradiances = [0, 200, 500, 800, 1000, 800, 500, 200, 0]
    forecast = monitor.forecast_yield(irradiances)
    assert len(forecast) == len(irradiances)
    assert forecast[0] == 0.0
    assert forecast[4] > forecast[2]  # Higher irradiance → more power


# ---------------------------------------------------------------------------
# Wind turbine tests
# ---------------------------------------------------------------------------

def test_wind_turbine_init():
    monitor = WindTurbineMonitor("turbine_01", rated_power_w=5000.0,
                                  rotor_diameter_m=5.0)
    assert monitor.turbine_id == "turbine_01"
    expected_area = math.pi * 2.5 ** 2
    assert abs(monitor.rotor_area_m2 - expected_area) < 0.01


def test_wind_turbine_power_curve_below_cut_in():
    monitor = WindTurbineMonitor("t1")
    assert monitor.power_curve(0.0) == 0.0
    assert monitor.power_curve(2.0) == 0.0  # Below cut-in


def test_wind_turbine_power_curve_rated():
    monitor = WindTurbineMonitor("t1", rated_power_w=5000.0)
    power = monitor.power_curve(12.0)  # Rated speed
    assert abs(power - 5000.0) < 100.0


def test_wind_turbine_power_curve_above_cut_out():
    monitor = WindTurbineMonitor("t1", rated_power_w=5000.0)
    assert monitor.power_curve(30.0) == 0.0  # Above cut-out


def test_wind_turbine_power_curve_monotonic():
    monitor = WindTurbineMonitor("t1")
    speeds = [3.0, 5.0, 8.0, 10.0, 12.0]  # All below rated
    powers = [monitor.power_curve(v) for v in speeds]
    for i in range(len(powers) - 1):
        assert powers[i] <= powers[i + 1], "Power curve should be monotonically increasing below rated speed"


def test_wind_turbine_fault_detection_over_speed():
    monitor = WindTurbineMonitor("t2", rated_power_w=5000.0)
    m = make_wind_metrics(power_w=5000.0, wind_speed=30.0)
    faults = monitor.detect_faults(m)
    assert any("OVER_SPEED" in f for f in faults)


def test_wind_turbine_fault_detection_vibration():
    monitor = WindTurbineMonitor("t3")
    m = make_wind_metrics(power_w=2000.0, wind_speed=8.0, vibration=8.0)
    faults = monitor.detect_faults(m)
    assert any("VIBRATION" in f for f in faults)


def test_wind_turbine_no_fault_normal():
    monitor = WindTurbineMonitor("t4")
    m = make_wind_metrics(power_w=2500.0, wind_speed=8.0, vibration=1.0, rpm=80.0)
    faults = monitor.detect_faults(m)
    # May have blade imbalance check, but no vibration or over-speed
    assert not any("VIBRATION" in f for f in faults)
    assert not any("OVER_SPEED" in f for f in faults)


def test_wind_turbine_capacity_factor():
    monitor = WindTurbineMonitor("t5", rated_power_w=5000.0)
    cf = monitor.calculate_capacity_factor(2500.0)
    assert abs(cf - 0.5) < 0.001
