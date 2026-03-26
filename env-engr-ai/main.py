#!/usr/bin/env python3
"""
Environmental Engineering AI Platform – CLI entry point.
"""
from __future__ import annotations

import random
import time
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    name="env-engr-ai",
    help="🌱 Environmental Engineering AI Platform",
    add_completion=False,
)
console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _banner() -> None:
    console.print(Panel(
        "[bold green]Environmental Engineering AI Platform[/bold green]\n"
        "[dim]Waste Management · Biofuel · Edible Oil · Renewable Energy[/dim]",
        style="green",
    ))


def _demo_waste_management() -> None:
    from src.waste_management.classifier import WasteClassifier, WasteOptimizer
    from src.waste_management.optimizer import (
        CollectionPoint, RouteOptimizer, CarbonFootprintCalculator
    )

    console.rule("[bold cyan]Waste Management Module[/bold cyan]")
    clf = WasteClassifier()
    opt = WasteOptimizer()

    samples = [
        {"weight": 12.0, "volume": 18.0, "moisture": 82.0, "temperature": 32.0, "methane_ppm": 25.0},
        {"weight": 2.0,  "volume": 5.0,  "moisture": 5.0,  "temperature": 20.0, "methane_ppm": 0.2},
        {"weight": 75.0, "volume": 90.0, "moisture": 3.0,  "temperature": 18.0, "methane_ppm": 0.1},
    ]

    table = Table(title="Waste Classification Results")
    table.add_column("Sample", style="cyan")
    table.add_column("Class", style="bold")
    table.add_column("Confidence", justify="right")
    table.add_column("Action")

    for i, features in enumerate(samples, 1):
        result = clf.classify(features)
        table.add_row(
            f"Sample {i}",
            result.waste_type.value,
            f"{result.confidence:.1%}",
            result.recommended_action[:50],
        )
    console.print(table)

    # Route optimiser
    optimizer = RouteOptimizer()
    for nid, fill, cap in [("depot", 0, 1000), ("bin_A", 90, 100),
                            ("bin_B", 85, 100), ("bin_C", 40, 100)]:
        optimizer.add_node(CollectionPoint(nid, f"Location {nid}", cap, fill))
    optimizer.add_edge("depot", "bin_A", 1.5)
    optimizer.add_edge("bin_A", "bin_B", 0.8)
    optimizer.add_edge("bin_B", "bin_C", 1.2)
    optimizer.add_edge("bin_C", "depot", 2.0)
    plan = optimizer.plan_collection_route("depot")
    console.print(f"  Route: {' → '.join(plan['route'])}")
    console.print(f"  Distance: {plan['total_distance_km']:.2f} km | "
                  f"Carbon: {plan['total_carbon_kg']:.3f} kg CO₂ | "
                  f"Collected: {plan['collected_kg']:.0f} kg")


def _demo_biofuel() -> None:
    from src.models.schemas import BiofuelMetrics, FermentationStage
    from src.biofuel.fermentation import FermentationController, FermentationMonitor
    from src.biofuel.process_control import BiofuelProcessController

    console.rule("[bold cyan]Biofuel Module[/bold cyan]")
    monitor = FermentationMonitor("batch_demo_001")
    controller = BiofuelProcessController()

    stages = [
        BiofuelMetrics(batch_id="demo", temperature=30.0, ph=5.0,
                       sugar_content=18.0, ethanol_yield=0.0,
                       stage=FermentationStage.INOCULATION, co2_rate=1.0),
        BiofuelMetrics(batch_id="demo", temperature=33.0, ph=4.5,
                       sugar_content=10.0, ethanol_yield=4.0,
                       stage=FermentationStage.EXPONENTIAL, co2_rate=30.0),
        BiofuelMetrics(batch_id="demo", temperature=31.0, ph=4.2,
                       sugar_content=2.0, ethanol_yield=10.0,
                       stage=FermentationStage.STATIONARY, co2_rate=5.0),
    ]

    table = Table(title="Fermentation Progress")
    table.add_column("Stage", style="cyan")
    table.add_column("Temp °C", justify="right")
    table.add_column("pH", justify="right")
    table.add_column("Sugar g/L", justify="right")
    table.add_column("Pred. Yield %", justify="right")

    for m in stages:
        status = monitor.update(m)
        outputs = controller.update(m)
        table.add_row(
            status["stage"],
            f"{m.temperature:.1f}",
            f"{m.ph:.2f}",
            f"{m.sugar_content:.1f}",
            f"{status['predicted_yield']:.2f}",
        )
    console.print(table)


