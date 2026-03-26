"""Gradio web GUI for environmental monitoring and sensor deployment."""
from __future__ import annotations

from datetime import datetime
from typing import Any

try:
    import gradio as gr
    _GRADIO_AVAILABLE = True
except ImportError:
    _GRADIO_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _MPL_AVAILABLE = True
except ImportError:
    _MPL_AVAILABLE = False

try:
    from src.sensors.laptop_bridge import SimulatedLaptopBridge, IoTSensorHub
    _BRIDGE_AVAILABLE = True
except ImportError:
    _BRIDGE_AVAILABLE = False

try:
    from src.agronomy.byproduct_market import ByproductMarketManager
    _MARKET_AVAILABLE = True
except ImportError:
    _MARKET_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helper: mock sensor table
# ---------------------------------------------------------------------------

def _get_sensor_data() -> list[dict[str, str]]:
    """Return a list of sensor reading dicts for display."""
    if _BRIDGE_AVAILABLE:
        bridge = SimulatedLaptopBridge(num_sensors=3, seed=int(datetime.now().timestamp()) % 1000)
        bridge.connect()
        readings = bridge.read_sensor_data()
        rows = [
            {
                "sensor_id": r.sensor_id,
                "value": f"{r.value:.3f}",
                "unit": r.unit,
                "quality": f"{r.quality:.2f}",
                "time": r.timestamp.strftime("%H:%M:%S"),
            }
            for r in readings
        ]
        bridge.disconnect()
        return rows
    return [
        {"sensor_id": "sim_temperature_00", "value": "20.123", "unit": "C", "quality": "0.95", "time": "00:00:00"},
        {"sensor_id": "sim_pH_01", "value": "7.012", "unit": "pH", "quality": "0.97", "time": "00:00:00"},
        {"sensor_id": "sim_dissolved_oxygen_02", "value": "8.001", "unit": "mg/L", "quality": "0.90", "time": "00:00:00"},
    ]


def _get_revenue_figure() -> Any:
    """Create a matplotlib bar chart of estimated byproduct revenues."""
    if not _MPL_AVAILABLE:
        return None

    if _MARKET_AVAILABLE:
        mgr = ByproductMarketManager()
        production = {
            "waste_management": 1000,
            "biofuel": 500,
            "edible_oil": 300,
            "renewable_energy": 2000,
            "water_treatment": 400,
        }
        result = mgr.calculate_monthly_revenue(production)
        rev = result["byproduct_revenues_usd"]
    else:
        rev = {
            "compost": 15.0,
            "biogas": 50.0,
            "CO2_food_grade": 36.0,
            "moringa_leaf_powder": 225.0,
            "excess_electricity": 160.0,
        }

    names = list(rev.keys())
    values = [rev[n] for n in names]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(names, values, color="steelblue")
    ax.set_title("Monthly Byproduct Revenue (USD)")
    ax.set_ylabel("USD")
    ax.set_xlabel("Byproduct")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Tab creator functions (must be called inside a gr.Blocks context)
# ---------------------------------------------------------------------------

def create_monitoring_tab() -> Any:
    """Create the Live Monitoring tab showing real-time sensor readings.

    Uses SimulatedLaptopBridge when no hardware is present.  Returns a
    gr.Tab() object containing a sensor data JSON view and a refresh button.
    MUST be called inside a ``gr.Blocks`` context so event handlers work.
    Returns None if Gradio is not available.
    """
    if not _GRADIO_AVAILABLE:
        return None

    with gr.Tab("📊 Live Monitoring") as tab:
        gr.Markdown("## Live Sensor Readings")
        gr.Markdown("Readings from all connected sensors (simulated when hardware absent).")
        sensor_json = gr.JSON(label="Sensor Data", value=_get_sensor_data())
        refresh_btn = gr.Button("🔄 Refresh Readings")
        refresh_btn.click(fn=_get_sensor_data, inputs=[], outputs=[sensor_json])

    return tab


def create_sensor_deploy_tab() -> Any:
    """Create the Sensor Deployment tab for configuring connected sensors.

    Shows detected serial ports and allows the user to test the connection.
    MUST be called inside a ``gr.Blocks`` context.
    Returns None if Gradio is unavailable.
    """
    if not _GRADIO_AVAILABLE:
        return None

    with gr.Tab("🔌 Sensor Deployment") as tab:
        gr.Markdown("## Sensor Deployment & Configuration")

        if _BRIDGE_AVAILABLE:
            from src.sensors.laptop_bridge import LaptopSensorBridge
            _bridge = LaptopSensorBridge()
            detected = _bridge.auto_detect_port() or "No device detected"
        else:
            detected = "Bridge library unavailable"

        gr.Textbox(value=detected, label="Auto-detected Port", interactive=False)
        port_input = gr.Textbox(placeholder="/dev/ttyACM0 or COM3", label="Override Port (optional)")
        test_btn = gr.Button("🔌 Test Connection")
        result_box = gr.Textbox(label="Connection Result", interactive=False)

        def test_connection(port: str) -> str:
            if not _BRIDGE_AVAILABLE:
                return "Bridge library not available"
            from src.sensors.laptop_bridge import LaptopSensorBridge
            p = port.strip() or None
            b = LaptopSensorBridge(port=p)
            ok = b.connect()
            b.disconnect()
            return "✅ Connection successful" if ok else "❌ Connection failed (no hardware?)"

        test_btn.click(fn=test_connection, inputs=[port_input], outputs=[result_box])

    return tab


