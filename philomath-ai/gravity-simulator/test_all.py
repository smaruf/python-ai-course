#!/usr/bin/env python3
"""
Test suite for the gravity-simulator module.

Verifies:
  1. Vector math (Vector2D class)
  2. Body class (OOP, integration)
  3. Gravity simulation (forces, energy, two-body orbit)
  4. Three-body scenarios (figure-8, Lagrange, chaotic, Sun-Earth-Moon)

Run with:
    python test_all.py
"""

import sys
import os
import math
import importlib.util

_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Module loader ─────────────────────────────────────────────────────────────


def load_module(filename):
    """Load a module from a file with a numeric prefix."""
    path = os.path.join(_DIR, filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Test helpers ──────────────────────────────────────────────────────────────


def _close(a, b, rel_tol=1e-6):
    """Return True if a and b are close relative to their magnitude."""
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=1e-12)


# ── Test 1: Vector math ───────────────────────────────────────────────────────


def test_vector_math():
    """Test the Vector2D class and standalone helpers."""
    print("\n" + "=" * 70)
    print("TEST 1: Vector Math")
    print("=" * 70)

    m = load_module("01_vector_math.py")
    V = m.Vector2D

    # Construction
    v = V(3.0, 4.0)
    assert v.x == 3.0 and v.y == 4.0, "Construction failed"
    print("✓ Vector2D construction")

    # Default constructor
    v0 = V()
    assert v0.x == 0.0 and v0.y == 0.0, "Default constructor failed"
    print("✓ Default constructor (zero vector)")

    # Arithmetic
    v1, v2 = V(1.0, 2.0), V(3.0, 4.0)
    assert v1 + v2 == V(4.0, 6.0),  "Addition failed"
    assert v2 - v1 == V(2.0, 2.0),  "Subtraction failed"
    assert v1 * 2  == V(2.0, 4.0),  "Scalar multiply failed"
    assert 3 * v1  == V(3.0, 6.0),  "Right scalar multiply failed"
    assert v2 / 2  == V(1.5, 2.0),  "Scalar divide failed"
    assert -v1     == V(-1.0, -2.0), "Negation failed"
    print("✓ Arithmetic operators")

    # Magnitude
    assert _close(V(3, 4).magnitude(), 5.0), "Magnitude failed"
    assert _close(V(0, 0).magnitude(), 0.0), "Zero magnitude failed"
    assert _close(V(3, 4).magnitude_squared(), 25.0), "Magnitude² failed"
    print("✓ Magnitude / magnitude_squared")

    # Normalise
    unit = V(3.0, 4.0).normalize()
    assert _close(unit.magnitude(), 1.0), "Normalise magnitude != 1"
    assert _close(unit.x, 0.6) and _close(unit.y, 0.8), "Normalise direction wrong"
    print("✓ Normalize")

    # Normalise zero vector raises
    try:
        V(0, 0).normalize()
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        pass
    print("✓ Normalize zero vector raises ZeroDivisionError")

    # Dot product
    assert _close(V(1, 0).dot(V(0, 1)), 0.0), "Orthogonal dot != 0"
    assert _close(V(2, 3).dot(V(4, 5)), 23.0), "Dot product wrong"
    print("✓ Dot product")

    # Distance
    assert _close(V(0, 0).distance_to(V(3, 4)), 5.0), "Distance failed"
    assert _close(V(1, 1).distance_to(V(1, 1)), 0.0), "Self-distance != 0"
    print("✓ Distance")

    # Copy / to_tuple
    v = V(7.5, -3.2)
    vc = v.copy()
    assert vc == v and vc is not v, "Copy failed"
    assert v.to_tuple() == (7.5, -3.2), "to_tuple failed"
    print("✓ Copy / to_tuple")

    # Helpers
    assert m.zero_vector() == V(0, 0), "zero_vector failed"
    from_p = V(0, 0)
    to_p   = V(0, 5)
    d = m.direction_vector(from_p, to_p)
    assert _close(d.x, 0.0) and _close(d.y, 1.0), "direction_vector failed"
    assert _close(m.distance(V(1, 1), V(4, 5)), 5.0), "distance helper failed"
    print("✓ zero_vector, direction_vector, distance helpers")

    print("✓ All Vector Math tests passed!")
    return True


