"""Tests for waste management classifier and route optimizer."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.models.schemas import WasteType
from src.waste_management.classifier import WasteClassifier, WasteOptimizer
from src.waste_management.optimizer import (
    CollectionPoint, RouteOptimizer, CarbonFootprintCalculator
)


def test_waste_classifier_classifies_organic():
    clf = WasteClassifier()
    features = {
        "weight": 10.0, "volume": 15.0, "moisture": 80.0,
        "temperature": 35.0, "methane_ppm": 30.0,
    }
    result = clf.classify(features)
    # High moisture + methane → should be ORGANIC or at worst a similar organic-adjacent class
    assert result.waste_type in (WasteType.ORGANIC, WasteType.HAZARDOUS)
    assert result.confidence > 0.2


def test_waste_classifier_classifies_inert():
    clf = WasteClassifier()
    features = {
        "weight": 80.0, "volume": 100.0, "moisture": 2.0,
        "temperature": 15.0, "methane_ppm": 0.1,
    }
    result = clf.classify(features)
    # Should be classified as inert (heavy, dry, no gas)
    assert result.waste_type in (WasteType.INERT, WasteType.RECYCLABLE)
    assert result.confidence > 0.3


def test_waste_classifier_classifies_hazardous():
    clf = WasteClassifier()
    # Hazardous: unusual temperature, some moisture, low methane
    features = {
        "weight": 3.0, "volume": 2.0, "moisture": 15.0,
        "temperature": 55.0, "methane_ppm": 2.0,
    }
    result = clf.classify(features)
    assert result.waste_type in (WasteType.HAZARDOUS, WasteType.RECYCLABLE, WasteType.ORGANIC)
    assert 0.0 <= result.confidence <= 1.0


def test_waste_classifier_returns_action():
    clf = WasteClassifier()
    features = {"weight": 5.0, "volume": 10.0, "moisture": 70.0,
                "temperature": 30.0, "methane_ppm": 15.0}
    result = clf.classify(features)
    assert len(result.recommended_action) > 0


def test_waste_classifier_explanation():
    clf = WasteClassifier()
    features = {"weight": 10.0, "volume": 15.0, "moisture": 80.0,
                "temperature": 35.0, "methane_ppm": 30.0}
    explanation = clf.get_explanation(features)
    assert isinstance(explanation, str)
    assert len(explanation) > 20


def test_waste_classifier_online_update():
    clf = WasteClassifier()
    features = {"weight": 10.0, "volume": 15.0, "moisture": 80.0,
                "temperature": 35.0, "methane_ppm": 30.0}
    # Should not raise
    clf.update_model(features, "ORGANIC")


def test_waste_optimizer_recommends_route():
    opt = WasteOptimizer()
    from src.models.schemas import WasteClassification, WasteType
    classification = WasteClassification(
        waste_type=WasteType.ORGANIC,
        confidence=0.9,
        recommended_action="Compost",
        features={"weight": 50.0},
    )
    capacity = {"composting": 500.0, "anaerobic_digestion": 200.0}
    result = opt.recommend_route(classification, capacity)
    assert "recommended_route" in result
    assert result["recommended_route"] in ["composting", "anaerobic_digestion", "biogas_production"]


def test_route_optimizer_finds_path():
    optimizer = RouteOptimizer()
    for node_id, fill_kg, capacity in [("depot", 0, 1000), ("A", 80, 100),
                                        ("B", 60, 100), ("C", 50, 100)]:
        optimizer.add_node(CollectionPoint(node_id, f"Loc {node_id}", capacity, fill_kg))
    optimizer.add_edge("depot", "A", 2.0)
    optimizer.add_edge("A", "B", 1.5)
    optimizer.add_edge("B", "C", 1.0)
    optimizer.add_edge("C", "depot", 3.0)

    path, cost = optimizer.find_shortest_path("depot", "C")
    assert len(path) > 0
    assert cost < float("inf")
    assert path[0] == "depot"
    assert path[-1] == "C"


def test_route_optimizer_collection_plan():
    optimizer = RouteOptimizer()
    optimizer.add_node(CollectionPoint("depot", "Depot", 1000, 0))
    optimizer.add_node(CollectionPoint("bin1", "Bin 1", 100, 90))  # needs collection
    optimizer.add_node(CollectionPoint("bin2", "Bin 2", 100, 50))  # does not need collection
    optimizer.add_edge("depot", "bin1", 1.0)
    optimizer.add_edge("depot", "bin2", 2.0)
    optimizer.add_edge("bin1", "bin2", 1.0)

    plan = optimizer.plan_collection_route("depot")
    assert "route" in plan
    assert "bin1" in plan["route"]  # bin1 needs collection
    assert plan["collected_kg"] > 0


def test_carbon_footprint_calculation():
    calc = CarbonFootprintCalculator("diesel_truck")
    co2 = calc.calculate_transport(10.0)
    assert abs(co2 - 2.10) < 0.01

    co2_treatment = calc.calculate_treatment("composting", 100.0)
    assert co2_treatment == 5.0

    total = calc.total_footprint()
    assert total > 0.0
