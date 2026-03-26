"""Tests for WaterTreatmentPlant and IrrigationController."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime

import pytest

from src.water_treatment.treatment_plant import (
    WaterQualityMetrics,
    WaterTreatmentPlant,
    TreatmentStage,
    WaterQualityMonitor,
)
from src.water_treatment.irrigation import (
    SoilMoistureZone,
    IrrigationController,
    IrrigationSchedule,
    WeatherForecast,
)


# ---------------------------------------------------------------------------
# WaterTreatmentPlant tests
# ---------------------------------------------------------------------------

def test_plant_init():
    plant = WaterTreatmentPlant(capacity_m3_per_day=5.0)
    assert plant.capacity_m3_per_day == 5.0


def test_plant_default_capacity():
    plant = WaterTreatmentPlant()
    assert plant.capacity_m3_per_day == 10.0


def test_process_stage_intake_no_change():
    plant = WaterTreatmentPlant()
    raw = WaterQualityMetrics(turbidity=20.0, e_coli=200.0)
    result = plant.process_stage(TreatmentStage.INTAKE, raw)
    assert result.turbidity == pytest.approx(20.0)
    assert result.e_coli == pytest.approx(200.0)


def test_process_stage_coagulation():
    plant = WaterTreatmentPlant()
    raw = WaterQualityMetrics(turbidity=20.0, tds=400.0)
    result = plant.process_stage(TreatmentStage.COAGULATION, raw)
    assert result.turbidity == pytest.approx(10.0)
    assert result.tds < 400.0


def test_process_stage_sedimentation():
    plant = WaterTreatmentPlant()
    raw = WaterQualityMetrics(turbidity=10.0, e_coli=100.0)
    result = plant.process_stage(TreatmentStage.SEDIMENTATION, raw)
    assert result.turbidity < 10.0
    assert result.e_coli < 100.0


def test_process_stage_filtration():
    plant = WaterTreatmentPlant()
    raw = WaterQualityMetrics(turbidity=2.0, e_coli=40.0)
    result = plant.process_stage(TreatmentStage.FILTRATION, raw)
    assert result.turbidity < 2.0
    assert result.e_coli < 40.0


def test_process_stage_disinfection():
    plant = WaterTreatmentPlant()
    raw = WaterQualityMetrics(e_coli=10.0, chlorine=0.0)
    result = plant.process_stage(TreatmentStage.DISINFECTION, raw)
    assert result.e_coli == pytest.approx(0.0)
    assert result.chlorine == pytest.approx(0.5)


def test_process_stage_distribution_chlorine_decay():
    plant = WaterTreatmentPlant()
    raw = WaterQualityMetrics(chlorine=0.5)
    result = plant.process_stage(TreatmentStage.DISTRIBUTION, raw)
    assert result.chlorine < 0.5


def test_run_full_treatment_returns_all_stages():
    plant = WaterTreatmentPlant()
    raw = WaterQualityMetrics()
    results = plant.run_full_treatment(raw)
    for stage in TreatmentStage:
        assert stage.value in results
        assert isinstance(results[stage.value], WaterQualityMetrics)


def test_run_full_treatment_improves_water():
    plant = WaterTreatmentPlant()
    raw = WaterQualityMetrics(turbidity=50.0, e_coli=500.0)
    results = plant.run_full_treatment(raw)
    final = results[TreatmentStage.DISTRIBUTION.value]
    assert final.turbidity < raw.turbidity
    assert final.e_coli < raw.e_coli


def test_check_who_standards_clean_water():
    plant = WaterTreatmentPlant()
    clean = WaterQualityMetrics(
        turbidity=1.0,
        ph=7.5,
        dissolved_oxygen=8.0,
        chlorine=0.5,
        tds=200.0,
        e_coli=0.0,
        temperature=20.0,
    )
    report = plant.check_who_standards(clean)
    assert isinstance(report, dict)
    assert all(report.values()), f"Expected all compliant, got {report}"


def test_check_who_standards_dirty_water():
    plant = WaterTreatmentPlant()
    dirty = WaterQualityMetrics(
        turbidity=50.0,
        ph=5.0,
        e_coli=100.0,
        chlorine=0.0,
    )
    report = plant.check_who_standards(dirty)
    assert report["turbidity"] is False
    assert report["ph"] is False
    assert report["e_coli"] is False


def test_estimate_chemical_costs_keys():
    plant = WaterTreatmentPlant()
    costs = plant.estimate_chemical_costs(10.0)
    assert "coagulant_usd" in costs
    assert "chlorine_usd" in costs
    assert "total_usd" in costs
    assert costs["total_usd"] > 0


def test_daily_production_report():
    plant = WaterTreatmentPlant()
    report = plant.daily_production_report()
    assert "volume_produced_m3" in report
    assert "compliance" in report
    assert "costs" in report
    assert isinstance(report["all_compliant"], bool)


# ---------------------------------------------------------------------------
# IrrigationController tests
# ---------------------------------------------------------------------------

def _make_zone(zone_id: str = "Z1", moisture: float = 30.0) -> SoilMoistureZone:
    return SoilMoistureZone(
        zone_id=zone_id,
        crop_type="wheat",
        area_m2=1000.0,
        current_moisture_pct=moisture,
        target_moisture_pct=60.0,
        last_irrigated=datetime.now(),
    )


def _make_forecast() -> WeatherForecast:
    return WeatherForecast(
        temperature_c=25.0,
        rainfall_mm=2.0,
        humidity_pct=50.0,
        wind_speed_ms=2.0,
        solar_radiation_wm2=200.0,
    )


def test_irrigation_add_zone():
    ctrl = IrrigationController()
    zone = _make_zone()
    ctrl.add_zone(zone)
    assert "Z1" in ctrl._zones


def test_irrigation_update_soil_moisture():
    ctrl = IrrigationController()
    ctrl.add_zone(_make_zone("Z2", moisture=30.0))
    ctrl.update_soil_moisture("Z2", 55.0)
    assert ctrl._zones["Z2"].current_moisture_pct == pytest.approx(55.0)


def test_irrigation_calculate_water_need_positive():
    ctrl = IrrigationController()
    ctrl.add_zone(_make_zone("Z3", moisture=20.0))
    need = ctrl.calculate_water_need("Z3", _make_forecast())
    assert isinstance(need, float)
    assert need >= 0.0


def test_irrigation_calculate_water_need_no_deficit():
    ctrl = IrrigationController()
    zone = _make_zone("Z4", moisture=80.0)
    zone.target_moisture_pct = 60.0
    ctrl.add_zone(zone)
    need = ctrl.calculate_water_need("Z4", _make_forecast())
    assert need == pytest.approx(0.0)


def test_irrigation_generate_schedule_returns_list():
    ctrl = IrrigationController()
    ctrl.add_zone(_make_zone("Z5", moisture=10.0))
    schedules = ctrl.generate_schedule(_make_forecast())
    assert isinstance(schedules, list)
    if schedules:
        assert isinstance(schedules[0], IrrigationSchedule)


def test_irrigation_generate_schedule_dry_zone():
    ctrl = IrrigationController()
    ctrl.add_zone(_make_zone("Z6", moisture=5.0))
    forecast = WeatherForecast(
        temperature_c=30.0,
        rainfall_mm=0.0,
        humidity_pct=30.0,
        wind_speed_ms=3.0,
        solar_radiation_wm2=300.0,
    )
    schedules = ctrl.generate_schedule(forecast)
    assert len(schedules) >= 1


def test_irrigation_estimate_water_savings():
    ctrl = IrrigationController()
    stats = ctrl.estimate_water_savings(1000.0, 700.0)
    assert stats["saved_liters"] == pytest.approx(300.0)
    assert stats["savings_percent"] == pytest.approx(30.0)


def test_irrigation_monthly_report():
    ctrl = IrrigationController()
    ctrl.add_zone(_make_zone("Z7", moisture=10.0))
    ctrl.generate_schedule(_make_forecast())
    report = ctrl.monthly_water_report()
    assert "total_events" in report
    assert "total_water_applied_liters" in report
    assert isinstance(report["active_zones"], int)
