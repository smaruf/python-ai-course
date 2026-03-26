# System Architecture

## Data Flow
```
Arduino (Serial JSON)
        │
        ▼
ArduinoSerialBridge ──► SensorRegistry ──► TimeSeriesBuffer ──► LocalDataStore
                                │                                      │
                                ▼                                      ▼
RPi sensors ──────────► SensorReading (Pydantic v2)          CSV / JSON files
                                │
                                ├─────────► AlertManager ──► Console/File/Webhook
                                │
                                ├─────────► WasteClassifier (AdaptiveNN)
                                │
                                ├─────────► FermentationMonitor (AdaptiveNN + PID)
                                │
                                ├─────────► OilQualityController (AdaptiveNN)
                                │
                                └─────────► SolarPanelMonitor / WindTurbineMonitor
                                                        │
                                                        ▼
                                               MonitoringDashboard (Rich TUI)
```

## AI Architecture

```
AdaptiveNeuralNetwork
├── NeuralNetwork (base)
│   ├── Weights: He/Xavier initialisation
│   ├── Forward pass: z = aW + b, a = activation(z)
│   ├── Backprop: MSE loss, chain rule
│   └── Mini-batch SGD
├── Online learning: update_online(x, y) with adaptation_rate
├── Drift detection: Page-Hinkley approximation
└── Confidence: |output - 0.5| normalised

AdaptiveAIController
├── Wraps AdaptiveNeuralNetwork
├── Online mean/variance normalisation (Welford's algorithm)
├── Z-score anomaly detection
└── domain-specific feature/output mapping

RuleEngine
├── Priority-sorted rules list
├── condition: Callable → bool
├── action: str
└── Exception-tolerant evaluation
```
