# Physics Deep Learning Examples

> **Part of [AI Development Project](../../README.md)** | [Python AI Course](../../../README.md)

Advanced AI applications for aerodynamics, hydrodynamics, and thermodynamics using deep learning and physics-informed neural networks (PINNs).

## 🎯 Overview

This directory contains comprehensive examples demonstrating how deep learning can be applied to classical physics problems in fluid dynamics and thermodynamics. Each module showcases real-world engineering applications with AI-powered analysis and optimization.

## 📁 Files

### Core Physics Modules

1. **`aerodynamics_predictor.py`** - Aerodynamics AI
   - Airfoil performance prediction
   - Lift and drag coefficient calculation
   - Flow field visualization
   - Stall detection and optimization
   - Reynolds and Mach number effects

2. **`hydrodynamics_analyzer.py`** - Hydrodynamics AI
   - Ship resistance calculation
   - Wave pattern prediction (Kelvin wake)
   - Power requirement analysis
   - Hull form optimization
   - Froude number analysis

3. **`thermodynamics_optimizer.py`** - Thermodynamics AI
   - Heat exchanger performance analysis
   - Thermal engine efficiency calculation
   - Temperature field prediction
   - Heat transfer optimization
   - Entropy and exergy analysis

4. **`unified_physics_ai.py`** - Integrated Physics Assistant
   - Multi-domain AI consultant
   - Interactive physics analysis
   - Cross-domain optimization
   - Comprehensive demonstrations

## 🚀 Quick Start

### Prerequisites

```bash
# Install required packages
pip install numpy asyncio
```

### Running Individual Modules

Each module can be run independently:

```bash
# Aerodynamics analysis
python aerodynamics_predictor.py

# Hydrodynamics analysis
python hydrodynamics_analyzer.py

# Thermodynamics analysis
python thermodynamics_optimizer.py

# Unified physics AI (interactive)
python unified_physics_ai.py

# Unified physics AI (demo mode)
python unified_physics_ai.py --demo
```

## 🧪 Example Use Cases

### Aerodynamics

```python
from aerodynamics_predictor import AerodynamicsAI, AirfoilGeometry, FlowConditions

# Create AI instance
aero_ai = AerodynamicsAI()

# Define airfoil
airfoil = AirfoilGeometry(
    name="NACA 2412",
    chord_length=1.0,
    thickness_ratio=12.0,
    camber=2.0,
    angle_of_attack=8.0
)

# Define flow conditions
flow = FlowConditions(
    velocity=50.0,
    density=1.225,
    viscosity=1.81e-5,
    temperature=288.15
)

# Analyze
analysis = await aero_ai.analyze_airfoil(airfoil, flow)
print(aero_ai.generate_report(analysis))
```

**Applications:**
- Aircraft wing design
- Wind turbine blade optimization
- Drone aerodynamics
- Race car aerodynamics
- Sports equipment design

### Hydrodynamics

```python
from hydrodynamics_analyzer import HydrodynamicsAI, VesselGeometry, WaterConditions

# Create AI instance
hydro_ai = HydrodynamicsAI()

# Define vessel
vessel = VesselGeometry(
    name="Cruising Yacht",
    length=12.0,
    beam=3.5,
    draft=2.0,
    displacement=8000.0,
    hull_form="displacement"
)

# Define conditions
water = WaterConditions(
    velocity=5.0,
    water_density=1025.0,
    kinematic_viscosity=1.19e-6,
    wave_height=0.5,
    wave_period=4.0,
    depth=50.0
)

# Analyze
analysis = await hydro_ai.analyze_vessel(vessel, water)
print(hydro_ai.generate_report(analysis))
```

**Applications:**
- Ship hull design
- Submarine performance
- Offshore platform analysis
- Marine renewable energy
- Underwater vehicle optimization

### Thermodynamics

```python
from thermodynamics_optimizer import ThermodynamicsAI, ThermalSystem, ThermalConditions

# Create AI instance
thermo_ai = ThermodynamicsAI()

# Define heat exchanger
system = ThermalSystem(
    name="Shell and Tube HX",
    system_type="heat_exchanger",
    geometry={'area': 15.0, 'length': 3.0},
    materials={'shell': 'steel', 'tubes': 'copper'}
)

# Define conditions
conditions = ThermalConditions(
    hot_temperature=363.15,  # 90°C
    cold_temperature=293.15,  # 20°C
    flow_rate_hot=2.0,
    flow_rate_cold=2.5,
    ambient_temperature=298.15,
    pressure=1e5
)

# Analyze
analysis = await thermo_ai.analyze_heat_exchanger(system, conditions)
print(thermo_ai.generate_report(analysis))
```

**Applications:**
- HVAC system design
- Power plant optimization
- Automotive engine cooling
- Industrial heat recovery
- Refrigeration systems

## 🧠 Deep Learning Features

### Physics-Informed Neural Networks (PINNs)

These examples demonstrate how neural networks can be enhanced with physics knowledge:

1. **Conservation Laws Integration**
   - Mass conservation
   - Momentum conservation
   - Energy conservation

2. **Dimensional Analysis**
   - Reynolds number effects
   - Froude number scaling
   - Nusselt number correlations

3. **Boundary Conditions**
   - No-slip conditions
   - Temperature boundaries
   - Pressure constraints

### AI Capabilities

