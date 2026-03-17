"""
The Three-Body Problem
======================

The three-body problem asks: given three masses and their initial positions
and velocities, how do they move under mutual gravitational attraction?

Unlike the two-body problem, there is *no closed-form analytical solution*
for general initial conditions.  We must simulate numerically.  This fact,
discovered by Henri Poincaré in 1887, was one of the first hints of *chaos
theory* – tiny differences in initial conditions produce wildly different
trajectories.

Despite the general chaos, mathematicians have found special **periodic
solutions** where the three bodies follow stable, repeating paths:

  1. **Lagrange / Euler solutions** (1772): Three bodies at the corners of
     an equilateral triangle (Lagrange) or collinear (Euler).  These are
     stable for appropriate mass ratios.

  2. **Figure-8 solution** (Chenciner & Montgomery, 2000): Three equal-mass
     bodies chase each other around a figure-8 curve.  This is one of the
     most beautiful discoveries in celestial mechanics.

  3. **Sun–Earth–Moon** system: A near-real scenario with very different
     masses, showing how the Moon's orbit is perturbed by the Sun.

This module uses *dimensionless units* where  G = 1, m = 1, length = 1.
This lets us focus on the physics without enormous numbers.

Learning Objectives:
- Apply OOP (Body class) to a multi-body simulation
- Understand why the three-body problem is chaotic
- Explore famous periodic solutions
- Observe how numerical precision affects long-term stability

Video Reference:
- Chapter 4 of "Programming for Lovers in Python"
- https://programmingforlovers.com/chapters/chapter-4/
"""

import math
import sys
import os
import copy

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from importlib.util import spec_from_file_location, module_from_spec as _mfs


def _load(name):
    path = os.path.join(_DIR, name)
    spec = spec_from_file_location(name[:-3], path)
    mod  = _mfs(spec)
    spec.loader.exec_module(mod)
    return mod


_vm   = _load("01_vector_math.py")
_body = _load("02_body.py")
_gsim = _load("03_gravity_simulation.py")

Vector2D          = _vm.Vector2D
zero_vector       = _vm.zero_vector
Body              = _body.Body
leapfrog_step     = _gsim.leapfrog_step
euler_step        = _gsim.euler_step
total_energy      = _gsim.total_energy
kinetic_energy    = _gsim.kinetic_energy
potential_energy  = _gsim.potential_energy


# ── Gravitational constant ────────────────────────────────────────────────────
# Set G_DIM = 1.0 for the dimensionless scenarios in this module.
# The SI-unit scenarios import G from 03_gravity_simulation.
G_DIM = 1.0   # dimensionless gravitational constant


# ── Scenario factories ────────────────────────────────────────────────────────


def create_figure_eight(max_trail=500):
    """
    Create the famous figure-8 three-body solution.

    Three equal-mass bodies (m = 1) in dimensionless units chase each other
    around a figure-8 curve.  This periodic solution was discovered in 2000
    by Alain Chenciner and Richard Montgomery.

    Initial conditions from: Chenciner & Montgomery (2000),
    "A remarkable periodic solution of the three-body problem in the case
     of equal masses", Annals of Mathematics 152, pp. 881–901.
    
    Rescaled so that G·m = 1 (i.e. G = 1, m = 1).

    Returns:
        list[Body]: Three bodies ready to simulate
    """
    # Chenciner-Montgomery initial conditions (G=1, m=1, T≈6.3259)
    x1, y1 =  0.9700436, -0.24308753
    x2, y2 = -0.9700436,  0.24308753
    x3, y3 =  0.0,         0.0

    vx_sum, vy_sum = -0.93240737, -0.86473146   # v3 = -(v1+v2)
    vx1, vy1 = -vx_sum / 2.0, -vy_sum / 2.0
    vx2, vy2 = -vx_sum / 2.0, -vy_sum / 2.0
    vx3, vy3 =  vx_sum,        vy_sum

    body1 = Body("Body 1", mass=1.0,
                 position=Vector2D(x1, y1),
                 velocity=Vector2D(vx1, vy1),
                 color=(255, 80, 80),
                 max_trail=max_trail)
    body2 = Body("Body 2", mass=1.0,
                 position=Vector2D(x2, y2),
                 velocity=Vector2D(vx2, vy2),
                 color=(80, 255, 80),
                 max_trail=max_trail)
    body3 = Body("Body 3", mass=1.0,
                 position=Vector2D(x3, y3),
                 velocity=Vector2D(vx3, vy3),
                 color=(80, 150, 255),
                 max_trail=max_trail)

    return [body1, body2, body3]


