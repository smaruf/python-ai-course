"""
AI-powered quality control for edible oils (BD and PL standards).
"""
from __future__ import annotations

from typing import Any

import numpy as np

from src.models.neural_network import AdaptiveNeuralNetwork
from src.models.schemas import EdibleOilMetrics, OilGrade


class OilQualityController:
    """
    AI-powered quality control for edible oils.
    Uses AdaptiveNeuralNetwork for real-time quality prediction.
    Supports BD (Bangladesh) and PL (Poland) food safety standards.
    """

    # Grade thresholds per standard {standard: {grade: {param: max_value}}}
    STANDARDS: dict[str, dict[OilGrade, dict[str, float]]] = {
        "PL": {  # European/Polish standards (EU Regulation 2568/91)
            OilGrade.EXTRA_VIRGIN: {"acidity_max": 0.8,  "peroxide_max": 20.0, "moisture_max": 0.2},
            OilGrade.VIRGIN:       {"acidity_max": 2.0,  "peroxide_max": 20.0, "moisture_max": 0.2},
            OilGrade.REFINED:      {"acidity_max": 0.3,  "peroxide_max": 5.0,  "moisture_max": 0.1},
            OilGrade.POMACE:       {"acidity_max": 1.0,  "peroxide_max": 15.0, "moisture_max": 0.3},
        },
        "BD": {  # Bangladesh standards (BSTI DS 1065)
            OilGrade.EXTRA_VIRGIN: {"acidity_max": 1.0,  "peroxide_max": 15.0, "moisture_max": 0.5},
            OilGrade.VIRGIN:       {"acidity_max": 2.0,  "peroxide_max": 20.0, "moisture_max": 0.5},
            OilGrade.REFINED:      {"acidity_max": 0.5,  "peroxide_max": 10.0, "moisture_max": 0.2},
            OilGrade.POMACE:       {"acidity_max": 1.5,  "peroxide_max": 20.0, "moisture_max": 0.5},
        },
    }

    # Output node order must match GRADE_ORDER
    GRADE_ORDER = [OilGrade.EXTRA_VIRGIN, OilGrade.VIRGIN,
                   OilGrade.REFINED, OilGrade.POMACE, OilGrade.OFF_GRADE]

    def __init__(self, standard: str = "PL") -> None:
        if standard not in self.STANDARDS:
            raise ValueError(f"Unknown standard '{standard}'. Use 'PL' or 'BD'.")
        self.standard = standard
        # Features: temperature, pressure, moisture, acidity, peroxide_value
        self._model = AdaptiveNeuralNetwork(
            layer_sizes=[5, 12, 8, 5],
            activations=["relu", "relu", "sigmoid"],
            learning_rate=0.01,
        )
        self._pretrain()

    def _feature_vector(self, metrics: EdibleOilMetrics) -> np.ndarray:
        raw = np.array([
            metrics.temperature / 80.0,
            metrics.pressure / 500.0,
            metrics.moisture_content / 5.0,
            metrics.acidity / 5.0,
            metrics.peroxide_value / 50.0,
        ], dtype=float)
        return np.clip(raw, 0.0, 1.0)

    def _pretrain(self) -> None:
        rng = np.random.default_rng(2)
        X, y = [], []
        std_thresholds = self.STANDARDS[self.standard]

        for _ in range(400):
            acidity = rng.uniform(0.1, 5.0)
            peroxide = rng.uniform(1.0, 50.0)
            moisture = rng.uniform(0.0, 3.0)
            temp = rng.uniform(10.0, 70.0)
            pressure = rng.uniform(0.0, 500.0)

            # Label based on rule-based logic
            grade = OilGrade.OFF_GRADE
            for g in [OilGrade.EXTRA_VIRGIN, OilGrade.VIRGIN,
                      OilGrade.REFINED, OilGrade.POMACE]:
                th = std_thresholds.get(g, {})
                if (acidity <= th.get("acidity_max", 9999) and
                        peroxide <= th.get("peroxide_max", 9999) and
                        moisture <= th.get("moisture_max", 9999)):
                    grade = g
                    break

            label = np.zeros(5)
            label[self.GRADE_ORDER.index(grade)] = 1.0
            features = np.array([temp / 80, pressure / 500,
                                   moisture / 5, acidity / 5, peroxide / 50])
            X.append(np.clip(features, 0.0, 1.0))
            y.append(label)

        self._model.train(np.array(X), np.array(y), epochs=40, verbose=False)

    def predict_grade(self, metrics: EdibleOilMetrics) -> tuple[OilGrade, float]:
        """Returns (grade, confidence)."""
        x = self._feature_vector(metrics).reshape(1, -1)
        out = self._model.predict(x).flatten()
        idx = int(np.argmax(out))
        confidence = float(out[idx])
        return self.GRADE_ORDER[idx], round(confidence, 4)

    def check_compliance(self, metrics: EdibleOilMetrics) -> dict[str, bool]:
        """Check compliance of each measured parameter against standard."""
        std = self.STANDARDS[self.standard]
        grade, _ = self.predict_grade(metrics)
        thresholds = std.get(grade, {})

        return {
            "acidity_ok": metrics.acidity <= thresholds.get("acidity_max", float("inf")),
            "peroxide_ok": metrics.peroxide_value <= thresholds.get("peroxide_max", float("inf")),
            "moisture_ok": metrics.moisture_content <= thresholds.get("moisture_max", float("inf")),
            "grade": grade.value,
            "standard": self.standard,
        }

    def generate_quality_report(
        self, batch_id: str, readings: list[EdibleOilMetrics]
    ) -> str:
        """Generate a quality report for a batch."""
        if not readings:
            return f"Batch {batch_id}: No readings available"

        grades: list[OilGrade] = []
        confidences: list[float] = []
        acidities: list[float] = []
        peroxides: list[float] = []

        for r in readings:
            grade, conf = self.predict_grade(r)
            grades.append(grade)
            confidences.append(conf)
            acidities.append(r.acidity)
            peroxides.append(r.peroxide_value)

        final_grade = max(set(grades), key=grades.count)  # Mode
        avg_confidence = float(np.mean(confidences))
        avg_acidity = float(np.mean(acidities))
        avg_peroxide = float(np.mean(peroxides))
        compliant = self.check_compliance(readings[-1])

        lines = [
            f"=== Quality Report: Batch {batch_id} ===",
            f"Standard: {self.standard}",
            f"Readings analysed: {len(readings)}",
            f"Assigned grade: {final_grade.value} (confidence: {avg_confidence:.1%})",
            f"Average acidity: {avg_acidity:.3f}%",
            f"Average peroxide value: {avg_peroxide:.2f} meq O₂/kg",
            f"Compliance: {'PASS' if all(v for k, v in compliant.items() if k.endswith('_ok')) else 'FAIL'}",
        ]
        return "\n".join(lines)
