"""
Gravity Simulation – Two-Body Orbits
======================================

This module implements Newton's law of universal gravitation and uses it
to simulate the orbit of one body around another (e.g. Earth around the
Sun).

Newton's Law of Universal Gravitation:
    F = G · m₁ · m₂ / r²

where:
    G  = 6.674 × 10⁻¹¹  N m² kg⁻²  (gravitational constant)
    m₁, m₂  = masses of the two bodies  (kg)
    r   = distance between their centres  (m)
    F   = magnitude of the attractive force  (N)

The *direction* of the force on body 1 is along the unit vector from
body 1 toward body 2.  (Body 2 feels the equal-and-opposite reaction.)

Numerical Integration – Euler's Method:
    a(t)     = F(t) / m               # acceleration from force
    v(t+dt)  = v(t) + a(t) · dt      # update velocity
    x(t+dt)  = x(t) + v(t) · dt      # update position

Euler's method is simple but introduces drift over long simulations.
The module also provides a *leapfrog* (Verlet) integrator which is much
more stable for orbital mechanics.

Learning Objectives:
- Apply Newton's law of gravitation to compute forces
- Implement Euler and leapfrog numerical integrators
- Observe how step-size (dt) affects accuracy
- Simulate a two-body system (Sun–Earth) and verify the orbital period

Video Reference:
- Chapter 4 of "Programming for Lovers in Python"
- https://programmingforlovers.com/chapters/chapter-4/
"""

import math
import copy
import sys
import os

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

Vector2D    = _vm.Vector2D
zero_vector = _vm.zero_vector
Body        = _body.Body
make_sun    = _body.make_sun
make_earth  = _body.make_earth


# ── Physical constant ─────────────────────────────────────────────────────────

G = 6.674e-11   # N m² kg⁻² – universal gravitational constant


# ── Core physics functions ────────────────────────────────────────────────────


def gravitational_force(body1, body2, softening=0.0):
    """
    Compute the gravitational force on *body1* due to *body2*.

    F = G · m₁ · m₂ / (r² + ε²) × r̂

    where ε (softening) prevents the denominator from becoming zero when
    bodies pass very close to each other.

    Args:
        body1      (Body)  : Body experiencing the force
        body2      (Body)  : Body exerting the force
        softening  (float) : Softening length (m); default 0

    Returns:
        Vector2D: Force vector acting *on* body1 (pointing toward body2)
    """
    diff   = body2.position - body1.position          # vector from 1 → 2
    dist_sq = diff.magnitude_squared() + softening ** 2
    dist    = math.sqrt(dist_sq)

    if dist == 0:
        return zero_vector()

    force_mag = G * body1.mass * body2.mass / dist_sq
    direction = diff / dist                            # unit vector 1 → 2
    return direction * force_mag


def net_force_on(body, all_bodies, softening=1e6):
    """
    Compute the total gravitational force on *body* from all other bodies.

    Args:
        body       (Body)       : Body experiencing the force
        all_bodies (list[Body]) : All bodies in the simulation
        softening  (float)      : Softening length (m); default 1e6 m

    Returns:
        Vector2D: Total force vector acting on *body*
    """
    total = zero_vector()
    for other in all_bodies:
        if other is not body:
            total = total + gravitational_force(body, other, softening)
    return total


# ── Integrators ───────────────────────────────────────────────────────────────


def euler_step(bodies, dt, softening=1e6):
    """
    Advance all bodies by one time step using *Euler integration*.

    WARNING: Euler integration accumulates energy error.  Use leapfrog for
    longer simulations.

    All forces are computed from current positions BEFORE any position is
    updated (this avoids order-of-update bias).

    Args:
        bodies    (list[Body]) : All bodies (modified in place)
        dt        (float)      : Time step (s)
        softening (float)      : Softening parameter (m)
    """
    forces = [net_force_on(b, bodies, softening) for b in bodies]
    for body, force in zip(bodies, forces):
        body.apply_force(force, dt)
        body.move(dt)


def leapfrog_step(bodies, dt, softening=1e6):
    """
    Advance all bodies by one time step using the *leapfrog (Störmer-Verlet)*
    integrator.

    The leapfrog method is *symplectic* – it conserves a modified energy
    exactly, making it far superior to Euler for long orbit simulations.

    Algorithm (velocity Verlet form):
        1. Compute accelerations from current positions.
        2. Half-step velocity:  v += a * dt/2
        3. Full-step position:  x += v * dt
        4. Recompute accelerations from new positions.
        5. Half-step velocity:  v += a_new * dt/2

    Args:
        bodies    (list[Body]) : All bodies (modified in place)
        dt        (float)      : Time step (s)
        softening (float)      : Softening parameter (m)
    """
    # Step 1 – current accelerations
    accs = [net_force_on(b, bodies, softening) / b.mass for b in bodies]

    # Step 2 – half-step velocity update
    for body, acc in zip(bodies, accs):
        body.velocity = body.velocity + acc * (dt / 2.0)

    # Step 3 – full position update (record trail here)
    for body in bodies:
        body.move(dt)

    # Step 4 – new accelerations
    new_accs = [net_force_on(b, bodies, softening) / b.mass for b in bodies]

    # Step 5 – second half-step velocity update
    for body, acc in zip(bodies, new_accs):
        body.velocity = body.velocity + acc * (dt / 2.0)


