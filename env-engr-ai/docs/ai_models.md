# AI Models Documentation

## NeuralNetwork (numpy-only MLP)

Layer sizes: configurable e.g. `[5, 16, 8, 4]`  
Activations: `relu`, `sigmoid`, `softmax`, `tanh`, `linear`  
Loss: MSE (regression and classification)  
Optimiser: Mini-batch SGD  

```
Input (5) → Dense(16, relu) → Dense(8, relu) → Output(4, sigmoid)
```

**Initialisers:**
- He init for ReLU layers: `W ~ N(0, sqrt(2/fan_in))`
- Xavier init for others: `W ~ N(0, sqrt(2/(fan_in+fan_out)))`

## AdaptiveNeuralNetwork

Extends `NeuralNetwork` with:
- `update_online(x, y)`: Single-sample SGD with `adaptation_rate`
- `detect_drift(losses)`: Compares recent loss mean to baseline (Page-Hinkley)
- `get_confidence(x)`: `mean(|output - 0.5|) × 2`

## Module-specific Architectures

| Module | Architecture | Features | Outputs |
|---|---|---|---|
| WasteClassifier | [5,16,8,4] | weight,volume,moisture,temp,methane | 4 waste classes |
| FermentationMonitor (yield) | [6,12,6,1] | temp,pH,sugar,CO2,ethanol,time | yield % |
| OilQualityController | [5,12,8,5] | temp,pressure,moisture,acidity,peroxide | 5 grades |
| WindTurbine (maintenance) | [5,10,6,1] | power_ratio,cf,vibration,rpm,age | fault_prob |