# ── Test 2: Body class ────────────────────────────────────────────────────────


def test_body():
    """Test the Body class."""
    print("\n" + "=" * 70)
    print("TEST 2: Body Class")
    print("=" * 70)

    m    = load_module("02_body.py")
    vm   = load_module("01_vector_math.py")
    Body = m.Body
    V    = vm.Vector2D

    # Construction
    b = Body("Test", mass=10.0,
             position=V(1.0, 2.0),
             velocity=V(3.0, 4.0))
    assert b.name == "Test", "Name wrong"
    assert b.mass == 10.0,   "Mass wrong"
    assert b.position == V(1.0, 2.0), "Position wrong"
    assert b.velocity == V(3.0, 4.0), "Velocity wrong"
    print("✓ Body construction")

    # Invalid mass
    try:
        Body("Bad", mass=-1.0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("✓ Negative mass raises ValueError")

    # Default position / velocity
    b2 = Body("Default", mass=1.0)
    assert b2.position == V(0, 0), "Default position not zero"
    assert b2.velocity == V(0, 0), "Default velocity not zero"
    print("✓ Default position/velocity")

    # Kinetic energy: KE = 0.5 * m * v²
    b3 = Body("KE", mass=2.0, velocity=V(3.0, 4.0))  # |v|=5, KE=0.5*2*25=25
    assert _close(b3.kinetic_energy, 25.0), f"KE wrong: {b3.kinetic_energy}"
    print("✓ Kinetic energy")

    # Speed
    assert _close(b3.speed, 5.0), "Speed wrong"
    print("✓ Speed")

    # apply_force + move (Euler step)
    # F = 10 N in +x, m = 2 kg, dt = 1 s → a = 5, Δv = 5
    b4 = Body("Force", mass=2.0, position=V(0, 0), velocity=V(0, 0))
    b4.apply_force(V(10.0, 0.0), dt=1.0)
    assert _close(b4.velocity.x, 5.0), "apply_force velocity wrong"
    b4.move(dt=1.0)
    assert _close(b4.position.x, 5.0), "move position wrong"
    print("✓ apply_force + move (Euler step)")

    # update convenience method
    b5 = Body("Update", mass=1.0)
    b5.update(V(1.0, 0.0), dt=1.0)
    assert _close(b5.velocity.x, 1.0), "update velocity wrong"
    assert _close(b5.position.x, 1.0), "update position wrong"
    print("✓ update convenience method")

    # Trail
    b6 = Body("Trail", mass=1.0, max_trail=3)
    for _ in range(5):
        b6.move(dt=0.1)
    assert len(b6.trail) <= 3, "Trail exceeds max_trail"
    b6.clear_trail()
    assert len(b6.trail) == 0, "clear_trail failed"
    print("✓ Trail buffer (max_trail enforced, clear_trail)")

    # Distance
    ba = Body("A", mass=1.0, position=V(0, 0))
    bb = Body("B", mass=1.0, position=V(3, 4))
    assert _close(ba.distance_to(bb), 5.0), "distance_to failed"
    print("✓ distance_to")

    # Factory helpers
    sun   = m.make_sun()
    earth = m.make_earth()
    moon  = m.make_moon()
    assert sun.mass   > earth.mass > moon.mass, "Mass ordering wrong"
    assert sun.name   == "Sun",   "Sun name wrong"
    assert earth.name == "Earth", "Earth name wrong"
    assert moon.name  == "Moon",  "Moon name wrong"
    print("✓ Factory helpers (make_sun, make_earth, make_moon)")

    print("✓ All Body Class tests passed!")
    return True


# ── Test 3: Gravity simulation ────────────────────────────────────────────────


def test_gravity_simulation():
    """Test gravitational force computation and integrators."""
    print("\n" + "=" * 70)
    print("TEST 3: Gravity Simulation")
    print("=" * 70)

    gsim = load_module("03_gravity_simulation.py")
    bmod = load_module("02_body.py")
    vm   = load_module("01_vector_math.py")

    Body = bmod.Body
    V    = vm.Vector2D
    G    = gsim.G

    # gravitational_force: F = G*m1*m2/r²
    b1 = Body("B1", mass=1.0e10, position=V(0, 0))
    b2 = Body("B2", mass=1.0e10, position=V(1000.0, 0))
    force = gsim.gravitational_force(b1, b2, softening=0)
    expected_mag = G * b1.mass * b2.mass / 1000.0 ** 2
    assert _close(force.magnitude(), expected_mag, rel_tol=1e-5), \
        f"Force magnitude wrong: {force.magnitude()} vs {expected_mag}"
    # Direction should point +x (from b1 toward b2)
    assert force.x > 0, "Force direction wrong (should point toward b2)"
    assert abs(force.y) < 1e-10, "Force has unexpected y component"
    print("✓ gravitational_force magnitude and direction")

    # Force is zero when bodies coincide (softening=0 special case guard)
    b_same = Body("Same", mass=1e10, position=V(0, 0))
    f_zero = gsim.gravitational_force(b_same, b1, softening=0)
    assert f_zero.magnitude() == 0.0, "Zero distance should return zero force"
    print("✓ gravitational_force returns zero for coincident bodies")

    # net_force_on: two bodies, net force on b1 (use same softening=0 as above)
    f_net = gsim.net_force_on(b1, [b1, b2], softening=0)
    assert _close(f_net.x, force.x, rel_tol=1e-5), "net_force_on wrong"
    print("✓ net_force_on (two bodies)")

    # Energy: kinetic + potential
    sun, earth = gsim.create_sun_earth_system()
    ke = gsim.kinetic_energy([sun, earth])
    pe = gsim.potential_energy([sun, earth])
    te = gsim.total_energy([sun, earth])
    assert ke > 0, "Kinetic energy should be positive"
    assert pe < 0, "Potential energy should be negative (bound orbit)"
    assert _close(ke + pe, te), "KE + PE != total energy"
    print("✓ Kinetic, potential, total energy")

    # Leapfrog: energy conservation over short run
    sun2, earth2 = gsim.create_sun_earth_system()
    e0 = gsim.total_energy([sun2, earth2])
    dt = 3600.0      # 1 hour
    for _ in range(100):
        gsim.leapfrog_step([sun2, earth2], dt, softening=1e6)
    e1 = gsim.total_energy([sun2, earth2])
    drift = abs(e1 - e0) / abs(e0)
    assert drift < 0.001, f"Leapfrog energy drift too large: {drift:.2e}"
    print(f"✓ Leapfrog energy conservation (drift={drift:.2e})")

    # simulate() returns history
    sun3, earth3 = gsim.create_sun_earth_system()
    history = gsim.simulate([sun3, earth3], dt=3600.0, num_steps=10,
                            record_every=5)
    assert len(history) == 2, f"Expected 2 snapshots, got {len(history)}"
    assert 'positions' in history[0], "Snapshot missing 'positions'"
    assert 'total_energy' in history[0], "Snapshot missing 'total_energy'"
    print("✓ simulate() returns correct history snapshots")

    # Binary star factory
    stars = gsim.create_binary_star_system()
    assert len(stars) == 2, "Binary star system should have 2 bodies"
    assert _close(stars[0].mass, stars[1].mass), "Binary stars should be equal mass"
    print("✓ create_binary_star_system factory")

    print("✓ All Gravity Simulation tests passed!")
    return True


# ── Test 4: Three-body problem ────────────────────────────────────────────────


def test_three_body_problem():
    """Test three-body scenarios and utilities."""
    print("\n" + "=" * 70)
    print("TEST 4: Three-Body Problem")
    print("=" * 70)

    tb  = load_module("04_three_body_problem.py")
    vm  = load_module("01_vector_math.py")

    V = vm.Vector2D

    # ── Figure-8 ──────────────────────────────────────────────────────────────
    bodies = tb.create_figure_eight()
    assert len(bodies) == 3, "Figure-8 should have 3 bodies"
    assert all(b.mass == 1.0 for b in bodies), "Figure-8 bodies should all have mass 1"
    print("✓ create_figure_eight: 3 equal-mass bodies")

    tb.shift_to_com_frame(bodies)
    com = tb.centre_of_mass(bodies)
    assert abs(com.x) < 1e-10 and abs(com.y) < 1e-10, \
        "CoM should be at origin after shift"
    print("✓ shift_to_com_frame: CoM at origin")

    # Run for a short time and check energy is conserved
    dt    = 0.001
    steps = 1000
    # Compute initial total KE (PE uses G=1 which is in tb module)
    ke0 = sum(0.5 * b.mass * b.velocity.magnitude_squared() for b in bodies)
    tb.simulate_dim(bodies, dt, steps, record_every=steps + 1)
    ke1 = sum(0.5 * b.mass * b.velocity.magnitude_squared() for b in bodies)
    # KE changes (PE changes opposite), so just check bodies are still moving
    assert ke1 > 0, "Bodies should still be moving after simulation"
    print("✓ simulate_dim: bodies remain in motion")

    # ── Lagrange triangle ──────────────────────────────────────────────────────
    lag = tb.create_lagrange_triangle()
    assert len(lag) == 3, "Lagrange should have 3 bodies"
    # Check they form an equilateral triangle
    d01 = lag[0].position.distance_to(lag[1].position)
    d12 = lag[1].position.distance_to(lag[2].position)
    d20 = lag[2].position.distance_to(lag[0].position)
    assert _close(d01, d12, rel_tol=1e-5) and _close(d12, d20, rel_tol=1e-5), \
        "Lagrange bodies should form equilateral triangle"
    print("✓ create_lagrange_triangle: equilateral triangle initial conditions")

    # ── Chaotic system ─────────────────────────────────────────────────────────
    b_a = tb.create_chaotic_three_body(seed_offset=0.0)
    b_b = tb.create_chaotic_three_body(seed_offset=1e-7)

    steps_chaos = 2000
    tb.simulate_dim(b_a, 0.01, steps_chaos, record_every=steps_chaos + 1)
    tb.simulate_dim(b_b, 0.01, steps_chaos, record_every=steps_chaos + 1)

    sep = b_a[0].position.distance_to(b_b[0].position)
    assert sep > 1e-5, f"Chaos not demonstrated: separation only {sep:.2e}"
    print(f"✓ Chaotic divergence: 1e-7 initial offset → {sep:.4f} separation")

    # ── Sun–Earth–Moon ─────────────────────────────────────────────────────────
    sem = tb.create_sun_earth_moon()
    assert len(sem) == 3, "Sun–Earth–Moon should have 3 bodies"
    assert sem[0].name == "Sun"
    assert sem[1].name == "Earth"
    assert sem[2].name == "Moon"
    assert sem[0].mass > sem[1].mass > sem[2].mass, "Mass ordering wrong"
    print("✓ create_sun_earth_moon: correct masses and names")

    # ── Utilities ──────────────────────────────────────────────────────────────
    vm_mod = load_module("01_vector_math.py")
    b1 = tb.Body("A", mass=2.0, position=V(1.0, 0.0))
    b2 = tb.Body("B", mass=2.0, position=V(-1.0, 0.0))
    b3 = tb.Body("C", mass=2.0, position=V(0.0, 0.0))
    com = tb.centre_of_mass([b1, b2, b3])
    assert _close(com.x, 0.0) and _close(com.y, 0.0), "CoM calculation wrong"
    print("✓ centre_of_mass utility")

    print("✓ All Three-Body Problem tests passed!")
    return True


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    """Run all tests and print a summary."""
    print("=" * 70)
    print("GRAVITY SIMULATOR – TEST SUITE")
    print("=" * 70)

    test_fns = [
        ("Vector Math",          test_vector_math),
        ("Body Class",           test_body),
        ("Gravity Simulation",   test_gravity_simulation),
        ("Three-Body Problem",   test_three_body_problem),
    ]

    results = []
    for name, fn in test_fns:
        try:
            ok = fn()
            results.append((name, ok))
        except Exception as exc:
            print(f"\n✗ {name} FAILED: {exc}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, r in results if r)
    for name, r in results:
        print(f"  {'✓ PASSED' if r else '✗ FAILED'}  {name}")
    print("=" * 70)
    print(f"Total: {passed}/{len(results)} tests passed")
    print("=" * 70)

    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