def _demo_edible_oil() -> None:
    from src.models.schemas import EdibleOilMetrics, OilGrade
    from src.edible_oil.extraction import CropType, ExtractionMonitor
    from src.edible_oil.quality_control import OilQualityController

    console.rule("[bold cyan]Edible Oil Module – Olive (PL) & Moringa/Marenga (BD)[/bold cyan]")

    batches = [
        ("Olive Cold Press", CropType.OLIVE, "PL",
         EdibleOilMetrics(batch_id="olive_001", temperature=22.0, pressure=250.0,
                          moisture_content=0.15, quality_grade=OilGrade.EXTRA_VIRGIN,
                          acidity=0.6, peroxide_value=12.0)),
        ("Moringa (Marenga)", CropType.MORINGA, "BD",
         EdibleOilMetrics(batch_id="moringa_001", temperature=30.0, pressure=200.0,
                          moisture_content=0.3, quality_grade=OilGrade.EXTRA_VIRGIN,
                          acidity=0.8, peroxide_value=10.0)),
    ]

    table = Table(title="Oil Quality Assessment")
    table.add_column("Batch", style="cyan")
    table.add_column("Standard")
    table.add_column("Grade", style="bold")
    table.add_column("Acidity %", justify="right")
    table.add_column("Peroxide", justify="right")
    table.add_column("Compliant")

    for name, crop_type, std, metrics in batches:
        qc = OilQualityController(standard=std)
        grade, confidence = qc.predict_grade(metrics)
        compliance = qc.check_compliance(metrics)
        is_compliant = all(v for k, v in compliance.items() if k.endswith("_ok"))
        table.add_row(
            name,
            std,
            grade.value,
            f"{metrics.acidity:.2f}",
            f"{metrics.peroxide_value:.1f}",
            "[green]✓ PASS[/green]" if is_compliant else "[red]✗ FAIL[/red]",
        )
    console.print(table)


def _demo_renewable_energy() -> None:
    from src.models.schemas import EnergySource, RenewableEnergyMetrics
    from src.renewable_energy.solar import SolarPanelMonitor
    from src.renewable_energy.wind import WindTurbineMonitor

    console.rule("[bold cyan]Renewable Energy Module[/bold cyan]")

    solar = SolarPanelMonitor("PV_01", rated_power_w=400.0, panel_area_m2=2.0)
    wind = WindTurbineMonitor("WT_01", rated_power_w=5000.0, rotor_diameter_m=5.0)

    # Solar forecast
    irradiances = [0, 100, 300, 600, 900, 1000, 950, 800, 600, 300, 100, 0]
    forecast = solar.forecast_yield(irradiances)
    table = Table(title="Solar Forecast (12 hours)")
    table.add_column("Hour", justify="right")
    table.add_column("Irradiance W/m²", justify="right")
    table.add_column("Forecast W", justify="right")
    for h, (irr, pwr) in enumerate(zip(irradiances, forecast)):
        table.add_row(f"{h:02d}:00", f"{irr}", f"{pwr:.0f}")
    console.print(table)

    # Wind power curve
    wind_table = Table(title="Wind Power Curve")
    wind_table.add_column("Wind Speed m/s", justify="right")
    wind_table.add_column("Power W", justify="right")
    wind_table.add_column("Cap. Factor", justify="right")
    for v in [0, 3, 5, 8, 10, 12, 15, 20, 25, 30]:
        p = wind.power_curve(float(v))
        cf = wind.calculate_capacity_factor(p)
        wind_table.add_row(f"{v}", f"{p:.0f}", f"{cf:.2f}")
    console.print(wind_table)


# ---------------------------------------------------------------------------
# CLI Commands
# ---------------------------------------------------------------------------

@app.command()
def demo(
    modules: list[str] = typer.Option(
        ["all"], help="Modules to demo: waste_management, biofuel, edible_oil, renewable_energy, all"
    )
) -> None:
    """Run interactive demo of all 4 environmental modules."""
    _banner()

    run_all = "all" in modules
    if run_all or "waste_management" in modules:
        _demo_waste_management()
    if run_all or "biofuel" in modules:
        _demo_biofuel()
    if run_all or "edible_oil" in modules:
        _demo_edible_oil()
    if run_all or "renewable_energy" in modules:
        _demo_renewable_energy()

    console.print("\n[bold green]✓ Demo complete![/bold green]")