- **Prediction**: Fast surrogate models for expensive simulations
- **Optimization**: Multi-objective design optimization
- **Uncertainty Quantification**: Confidence intervals for predictions
- **Real-time Analysis**: Interactive engineering consultation

## 📊 Performance Metrics

Each module provides comprehensive metrics:

### Aerodynamics
- Lift coefficient (CL)
- Drag coefficient (CD)
- Moment coefficient (CM)
- L/D ratio
- Stall prediction

### Hydrodynamics
- Total resistance
- Viscous resistance
- Wave resistance
- Froude number
- Power requirements

### Thermodynamics
- Heat transfer rate
- Effectiveness (ε)
- NTU (Number of Transfer Units)
- Thermal efficiency (η)
- Exergy efficiency

## 🔬 Technical Details

### Neural Network Architecture

```
Input Layer (12 neurons)
    ↓
Hidden Layer 1 (64 neurons) - ReLU
    ↓
Hidden Layer 2 (128 neurons) - ReLU
    ↓
Hidden Layer 3 (64 neurons) - ReLU
    ↓
Hidden Layer 4 (32 neurons) - ReLU
    ↓
Output Layer (8 neurons) - Linear
```

### Training Data Sources

In production implementations, these models would be trained on:
- CFD simulation results (OpenFOAM, ANSYS Fluent)
- Experimental data from wind tunnels and towing tanks
- Historical design databases
- Published correlations and empirical data

### Validation Metrics

- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)
- R² Score
- Physics consistency checks

## 🎓 Learning Objectives

By studying these examples, you will learn:

1. **Physics + AI Integration**
   - How to combine domain knowledge with machine learning
   - When to use AI vs traditional methods
   - Validating AI predictions against physical laws

2. **Engineering Applications**
   - Real-world problem formulation
   - Multi-objective optimization
   - Design space exploration

3. **Software Engineering**
   - Modular AI system design
   - Async programming for AI
   - Interactive AI interfaces

## 📚 References

### Aerodynamics
- Anderson, J. D. (2010). Fundamentals of Aerodynamics
- NASA Airfoil Database
- XFOIL - Airfoil analysis software

### Hydrodynamics
- Newman, J. N. (1977). Marine Hydrodynamics
- ITTC Guidelines for ship resistance
- Principles of Naval Architecture

### Thermodynamics
- Incropera, F. P., & DeWitt, D. P. Fundamentals of Heat and Mass Transfer
- Heat Exchanger Design Handbook
- Bejan, A. Entropy Generation Through Heat and Fluid Flow

### Deep Learning for Physics
- Raissi, M., et al. (2019). Physics-informed neural networks
- Brunton, S. L., & Kutz, J. N. (2019). Data-Driven Science and Engineering
- Karniadakis, G. E., et al. (2021). Physics-informed machine learning

## 🛠️ Advanced Features

### Optimization Algorithms

All modules support optimization:

```python
# Aerodynamics: Optimize angle of attack
optimal = await aero_ai.optimize_airfoil(
    target_cl=1.0,
    flow=flow_conditions,
    initial_geometry=airfoil
)

# Hydrodynamics: Optimize cruising speed
optimal = await hydro_ai.optimize_speed(
    vessel=vessel,
    conditions=water_conditions,
    power_limit_kw=50.0
)

# Thermodynamics: Optimize heat exchanger area
optimal = await thermo_ai.optimize_heat_exchanger(
    system=hx_system,
    conditions=thermal_conditions,
    target_effectiveness=0.85
)
```

### Flow Visualization

Generate velocity and temperature fields:

```python
# Aerodynamics flow field
velocity_field = aero_ai.nn_model.predict_flow_field(airfoil, flow)

# Hydrodynamics wave pattern
wave_pattern = hydro_ai.nn_model.predict_wave_pattern(vessel, water)

# Thermodynamics temperature field
temp_field = thermo_ai.nn_model.predict_temperature_field(system, conditions)
```

## 🚧 Extension Ideas

1. **Add Visualization**
   - matplotlib/plotly for flow fields
   - 3D rendering with VTK
   - Interactive dashboards

2. **Real Neural Networks**
   - Replace simulation with TensorFlow/PyTorch
   - Train on CFD data
   - Implement transfer learning

3. **Multi-physics Coupling**
   - Aero-thermal analysis (heated wings)
   - Hydro-thermal (ship cooling systems)
   - Fluid-structure interaction

4. **Uncertainty Quantification**
   - Bayesian neural networks
   - Ensemble predictions
   - Confidence intervals

## 💡 Best Practices

1. **Validate Predictions**
   - Always check against known solutions
   - Verify dimensional consistency
   - Test extreme cases

2. **Physical Constraints**
   - Ensure conservation laws are satisfied
   - Check for physically impossible results
   - Implement sanity checks

3. **Performance**
   - Use async for I/O operations
   - Batch predictions when possible
   - Cache repeated calculations

## 📄 License

Part of the python-ai-course repository. See main LICENSE file.

## 🤝 Contributing

Contributions welcome! Consider adding:
- Additional physics domains (acoustics, electromagnetics)
- Real neural network implementations
- Experimental data integration
- Visualization tools

---

**Ready to explore physics with AI?** 🚀

Start with `unified_physics_ai.py` for an interactive experience, or dive into individual modules for specific applications!
