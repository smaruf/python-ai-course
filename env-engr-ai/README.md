# Environmental Engineering AI Platform 🌱

A production-ready AI system for environmental engineering applications.  
Covers **Waste Management**, **Biofuel Production**, **Edible Oil Processing**, and **Renewable Energy** monitoring.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Environmental Engineering AI Platform                  │
├──────────────┬──────────────────┬─────────────────┬──────────────────────────┤
│   Hardware   │   Data Layer     │    AI Engine     │   Monitoring/Control     │
│              │                  │                  │                          │
│  ┌─────────┐ │ ┌──────────────┐ │ ┌──────────────┐│ ┌───────────────────┐   │
│  │ Arduino │─┼─│SerialBridge  │ │ │NeuralNetwork ││ │ MonitoringDashbrd │   │
│  └─────────┘ │ └──────┬───────┘ │ │(numpy-only)  ││ │ (Rich TUI)        │   │
│              │        │         │ └──────────────┘│ └───────────────────┘   │
│  ┌─────────┐ │ ┌──────▼───────┐ │ ┌──────────────┐│ ┌───────────────────┐   │
│  │  RPi    │─┼─│SensorRegistry│ │ │AdaptiveNN    ││ │ AlertManager       │   │
│  │ DHT22   │ │ └──────┬───────┘ │ │(online learn)││ └───────────────────┘   │
│  │ DS18B20 │ │        │         │ └──────────────┘│ ┌───────────────────┐   │
│  │ MQ135   │ │ ┌──────▼───────┐ │ ┌──────────────┐│ │ DataStore         │   │
│  │ pH EZO  │ │ │TimeSeriesBuf │ │ │RuleEngine    ││ │ (CSV/JSON/Buffer) │   │
│  └─────────┘ │ └──────────────┘ │ └──────────────┘│ └───────────────────┘   │
└──────────────┴──────────────────┴─────────────────┴──────────────────────────┘
                                          │
                ┌─────────────────────────┼──────────────────────┐
                │                         │                       │
     ┌──────────▼─────┐      ┌────────────▼──────┐   ┌──────────▼──────────┐
     │ Waste Mgmt      │      │  Biofuel           │   │  Edible Oil          │
     │ WasteClassifier │      │  FermentationMon   │   │  ExtractionMonitor   │
     │ RouteOptimizer  │      │  FermentationCtrl  │   │  OilQualityCtrl      │
     │ CarbonCalc      │      │  BiofuelProcCtrl   │   │  Olive (PL)          │
     └─────────────────┘      │  PIDController     │   │  Moringa/Marenga(BD) │
                              └────────────────────┘   └──────────────────────┘
