# Gravity Simulator – Three-Body Problem

> **Part of [Philomath AI](../README.md)** – Chapter 4: *Using Object-Oriented Programming to Solve the Three Body Problem*  
> Course: [Programming for Lovers in Python](https://programmingforlovers.com/chapters/chapter-4/) by Phillip Compeau

A Python implementation of a gravity simulator built with OOP, Newtonian
mechanics, and a live [pygame](https://www.pygame.org/) visualization.

---

## 📚 Background

The **three-body problem** asks: given three masses and their initial
positions and velocities, how do they move under mutual gravitational
attraction?

Unlike the two-body problem (e.g., Earth orbiting the Sun), there is
*no closed-form analytical solution* for general initial conditions.
Henri Poincaré proved in 1887 that the general three-body problem is
**chaotic** – tiny changes in initial conditions produce wildly different
trajectories over time.

Despite the chaos, mathematicians have found beautiful **periodic
solutions** where the bodies follow repeating paths forever:

| Scenario | Description |
|---|---|
| **Figure-8** | Three equal-mass bodies chase each other in a figure-8 curve (Chenciner & Montgomery, 2000) |
| **Lagrange Triangle** | Three equal-mass bodies at the corners of an equilateral triangle orbiting their centre of mass |
| **Chaotic** | Near-symmetric initial conditions that quickly diverge, demonstrating sensitivity to initial conditions |
| **Sun–Earth–Moon** | Realistic SI-unit simulation of the inner solar system |

---

## 📁 File Structure

```
gravity-simulator/
├── 01_vector_math.py         # Vector2D class: add, subtract, scale, normalize
├── 02_body.py                # Body class: mass, position, velocity, Euler step
├── 03_gravity_simulation.py  # Newton's law, Euler & leapfrog integrators, two-body orbit
├── 04_three_body_problem.py  # Four three-body scenarios, chaos demo, CoM utilities
├── 05_pygame_visualization.py# Interactive pygame window: 4 scenarios, trails, controls
├── test_all.py               # Test suite (4 groups, run standalone)
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Install dependencies

```bash
pip install pygame
```

(numpy / matplotlib are **not** required; the simulator uses only the
Python standard library plus pygame.)

### Run the interactive visualization

```bash
cd philomath-ai/gravity-simulator
python 05_pygame_visualization.py
```

### Run the text demos (no display needed)

```bash
python 01_vector_math.py        # Vector math demo
python 02_body.py               # Body class demo
python 03_gravity_simulation.py # Two-body orbit for ~1 year
python 04_three_body_problem.py # Figure-8, Lagrange, chaos demo
```

### Run the test suite

```bash
python test_all.py
```

Expected output: `Total: 4/4 tests passed`

---

## 🎮 Visualization Controls

| Key | Action |
|---|---|
| `1` | Figure-8 solution (Chenciner-Montgomery) |
| `2` | Lagrange equilateral triangle |
| `3` | Chaotic three-body system |
| `4` | Sun – Earth – Moon (SI units) |
| `SPACE` | Pause / resume |
| `R` | Reset current scenario |
| `T` | Toggle trails on / off |
| `+` / `-` | Zoom in / out |
| `Arrow keys` | Pan the view |
| `S` / `F` | Slow down / speed up |
| `ESC` / `Q` | Quit |

---

## 🔬 Physics

### Newton's Law of Universal Gravitation

```
F = G · m₁ · m₂ / r²
```

- **G** = 6.674 × 10⁻¹¹ N m² kg⁻² (gravitational constant)
- **m₁, m₂** = masses of the two bodies
- **r** = distance between centres
- **F** = magnitude of the attractive force

The *direction* of the force on body 1 points along the unit vector
from body 1 toward body 2.

### Numerical Integration

Since there is no analytical solution, we integrate numerically.

**Euler's method** (first-order, simple but drifts):

```
a(t)    = F(t) / m
v(t+dt) = v(t) + a(t) · dt
x(t+dt) = x(t) + v(t) · dt
```

**Leapfrog / Störmer-Verlet** (second-order, *symplectic* – conserves
energy over long runs):

```
v(t + dt/2) = v(t)       + a(t)       · dt/2
x(t + dt)   = x(t)       + v(t+dt/2)  · dt
v(t + dt)   = v(t+dt/2)  + a(t+dt)    · dt/2
```

The leapfrog integrator is used by default.  The two-body demo
demonstrates near-zero energy drift over a full year (< 1 × 10⁻¹²).

---

## 🧩 Module Overview

### `01_vector_math.py` – `Vector2D`

```python
from 01_vector_math import Vector2D, zero_vector, direction_vector, distance

v = Vector2D(3.0, 4.0)
print(v.magnitude())        # 5.0
print(v.normalize())        # Vector2D(0.6, 0.8)
print(v + Vector2D(1, 1))   # Vector2D(4.0, 5.0)
```

### `02_body.py` – `Body`

```python
from 02_body import Body, make_sun, make_earth
from 01_vector_math import Vector2D

earth = make_earth()
print(earth.kinetic_energy)     # 2.65e+33 J
print(earth.speed)              # 29780.0 m/s

# Apply gravitational force for 1 second (Euler step)
earth.apply_force(Vector2D(-1e20, 0), dt=1.0)
earth.move(dt=1.0)
```

### `03_gravity_simulation.py`

```python
from 03_gravity_simulation import (
    gravitational_force, net_force_on,
    leapfrog_step, simulate,
    create_sun_earth_system, total_energy
)

bodies  = create_sun_earth_system()
history = simulate(bodies, dt=3600.0, num_steps=8766)   # ~1 year
print(history[-1]['total_energy'])
```

### `04_three_body_problem.py`

```python
from 04_three_body_problem import (
    create_figure_eight, create_lagrange_triangle,
    create_chaotic_three_body, create_sun_earth_moon,
    simulate_dim, shift_to_com_frame, centre_of_mass
)

bodies = create_figure_eight()
shift_to_com_frame(bodies)
simulate_dim(bodies, dt=0.001, num_steps=6326)   # ~1 period
```

---

## 📖 Learning Path

1. **Start with vectors**: `01_vector_math.py` – understand 2-D vector
   arithmetic; these are the building blocks of all physics.

2. **Build the Body class**: `02_body.py` – see how OOP encapsulates
   state (position, velocity, mass) and behaviour (apply force, move).

3. **Add gravity**: `03_gravity_simulation.py` – derive Newton's
   gravitational law, implement Euler and leapfrog integrators, and
   simulate a Sun–Earth orbit for one year.

4. **Solve the three-body problem**: `04_three_body_problem.py` –
   explore periodic solutions (figure-8, Lagrange triangle) and
   demonstrate sensitivity to initial conditions (chaos).

5. **Visualise**: `05_pygame_visualization.py` – watch the bodies move
   in real time, toggle trails, zoom, pan, and switch scenarios.

---

## 🌍 Real-World Applications

- **Astrodynamics**: planning spacecraft trajectories (Lagrange points
  L1–L5 are used by JWST, SOHO, and others)
- **Celestial mechanics**: modelling the long-term stability of
  planetary systems
- **Chaos theory**: one of the first concrete examples of deterministic
  chaos discovered by Poincaré (1887)
- **Molecular dynamics**: the same equations govern atom-to-atom forces
  in MD simulations
- **N-body simulations**: galaxy formation and dark matter modelling
  (e.g., the Millennium Simulation)

---

## 📄 License

See the main repository [LICENSE](../../LICENSE) file.

## 🙏 Acknowledgments

- **Phillip Compeau** – Course creator, Carnegie Mellon University
- **Alain Chenciner & Richard Montgomery** – Discoverers of the
  figure-8 solution (2000)
- **Henri Poincaré** – Pioneer of chaos theory through the three-body
  problem (1887)
- **Programming for Lovers** – Open online course:
  <https://programmingforlovers.com>
