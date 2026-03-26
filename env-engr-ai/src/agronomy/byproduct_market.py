"""Byproduct catalog and selling strategy for the circular economy platform."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Byproduct:
    """Describes a byproduct from a production process."""
    name: str
    source_process: str
    quantity_per_unit_input: float
    unit: str
    market_price_usd_per_unit: float
    shelf_life_days: int
    market_channels: list[str]
    description: str


@dataclass
class MarketAnalysis:
    """Revenue and market analysis for a single byproduct."""
    byproduct_name: str
    monthly_revenue_usd: float
    annual_revenue_usd: float
    market_size: str
    competition_level: str
    recommended_channels: list[str]


# ---------------------------------------------------------------------------
# ByproductMarketManager
# ---------------------------------------------------------------------------

class ByproductMarketManager:
    """Manages the byproduct catalogue and market analysis for all production
    processes in the circular economy platform."""

    def __init__(self) -> None:
        """Initialise with pre-loaded byproducts from all platform processes."""
        self._byproducts: list[Byproduct] = [
            # --- waste_management ---
            Byproduct(
                name="compost",
                source_process="waste_management",
                quantity_per_unit_input=0.3,
                unit="kg",
                market_price_usd_per_unit=0.05,
                shelf_life_days=365,
                market_channels=["local farmers", "garden centers"],
                description="Finished compost from organic waste decomposition.",
            ),
            Byproduct(
                name="biogas",
                source_process="waste_management",
                quantity_per_unit_input=0.2,
                unit="m3",
                market_price_usd_per_unit=0.50,
                shelf_life_days=0,
                market_channels=["local grid", "cooking fuel"],
                description="Methane-rich biogas from anaerobic digestion.",
            ),
            Byproduct(
                name="recycled_materials",
                source_process="waste_management",
                quantity_per_unit_input=0.15,
                unit="kg",
                market_price_usd_per_unit=0.10,
                shelf_life_days=730,
                market_channels=["recyclers", "manufacturers"],
                description="Sorted recyclable materials (plastics, metals, paper).",
            ),
            # --- biofuel ---
            Byproduct(
                name="CO2_food_grade",
                source_process="biofuel",
                quantity_per_unit_input=0.48,
                unit="kg",
                market_price_usd_per_unit=0.15,
                shelf_life_days=0,
                market_channels=["beverage industry", "greenhouses"],
                description="Food-grade CO₂ captured during fermentation.",
            ),
            Byproduct(
                name="distillers_grain",
                source_process="biofuel",
                quantity_per_unit_input=0.30,
                unit="kg",
                market_price_usd_per_unit=0.30,
                shelf_life_days=90,
                market_channels=["animal feed"],
                description="Protein-rich distillers grain (animal feed).",
            ),
            Byproduct(
                name="glycerol",
                source_process="biofuel",
                quantity_per_unit_input=0.10,
                unit="kg",
                market_price_usd_per_unit=0.40,
                shelf_life_days=365,
                market_channels=["cosmetics", "pharmaceuticals"],
                description="Crude glycerol from biodiesel transesterification.",
            ),
            # --- edible_oil ---
            Byproduct(
                name="olive_pomace",
                source_process="edible_oil",
                quantity_per_unit_input=0.40,
                unit="kg",
                market_price_usd_per_unit=0.25,
                shelf_life_days=180,
                market_channels=["cosmetics", "pomace oil production"],
                description="Olive pomace remaining after oil extraction.",
            ),
            Byproduct(
                name="moringa_seed_cake",
                source_process="edible_oil",
                quantity_per_unit_input=0.60,
                unit="kg",
                market_price_usd_per_unit=0.20,
                shelf_life_days=180,
                market_channels=["fertilizer", "water purification"],
                description="Moringa seed press cake; excellent organic fertilizer.",
            ),
            Byproduct(
                name="moringa_leaf_powder",
                source_process="edible_oil",
                quantity_per_unit_input=0.05,
                unit="kg",
                market_price_usd_per_unit=15.0,
                shelf_life_days=730,
                market_channels=["health food stores", "online retail", "export"],
                description="Dried moringa leaf powder – premium nutritional supplement.",
            ),
            # --- renewable_energy ---
            Byproduct(
                name="excess_electricity",
                source_process="renewable_energy",
                quantity_per_unit_input=1.0,
                unit="kWh",
                market_price_usd_per_unit=0.08,
                shelf_life_days=0,
                market_channels=["grid feed-in", "local micro-grid"],
                description="Excess solar/wind electricity sold back to the grid.",
            ),
            Byproduct(
                name="heat_recovery",
                source_process="renewable_energy",
                quantity_per_unit_input=1.0,
                unit="kWh",
                market_price_usd_per_unit=0.02,
                shelf_life_days=0,
                market_channels=["district heating", "industrial heat users"],
                description="Recovered waste heat from generation systems.",
            ),
            # --- water_treatment ---
            Byproduct(
                name="treated_sludge",
                source_process="water_treatment",
                quantity_per_unit_input=0.05,
                unit="kg",
                market_price_usd_per_unit=0.03,
                shelf_life_days=30,
                market_channels=["fertilizer", "land application"],
                description="Treated water treatment sludge for land application.",
            ),
        ]
        self._byproduct_index: dict[str, Byproduct] = {b.name: b for b in self._byproducts}

    def list_byproducts(self, source_process: str | None = None) -> list[Byproduct]:
        """Return all byproducts, optionally filtered by source_process.

        Args:
            source_process: If provided, only byproducts from this process are
                returned.  Pass None to get all.
        """
        if source_process is None:
            return list(self._byproducts)
        sp = source_process.lower()
        return [b for b in self._byproducts if b.source_process == sp]

    def calculate_monthly_revenue(
        self, production_data: dict[str, float]
    ) -> dict[str, Any]:
        """Estimate monthly revenue from byproduct sales.

        Args:
            production_data: maps *source_process* name to monthly production
                volume in the primary input unit (e.g. kg waste processed).

        Returns a dict with per-byproduct revenue and a total.
        """
        revenues: dict[str, float] = {}
        total = 0.0

        for byproduct in self._byproducts:
            process = byproduct.source_process
            if process not in production_data:
                continue
            input_volume = production_data[process]
            quantity = input_volume * byproduct.quantity_per_unit_input
            revenue = quantity * byproduct.market_price_usd_per_unit
            revenues[byproduct.name] = round(revenue, 2)
            total += revenue

        return {
            "byproduct_revenues_usd": revenues,
            "total_monthly_revenue_usd": round(total, 2),
            "annual_projection_usd": round(total * 12, 2),
        }

    def market_opportunity_report(self) -> str:
        """Generate a formatted market opportunity report for all byproducts.

        Returns a multi-line string report.
        """
        lines = [
            "=" * 65,
            "  BYPRODUCT MARKET OPPORTUNITY REPORT",
            "=" * 65,
            "",
        ]
        by_process: dict[str, list[Byproduct]] = {}
        for b in self._byproducts:
            by_process.setdefault(b.source_process, []).append(b)

        for process, products in sorted(by_process.items()):
            lines.append(f"Process: {process.upper()}")
            lines.append("-" * 45)
            for b in products:
                lines.append(f"  {b.name}")
                lines.append(f"    Price : ${b.market_price_usd_per_unit:.2f}/{b.unit}")
                lines.append(f"    Channels: {', '.join(b.market_channels)}")
                lines.append(f"    {b.description}")
            lines.append("")

        lines += [
            "TOP OPPORTUNITIES BY UNIT PRICE",
            "-" * 45,
        ]
        sorted_bp = sorted(self._byproducts, key=lambda b: b.market_price_usd_per_unit, reverse=True)
        for b in sorted_bp[:5]:
            lines.append(f"  {b.name} (${b.market_price_usd_per_unit:.2f}/{b.unit}) — {b.source_process}")

        lines.append("=" * 65)
        return "\n".join(lines)

    def sales_channels_guide(self, byproduct_name: str) -> dict[str, Any]:
        """Return a detailed selling guide for a specific byproduct.

        Returns a dict with channels, pricing, and shelf-life information.
        """
        name = byproduct_name.lower()
        byproduct = self._byproduct_index.get(name)
        if byproduct is None:
            return {"error": f"Byproduct '{byproduct_name}' not found."}

        return {
            "byproduct": byproduct.name,
            "source_process": byproduct.source_process,
            "market_channels": byproduct.market_channels,
            "unit_price_usd": byproduct.market_price_usd_per_unit,
            "unit": byproduct.unit,
            "shelf_life_days": byproduct.shelf_life_days,
            "description": byproduct.description,
            "tips": [
                f"List on agricultural marketplace for {byproduct.market_channels[0]}",
                "Build local relationships for recurring orders",
                "Ensure quality certification for premium pricing",
            ],
        }