def create_lagrange_triangle(max_trail=500):
    """
    Create the Lagrange equilateral-triangle three-body solution.

    Three equal-mass bodies sit at the corners of an equilateral triangle
    and orbit their common centre of mass.  This is one of the five Lagrange
    points solutions.

    In dimensionless units (G = 1, m = 1, side length = 1):
    - The orbital period is T = 2π / sqrt(3 · G · m / L³)
      = 2π / sqrt(3) ≈ 3.6276 time units.

    Returns:
        list[Body]: Three bodies ready to simulate
    """
    L = 1.0        # side length of the equilateral triangle
    m = 1.0        # mass of each body
    r = L / math.sqrt(3)   # circumradius

    # Angular velocity for circular orbits: ω = sqrt(G·m/L³ · 3)
    omega = math.sqrt(G_DIM * m * 3 / L ** 3)

    # Corners of the equilateral triangle (centred at origin)
    angles = [math.pi / 2,
              math.pi / 2 + 2 * math.pi / 3,
              math.pi / 2 + 4 * math.pi / 3]

    colors = [(255, 200, 50), (50, 200, 255), (255, 80, 200)]
    bodies = []
    for i, (angle, color) in enumerate(zip(angles, colors)):
        pos_x = r * math.cos(angle)
        pos_y = r * math.sin(angle)
        # Velocity is perpendicular to the radius vector (tangential)
        vel_x = -omega * r * math.sin(angle)
        vel_y =  omega * r * math.cos(angle)
        bodies.append(Body(
            f"Body {i+1}", mass=m,
            position=Vector2D(pos_x, pos_y),
            velocity=Vector2D(vel_x, vel_y),
            color=color,
            max_trail=max_trail,
        ))

    return bodies


def create_chaotic_three_body(seed_offset=0.0, max_trail=500):
    """
    Create a three-body system with chaotic dynamics.

    Starts from a near-symmetric configuration; tiny perturbations lead
    to dramatically different trajectories – demonstrating chaos.

    Args:
        seed_offset (float): Small position perturbation to show chaos
        max_trail   (int)  : Trail length

    Returns:
        list[Body]: Three bodies ready to simulate
    """
    body1 = Body("Body 1", mass=3.0,
                 position=Vector2D(0.0 + seed_offset, 1.0),
                 velocity=Vector2D(0.0,  0.0),
                 color=(255, 100, 50),
                 max_trail=max_trail)
    body2 = Body("Body 2", mass=4.0,
                 position=Vector2D(-1.0, -0.5),
                 velocity=Vector2D(0.0,  0.0),
                 color=(50, 200, 100),
                 max_trail=max_trail)
    body3 = Body("Body 3", mass=2.0,
                 position=Vector2D(1.0,  -0.5),
                 velocity=Vector2D(0.0,  0.0),
                 color=(80, 130, 255),
                 max_trail=max_trail)
    return [body1, body2, body3]


def create_sun_earth_moon(max_trail=500):
    """
    Create a Sun–Earth–Moon system in SI units.

    Uses realistic masses and initial positions.  The Moon starts at
    Earth's position + the Earth–Moon distance, with the combined
    Earth + Moon orbital velocity.

    Returns:
        list[Body]: [Sun, Earth, Moon]
    """
    from importlib.util import spec_from_file_location, module_from_spec
    _b = _load("02_body.py")
    make_sun   = _b.make_sun
    make_earth = _b.make_earth
    make_moon  = _b.make_moon

    sun   = make_sun(max_trail=0)
    earth = make_earth(max_trail=max_trail)
    moon  = make_moon(max_trail=max_trail)
    return [sun, earth, moon]


# ── Dimensionless leapfrog ────────────────────────────────────────────────────


def _grav_force_dim(b1, b2, softening=1e-4):
    """Gravitational force using G_DIM = 1 (dimensionless)."""
    diff    = b2.position - b1.position
    dist_sq = diff.magnitude_squared() + softening ** 2
    dist    = math.sqrt(dist_sq)
    if dist == 0:
        return zero_vector()
    force_mag = G_DIM * b1.mass * b2.mass / dist_sq
    return (diff / dist) * force_mag


def _net_force_dim(body, all_bodies, softening=1e-4):
    """Net gravitational force in dimensionless units."""
    total = zero_vector()
    for other in all_bodies:
        if other is not body:
            total = total + _grav_force_dim(body, other, softening)
    return total


def leapfrog_step_dim(bodies, dt, softening=1e-4):
    """
    Leapfrog integrator for dimensionless-unit simulations (G = 1).

    Args:
        bodies    (list[Body]): All bodies (modified in place)
        dt        (float)     : Time step (dimensionless)
        softening (float)     : Softening length (dimensionless)
    """
    accs = [_net_force_dim(b, bodies, softening) / b.mass for b in bodies]
    for body, acc in zip(bodies, accs):
        body.velocity = body.velocity + acc * (dt / 2.0)
    for body in bodies:
        body.move(dt)
    new_accs = [_net_force_dim(b, bodies, softening) / b.mass for b in bodies]
    for body, acc in zip(bodies, new_accs):
        body.velocity = body.velocity + acc * (dt / 2.0)