```

---

## Modules

### 1. Waste Management (`src/waste_management/`)
- **WasteClassifier**: AdaptiveNeuralNetwork classifies waste as ORGANIC, RECYCLABLE, HAZARDOUS, or INERT
- **WasteOptimizer**: Recommends optimal processing routes with carbon footprint calculation
- **RouteOptimizer**: Dijkstra-based collection route planning
- **CollectionScheduler**: Time-based scheduling with fill rate prediction
- **CarbonFootprintCalculator**: Transport and treatment emission tracking

### 2. Biofuel Production (`src/biofuel/`)
- **FermentationMonitor**: Tracks 4-stage fermentation (Inoculation → Exponential → Stationary → Decline)
- **FermentationController**: PID-based temperature and pH control
- **PIDController**: Anti-windup PID with output clamping
- **BiofuelProcessController**: Multi-PID controller with safety interlocks

### 3. Edible Oil Processing (`src/edible_oil/`)
- **ExtractionMonitor**: Monitors Olive (PL/EU standard) and Moringa/Marenga (BD/BSTI standard) extraction
- **OilQualityController**: AI-powered grade prediction (Extra Virgin → Off-grade)
- Supports dual regulatory standards: Polish (EU Reg 2568/91) and Bangladesh (BSTI DS 1065)

### 4. Renewable Energy (`src/renewable_energy/`)
- **SolarPanelMonitor**: PV efficiency tracking, P&O MPPT algorithm, fault detection (shading, hot spots)
- **WindTurbineMonitor**: Betz limit power curve, vibration anomaly detection, predictive maintenance NN

### 5. Water Treatment Plant (`src/water_treatment/`)
- **WaterTreatmentPlant**: Full 6-stage treatment simulation (Intake → Coagulation → Sedimentation → Filtration → Disinfection → Distribution)
- **WaterQualityMonitor**: AI-powered anomaly detection using `AdaptiveAIController`
- **WaterQualityMetrics**: Tracks turbidity, pH, dissolved oxygen, chlorine, TDS, E.coli, temperature
- WHO drinking water standard compliance checks built-in
- Chemical cost estimation (coagulants, chlorine)
- Small home/village scale (10 m³/day default)

### 6. Smart Irrigation (`src/water_treatment/irrigation.py`)
- **IrrigationController**: AI-optimized irrigation scheduling
- **Penman-Monteith ET₀** evapotranspiration calculation
- Soil moisture zone management with per-zone targets
- Weather forecast integration for predictive scheduling
- Drip irrigation and sprinkler support
- Water savings estimation vs traditional irrigation

### 7. Agronomy – Cross-Planting Guide (`src/agronomy/`)
- **AgronomyAdvisor**: Feasibility assessment for BD (Bangladesh) ↔ PL (Poland) cross-planting
  - Olive trees in Bangladesh 🇧🇩
  - Moringa/Marenga trees in Poland 🇵🇱
  - Sunflower and Rapeseed (biodiesel crops) for both countries
- Climate-based scoring (temperature, rainfall, frost tolerance, soil pH)
- Variety recommendations (cold-hardy olive for PL, drought-tolerant Moringa for BD)
- Month-by-month planting calendars
- **ByproductMarketManager**: Complete byproduct catalog with pricing and sales channels
  - 10+ byproducts tracked across all processes
  - Monthly revenue calculation
  - Market opportunity reports

### 8. Laptop/IoT Direct Sensor Bridge (`src/sensors/laptop_bridge.py`)
- **LaptopSensorBridge**: USB serial connection to Arduino/sensors without Raspberry Pi
- **MQTTSensorBridge**: WiFi/MQTT IoT sensor integration (paho-mqtt)
- **SimulatedLaptopBridge**: Full simulation mode for testing without hardware
- **IoTSensorHub**: Manages multiple bridges simultaneously (USB + MQTT)
- Auto-detection of serial ports
- Graceful imports (works without pyserial or paho-mqtt installed)

---

## Hardware Requirements

### Raspberry Pi Node
- Raspberry Pi 3B+/4/Zero 2W
- DHT22 (temperature + humidity) – GPIO pin 4
- DS18B20 (water temperature) – 1-Wire on GPIO 4
- Atlas Scientific EZO-pH (I²C, 0x63)
- MQ135 (CO₂/air quality) + ADS1115 ADC

### Arduino Node
- Arduino Uno/Nano/Mega
- NTC 10kΩ thermistor (A0)
- pH analog sensor (A1)
- Capacitive moisture sensor (A2)

### Laptop/Direct Connection (no RPi needed)
- Any laptop with USB port running this platform
- Arduino connected via USB serial (auto-detected)
- ESP32/ESP8266 sensors via WiFi MQTT broker
- Works on Windows, macOS, Linux

---

## Quick Start

### 1. Install dependencies
```bash
cd env-engr-ai
pip install -r requirements.txt
```

### 2. Run demo (original 4 modules)
```bash
python main.py demo
```

### 3. Water treatment + irrigation demo
```bash
python main.py water
```

### 4. Agronomy cross-planting + byproduct market
```bash
python main.py agronomy
```

### 5. Launch Gradio web GUI
```bash
python main.py gui
# Then open http://localhost:7860 in your browser
```

### 6. Sensor deployment wizard (auto-detect ports)
```bash
python main.py deploy
```

### 7. Start monitoring dashboard (30 seconds)
```bash
python main.py monitor --duration 30
```

### 8. Run simulations
```bash
python main.py simulate --module biofuel --steps 20
```

### 9. Run tests
```bash
python -m pytest tests/ -v --tb=short
```

---

## Business Plan Summary

See [`docs/business_plan.md`](docs/business_plan.md) for the full business plan.

| Metric | Starter (0.5 ha) | Full Scale (5 ha) |
|--------|-----------------|-------------------|
| Capital investment | $12,000–$20,000 | $80,000–$150,000 |
| Annual revenue (Year 3+) | $8,000–$15,000 | $50,000–$150,000 |
| Break-even | 5–7 years | 3–5 years |
| Primary products | Olive oil, Moringa oil, Bioethanol | Same + commercial scale |
| Key byproducts | Moringa leaf powder, Compost, Biogas | + Export-grade oil, Carbon credits |

---

## Home Industry Demonstration

See [`docs/home_industry_guide.md`](docs/home_industry_guide.md) for the complete guide.

This platform enables a **zero-waste circular economy** at home scale:
- Every process output becomes the input to another process
- Water is treated and recycled (80%+ recovery)
- Solar + biogas provides ≥85% energy self-sufficiency
- All crop residues become fertilizer or biofuel feedstock
- AI monitoring ensures optimal performance with minimal labor (15 hr/week)

**Minimum demo setup:** $420 (Moringa pots + water filter + Arduino + 100W solar panel)

---

## GUI – Gradio Web Interface

```bash
# Install Gradio (if not already)
pip install gradio>=4.0.0

