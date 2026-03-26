"""
Waste classification and optimisation using AdaptiveNeuralNetwork.
"""
from __future__ import annotations

import uuid
from typing import Any

import numpy as np

from src.models.neural_network import AdaptiveNeuralNetwork
from src.models.schemas import WasteClassification, WasteType


class WasteClassifier:
    """
    Classifies waste using AdaptiveNeuralNetwork.
    Features: weight(kg), volume(L), moisture(%), temperature(°C), methane_ppm
    Classes: ORGANIC, RECYCLABLE, HAZARDOUS, INERT
    """

    FEATURE_NAMES = ["weight", "volume", "moisture", "temperature", "methane_ppm"]
    CLASS_NAMES = ["ORGANIC", "RECYCLABLE", "HAZARDOUS", "INERT"]

    # Recommended actions per class
    ACTIONS = {
        "ORGANIC":    "Route to anaerobic digestion or composting facility",
        "RECYCLABLE": "Route to materials recovery facility (MRF)",
        "HAZARDOUS":  "Route to secure hazardous waste treatment facility",
        "INERT":      "Route to inert landfill or construction aggregate reuse",
    }

    def __init__(self) -> None:
        self._model = AdaptiveNeuralNetwork(
            layer_sizes=[5, 16, 8, 4],
            activations=["relu", "relu", "sigmoid"],
            learning_rate=0.01,
            adaptation_rate=0.001,
        )
        self._label_encoder = {name: i for i, name in enumerate(self.CLASS_NAMES)}
        self._pretrain()

    def _feature_vector(self, features: dict[str, float]) -> np.ndarray:
        raw = np.array([features.get(f, 0.0) for f in self.FEATURE_NAMES], dtype=float)
        # Normalise using domain knowledge
        norms = np.array([50.0, 50.0, 100.0, 50.0, 100.0])
        return np.clip(raw / norms, 0.0, 1.0)

    def _make_label_vector(self, class_name: str) -> np.ndarray:
        y = np.zeros(4)
        y[self._label_encoder[class_name]] = 1.0
        return y

    def _generate_synthetic_samples(self) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(0)
        samples_per_class = 200
        X_list, y_list = [], []

        profiles = {
            "ORGANIC":    {"weight": (1, 20),  "volume": (1, 30),  "moisture": (50, 95), "temperature": (20, 45), "methane_ppm": (5, 50)},
            "RECYCLABLE": {"weight": (0.1, 5), "volume": (0.5, 20),"moisture": (0, 20),  "temperature": (15, 30), "methane_ppm": (0, 2)},
            "HAZARDOUS":  {"weight": (0.1, 10),"volume": (0.1, 10),"moisture": (0, 30),  "temperature": (10, 60), "methane_ppm": (0, 5)},
            "INERT":      {"weight": (5, 100), "volume": (5, 150), "moisture": (0, 10),  "temperature": (10, 25), "methane_ppm": (0, 1)},
        }

        for cls, ranges in profiles.items():
            for _ in range(samples_per_class):
                sample = {
                    feat: rng.uniform(lo, hi)
                    for feat, (lo, hi) in ranges.items()
                }
                X_list.append(self._feature_vector(sample))
                y_list.append(self._make_label_vector(cls))

        return np.array(X_list), np.array(y_list)

    def _pretrain(self) -> None:
        X, y = self._generate_synthetic_samples()
        self._model.train(X, y, epochs=50, batch_size=32, verbose=False)

    def classify(self, features: dict[str, float]) -> WasteClassification:
        """Classify waste and return WasteClassification with confidence."""
        x = self._feature_vector(features)
        out = self._model.predict(x.reshape(1, -1)).flatten()
        class_idx = int(np.argmax(out))
        confidence = float(out[class_idx])
        waste_class = self.CLASS_NAMES[class_idx]
        return WasteClassification(
            reading_id=str(uuid.uuid4()),
            waste_type=WasteType(waste_class),
            confidence=round(confidence, 4),
            recommended_action=self.ACTIONS[waste_class],
            features=dict(features),
        )

    def update_model(self, features: dict[str, float], true_label: str) -> None:
        """Online update from verified classification."""
        x = self._feature_vector(features)
        y = self._make_label_vector(true_label.upper())
        self._model.update_online(x, y)

    def get_explanation(self, features: dict[str, float]) -> str:
        """Generate human-readable explanation for the classification."""
        classification = self.classify(features)
        moisture = features.get("moisture", 0.0)
        methane = features.get("methane_ppm", 0.0)
        weight = features.get("weight", 0.0)

        reasons: list[str] = []
        if classification.waste_type == WasteType.ORGANIC:
            reasons.append(f"High moisture content ({moisture:.1f}%) suggests biodegradable material")
            if methane > 10:
                reasons.append(f"Methane emission ({methane:.1f} ppm) indicates active decomposition")
        elif classification.waste_type == WasteType.RECYCLABLE:
            reasons.append(f"Low moisture ({moisture:.1f}%) and weight ({weight:.1f} kg) suggest dry recyclables")
        elif classification.waste_type == WasteType.HAZARDOUS:
            reasons.append("Sensor profile matches known hazardous material patterns")
        elif classification.waste_type == WasteType.INERT:
            reasons.append(f"High mass ({weight:.1f} kg) with very low moisture indicates inert material")

        reason_str = "; ".join(reasons) if reasons else "AI pattern matching"
        return (
            f"Classified as {classification.waste_type.value} "
            f"(confidence: {classification.confidence:.1%}). "
            f"Reason: {reason_str}. "
            f"Action: {classification.recommended_action}"
        )


