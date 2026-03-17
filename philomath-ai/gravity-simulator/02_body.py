"""
The Body Class – Object-Oriented Physics
=========================================

This module introduces the *Body* class, the fundamental building block
of our gravity simulator.  Each Body represents a physical object (star,
planet, moon, or any mass) with:

  - A **mass**  (kg or dimensionless solar-mass units)
  - A **position** (Vector2D, in metres or AU)
  - A **velocity** (Vector2D, in m/s or AU/year)
  - A **name** and **colour** for display

Why OOP?
--------
The three-body problem involves three separate objects that each need to
track their own state.  By encapsulating that state in a class we can:

  1. Create any number of bodies with a single line.
  2. Update each body independently.
  3. Add features (spin, radius, trails) without changing other code.

This mirrors the Object-Oriented Programming chapter of
"Programming for Lovers in Python" (Chapter 4).

Learning Objectives:
- Define a class with ``__init__``, properties, and methods
- Store state (position, velocity) in instance variables
- Implement Euler integration: x(t+dt) = x(t) + v(t)·dt
- Use dunder methods (``__repr__``, ``__str__``) for debugging

Video Reference:
- Chapter 4 of "Programming for Lovers in Python"
- https://programmingforlovers.com/chapters/chapter-4/
"""

import math
import sys
import os

# Allow running this file standalone (imports sibling module)
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

_vm = _load("01_vector_math.py")
Vector2D = _vm.Vector2D
zero_vector = _vm.zero_vector


class Body:
    """
    A physical body in 2-D space.

    Attributes:
        name     (str)      : Human-readable label (e.g. 'Sun', 'Earth')
        mass     (float)    : Mass in kg (or dimensionless units)
        position (Vector2D) : Current position
        velocity (Vector2D) : Current velocity
        color    (tuple)    : RGB colour tuple for pygame rendering
        trail    (list)     : List of past positions for drawing a trail
        max_trail(int)      : Maximum number of trail points stored

    Examples:
        >>> b = Body("Earth", mass=5.97e24, position=Vector2D(1.5e11, 0),
        ...          velocity=Vector2D(0, 29_800))
        >>> b.mass
        5.97e+24
    """

    def __init__(self, name, mass, position=None, velocity=None,
                 color=(255, 255, 255), max_trail=300):
        """
        Initialise a Body.

        Args:
            name     : Descriptive label
            mass     : Mass in simulation units (must be > 0)
            position : Initial position (Vector2D; default origin)
            velocity : Initial velocity (Vector2D; default zero)
            color    : RGB tuple for rendering (default white)
            max_trail: Maximum trail length (set to 0 to disable)
        """
        if mass <= 0:
            raise ValueError(f"Mass must be positive, got {mass}")

        self.name      = name
        self.mass      = float(mass)
        self.position  = position.copy() if position is not None else zero_vector()
        self.velocity  = velocity.copy() if velocity is not None else zero_vector()
        self.color     = color
        self.trail     = []
        self.max_trail = max_trail

    # ── Integration methods ───────────────────────────────────────────────────

    def apply_force(self, force, dt):
        """
        Apply a force vector for time step *dt* using Euler integration.

        This updates the velocity only.  Call ``move(dt)`` afterwards to
        update the position.

        Newton's second law:  a = F / m
        Euler velocity update: v(t+dt) = v(t) + a·dt

        Args:
            force (Vector2D): Net force acting on the body
            dt    (float)   : Time step in seconds (or simulation units)
        """
        acceleration = force / self.mass
        self.velocity = self.velocity + acceleration * dt

    def move(self, dt):
        """
        Update the position using the current velocity (Euler step).

        Euler position update: x(t+dt) = x(t) + v(t)·dt

        Also records the current position in the trail buffer.

        Args:
            dt (float): Time step in seconds (or simulation units)
        """
        # Record trail point before moving
        if self.max_trail > 0:
            self.trail.append(self.position.copy())
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)

        self.position = self.position + self.velocity * dt

    def update(self, force, dt):
        """
        Convenience method: apply force then update position in one call.

        Note: For multi-body simulations use the split apply_force / move
        pattern so that all forces are computed with the *old* positions
        before any body has moved.

        Args:
            force (Vector2D): Net force acting on the body
            dt    (float)   : Time step
        """
        self.apply_force(force, dt)
        self.move(dt)

    # ── Computed properties ───────────────────────────────────────────────────

    @property
    def kinetic_energy(self):
        """
        Return the kinetic energy: KE = ½ m |v|².

        Returns:
            float: Kinetic energy in simulation units
        """
        return 0.5 * self.mass * self.velocity.magnitude_squared()

    @property
    def speed(self):
        """Return the current speed |v|."""
        return self.velocity.magnitude()

    def distance_to(self, other):
        """
        Return the distance from this body to another.

        Args:
            other (Body): Another body

        Returns:
            float: Distance
        """
        return self.position.distance_to(other.position)

    # ── Trail management ──────────────────────────────────────────────────────

    def clear_trail(self):
        """Erase the stored trail."""
        self.trail.clear()

    # ── Dunder methods ────────────────────────────────────────────────────────

    def __repr__(self):
        return (f"Body(name={self.name!r}, mass={self.mass:.3g}, "
                f"pos=({self.position.x:.3g}, {self.position.y:.3g}), "
                f"vel=({self.velocity.x:.3g}, {self.velocity.y:.3g}))")

    def __str__(self):
        return (f"{self.name}: "
                f"pos=({self.position.x:.3e}, {self.position.y:.3e}) "
                f"vel=({self.velocity.x:.3e}, {self.velocity.y:.3e}) "
                f"speed={self.speed:.3e}")


