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


def _demo_water() -> None:
    from src.water_treatment.treatment_plant import (
        WaterQualityMetrics, WaterTreatmentPlant, WaterQualityMonitor
    )
    from src.water_treatment.irrigation import (
        IrrigationController, SoilMoistureZone, WeatherForecast
    )
    from datetime import datetime

    console.rule("[bold cyan]Water Treatment Module[/bold cyan]")

    plant = WaterTreatmentPlant(capacity_m3_per_day=10.0)
    raw_water = WaterQualityMetrics(
        turbidity=45.0, ph=7.2, dissolved_oxygen=8.0,
        chlorine=0.0, tds=320.0, e_coli=150.0, temperature=22.0
    )
    results = plant.run_full_treatment(raw_water)
    table = Table(title="Water Treatment Stages")
    table.add_column("Stage", style="cyan")
    table.add_column("Turbidity NTU", justify="right")
    table.add_column("pH", justify="right")
    table.add_column("Chlorine mg/L", justify="right")
    table.add_column("E.coli CFU/100mL", justify="right")
    for stage_name, metrics in results.items():
        table.add_row(
            stage_name,
            f"{metrics.turbidity:.2f}",
            f"{metrics.ph:.2f}",
            f"{metrics.chlorine:.2f}",
            f"{metrics.e_coli:.1f}",
        )
    console.print(table)

    final = list(results.values())[-1]
    who = plant.check_who_standards(final)
    compliant = all(who.values())
    console.print(f"  WHO Compliance: {'[green]✓ ALL PASS[/green]' if compliant else '[red]✗ FAILED[/red]'}")

    report = plant.daily_production_report()
    console.print(f"  Daily report: {report['volume_m3']} m³ produced, cost ${report['total_cost_usd']:.2f}")

    console.rule("[bold cyan]Smart Irrigation Module[/bold cyan]")
    controller = IrrigationController()
    zone = SoilMoistureZone(
        zone_id="zone_01", crop_type="olive", area_m2=250.0,
        current_moisture_pct=35.0, target_moisture_pct=65.0,
        last_irrigated=datetime.now()
    )
    controller.add_zone(zone)
    forecast = WeatherForecast(
        temperature_c=28.0, rainfall_mm=0.0, humidity_pct=60.0,
        wind_speed_ms=2.5, solar_radiation_wm2=650.0,
        forecast_date=datetime.now()
    )
    need = controller.calculate_water_need("zone_01", forecast)
    console.print(f"  Zone 01 (olive, 250 m²) water need: {need:.1f} L")
    schedule = controller.generate_schedule(forecast)
    console.print(f"  Generated {len(schedule)} irrigation schedules")


def _demo_agronomy() -> None:
    from src.agronomy.planting_guide import AgronomyAdvisor
    from src.agronomy.byproduct_market import ByproductMarketManager

    console.rule("[bold cyan]Agronomy Cross-Planting Module (BD ↔ PL)[/bold cyan]")
    advisor = AgronomyAdvisor()

    table = Table(title="Crop Feasibility by Country")
    table.add_column("Crop", style="cyan")
    table.add_column("Country", style="bold")
    table.add_column("Feasibility", justify="right")
    table.add_column("Risk", justify="right")
    table.add_column("Est. Yield %", justify="right")

    for crop in ["OLIVE", "MORINGA", "SUNFLOWER", "RAPESEED"]:
        for country in ["BD", "PL"]:
            f = advisor.assess_feasibility(crop, country)
            table.add_row(
                crop, country,
                f"{f.feasibility_score:.2f}",
                f.risk_level,
                f"{f.estimated_yield_pct_of_optimal:.0f}%",
            )
    console.print(table)

    console.rule("[bold cyan]Byproduct Market Module[/bold cyan]")
    mgr = ByproductMarketManager()
    byproducts = mgr.list_byproducts()
    bp_table = Table(title="Available Byproducts")
    bp_table.add_column("Name", style="cyan")
    bp_table.add_column("Source", style="dim")
    bp_table.add_column("Price/unit", justify="right")
    for bp in byproducts[:8]:
        bp_table.add_row(bp.name, bp.source_process, f"${bp.market_price_usd_per_unit:.2f}/{bp.unit}")
    console.print(bp_table)

    production_data = {
        "waste_management": 1000.0,
        "biofuel": 100.0,
        "edible_oil": 200.0,
        "renewable_energy": 500.0,
        "water_treatment": 500.0,
    }
    revenue = mgr.calculate_monthly_revenue(production_data)
    total = sum(v for v in revenue.values() if isinstance(v, float) and v > 0)
    console.print(f"  Estimated monthly byproduct revenue: [bold green]${total:.2f}[/bold green]")


@app.command()
def water(
    capacity: float = typer.Option(10.0, help="Plant capacity in m³/day"),
) -> None:
    """Demo water treatment plant and smart irrigation system."""
    _banner()
    _demo_water()
    console.print("\n[bold green]✓ Water module demo complete![/bold green]")


@app.command()
def agronomy() -> None:
    """Show cross-planting guide (BD↔PL) and byproduct market analysis."""
    _banner()
    _demo_agronomy()
    console.print("\n[bold green]✓ Agronomy module demo complete![/bold green]")


@app.command()
def gui(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(7860, help="Port to listen on"),
    share: bool = typer.Option(False, help="Create public Gradio share link"),
) -> None:
    """Launch the Gradio web GUI for monitoring and sensor deployment."""
    _banner()
    console.print(f"[dim]Launching GUI on {host}:{port}...[/dim]")
    try:
        from gui.app import launch_gui
        launch_gui(host=host, port=port, share=share)
    except ImportError as e:
        console.print(f"[red]Failed to import GUI: {e}[/red]")
        console.print("[yellow]Install gradio: pip install gradio>=4.0.0[/yellow]")


@app.command()
def deploy(
    port: str = typer.Option(None, help="Serial port (auto-detect if not specified)"),
) -> None:
    """Sensor deployment wizard – auto-detect ports, configure, and test connections."""
    _banner()
    console.print("[bold cyan]🔌 Sensor Deployment Wizard[/bold cyan]\n")
    from src.sensors.laptop_bridge import LaptopSensorBridge, SimulatedLaptopBridge, IoTSensorHub

    bridge = LaptopSensorBridge(port=port)
    detected = bridge.auto_detect_port()
    if detected:
        console.print(f"  [green]Detected sensor port:[/green] {detected}")
    else:
        console.print("  [yellow]No hardware sensor detected – using simulation mode[/yellow]")

    sim = SimulatedLaptopBridge(num_sensors=3)
    sim.connect()
    readings = sim.read_sensor_data()
    table = Table(title="Simulated Sensor Readings")
    table.add_column("Sensor ID", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Unit")
    table.add_column("Quality", justify="right")
    for r in readings:
        table.add_row(r.sensor_id, f"{r.value:.3f}", r.unit, f"{r.quality:.2f}")
    console.print(table)
    sim.disconnect()
    console.print("\n[bold green]✓ Deployment wizard complete![/bold green]")


# ---------------------------------------------------------------------------
# Update demo command to include water and agronomy
# ---------------------------------------------------------------------------

@app.command(name="demo-all")
def demo_all() -> None:
    """Run the complete demo including water treatment and agronomy modules."""
    _banner()
    _demo_waste_management()
    _demo_biofuel()
    _demo_edible_oil()
    _demo_renewable_energy()
    _demo_water()
    _demo_agronomy()
    console.print("\n[bold green]✓ Full platform demo complete![/bold green]")


if __name__ == "__main__":
    app()