def create_system_overview_tab() -> Any:
    """Create the System Overview tab showing status of all domain modules.

    Checks import availability of each major module.  Returns a gr.Tab()
    object.  Returns None if Gradio is unavailable.
    """
    if not _GRADIO_AVAILABLE:
        return None

    module_checks = [
        ("Waste Management", "src.waste_management.optimizer"),
        ("Biofuel", "src.biofuel.fermentation"),
        ("Edible Oil", "src.edible_oil.extraction"),
        ("Renewable Energy", "src.renewable_energy.solar"),
        ("Water Treatment", "src.water_treatment.treatment_plant"),
        ("Irrigation", "src.water_treatment.irrigation"),
    ]

    rows: list[list[str]] = []
    for label, module_path in module_checks:
        try:
            __import__(module_path)
            status = "✅ Online"
        except ImportError:
            status = "⚠️ Unavailable"
        rows.append([label, status])

    with gr.Tab("🌍 System Overview") as tab:
        gr.Markdown("## Environmental Engineering Platform — Module Status")
        status_md_lines = ["| Module | Status |", "|---|---|"]
        for label, status in rows:
            status_md_lines.append(f"| {label} | {status} |")
        gr.Markdown("\n".join(status_md_lines))
        gr.Markdown(f"**Platform timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return tab


def create_business_analytics_tab() -> Any:
    """Create the Business Analytics tab showing byproduct revenue charts.

    Displays a bar chart of estimated monthly revenues per byproduct.
    Returns a gr.Tab() object.  Returns None if Gradio is unavailable.
    """
    if not _GRADIO_AVAILABLE:
        return None

    with gr.Tab("💰 Business Analytics") as tab:
        gr.Markdown("## Byproduct Revenue Analytics")
        gr.Markdown("Estimated monthly revenue from circular economy byproducts.")

        fig = _get_revenue_figure()
        if fig is not None:
            gr.Plot(value=fig, label="Monthly Revenue by Byproduct")
        else:
            gr.Markdown("*Matplotlib not available — cannot render chart.*")

        if _MARKET_AVAILABLE:
            mgr = ByproductMarketManager()
            report = mgr.market_opportunity_report()
            gr.Textbox(value=report, label="Market Opportunity Report", lines=20, interactive=False)

    return tab


# ---------------------------------------------------------------------------
# Main launch function
# ---------------------------------------------------------------------------

def launch_gui(
    host: str = "0.0.0.0",
    port: int = 7860,
    share: bool = False,
) -> None:
    """Launch the Gradio web GUI for the Environmental Engineering AI platform.

    This function builds a multi-tab Gradio Blocks interface and starts the
    web server.  The interface contains four tabs:
        1. 📊 Live Monitoring   – real-time sensor readings table
        2. 🔌 Sensor Deployment – serial port detection and test connection
        3. 🌍 System Overview   – health status of all platform modules
        4. 💰 Business Analytics – byproduct revenue bar chart

    Args:
        host: The network interface to bind to (default "0.0.0.0" = all).
        port: TCP port number (default 7860).
        share: If True, Gradio will create a public tunnel URL via gradio.live.

    Raises:
        RuntimeError: Implicitly if Gradio cannot start the server.

    Example::

        from gui.app import launch_gui
        launch_gui(host="127.0.0.1", port=8080)
    """
    if not _GRADIO_AVAILABLE:
        print(
            "Gradio is not installed.  Install it with:\n"
            "  pip install gradio>=4.0\n"
            "Then re-run this script."
        )
        return

    with gr.Blocks(title="Environmental Engineering AI Platform") as demo:
        gr.Markdown("# 🌿 Environmental Engineering AI Platform")
        gr.Markdown(
            "Monitoring, water treatment, agronomy, and byproduct markets in one place."
        )
        create_monitoring_tab()
        create_sensor_deploy_tab()
        create_system_overview_tab()
        create_business_analytics_tab()

    demo.launch(server_name=host, server_port=port, share=share)
