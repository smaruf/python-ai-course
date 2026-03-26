"""Tests for AgronomyAdvisor and ByproductMarketManager."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.agronomy.planting_guide import AgronomyAdvisor, PlantingFeasibility
from src.agronomy.byproduct_market import ByproductMarketManager, Byproduct


# ---------------------------------------------------------------------------
# AgronomyAdvisor tests
# ---------------------------------------------------------------------------

_CROPS = ["OLIVE", "MORINGA", "SUNFLOWER", "RAPESEED"]
_COUNTRIES = ["BD", "PL"]


def test_assess_feasibility_returns_type():
    advisor = AgronomyAdvisor()
    result = advisor.assess_feasibility("OLIVE", "PL")
    assert isinstance(result, PlantingFeasibility)


def test_assess_feasibility_score_range():
    advisor = AgronomyAdvisor()
    for crop in _CROPS:
        for country in _COUNTRIES:
            feas = advisor.assess_feasibility(crop, country)
            assert 0.0 <= feas.feasibility_score <= 1.0, (
                f"{crop}/{country} score out of range: {feas.feasibility_score}"
            )


def test_assess_feasibility_moringa_bd_high_score():
    """Moringa should score higher in Bangladesh than in Poland."""
    advisor = AgronomyAdvisor()
    bd = advisor.assess_feasibility("MORINGA", "BD")
    pl = advisor.assess_feasibility("MORINGA", "PL")
    assert bd.feasibility_score > pl.feasibility_score


def test_assess_feasibility_rapeseed_pl_better_than_bd():
    """Rapeseed is more suited to Poland's cool climate."""
    advisor = AgronomyAdvisor()
    pl = advisor.assess_feasibility("RAPESEED", "PL")
    bd = advisor.assess_feasibility("RAPESEED", "BD")
    assert pl.feasibility_score > bd.feasibility_score


def test_assess_feasibility_risk_level_present():
    advisor = AgronomyAdvisor()
    result = advisor.assess_feasibility("SUNFLOWER", "BD")
    assert result.risk_level in {"LOW", "MEDIUM", "HIGH", "VERY_HIGH"}


def test_assess_feasibility_adaptations_is_list():
    advisor = AgronomyAdvisor()
    result = advisor.assess_feasibility("OLIVE", "PL")
    assert isinstance(result.adaptations_needed, list)


def test_assess_feasibility_unknown_returns_zero():
    advisor = AgronomyAdvisor()
    result = advisor.assess_feasibility("BANANA", "ZZ")
    assert result.feasibility_score == pytest.approx(0.0)


def test_recommend_varieties_olive_poland():
    advisor = AgronomyAdvisor()
    varieties = advisor.recommend_varieties("OLIVE", "PL")
    assert "Arbequina" in varieties
    assert "Leccino" in varieties
    assert "Koroneiki" in varieties


def test_recommend_varieties_moringa_bd():
    advisor = AgronomyAdvisor()
    varieties = advisor.recommend_varieties("MORINGA", "BD")
    assert len(varieties) >= 1


def test_recommend_varieties_returns_list():
    advisor = AgronomyAdvisor()
    for crop in _CROPS:
        for country in _COUNTRIES:
            v = advisor.recommend_varieties(crop, country)
            assert isinstance(v, list)
            assert len(v) >= 1


def test_planting_calendar_returns_12_months():
    advisor = AgronomyAdvisor()
    cal = advisor.planting_calendar("OLIVE", "PL")
    assert isinstance(cal, dict)
    assert len(cal) == 12


def test_planting_calendar_all_combos():
    advisor = AgronomyAdvisor()
    for crop in _CROPS:
        for country in _COUNTRIES:
            cal = advisor.planting_calendar(crop, country)
            assert len(cal) == 12, f"Calendar for {crop}/{country} missing months"


def test_cross_planting_report_is_string():
    advisor = AgronomyAdvisor()
    report = advisor.cross_planting_report()
    assert isinstance(report, str)
    assert len(report) > 100


def test_cross_planting_report_contains_countries():
    advisor = AgronomyAdvisor()
    report = advisor.cross_planting_report()
    assert "Bangladesh" in report
    assert "Poland" in report


def test_land_requirements_olive():
    advisor = AgronomyAdvisor()
    result = advisor.land_requirements("OLIVE", 3000.0)
    assert result["land_required_ha"] == pytest.approx(1.0)
    assert result["land_required_m2"] == pytest.approx(10_000.0)


def test_land_requirements_unknown_crop():
    advisor = AgronomyAdvisor()
    result = advisor.land_requirements("UNKNOWN_CROP", 100.0)
    assert "error" in result


# ---------------------------------------------------------------------------
# ByproductMarketManager tests
# ---------------------------------------------------------------------------

def test_list_byproducts_all():
    mgr = ByproductMarketManager()
    all_bp = mgr.list_byproducts()
    assert len(all_bp) >= 10
    assert all(isinstance(b, Byproduct) for b in all_bp)


def test_list_byproducts_filter_waste():
    mgr = ByproductMarketManager()
    waste = mgr.list_byproducts("waste_management")
    assert len(waste) >= 1
    assert all(b.source_process == "waste_management" for b in waste)


def test_list_byproducts_filter_biofuel():
    mgr = ByproductMarketManager()
    biofuel = mgr.list_byproducts("biofuel")
    names = [b.name for b in biofuel]
    assert "CO2_food_grade" in names


def test_list_byproducts_filter_edible_oil():
    mgr = ByproductMarketManager()
    oil = mgr.list_byproducts("edible_oil")
    names = [b.name for b in oil]
    assert "moringa_leaf_powder" in names


def test_calculate_monthly_revenue_returns_total():
    mgr = ByproductMarketManager()
    production = {"waste_management": 1000, "biofuel": 500}
    result = mgr.calculate_monthly_revenue(production)
    assert "total_monthly_revenue_usd" in result
    assert result["total_monthly_revenue_usd"] > 0


def test_calculate_monthly_revenue_annual_projection():
    mgr = ByproductMarketManager()
    production = {"edible_oil": 200}
    result = mgr.calculate_monthly_revenue(production)
    monthly = result["total_monthly_revenue_usd"]
    annual = result["annual_projection_usd"]
    assert annual == pytest.approx(monthly * 12, rel=1e-3)


def test_market_opportunity_report_is_string():
    mgr = ByproductMarketManager()
    report = mgr.market_opportunity_report()
    assert isinstance(report, str)
    assert len(report) > 50


def test_market_opportunity_report_contains_processes():
    mgr = ByproductMarketManager()
    report = mgr.market_opportunity_report()
    for process in ["WASTE_MANAGEMENT", "BIOFUEL", "EDIBLE_OIL"]:
        assert process in report


def test_sales_channels_guide_known():
    mgr = ByproductMarketManager()
    guide = mgr.sales_channels_guide("compost")
    assert guide["byproduct"] == "compost"
    assert isinstance(guide["market_channels"], list)
    assert len(guide["market_channels"]) >= 1


def test_sales_channels_guide_moringa_leaf_powder():
    mgr = ByproductMarketManager()
    guide = mgr.sales_channels_guide("moringa_leaf_powder")
    assert guide["unit_price_usd"] == pytest.approx(15.0)


def test_sales_channels_guide_unknown():
    mgr = ByproductMarketManager()
    result = mgr.sales_channels_guide("nonexistent_byproduct")
    assert "error" in result
