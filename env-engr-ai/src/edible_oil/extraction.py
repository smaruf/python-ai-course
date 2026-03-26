"""
Edible oil extraction monitoring: Olive (PL standard) and Moringa/Marenga (BD standard).
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from src.models.schemas import EdibleOilMetrics, OilGrade


class CropType(Enum):
    OLIVE = "OLIVE"
    MORINGA = "MORINGA"  # "Marenga" in local Bengali usage


class ExtractionMonitor:
    """
    Monitors cold-press/solvent extraction of edible oils.
    Crops: Olive (Poland standard – PL), Moringa (Bangladesh standard – BD).
    """

    PROCESS_PARAMS: dict[CropType, dict] = {
        CropType.OLIVE: {
            "optimal_temp_range": (18.0, 27.0),   # Cold press
            "max_pressure": 400.0,                  # bar
            "target_moisture": 2.0,                 # %
            "standard": "PL",
            "typical_yield_pct": 20.0,              # % oil from olive weight
            "max_acidity": 0.8,
            "max_peroxide": 20.0,
        },
        CropType.MORINGA: {
            "optimal_temp_range": (25.0, 35.0),
            "max_pressure": 300.0,
            "target_moisture": 5.0,
            "standard": "BD",
            "typical_yield_pct": 35.0,              # Moringa seed ~35-38% oil
            "max_acidity": 1.0,
            "max_peroxide": 15.0,
        },
    }

    def __init__(self, batch_id: str, crop_type: CropType) -> None:
        self.batch_id = batch_id
        self.crop_type = crop_type
        self._params = self.PROCESS_PARAMS[crop_type]
        self._history: list[EdibleOilMetrics] = []
        self._recommendations: list[str] = []

    def update(self, metrics: EdibleOilMetrics) -> dict[str, Any]:
        """Process new metrics reading, return status dict."""
        self._history.append(metrics)
        grade = self.assess_quality(metrics)
        recs = self.get_process_recommendations()

        deviations: dict[str, Any] = {}
        temp_lo, temp_hi = self._params["optimal_temp_range"]
        if not (temp_lo <= metrics.temperature <= temp_hi):
            deviations["temperature"] = {
                "value": metrics.temperature,
                "optimal": (temp_lo, temp_hi),
            }
        if metrics.pressure > self._params["max_pressure"]:
            deviations["pressure"] = {
                "value": metrics.pressure,
                "max": self._params["max_pressure"],
            }
        if metrics.moisture_content > self._params["target_moisture"] * 1.5:
            deviations["moisture"] = {
                "value": metrics.moisture_content,
                "target": self._params["target_moisture"],
            }

        return {
            "batch_id": self.batch_id,
            "crop_type": self.crop_type.value,
            "standard": self._params["standard"],
            "assessed_grade": grade.value,
            "deviations": deviations,
            "recommendations": recs,
        }

    def calculate_yield(self, input_mass_kg: float, output_volume_L: float) -> float:
        """Calculate extraction yield as percentage."""
        # Moringa oil density ~0.90 g/mL, olive oil ~0.91 g/mL
        density = 0.910 if self.crop_type == CropType.OLIVE else 0.900
        output_mass_kg = output_volume_L * density
        if input_mass_kg <= 0:
            return 0.0
        return round((output_mass_kg / input_mass_kg) * 100.0, 2)

    def assess_quality(self, metrics: EdibleOilMetrics) -> OilGrade:
        """Assess quality grade based on acidity and peroxide values."""
        if self.crop_type == CropType.OLIVE:
            if metrics.acidity <= 0.8 and metrics.peroxide_value <= 20.0:
                return OilGrade.EXTRA_VIRGIN
            elif metrics.acidity <= 2.0 and metrics.peroxide_value <= 20.0:
                return OilGrade.VIRGIN
            elif metrics.acidity <= 0.3 and metrics.peroxide_value <= 5.0:
                return OilGrade.REFINED
            elif metrics.acidity <= 1.0 and metrics.peroxide_value <= 10.0:
                return OilGrade.POMACE
            return OilGrade.OFF_GRADE
        else:  # MORINGA / BD standard
            if metrics.acidity <= 1.0 and metrics.peroxide_value <= 15.0:
                return OilGrade.EXTRA_VIRGIN
            elif metrics.acidity <= 2.0 and metrics.peroxide_value <= 20.0:
                return OilGrade.VIRGIN
            elif metrics.acidity <= 0.5:
                return OilGrade.REFINED
            return OilGrade.OFF_GRADE

    def get_process_recommendations(self) -> list[str]:
        """Get process optimisation recommendations."""
        if not self._history:
            return ["No data yet – awaiting first reading"]
        latest = self._history[-1]
        recs: list[str] = []
        temp_lo, temp_hi = self._params["optimal_temp_range"]

        if latest.temperature < temp_lo:
            recs.append(
                f"Temperature {latest.temperature:.1f}°C below optimal "
                f"{temp_lo}–{temp_hi}°C – increase slightly"
            )
        elif latest.temperature > temp_hi:
            recs.append(
                f"Temperature {latest.temperature:.1f}°C above optimal "
                f"{temp_lo}–{temp_hi}°C – cool down (risk of oxidation)"
            )

        if latest.pressure > self._params["max_pressure"] * 0.9:
            recs.append(
                f"Pressure {latest.pressure:.0f} bar approaching max "
                f"{self._params['max_pressure']:.0f} bar – reduce feed rate"
            )

        if latest.moisture_content > self._params["target_moisture"] * 1.2:
            recs.append(
                f"Moisture {latest.moisture_content:.1f}% exceeds target "
                f"{self._params['target_moisture']:.1f}% – improve drying stage"
            )

        if latest.acidity > self._params["max_acidity"]:
            recs.append(
                f"Acidity {latest.acidity:.2f}% exceeds standard max "
                f"{self._params['max_acidity']:.2f}% – check fruit/seed freshness"
            )

        if not recs:
            recs.append("All parameters within optimal range")
        return recs

    @property
    def standard(self) -> str:
        return self._params["standard"]
