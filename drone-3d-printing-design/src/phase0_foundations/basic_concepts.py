"""
Phase 0: Python Foundations - Basic Concepts

This module covers fundamental Python concepts needed for parametric CAD design.
"""

# 1. Variables and Basic Math
def calculate_circle_area(radius: float) -> float:
    """Calculate the area of a circle."""
    import math
    return math.pi * radius ** 2


def calculate_rectangle_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    return length * width


# 2. Classes and Objects
class Point3D:
    """Represents a point in 3D space."""
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def distance_to(self, other: 'Point3D') -> float:
        """Calculate distance to another point."""
        import math
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def __repr__(self) -> str:
        return f"Point3D({self.x}, {self.y}, {self.z})"


class Vector3D:
    """Represents a vector in 3D space."""
    
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def magnitude(self) -> float:
        """Calculate the magnitude of the vector."""
        import math
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self) -> 'Vector3D':
        """Return a normalized (unit) vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)
    
    def dot(self, other: 'Vector3D') -> float:
        """Calculate dot product with another vector."""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vector3D') -> 'Vector3D':
        """Calculate cross product with another vector."""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def __repr__(self) -> str:
        return f"Vector3D({self.x}, {self.y}, {self.z})"


# 3. Lists and Dictionaries for Part Properties
class PartProperties:
    """Store and manage part properties."""
    
    def __init__(self):
        self.properties = {}
    
    def add_property(self, name: str, value: any):
        """Add a property to the part."""
        self.properties[name] = value
    
    def get_property(self, name: str, default=None):
        """Get a property value."""
        return self.properties.get(name, default)
    
    def list_properties(self):
        """List all properties."""
        return list(self.properties.keys())
    
    def __repr__(self) -> str:
        return f"PartProperties({self.properties})"


# 4. Functions for Parametric Design
def generate_mounting_holes(
    count: int,
    radius: float,
    hole_diameter: float
) -> list[tuple[float, float]]:
    """
    Generate coordinates for evenly-spaced mounting holes in a circle.
    
    Args:
        count: Number of holes
        radius: Radius of the circle
        hole_diameter: Diameter of each hole
    
    Returns:
        List of (x, y) coordinates
    """
    import math
    holes = []
    angle_step = 2 * math.pi / count
    
    for i in range(count):
        angle = i * angle_step
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        holes.append((x, y))
    
    return holes


def calculate_material_volume(
    outer_radius: float,
    inner_radius: float,
    height: float
) -> float:
    """
    Calculate volume of a hollow cylinder.
    
    Args:
        outer_radius: Outer radius
        inner_radius: Inner radius (0 for solid)
        height: Height of cylinder
    
    Returns:
        Volume in cubic units
    """
    import math
    outer_volume = math.pi * outer_radius ** 2 * height
    inner_volume = math.pi * inner_radius ** 2 * height
    return outer_volume - inner_volume


# 5. Example Usage
if __name__ == "__main__":
    print("=== Phase 0: Python Foundations ===\n")
    
    # Example 1: Basic calculations
    print("1. Basic Calculations:")
    area = calculate_circle_area(10)
    print(f"   Circle area (r=10): {area:.2f}")
    
    rect_area = calculate_rectangle_area(20, 15)
    print(f"   Rectangle area (20x15): {rect_area:.2f}\n")
    
    # Example 2: 3D Points
    print("2. 3D Points:")
    p1 = Point3D(0, 0, 0)
    p2 = Point3D(10, 10, 10)
    distance = p1.distance_to(p2)
    print(f"   Point 1: {p1}")
    print(f"   Point 2: {p2}")
    print(f"   Distance: {distance:.2f}\n")
    
    # Example 3: Vectors
    print("3. Vectors:")
    v1 = Vector3D(1, 0, 0)
    v2 = Vector3D(0, 1, 0)
    cross = v1.cross(v2)
    print(f"   Vector 1: {v1}")
    print(f"   Vector 2: {v2}")
    print(f"   Cross product: {cross}\n")
    
    # Example 4: Mounting holes
    print("4. Mounting Holes:")
    holes = generate_mounting_holes(4, 20, 3)
    for i, (x, y) in enumerate(holes):
        print(f"   Hole {i+1}: x={x:.2f}, y={y:.2f}")
    
    # Example 5: Volume calculation
    print("\n5. Volume Calculation:")
    volume = calculate_material_volume(15, 10, 5)
    print(f"   Hollow cylinder volume: {volume:.2f} cubic units")
    
    # Example 6: Part properties
    print("\n6. Part Properties:")
    part = PartProperties()
    part.add_property("material", "PLA")
    part.add_property("weight", 25.5)
    part.add_property("color", "black")
    print(f"   {part}")
    print(f"   Material: {part.get_property('material')}")