# ── Factory helpers ───────────────────────────────────────────────────────────


def make_sun(position=None, velocity=None):
    """Create a Sun-like body (SI units: mass in kg, position in m)."""
    return Body(
        name="Sun",
        mass=1.989e30,
        position=position or Vector2D(0.0, 0.0),
        velocity=velocity or zero_vector(),
        color=(255, 220, 50),
        max_trail=0,          # The Sun barely moves in a 2-body system
    )


def make_earth(position=None, velocity=None):
    """Create an Earth-like body (SI units)."""
    return Body(
        name="Earth",
        mass=5.972e24,
        position=position or Vector2D(1.496e11, 0.0),   # 1 AU from origin
        velocity=velocity or Vector2D(0.0, 29_780.0),   # ~29.78 km/s
        color=(50, 130, 255),
    )


def make_moon(position=None, velocity=None):
    """Create a Moon-like body (SI units, relative to Earth's position)."""
    earth_pos = Vector2D(1.496e11, 0.0)
    return Body(
        name="Moon",
        mass=7.342e22,
        position=position or Vector2D(earth_pos.x + 3.844e8, earth_pos.y),
        velocity=velocity or Vector2D(0.0, 29_780.0 + 1_022.0),
        color=(200, 200, 200),
    )


# ── Demo ──────────────────────────────────────────────────────────────────────


def _demo():
    """Demonstrate the Body class."""
    print("=" * 55)
    print("BODY CLASS DEMO")
    print("=" * 55)

    sun   = make_sun()
    earth = make_earth()
    moon  = make_moon()

    print(f"\n{sun}")
    print(f"{earth}")
    print(f"{moon}")

    print(f"\nEarth–Sun distance: {earth.distance_to(sun):.3e} m")
    print(f"Earth kinetic energy: {earth.kinetic_energy:.3e} J")
    print(f"Earth speed: {earth.speed:.3f} m/s")

    # Tiny simulation step (1 second)
    dt = 1.0
    G  = 6.674e-11
    r  = earth.distance_to(sun)
    F_mag = G * sun.mass * earth.mass / r**2
    direction = (sun.position - earth.position).normalize()
    force = direction * F_mag

    earth.apply_force(force, dt)
    earth.move(dt)
    print(f"\nAfter 1 s of gravitational pull toward Sun:")
    print(f"  New velocity: ({earth.velocity.x:.3f}, {earth.velocity.y:.3f}) m/s")
    print(f"  New position: ({earth.position.x:.3e}, {earth.position.y:.3e}) m")

    print("\n✓ Body class demonstration complete")


if __name__ == "__main__":
    _demo()
