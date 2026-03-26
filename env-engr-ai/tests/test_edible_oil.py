"""Tests for edible oil extraction and quality control."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.models.schemas import EdibleOilMetrics, OilGrade
from src.edible_oil.extraction import CropType, ExtractionMonitor
from src.edible_oil.quality_control import OilQualityController


def make_oil_metrics(acidity=0.5, peroxide=10.0, moisture=0.1,
                     temp=22.0, pressure=250.0) -> EdibleOilMetrics:
    return EdibleOilMetrics(
        batch_id="oil_test",
        temperature=temp,
        pressure=pressure,
        moisture_content=moisture,
        quality_grade=OilGrade.EXTRA_VIRGIN,
        acidity=acidity,
        peroxide_value=peroxide,
    )


def test_extraction_monitor_olive_init():
    monitor = ExtractionMonitor("olive_batch_01", CropType.OLIVE)
    assert monitor.batch_id == "olive_batch_01"
    assert monitor.crop_type == CropType.OLIVE
    assert monitor.standard == "PL"


def test_extraction_monitor_moringa_init():
    monitor = ExtractionMonitor("moringa_batch_01", CropType.MORINGA)
    assert monitor.standard == "BD"


def test_extraction_monitor_olive_update():
    monitor = ExtractionMonitor("olive_01", CropType.OLIVE)
    m = make_oil_metrics(acidity=0.6, peroxide=15.0, temp=22.0)
    status = monitor.update(m)
    assert "assessed_grade" in status
    assert "recommendations" in status
    assert status["standard"] == "PL"


def test_extraction_monitor_moringa():
    monitor = ExtractionMonitor("moringa_01", CropType.MORINGA)
    m = make_oil_metrics(acidity=0.8, peroxide=12.0, temp=30.0, pressure=200.0)
    status = monitor.update(m)
    assert status["standard"] == "BD"
    assert "assessed_grade" in status


def test_extraction_monitor_yield():
    monitor = ExtractionMonitor("test_01", CropType.OLIVE)
    yield_pct = monitor.calculate_yield(input_mass_kg=100.0, output_volume_L=22.0)
    # 22 L × 0.91 kg/L = 20.02 kg / 100 kg = 20.02%
    assert 18.0 <= yield_pct <= 22.0


def test_extraction_monitor_quality_assessment_extra_virgin():
    monitor = ExtractionMonitor("ev_01", CropType.OLIVE)
    m = make_oil_metrics(acidity=0.5, peroxide=12.0)
    grade = monitor.assess_quality(m)
    assert grade == OilGrade.EXTRA_VIRGIN


def test_extraction_monitor_quality_assessment_off_grade():
    monitor = ExtractionMonitor("off_01", CropType.OLIVE)
    m = make_oil_metrics(acidity=5.0, peroxide=80.0)
    grade = monitor.assess_quality(m)
    assert grade == OilGrade.OFF_GRADE


def test_extraction_monitor_recommendations_temp_warning():
    monitor = ExtractionMonitor("warn_01", CropType.OLIVE)
    # Temperature too high for cold press
    m = make_oil_metrics(temp=40.0)
    monitor.update(m)
    recs = monitor.get_process_recommendations()
    assert any("temperature" in r.lower() or "cool" in r.lower() for r in recs)


# ---------------------------------------------------------------------------
# OilQualityController tests
# ---------------------------------------------------------------------------

def test_quality_controller_init_pl():
    qc = OilQualityController(standard="PL")
    assert qc.standard == "PL"


def test_quality_controller_init_bd():
    qc = OilQualityController(standard="BD")
    assert qc.standard == "BD"


def test_quality_controller_invalid_standard():
    with pytest.raises(ValueError):
        OilQualityController(standard="XX")


def test_quality_controller_predict_grade():
    qc = OilQualityController(standard="PL")
    m = make_oil_metrics(acidity=0.5, peroxide=10.0)
    grade, confidence = qc.predict_grade(m)
    assert isinstance(grade, OilGrade)
    assert 0.0 <= confidence <= 1.0


def test_quality_controller_compliance_pl():
    qc = OilQualityController(standard="PL")
    # Should pass for extra virgin PL standard
    m = make_oil_metrics(acidity=0.5, peroxide=15.0, moisture=0.1)
    compliance = qc.check_compliance(m)
    assert "acidity_ok" in compliance
    assert "peroxide_ok" in compliance
    assert "moisture_ok" in compliance
    assert compliance["standard"] == "PL"


def test_quality_controller_compliance_bd():
    qc = OilQualityController(standard="BD")
    m = make_oil_metrics(acidity=0.8, peroxide=12.0, moisture=0.4)
    compliance = qc.check_compliance(m)
    assert compliance["standard"] == "BD"


def test_quality_controller_generate_report():
    qc = OilQualityController(standard="PL")
    readings = [make_oil_metrics(acidity=0.5 + i * 0.1, peroxide=10.0 + i)
                for i in range(5)]
    report = qc.generate_quality_report("batch_001", readings)
    assert "batch_001" in report
    assert "PL" in report
    assert "Readings" in report


def test_quality_controller_empty_report():
    qc = OilQualityController(standard="PL")
    report = qc.generate_quality_report("empty_batch", [])
    assert "No readings" in report or "empty_batch" in report