class WasteOptimizer:
    """Recommends optimal processing routes for classified waste."""

    PROCESSING_ROUTES: dict[str, list[str]] = {
        "ORGANIC":    ["composting", "anaerobic_digestion", "biogas_production"],
        "RECYCLABLE": ["sorting", "cleaning", "material_recovery"],
        "HAZARDOUS":  ["neutralization", "secure_landfill", "incineration"],
        "INERT":      ["landfill", "construction_aggregate", "road_base"],
    }

    # kg CO2-eq per kg waste per route
    CARBON_FACTORS: dict[str, float] = {
        "composting":          0.05,
        "anaerobic_digestion": -0.30,  # Net negative (avoided emissions)
        "biogas_production":   -0.50,
        "sorting":             0.02,
        "cleaning":            0.03,
        "material_recovery":   -0.20,
        "neutralization":      0.10,
        "secure_landfill":     0.80,
        "incineration":        1.20,
        "landfill":            0.60,
        "construction_aggregate": 0.01,
        "road_base":           0.02,
    }

    def recommend_route(
        self,
        classification: WasteClassification,
        capacity: dict[str, float],
    ) -> dict[str, Any]:
        """
        Recommend optimal route based on classification and facility capacity.
        capacity: {route_name: available_capacity_kg}
        """
        waste_class = classification.waste_type.value
        routes = self.PROCESSING_ROUTES.get(waste_class, ["landfill"])
        volume_kg = classification.features.get("weight", 1.0)

        # Score routes: prefer low carbon AND sufficient capacity
        scored: list[tuple[float, str]] = []
        for route in routes:
            cap = capacity.get(route, float("inf"))
            if cap < volume_kg:
                continue  # Skip full facility
            carbon = self.calculate_carbon_footprint(route, volume_kg)
            scored.append((carbon, route))

        if not scored:
            # Fallback: use all routes ignoring capacity
            scored = [(self.calculate_carbon_footprint(r, volume_kg), r) for r in routes]

        scored.sort(key=lambda x: x[0])
        best_carbon, best_route = scored[0]

        return {
            "recommended_route": best_route,
            "waste_class": waste_class,
            "carbon_footprint_kg_co2": round(best_carbon, 4),
            "volume_kg": volume_kg,
            "all_options": [{"route": r, "carbon": round(self.calculate_carbon_footprint(r, volume_kg), 4)} for _, r in scored],
        }

    def calculate_carbon_footprint(self, route: str, volume_kg: float) -> float:
        factor = self.CARBON_FACTORS.get(route, 0.5)
        return factor * volume_kg

    def generate_report(self, classifications: list[WasteClassification]) -> str:
        lines: list[str] = ["=== Waste Management Report ===", ""]
        by_type: dict[str, list[WasteClassification]] = {}
        for c in classifications:
            key = c.waste_type.value
            by_type.setdefault(key, []).append(c)

        total_weight = sum(c.features.get("weight", 0.0) for c in classifications)
        lines.append(f"Total waste processed: {total_weight:.1f} kg")
        lines.append(f"Total batches: {len(classifications)}")
        lines.append("")

        for waste_type, batch in by_type.items():
            type_weight = sum(c.features.get("weight", 0.0) for c in batch)
            avg_confidence = np.mean([c.confidence for c in batch])
            lines.append(f"{waste_type}: {len(batch)} batches, {type_weight:.1f} kg, "
                         f"avg confidence {avg_confidence:.1%}")

        lines.append("")
        lines.append("Recommended Actions:")
        for waste_type, batch in by_type.items():
            routes = self.PROCESSING_ROUTES.get(waste_type, ["landfill"])
            lines.append(f"  {waste_type}: {' -> '.join(routes)}")

        return "\n".join(lines)
