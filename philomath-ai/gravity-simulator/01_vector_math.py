"""
2-D Vector Mathematics
======================

This module introduces the Vector2D class – the building block for
representing positions, velocities, and forces in the gravity simulator.

Before we can simulate gravity, we need a way to work with 2-D vectors
in Python.  A vector has both a *magnitude* (size) and a *direction*, and
we need to be able to add, subtract, scale, and normalise them.

Learning Objectives:
- Understand what a 2-D vector is and why it is useful
- Implement a Vector2D class with operator overloading
- Calculate distance, magnitude, and unit (normalised) vectors
- Apply vectors to basic physics: position, velocity, and force

Key Concepts:
- ``+`` / ``-`` : vector addition and subtraction
- ``*`` / ``/`` : scaling a vector by a scalar
- Magnitude    : length of a vector, |v| = sqrt(x² + y²)
- Normalise    : unit vector in the same direction, v / |v|
- Dot product  : v₁ · v₂ = x₁x₂ + y₁y₂
- Distance     : |v₁ - v₂|

Video Reference:
- Chapter 4 of "Programming for Lovers in Python"
- https://programmingforlovers.com/chapters/chapter-4/
"""

import math


class Vector2D:
    """
    A 2-D vector with x and y components.

    Supports common arithmetic operations, magnitude, normalisation,
    dot product, and distance calculations.

    Examples:
        >>> v = Vector2D(3.0, 4.0)
        >>> v.magnitude()
        5.0
        >>> v.normalize()
        Vector2D(0.6, 0.8)
        >>> Vector2D(1, 2) + Vector2D(3, 4)
        Vector2D(4, 6)
    """

    def __init__(self, x=0.0, y=0.0):
        """
        Initialise a 2-D vector.

        Args:
            x: Horizontal component (default 0.0)
            y: Vertical component (default 0.0)
        """
        self.x = float(x)
        self.y = float(y)

    # ── Arithmetic operators ──────────────────────────────────────────────────

    def __add__(self, other):
        """Vector addition: self + other."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Vector subtraction: self - other."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """Scalar multiplication: self * scalar."""
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        """Right scalar multiplication: scalar * self."""
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        """Scalar division: self / scalar."""
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide a vector by zero")
        return Vector2D(self.x / scalar, self.y / scalar)

    def __neg__(self):
        """Unary negation: -self."""
        return Vector2D(-self.x, -self.y)

    def __eq__(self, other):
        """Equality check (float-safe, duck-typed for cross-module compatibility)."""
        try:
            return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
        except AttributeError:
            return NotImplemented

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

    # ── Vector operations ─────────────────────────────────────────────────────

    def magnitude(self):
        """
        Return the length (magnitude) of the vector.

        |v| = sqrt(x² + y²)

        Returns:
            float: Length of the vector
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def magnitude_squared(self):
        """
        Return the squared length of the vector (avoids a sqrt call).

        Returns:
            float: Squared length of the vector
        """
        return self.x ** 2 + self.y ** 2

    def normalize(self):
        """
        Return a unit vector pointing in the same direction.

        Raises:
            ZeroDivisionError: If the vector has zero magnitude

        Returns:
            Vector2D: Unit vector (magnitude == 1)
        """
        mag = self.magnitude()
        if mag == 0:
            raise ZeroDivisionError("Cannot normalize the zero vector")
        return self / mag

    def dot(self, other):
        """
        Compute the dot product of this vector with another.

        v₁ · v₂ = x₁x₂ + y₁y₂

        Args:
            other: Another Vector2D

        Returns:
            float: Dot product
        """
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        """
        Return the Euclidean distance from this vector to another.

        Args:
            other: Another Vector2D (treated as a point in 2-D space)

        Returns:
            float: Distance between the two points
        """
        return (self - other).magnitude()

    def copy(self):
        """Return a copy of this vector."""
        return Vector2D(self.x, self.y)

    def to_tuple(self):
        """Return (x, y) as a plain tuple."""
        return (self.x, self.y)


# ── Standalone helper functions ───────────────────────────────────────────────


def zero_vector():
    """Return the zero vector (0, 0)."""
    return Vector2D(0.0, 0.0)


def direction_vector(from_pos, to_pos):
    """
    Return the unit vector pointing from *from_pos* to *to_pos*.

    Args:
        from_pos: Starting position (Vector2D)
        to_pos:   Target position (Vector2D)

    Returns:
        Vector2D: Unit vector from from_pos to to_pos

    Raises:
        ZeroDivisionError: If the two positions are identical
    """
    diff = to_pos - from_pos
    return diff.normalize()


def distance(pos1, pos2):
    """
    Return the Euclidean distance between two positions.

    Args:
        pos1: First position (Vector2D)
        pos2: Second position (Vector2D)

    Returns:
        float: Distance between the two points
    """
    return pos1.distance_to(pos2)


# ── Demo ──────────────────────────────────────────────────────────────────────


def _demo():
    """Demonstrate basic vector operations."""
    print("=" * 55)
    print("VECTOR MATH DEMO")
    print("=" * 55)

    v1 = Vector2D(3.0, 4.0)
    v2 = Vector2D(1.0, 2.0)

    print(f"\nv1 = {v1}")
    print(f"v2 = {v2}")

    print(f"\nv1 + v2 = {v1 + v2}")
    print(f"v1 - v2 = {v1 - v2}")
    print(f"v1 * 2  = {v1 * 2}")
    print(f"v1 / 2  = {v1 / 2}")
    print(f"-v1     = {-v1}")

    print(f"\n|v1|  = {v1.magnitude():.4f}  (expected 5.0)")
    print(f"|v1|² = {v1.magnitude_squared():.4f}  (expected 25.0)")
    print(f"v1 normalised = {v1.normalize()}")

    print(f"\nv1 · v2 = {v1.dot(v2):.4f}  (expected {3*1 + 4*2})")
    print(f"distance(v1, v2) = {v1.distance_to(v2):.4f}")

    origin = Vector2D(0, 0)
    target = Vector2D(0, 5)
    print(f"\ndirection from origin to (0,5) = {direction_vector(origin, target)}")

    print("\n✓ Vector math demonstration complete")


if __name__ == "__main__":
    _demo()