# Launch
python main.py gui --port 7860
```

The web interface has 4 tabs:
1. **📊 Live Monitoring** – real-time sensor readings with auto-refresh
2. **🔌 Sensor Deployment** – detect ports, configure and test sensors
3. **🌍 System Overview** – status of all 6 modules
4. **💰 Business Analytics** – byproduct revenues and production costs

---

## Project Structure

```
env-engr-ai/
├── main.py                       # CLI entry point (typer)
├── requirements.txt
├── gui/
│   └── app.py                    # Gradio web GUI (4 tabs)
├── src/
│   ├── models/
│   │   ├── schemas.py            # Pydantic v2 schemas
│   │   ├── neural_network.py     # Pure numpy MLP + AdaptiveNN
│   │   └── adaptive_ai.py        # AdaptiveAIController + RuleEngine
│   ├── sensors/
│   │   ├── base.py               # AbstractSensor, SensorRegistry, MockSensor
│   │   ├── rpi_sensors.py        # DHT22, MQ135, DS18B20, PHSensor
│   │   ├── arduino_sensors.py    # ArduinoSerialBridge, SimulatedArduinoBridge
│   │   └── laptop_bridge.py      # LaptopSensorBridge, MQTTSensorBridge, IoTSensorHub
│   ├── waste_management/
│   │   ├── classifier.py         # WasteClassifier, WasteOptimizer
│   │   └── optimizer.py          # RouteOptimizer, CollectionScheduler
│   ├── biofuel/
│   │   ├── fermentation.py       # FermentationMonitor, FermentationController
│   │   └── process_control.py    # PIDController, BiofuelProcessController
│   ├── edible_oil/
│   │   ├── extraction.py         # ExtractionMonitor (Olive/Moringa)
│   │   └── quality_control.py    # OilQualityController (PL/BD standards)
│   ├── renewable_energy/
│   │   ├── solar.py              # SolarPanelMonitor, MPPT
│   │   └── wind.py               # WindTurbineMonitor, power curve
│   ├── water_treatment/
│   │   ├── treatment_plant.py    # WaterTreatmentPlant, WaterQualityMonitor
│   │   └── irrigation.py         # IrrigationController, Penman-Monteith ET₀
│   ├── agronomy/
│   │   ├── planting_guide.py     # AgronomyAdvisor, BD↔PL cross-planting
│   │   └── byproduct_market.py   # ByproductMarketManager, circular economy catalog
│   └── monitoring/
│       ├── dashboard.py          # Rich TUI dashboard
│       ├── alerting.py           # AlertManager
│       └── data_store.py         # LocalDataStore, TimeSeriesBuffer
├── firmware/
│   ├── rpi/sensor_node.py        # RPi data collection daemon
│   └── arduino/sensor_node.ino   # Arduino sketch
├── tests/                        # pytest test suite (90+ tests)
└── docs/
    ├── architecture.md           # System architecture
    ├── ai_models.md              # AI model documentation
    ├── hardware_setup.md         # Raspberry Pi + Arduino setup
    ├── monitoring.md             # Monitoring dashboard guide
    ├── infrastructure.md         # Infrastructure construction guide
    ├── business_plan.md          # Full business plan with ROI
    └── home_industry_guide.md    # Sustainable home industry guide
```

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Single module
python -m pytest tests/test_biofuel.py -v
```

---

## Regulatory Standards

| Crop/Process | Standard | Authority |
|---|---|---|
| Olive Oil | EU Regulation 2568/91 | European Commission |
| Moringa Oil (Marenga) | BSTI DS 1065 | Bangladesh Standards & Testing Institution |
| Biofuel (Ethanol) | EN 15376 | European Standards |
| Waste Classification | Basel Convention | UNEP |
