"""
Phase 3: Python-Based CAD - CadQuery Basics

This module demonstrates fundamental CadQuery concepts for parametric design.
"""

try:
    import cadquery as cq
    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False
    print("Warning: CadQuery not installed. Install with: pip install cadquery")


def create_simple_box(length: float, width: float, height: float) -> object:
    """
    Create a simple box.
    
    Args:
        length: Length of the box
        width: Width of the box
        height: Height of the box
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    result = cq.Workplane("XY").box(length, width, height)
    return result


def create_cylinder(radius: float, height: float) -> object:
    """
    Create a simple cylinder.
    
    Args:
        radius: Radius of the cylinder
        height: Height of the cylinder
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    result = (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(height)
    )
    return result


def create_hollow_cylinder(
    outer_radius: float,
    inner_radius: float,
    height: float
) -> object:
    """
    Create a hollow cylinder (tube).
    
    Args:
        outer_radius: Outer radius
        inner_radius: Inner radius
        height: Height
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    result = (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(height)
    )
    return result


def create_box_with_holes(
    length: float,
    width: float,
    height: float,
    hole_diameter: float,
    hole_spacing: float = None
) -> object:
    """
    Create a box with holes on top.
    
    Args:
        length: Length of the box
        width: Width of the box
        height: Height of the box
        hole_diameter: Diameter of holes
        hole_spacing: Spacing between holes (default: diameter * 2)
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    if hole_spacing is None:
        hole_spacing = hole_diameter * 2
    
    result = (
        cq.Workplane("XY")
        .box(length, width, height)
        .faces(">Z")
        .workplane()
        .rarray(hole_spacing, hole_spacing, 2, 2)
        .hole(hole_diameter)
    )
    return result


def create_filleted_box(
    length: float,
    width: float,
    height: float,
    fillet_radius: float
) -> object:
    """
    Create a box with filleted edges.
    
    Args:
        length: Length of the box
        width: Width of the box
        height: Height of the box
        fillet_radius: Radius of fillets
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    result = (
        cq.Workplane("XY")
        .box(length, width, height)
        .edges("|Z")
        .fillet(fillet_radius)
    )
    return result


def create_chamfered_cylinder(
    radius: float,
    height: float,
    chamfer_size: float
) -> object:
    """
    Create a cylinder with chamfered edges.
    
    Args:
        radius: Radius of cylinder
        height: Height of cylinder
        chamfer_size: Size of chamfer
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    result = (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(height)
        .edges(">Z")
        .chamfer(chamfer_size)
    )
    return result


def create_mounting_plate(
    length: float,
    width: float,
    thickness: float,
    hole_diameter: float,
    edge_distance: float = 5.0
) -> object:
    """
    Create a mounting plate with corner holes.
    
    Args:
        length: Length of plate
        width: Width of plate
        thickness: Thickness of plate
        hole_diameter: Diameter of mounting holes
        edge_distance: Distance from edge to hole center
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    # Create base plate
    result = cq.Workplane("XY").box(length, width, thickness)
    
    # Add corner holes
    half_length = length / 2 - edge_distance
    half_width = width / 2 - edge_distance
    
    result = (
        result
        .faces(">Z")
        .workplane()
        .pushPoints([
            (-half_length, -half_width),
            (half_length, -half_width),
            (half_length, half_width),
            (-half_length, half_width)
        ])
        .hole(hole_diameter)
    )
    
    return result


def create_circular_pattern(
    base_radius: float,
    feature_count: int,
    feature_size: float
) -> object:
    """
    Create a circular pattern of features.
    
    Args:
        base_radius: Radius of the circular pattern
        feature_count: Number of features
        feature_size: Size of each feature
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    import math
    
    # Create base
    result = (
        cq.Workplane("XY")
        .circle(base_radius + 5)
        .extrude(5)
    )
    
    # Add circular pattern of holes
    angle_step = 360 / feature_count
    points = []
    for i in range(feature_count):
        angle_rad = math.radians(i * angle_step)
        x = base_radius * math.cos(angle_rad)
        y = base_radius * math.sin(angle_rad)
        points.append((x, y))
    
    result = (
        result
        .faces(">Z")
        .workplane()
        .pushPoints(points)
        .hole(feature_size)
    )
    
    return result


# Example usage and demonstration
if __name__ == "__main__":
    print("=== Phase 3: CadQuery Basics ===\n")
    
    if not CADQUERY_AVAILABLE:
        print("CadQuery is not installed.")
        print("Install it with: pip install cadquery")
        print("\nNote: Some dependencies may require conda.")
        print("Visit: https://cadquery.readthedocs.io/en/latest/installation.html")
    else:
        print("CadQuery is available!")
        print("\nCreating example parts...\n")
        
        # Example 1: Simple box
        print("1. Creating simple box (20x15x10)...")
        box = create_simple_box(20, 15, 10)
        
        # Example 2: Cylinder
        print("2. Creating cylinder (r=10, h=20)...")
        cylinder = create_cylinder(10, 20)
        
        # Example 3: Hollow cylinder
        print("3. Creating hollow cylinder...")
        tube = create_hollow_cylinder(15, 10, 25)
        
        # Example 4: Filleted box
        print("4. Creating filleted box...")
        filleted = create_filleted_box(30, 20, 10, 2)
        
        # Example 5: Mounting plate
        print("5. Creating mounting plate...")
        plate = create_mounting_plate(50, 40, 3, 3.2)
        
        # Example 6: Circular pattern
        print("6. Creating circular pattern...")
        pattern = create_circular_pattern(20, 6, 3)
        
        print("\nAll examples created successfully!")
        print("\nTo visualize these parts:")
        print("- Install CQ-Editor: https://github.com/CadQuery/CQ-editor")
        print("- Or export to STL and view in your slicer")
        
        # Example of exporting
        try:
            print("\nExporting mounting plate to STL...")
            cq.exporters.export(plate, "/tmp/mounting_plate.stl")
            print("✓ Exported to /tmp/mounting_plate.stl")
        except Exception as e:
            print(f"Export failed: {e}")