def simulate_dim(bodies, dt, num_steps, record_every=1):
    """
    Run a dimensionless-unit three-body simulation.

    Args:
        bodies      (list[Body]) : Starting state (modified in place)
        dt          (float)      : Time step (dimensionless)
        num_steps   (int)        : Total number of steps
        record_every(int)        : Record snapshot every N steps

    Returns:
        list[dict]: Snapshot list (same format as simulate() in module 03)
    """
    history = []
    for step in range(num_steps):
        if step % record_every == 0:
            history.append({
                'step':       step,
                'time':       step * dt,
                'positions':  [b.position.copy() for b in bodies],
                'velocities': [b.velocity.copy() for b in bodies],
            })
        leapfrog_step_dim(bodies, dt)
    return history


# ── Utility: centre-of-mass ───────────────────────────────────────────────────


def centre_of_mass(bodies):
    """
    Return the centre-of-mass position of a system of bodies.

    Args:
        bodies (list[Body]): Bodies in the system

    Returns:
        Vector2D: Centre-of-mass position
    """
    total_mass = sum(b.mass for b in bodies)
    cx = sum(b.mass * b.position.x for b in bodies) / total_mass
    cy = sum(b.mass * b.position.y for b in bodies) / total_mass
    return Vector2D(cx, cy)


def centre_of_mass_velocity(bodies):
    """Return the centre-of-mass velocity of the system."""
    total_mass = sum(b.mass for b in bodies)
    vx = sum(b.mass * b.velocity.x for b in bodies) / total_mass
    vy = sum(b.mass * b.velocity.y for b in bodies) / total_mass
    return Vector2D(vx, vy)


def shift_to_com_frame(bodies):
    """
    Shift all bodies so the centre of mass is at the origin with zero
    net momentum.  This is the standard inertial frame for three-body
    simulations.

    Args:
        bodies (list[Body]): Modified in place
    """
    com_pos = centre_of_mass(bodies)
    com_vel = centre_of_mass_velocity(bodies)
    for b in bodies:
        b.position = b.position - com_pos
        b.velocity = b.velocity - com_vel


# ── Demo ──────────────────────────────────────────────────────────────────────


def _demo():
    """Demonstrate three-body scenarios."""
    print("=" * 60)
    print("THREE-BODY PROBLEM DEMO")
    print("=" * 60)

    # ── Figure-8 ─────────────────────────────────────────────────────────────
    print("\n1. FIGURE-8 SOLUTION")
    print("-" * 40)
    bodies = create_figure_eight()
    shift_to_com_frame(bodies)
    for b in bodies:
        print(f"  {b}")

    T = 6.3259        # approximate period in dimensionless units
    dt = 0.001
    steps = int(T / dt)
    print(f"\n  Simulating for one period T ≈ {T} (steps={steps:,}, dt={dt})")

    initial_energy = sum(
        0.5 * b.mass * b.velocity.magnitude_squared() for b in bodies
    )
    simulate_dim(bodies, dt, steps, record_every=steps + 1)
    final_energy = sum(
        0.5 * b.mass * b.velocity.magnitude_squared() for b in bodies
    )
    print(f"  Initial KE: {initial_energy:.6f}")
    print(f"  Final   KE: {final_energy:.6f}")

    print(f"\n  Body positions after one period:")
    for b in bodies:
        print(f"    {b.name}: ({b.position.x:.4f}, {b.position.y:.4f})")

    # ── Lagrange triangle ─────────────────────────────────────────────────────
    print("\n2. LAGRANGE EQUILATERAL TRIANGLE")
    print("-" * 40)
    bodies_L = create_lagrange_triangle()
    for b in bodies_L:
        print(f"  {b}")

    # ── Chaotic example ───────────────────────────────────────────────────────
    print("\n3. CHAOTIC THREE-BODY SYSTEM")
    print("-" * 40)
    b_normal = create_chaotic_three_body(seed_offset=0.0)
    b_perturb = create_chaotic_three_body(seed_offset=1e-7)
    print(f"  Initial separation (Body 1): 0.0 vs 1e-7")

    steps_chaos = 5000
    dt_chaos    = 0.01
    simulate_dim(b_normal,  dt_chaos, steps_chaos, record_every=steps_chaos + 1)
    simulate_dim(b_perturb, dt_chaos, steps_chaos, record_every=steps_chaos + 1)

    sep = b_normal[0].position.distance_to(b_perturb[0].position)
    print(f"  After {steps_chaos * dt_chaos:.0f} time units, Body 1 separation:")
    print(f"    {sep:.4f} units  (started at 1e-7: shows chaos!)")

    print("\n✓ Three-body demo complete")


if __name__ == "__main__":
    _demo()
