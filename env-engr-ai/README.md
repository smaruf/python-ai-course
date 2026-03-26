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

---

## Quick Start

### 1. Install dependencies
```bash
cd env-engr-ai
pip install -r requirements.txt
```

### 2. Run demo
```bash
python main.py demo
```

### 3. Start monitoring dashboard (30 seconds)
```bash
python main.py monitor --duration 30
```

### 4. Run simulations
```bash
python main.py simulate --module biofuel --steps 20
```

### 5. Run tests
```bash
python -m pytest tests/ -v --tb=short
```

---

## Project Structure

```
env-engr-ai/
├── main.py                       # CLI entry point (typer)
├── requirements.txt
├── src/
│   ├── models/
│   │   ├── schemas.py            # Pydantic v2 schemas
│   │   ├── neural_network.py     # Pure numpy MLP + AdaptiveNN
│   │   └── adaptive_ai.py        # AdaptiveAIController + RuleEngine
│   ├── sensors/
│   │   ├── base.py               # AbstractSensor, SensorRegistry, MockSensor
│   │   ├── rpi_sensors.py        # DHT22, MQ135, DS18B20, PHSensor
│   │   └── arduino_sensors.py    # ArduinoSerialBridge, SimulatedArduinoBridge
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
│   └── monitoring/
│       ├── dashboard.py          # Rich TUI dashboard
│       ├── alerting.py           # AlertManager
│       └── data_store.py         # LocalDataStore, TimeSeriesBuffer
├── firmware/
│   ├── rpi/sensor_node.py        # RPi data collection daemon
│   └── arduino/sensor_node.ino  # Arduino sketch
├── tests/                        # pytest test suite
└── docs/                         # Architecture and setup docs
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