# ── Simulation runner ─────────────────────────────────────────────────────────


def simulate(bodies, dt, num_steps, integrator="leapfrog", softening=1e6,
             record_every=1):
    """
    Run the gravity simulation for *num_steps* steps.

    Args:
        bodies      (list[Body]) : Starting state (modified in place)
        dt          (float)      : Time step (s)
        num_steps   (int)        : Total number of steps to run
        integrator  (str)        : 'euler' or 'leapfrog' (default)
        softening   (float)      : Softening length (m)
        record_every(int)        : Record system state every N steps

    Returns:
        list[dict]: Snapshot list; each dict has keys
            'step', 'time', 'positions', 'velocities', 'total_energy'
    """
    step_fn = euler_step if integrator == "euler" else leapfrog_step
    history = []

    for step in range(num_steps):
        if step % record_every == 0:
            history.append({
                'step':        step,
                'time':        step * dt,
                'positions':   [b.position.copy() for b in bodies],
                'velocities':  [b.velocity.copy() for b in bodies],
                'total_energy': total_energy(bodies),
            })
        step_fn(bodies, dt, softening)

    return history


# ── Energy calculations ───────────────────────────────────────────────────────


def kinetic_energy(bodies):
    """Return the total kinetic energy of the system."""
    return sum(b.kinetic_energy for b in bodies)


def potential_energy(bodies):
    """
    Return the total gravitational potential energy of the system.

    PE = -G · m₁ · m₂ / r   (summed over all unique pairs)
    """
    pe = 0.0
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            r = bodies[i].distance_to(bodies[j])
            if r > 0:
                pe -= G * bodies[i].mass * bodies[j].mass / r
    return pe


def total_energy(bodies):
    """Return the total mechanical energy (KE + PE) of the system."""
    return kinetic_energy(bodies) + potential_energy(bodies)


# ── Pre-built scenarios ───────────────────────────────────────────────────────


def create_sun_earth_system():
    """
    Create a Sun–Earth two-body system in SI units.

    The Earth starts at 1 AU to the right of the Sun with the correct
    circular-orbit velocity.  The Sun is fixed at the origin (it is
    ~333,000× heavier than Earth, so it barely moves).

    Returns:
        list[Body]: [sun, earth]
    """
    sun   = make_sun()
    earth = make_earth()
    return [sun, earth]


def create_binary_star_system():
    """
    Create an equal-mass binary star system.

    Two stars of equal mass orbit their common centre of mass on
    circular orbits.  The separation is 1 AU; velocities are set to
    maintain a circular orbit.

    Returns:
        list[Body]: [star_a, star_b]
    """
    m      = 1.989e30           # 1 solar mass each
    sep    = 1.496e11 / 2       # half the total separation = 0.5 AU
    v_circ = math.sqrt(G * m / (2 * sep))  # circular orbit speed

    star_a = Body(
        "Star A", mass=m,
        position=Vector2D(-sep, 0.0),
        velocity=Vector2D(0.0, -v_circ),
        color=(255, 160, 80),
    )
    star_b = Body(
        "Star B", mass=m,
        position=Vector2D(sep, 0.0),
        velocity=Vector2D(0.0, v_circ),
        color=(80, 160, 255),
    )
    return [star_a, star_b]


# ── Demo ──────────────────────────────────────────────────────────────────────


def _demo():
    """Demonstrate a two-body Sun–Earth simulation."""
    print("=" * 60)
    print("TWO-BODY GRAVITY SIMULATION DEMO")
    print("=" * 60)

    bodies  = create_sun_earth_system()
    sun, earth = bodies

    dt          = 3600.0          # 1 hour time step
    one_year_s  = 365.25 * 86400  # seconds in a year
    steps       = int(one_year_s / dt)

    print(f"\nSimulating Earth's orbit for ~1 year")
    print(f"  Time step  : {dt:.0f} s  (1 hour)")
    print(f"  Total steps: {steps:,}")
    print(f"  Integrator : leapfrog")

    e0 = total_energy(bodies)
    print(f"\nInitial total energy: {e0:.4e} J")
    print(f"Initial Earth speed:  {earth.speed:.1f} m/s")

    # Run for 1 year
    simulate(bodies, dt, steps, integrator="leapfrog",
             record_every=steps + 1)   # suppress history recording

    ef = total_energy(bodies)
    print(f"\nAfter ~1 year:")
    print(f"  Final total energy: {ef:.4e} J")
    print(f"  Energy drift:       {abs(ef - e0) / abs(e0) * 100:.4f} %")
    print(f"  Earth position:     ({earth.position.x:.3e}, "
          f"{earth.position.y:.3e}) m")
    print(f"  Earth–Sun distance: {earth.distance_to(sun):.3e} m")
    print(f"  Expected (~1 AU):    1.496e+11 m")

    print("\n✓ Two-body gravity simulation complete")


if __name__ == "__main__":
    _demo()
