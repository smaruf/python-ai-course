"""Olive and Moringa cross-planting feasibility guide for Bangladesh and Poland."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ClimateProfile:
    """Climate and soil profile for a country or region."""
    country: str
    avg_temp_c: float
    min_temp_c: float
    max_temp_c: float
    annual_rainfall_mm: float
    humidity_pct: float
    frost_days_per_year: int
    soil_ph: float


@dataclass
class CropRequirements:
    """Agronomic requirements for a crop."""
    crop_name: str
    optimal_temp_range: tuple[float, float]
    min_temp_tolerance: float
    annual_rainfall_min: float
    annual_rainfall_max: float
    soil_ph_range: tuple[float, float]
    frost_tolerance: bool
    days_to_first_harvest: int
    yield_kg_per_hectare: float


@dataclass
class PlantingFeasibility:
    """Feasibility assessment for growing a crop in a specific country."""
    crop: str
    country: str
    feasibility_score: float          # 0.0 – 1.0
    risk_level: str
    adaptations_needed: list[str]
    estimated_yield_pct_of_optimal: float


# ---------------------------------------------------------------------------
# AgronomyAdvisor
# ---------------------------------------------------------------------------

class AgronomyAdvisor:
    """Provides planting feasibility assessments and recommendations for
    Olive, Moringa, Sunflower, and Rapeseed in Bangladesh and Poland."""

    # Pre-loaded climate profiles
    _CLIMATES: dict[str, ClimateProfile] = {
        "BD": ClimateProfile(
            country="Bangladesh",
            avg_temp_c=25.0,
            min_temp_c=8.0,
            max_temp_c=40.0,
            annual_rainfall_mm=2000,
            humidity_pct=75.0,
            frost_days_per_year=0,
            soil_ph=6.0,
        ),
        "PL": ClimateProfile(
            country="Poland",
            avg_temp_c=8.5,
            min_temp_c=-20.0,
            max_temp_c=35.0,
            annual_rainfall_mm=600,
            humidity_pct=75.0,
            frost_days_per_year=120,
            soil_ph=6.5,
        ),
    }

    # Pre-loaded crop requirements
    _CROPS: dict[str, CropRequirements] = {
        "OLIVE": CropRequirements(
            crop_name="OLIVE",
            optimal_temp_range=(15.0, 25.0),
            min_temp_tolerance=-10.0,
            annual_rainfall_min=400,
            annual_rainfall_max=800,
            soil_ph_range=(6.0, 8.5),
            frost_tolerance=True,
            days_to_first_harvest=4 * 365,
            yield_kg_per_hectare=3000,
        ),
        "MORINGA": CropRequirements(
            crop_name="MORINGA",
            optimal_temp_range=(25.0, 35.0),
            min_temp_tolerance=0.0,
            annual_rainfall_min=250,
            annual_rainfall_max=2000,
            soil_ph_range=(5.0, 9.0),
            frost_tolerance=False,
            days_to_first_harvest=90,
            yield_kg_per_hectare=8000,
        ),
        "SUNFLOWER": CropRequirements(
            crop_name="SUNFLOWER",
            optimal_temp_range=(18.0, 28.0),
            min_temp_tolerance=-5.0,
            annual_rainfall_min=500,
            annual_rainfall_max=1000,
            soil_ph_range=(6.0, 7.5),
            frost_tolerance=False,
            days_to_first_harvest=120,
            yield_kg_per_hectare=2500,
        ),
        "RAPESEED": CropRequirements(
            crop_name="RAPESEED",
            optimal_temp_range=(10.0, 20.0),
            min_temp_tolerance=-15.0,
            annual_rainfall_min=450,
            annual_rainfall_max=900,
            soil_ph_range=(5.5, 7.5),
            frost_tolerance=True,
            days_to_first_harvest=300,
            yield_kg_per_hectare=3500,
        ),
    }

    # Cold-hardy olive varieties recommended for Poland
    _OLIVE_VARIETIES_PL = ["Arbequina", "Leccino", "Koroneiki"]
    # Drought-tolerant moringa varieties for Bangladesh
    _MORINGA_VARIETIES_BD = ["PKM-1", "ODC3", "Bhagya"]

    def assess_feasibility(
        self, crop_name: str, country: str
    ) -> PlantingFeasibility:
        """Score the feasibility of growing *crop_name* in *country*.

        Scoring factors: temperature match, rainfall match, frost risk,
        and soil pH compatibility.  Returns a PlantingFeasibility instance.
        """
        crop_key = crop_name.upper()
        country_key = country.upper()

        if crop_key not in self._CROPS or country_key not in self._CLIMATES:
            return PlantingFeasibility(
                crop=crop_name,
                country=country,
                feasibility_score=0.0,
                risk_level="UNKNOWN",
                adaptations_needed=["Unknown crop or country"],
                estimated_yield_pct_of_optimal=0.0,
            )

        crop = self._CROPS[crop_key]
        climate = self._CLIMATES[country_key]
        adaptations: list[str] = []

        # --- Temperature score (0-1) ---
        opt_lo, opt_hi = crop.optimal_temp_range
        avg = climate.avg_temp_c
        temp_range = opt_hi - opt_lo
        if temp_range == 0:
            temp_score = 1.0 if avg == opt_lo else 0.0
        else:
            overshoot = max(0.0, avg - opt_hi)
            undershoot = max(0.0, opt_lo - avg)
            deviation = (overshoot + undershoot) / temp_range
            temp_score = max(0.0, 1.0 - deviation)

        if climate.min_temp_c < crop.min_temp_tolerance:
            temp_score *= 0.5
            adaptations.append(
                f"Protect from frost (country min {climate.min_temp_c}°C < crop tolerance {crop.min_temp_tolerance}°C)"
            )

        # --- Rainfall score (0-1) ---
        rain = climate.annual_rainfall_mm
        if crop.annual_rainfall_min <= rain <= crop.annual_rainfall_max:
            rain_score = 1.0
        elif rain < crop.annual_rainfall_min:
            gap = crop.annual_rainfall_min - rain
            rain_score = max(0.0, 1.0 - gap / crop.annual_rainfall_min)
            adaptations.append(f"Supplemental irrigation needed ({gap:.0f} mm deficit)")
        else:
            excess = rain - crop.annual_rainfall_max
            rain_score = max(0.0, 1.0 - excess / crop.annual_rainfall_max)
            adaptations.append(f"Drainage management needed ({excess:.0f} mm excess)")

        # --- Frost score (0-1) ---
        frost_score = 1.0
        if not crop.frost_tolerance and climate.frost_days_per_year > 60:
            frost_score = 0.1
            adaptations.append(
                f"Severe frost risk: {climate.frost_days_per_year} frost days/year, crop not frost-tolerant"
            )
        elif not crop.frost_tolerance and climate.frost_days_per_year > 0:
            frost_score = 0.6
            adaptations.append("Light frost protection recommended")

        # --- Soil pH score (0-1) ---
        ph_lo, ph_hi = crop.soil_ph_range
        soil_ph = climate.soil_ph
        if ph_lo <= soil_ph <= ph_hi:
            ph_score = 1.0
        else:
            deviation = min(abs(soil_ph - ph_lo), abs(soil_ph - ph_hi))
            ph_score = max(0.0, 1.0 - deviation / 2.0)
            adaptations.append(f"Soil pH amendment required (current {soil_ph}, target {ph_lo}-{ph_hi})")

        # Weighted overall score
        overall = 0.35 * temp_score + 0.30 * rain_score + 0.25 * frost_score + 0.10 * ph_score

        if overall >= 0.75:
            risk = "LOW"
        elif overall >= 0.50:
            risk = "MEDIUM"
        elif overall >= 0.25:
            risk = "HIGH"
        else:
            risk = "VERY_HIGH"

        yield_pct = overall * 100.0

        return PlantingFeasibility(
            crop=crop_key,
            country=country_key,
            feasibility_score=round(overall, 3),
            risk_level=risk,
            adaptations_needed=adaptations,
            estimated_yield_pct_of_optimal=round(yield_pct, 1),
        )

    def recommend_varieties(self, crop_name: str, country: str) -> list[str]:
        """Recommend suitable varieties for the crop–country combination.

        Returns cold-hardy olive varieties for Poland, drought-tolerant
        Moringa varieties for Bangladesh, and generic guidance otherwise.
        """
        crop_key = crop_name.upper()
        country_key = country.upper()

        if crop_key == "OLIVE" and country_key == "PL":
            return self._OLIVE_VARIETIES_PL
        if crop_key == "MORINGA" and country_key == "BD":
            return self._MORINGA_VARIETIES_BD
        if crop_key == "RAPESEED" and country_key == "PL":
            return ["Cabriolet", "Orkan", "Visby"]
        if crop_key == "SUNFLOWER" and country_key == "BD":
            return ["BARI Surjomukhi-2", "Hysun 33"]
        return [f"{crop_key} – standard commercial varieties"]

    def planting_calendar(
        self, crop_name: str, country: str
    ) -> dict[str, str]:
        """Return a month-by-month planting calendar for the crop and country.

        Returns a dict mapping month name to recommended activity.
        """
        crop_key = crop_name.upper()
        country_key = country.upper()

        calendars: dict[tuple[str, str], dict[str, str]] = {
            ("OLIVE", "BD"): {
                "January": "Pruning, soil amendment",
                "February": "Fertilisation",
                "March": "Planting season begins",
                "April": "Irrigation management",
                "May": "Pest monitoring",
                "June": "Summer maintenance",
                "July": "Fruit development",
                "August": "Irrigation increase",
                "September": "Early harvest",
                "October": "Main harvest",
                "November": "Post-harvest pruning",
                "December": "Rest period",
            },
            ("OLIVE", "PL"): {
                "January": "Frost protection, dormant pruning",
                "February": "Inspect winter damage",
                "March": "Remove frost protection gradually",
                "April": "Fertilisation, bud burst monitoring",
                "May": "Pest monitoring, irrigation setup",
                "June": "Flower pollination support",
                "July": "Fruit development, irrigation",
                "August": "Irrigation, green olive stage",
                "September": "Early harvest (green olives)",
                "October": "Main harvest, cold hardy prep",
                "November": "Apply winter mulch",
                "December": "Frost protection applied",
            },
            ("MORINGA", "BD"): {
                "January": "Harvest leaves and pods",
                "February": "Pruning, compost application",
                "March": "New planting if needed",
                "April": "Irrigation during dry spell",
                "May": "Pre-monsoon fertilisation",
                "June": "Monsoon – reduce irrigation",
                "July": "Weed management",
                "August": "Drainage monitoring",
                "September": "Post-monsoon fertilise",
                "October": "Pod harvest",
                "November": "Leaf harvest peak",
                "December": "Harvest and market",
            },
            ("MORINGA", "PL"): {
                "January": "Greenhouse growing only",
                "February": "Seed germination in greenhouse",
                "March": "Seedling preparation",
                "April": "Transplant after last frost risk",
                "May": "Outdoor planting (greenhouse hardened)",
                "June": "Rapid growth, irrigation",
                "July": "First leaf harvest",
                "August": "Continuous harvest",
                "September": "Final harvest before frost",
                "October": "Bring indoors / end season",
                "November": "Indoor overwintering if desired",
                "December": "Indoor growing",
            },
            ("SUNFLOWER", "BD"): {
                "January": "Soil preparation",
                "February": "Sowing (Rabi season)",
                "March": "Seedling establishment",
                "April": "Vegetative growth, fertilise",
                "May": "Flowering",
                "June": "Seed fill",
                "July": "Harvest",
                "August": "Land preparation for next crop",
                "September": "Kharif sowing possible",
                "October": "Vegetative growth",
                "November": "Flowering (Kharif)",
                "December": "Harvest (Kharif)",
            },
            ("SUNFLOWER", "PL"): {
                "January": "Planning, seed selection",
                "February": "Soil testing",
                "March": "Soil preparation",
                "April": "Sowing (late April)",
                "May": "Emergence and establishment",
                "June": "Vegetative growth",
                "July": "Budding and flowering",
                "August": "Seed fill",
                "September": "Harvest",
                "October": "Post-harvest soil work",
                "November": "Cover crop or ploughing",
                "December": "Rest",
            },
            ("RAPESEED", "BD"): {
                "January": "Harvest (Rabi season)",
                "February": "Post-harvest soil prep",
                "March": "Summer crop rotation",
                "April": "Monitor soil",
                "May": "Irrigate if needed",
                "June": "Prepare for Kharif sowing",
                "July": "Sowing (Kharif)",
                "August": "Seedling establishment",
                "September": "Vegetative growth",
                "October": "Flowering",
                "November": "Pod fill",
                "December": "Pre-harvest",
            },
            ("RAPESEED", "PL"): {
                "January": "Winter crop dormant",
                "February": "Monitor winter crop",
                "March": "Spring fertilisation",
                "April": "Rapid growth",
                "May": "Flowering",
                "June": "Pod fill",
                "July": "Harvest",
                "August": "Soil preparation, early sowing",
                "September": "Autumn sowing",
                "October": "Establishment before frost",
                "November": "Crop in winter dormancy",
                "December": "Winter dormancy",
            },
        }

        key = (crop_key, country_key)
        if key in calendars:
            return calendars[key]

        return {m: "Consult local agronomist" for m in [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]}

    def cross_planting_report(self) -> str:
        """Generate a comprehensive cross-planting report for BD↔PL.

        Returns a multi-line formatted string suitable for display or export.
        """
        lines = [
            "=" * 70,
            "  CROSS-PLANTING FEASIBILITY REPORT: Bangladesh ↔ Poland",
            "=" * 70,
            "",
        ]
        for crop in ["OLIVE", "MORINGA", "SUNFLOWER", "RAPESEED"]:
            lines.append(f"CROP: {crop}")
            lines.append("-" * 50)
            for country in ["BD", "PL"]:
                feas = self.assess_feasibility(crop, country)
                climate = self._CLIMATES[country]
                lines.append(
                    f"  {climate.country} ({country}): "
                    f"Score={feas.feasibility_score:.2f}  "
                    f"Risk={feas.risk_level}  "
                    f"Est. Yield={feas.estimated_yield_pct_of_optimal:.0f}% of optimal"
                )
                if feas.adaptations_needed:
                    for a in feas.adaptations_needed:
                        lines.append(f"    ⚠ {a}")
                varieties = self.recommend_varieties(crop, country)
                lines.append(f"    Recommended varieties: {', '.join(varieties)}")
            lines.append("")

        lines += [
            "KEY INSIGHTS",
            "-" * 50,
            "• Bangladesh excels for Moringa (tropical conditions ideal).",
            "• Poland excels for Rapeseed and cold-climate oil crops.",
            "• Olive cultivation in Poland requires cold-hardy varieties",
            "  and frost protection (Arbequina, Leccino, Koroneiki).",
            "• Moringa in Poland only viable in greenhouses or warm summers.",
            "• Cross-pollination of expertise: BD Moringa leaf powder export",
            "  to PL health-food market; PL Rapeseed oil export to BD.",
            "=" * 70,
        ]
        return "\n".join(lines)

    def land_requirements(
        self, crop_name: str, target_yield_kg: float
    ) -> dict[str, Any]:
        """Calculate how much land is needed to achieve a target yield.

        Returns a dict with land area (hectares and m²) and yield assumptions.
        """
        crop_key = crop_name.upper()
        if crop_key not in self._CROPS:
            return {"error": f"Unknown crop: {crop_name}"}

        crop = self._CROPS[crop_key]
        hectares = target_yield_kg / crop.yield_kg_per_hectare
        return {
            "crop": crop_key,
            "target_yield_kg": target_yield_kg,
            "land_required_ha": round(hectares, 4),
            "land_required_m2": round(hectares * 10_000, 1),
            "assumed_yield_kg_per_ha": crop.yield_kg_per_hectare,
            "days_to_first_harvest": crop.days_to_first_harvest,
        }