@app.command()
def monitor(
    duration: int = typer.Option(30, help="Monitoring duration in seconds"),
) -> None:
    """Start real-time monitoring dashboard with simulated data."""
    from src.models.schemas import (
        AlertSeverity, SensorConfig, SensorType, SystemStatus
    )
    from src.sensors.base import MockSensor, SensorRegistry
    from src.monitoring.alerting import AlertManager
    from src.monitoring.dashboard import DashboardConfig, MonitoringDashboard

    _banner()
    console.print(f"[dim]Starting {duration}s monitoring session...[/dim]")

    # Set up sensors
    registry = SensorRegistry()
    sensor_configs = [
        ("temp_01", SensorType.TEMPERATURE, "reactor"),
        ("ph_01", SensorType.PH, "reactor"),
        ("co2_01", SensorType.CO2, "exhaust"),
        ("solar_01", SensorType.SOLAR_IRRADIANCE, "roof"),
        ("wind_01", SensorType.WIND_SPEED, "mast"),
    ]
    for sid, stype, loc in sensor_configs:
        cfg = SensorConfig(sensor_id=sid, sensor_type=stype, location=loc)
        s = MockSensor(cfg)
        registry.register(s)
    registry.initialize_all()

    alert_mgr = AlertManager(log_file="monitoring_alerts.log")
    alert_mgr.add_rule(
        lambda r: (AlertSeverity.WARNING, f"High CO2: {r.value:.0f} ppm")
        if r.sensor_id == "co2_01" and r.value > 1500 else None
    )

    config = DashboardConfig(refresh_interval_s=2.0)
    dashboard = MonitoringDashboard(config)

    def data_source():
        readings = registry.read_all()
        for r in readings:
            alert_mgr.process_reading(r)
        alerts = alert_mgr.get_active_alerts()
        status = SystemStatus(
            active_sensors=registry.list_sensors(),
            alerts=alerts,
            module_statuses={
                "waste_management": "OK",
                "biofuel": "OK",
                "edible_oil": "OK",
                "renewable_energy": "OK",
            },
        )
        return status, readings

    dashboard.run_live(data_source, duration_s=float(duration))
    console.print("\n[bold green]✓ Monitoring session complete![/bold green]")


@app.command()
def simulate(
    module: str = typer.Option("all", help="Module to simulate"),
    steps: int = typer.Option(10, help="Number of simulation steps"),
) -> None:
    """Run simulation of sensors and AI processing."""
    _banner()
    console.print(f"[dim]Simulating {steps} steps for module: {module}[/dim]\n")

    from src.models.schemas import (
        AlertSeverity, BiofuelMetrics, FermentationStage, SensorConfig, SensorType
    )
    from src.sensors.base import MockSensor
    from src.models.adaptive_ai import AdaptiveAIController, RuleEngine

    # Universal AI controller
    controller = AdaptiveAIController(
        domain="fermentation",
        feature_names=["temperature", "ph", "co2"],
        output_names=["alert_level", "quality_index"],
    )

    rng = random.Random(42)
    table = Table(title=f"Simulation: {module} ({steps} steps)")
    table.add_column("Step", justify="right")
    table.add_column("Temp", justify="right")
    table.add_column("pH", justify="right")
    table.add_column("CO2", justify="right")
    table.add_column("Alert Level", justify="right")
    table.add_column("Quality", justify="right")

    for step in range(1, steps + 1):
        features = {
            "temperature": 28.0 + rng.gauss(0, 3),
            "ph": 5.0 + rng.gauss(0, 0.5),
            "co2": 400.0 + rng.gauss(0, 100),
        }
        predictions = controller.process_reading(features)
        table.add_row(
            str(step),
            f"{features['temperature']:.1f}",
            f"{features['ph']:.2f}",
            f"{features['co2']:.0f}",
            f"{predictions['alert_level']:.3f}",
            f"{predictions['quality_index']:.3f}",
        )
        time.sleep(0.05)

    console.print(table)
    console.print(f"\n[bold green]✓ Simulation complete![/bold green]")


if __name__ == "__main__":
    app()
