"""Water treatment plant simulation for producing clean drinking water."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    import numpy as np
    _NP = True
except ImportError:
    _NP = False

try:
    from src.models.adaptive_ai import AdaptiveAIController
    _AI = True
except ImportError:
    _AI = False


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class WaterQualityMetrics:
    """Measurements describing the quality of a water sample."""

    turbidity: float = 10.0       # NTU
    ph: float = 7.0               # dimensionless
    dissolved_oxygen: float = 8.0 # mg/L
    chlorine: float = 0.0         # mg/L
    tds: float = 300.0            # mg/L total dissolved solids
    e_coli: float = 100.0         # CFU/100 mL
    temperature: float = 20.0     # °C


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TreatmentStage(str, Enum):
    """Stages of a municipal water treatment process."""
    INTAKE = "INTAKE"
    COAGULATION = "COAGULATION"
    SEDIMENTATION = "SEDIMENTATION"
    FILTRATION = "FILTRATION"
    DISINFECTION = "DISINFECTION"
    DISTRIBUTION = "DISTRIBUTION"


# WHO drinking water standards (boolean checks: True = compliant)
_WHO = {
    "turbidity":         lambda m: m.turbidity < 4.0,
    "ph":                lambda m: 6.5 <= m.ph <= 8.5,
    "dissolved_oxygen":  lambda m: m.dissolved_oxygen > 5.0,
    "chlorine":          lambda m: 0.2 <= m.chlorine <= 5.0,
    "tds":               lambda m: m.tds < 600.0,
    "e_coli":            lambda m: m.e_coli == 0.0,
    "temperature":       lambda m: m.temperature < 25.0,
}


# ---------------------------------------------------------------------------
# WaterTreatmentPlant
# ---------------------------------------------------------------------------

class WaterTreatmentPlant:
    """Simulates a small-scale water treatment plant (home/village)."""

    def __init__(self, capacity_m3_per_day: float = 10.0) -> None:
        """Initialise plant with given daily capacity in cubic metres."""
        self.capacity_m3_per_day = capacity_m3_per_day
        self._production_log: list[dict[str, Any]] = []

    def process_stage(
        self, stage: TreatmentStage, input_metrics: WaterQualityMetrics
    ) -> WaterQualityMetrics:
        """Simulate the effect of one treatment stage on water quality.

        Returns a new WaterQualityMetrics instance reflecting the changes
        produced by the given stage.
        """
        import copy
        m = copy.copy(input_metrics)

        if stage == TreatmentStage.INTAKE:
            pass  # no change at intake

        elif stage == TreatmentStage.COAGULATION:
            m.turbidity *= 0.50
            m.tds *= 0.95

        elif stage == TreatmentStage.SEDIMENTATION:
            m.turbidity *= (1 - 0.80)
            m.e_coli *= (1 - 0.60)

        elif stage == TreatmentStage.FILTRATION:
            m.turbidity = max(0.0, m.turbidity * 0.05)
            m.e_coli *= (1 - 0.90)

        elif stage == TreatmentStage.DISINFECTION:
            m.e_coli = 0.0
            m.chlorine = 0.5

        elif stage == TreatmentStage.DISTRIBUTION:
            m.chlorine = max(0.0, m.chlorine - 0.05)

        return m

    def run_full_treatment(
        self, raw_water: WaterQualityMetrics
    ) -> dict[str, WaterQualityMetrics]:
        """Run water through all treatment stages in order.

        Returns a dict mapping stage name to post-stage WaterQualityMetrics.
        """
        stages = list(TreatmentStage)
        results: dict[str, WaterQualityMetrics] = {}
        current = raw_water
        for stage in stages:
            current = self.process_stage(stage, current)
            results[stage.value] = current
        self._production_log.append({"raw": raw_water, "treated": current})
        return results

    def check_who_standards(self, metrics: WaterQualityMetrics) -> dict[str, bool]:
        """Check whether the given metrics comply with WHO drinking water standards.

        Returns a dict of parameter name → True/False (True = compliant).
        """
        return {param: check(metrics) for param, check in _WHO.items()}

    def estimate_chemical_costs(self, volume_m3: float) -> dict[str, float]:
        """Estimate chemical input costs for treating the given water volume.

        Returns a dict with cost categories in USD.
        """
        coagulant_cost = volume_m3 * 0.12    # alum/coagulant ~$0.12/m³
        chlorine_cost = volume_m3 * 0.05     # NaOCl ~$0.05/m³
        ph_adjustment = volume_m3 * 0.03     # lime/acid ~$0.03/m³
        total = coagulant_cost + chlorine_cost + ph_adjustment
        return {
            "coagulant_usd": round(coagulant_cost, 4),
            "chlorine_usd": round(chlorine_cost, 4),
            "ph_adjustment_usd": round(ph_adjustment, 4),
            "total_usd": round(total, 4),
        }

    def daily_production_report(self) -> dict[str, Any]:
        """Generate a daily production summary.

        Returns a dict with volume produced, compliance status, and cost.
        """
        volume = self.capacity_m3_per_day
        costs = self.estimate_chemical_costs(volume)
        raw_sample = WaterQualityMetrics()
        treatment = self.run_full_treatment(raw_sample)
        final_key = TreatmentStage.DISTRIBUTION.value
        final_metrics = treatment[final_key]
        compliance = self.check_who_standards(final_metrics)
        return {
            "volume_produced_m3": volume,
            "compliance": compliance,
            "all_compliant": all(compliance.values()),
            "costs": costs,
            "final_quality": final_metrics,
        }


# ---------------------------------------------------------------------------
# WaterQualityMonitor
# ---------------------------------------------------------------------------

class WaterQualityMonitor:
    """AI-powered water quality anomaly detector."""

    _FEATURES = [
        "turbidity", "ph", "dissolved_oxygen", "chlorine",
        "tds", "e_coli", "temperature",
    ]

    def __init__(self) -> None:
        """Initialise the monitor with an AdaptiveAIController."""
        if _AI:
            self._controller = AdaptiveAIController(
                domain="water_quality",
                feature_names=self._FEATURES,
                output_names=["anomaly_score"],
            )
        else:
            self._controller = None

    def analyze(self, metrics: WaterQualityMetrics) -> dict[str, Any]:
        """Analyse water quality metrics and detect anomalies.

        Returns a dict with anomaly flag, score, and WHO compliance summary.
        """
        features: dict[str, float] = {
            "turbidity": metrics.turbidity,
            "ph": metrics.ph,
            "dissolved_oxygen": metrics.dissolved_oxygen,
            "chlorine": metrics.chlorine,
            "tds": metrics.tds,
            "e_coli": metrics.e_coli,
            "temperature": metrics.temperature,
        }
        anomaly_score = 0.0
        if self._controller is not None:
            result = self._controller.predict(features)
            anomaly_score = float(result.get("anomaly_score", 0.0))

        plant = WaterTreatmentPlant()
        compliance = plant.check_who_standards(metrics)
        violations = [k for k, v in compliance.items() if not v]

        return {
            "anomaly_score": anomaly_score,
            "anomaly_detected": bool(violations),
            "violations": violations,
            "who_compliance": compliance,
        }
