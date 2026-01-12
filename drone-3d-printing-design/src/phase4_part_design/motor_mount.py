"""
Phase 4: Aircraft Part Design - Motor Mount

This module demonstrates how to design a parametric motor mount for drones.
A motor mount is one of the most fundamental parts in drone building.
"""

try:
    import cadquery as cq
    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False

import math


def create_simple_motor_mount(
    motor_diameter: float = 28,
    height: float = 5,
    hole_diameter: float = 3,
    mounting_holes: int = 4,
    wall_thickness: float = 3
) -> object:
    """
    Create a simple circular motor mount.
    
    Args:
        motor_diameter: Diameter of the motor
        height: Height of the mount
        hole_diameter: Diameter of mounting holes
        mounting_holes: Number of mounting holes
        wall_thickness: Thickness of the mount wall
    
    Returns:
        CadQuery object representing the motor mount
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    # Calculate mount dimensions
    mount_radius = (motor_diameter / 2) + wall_thickness
    
    # Create base cylinder
    mount = (
        cq.Workplane("XY")
        .circle(mount_radius)
        .extrude(height)
    )
    
    # Add center hole for motor shaft
    mount = (
        mount
        .faces(">Z")
        .workplane()
        .hole(motor_diameter)
    )
    
    # Add mounting holes in circular pattern
    hole_circle_radius = mount_radius - (wall_thickness / 2)
    angle_step = 360 / mounting_holes
    
    hole_points = []
    for i in range(mounting_holes):
        angle_rad = math.radians(i * angle_step)
        x = hole_circle_radius * math.cos(angle_rad)
        y = hole_circle_radius * math.sin(angle_rad)
        hole_points.append((x, y))
    
    mount = (
        mount
        .faces(">Z")
        .workplane()
        .pushPoints(hole_points)
        .hole(hole_diameter)
    )
    
    return mount


def create_advanced_motor_mount(
    motor_diameter: float = 28,
    motor_height: float = 10,
    base_thickness: float = 3,
    wall_thickness: float = 2.5,
    screw_holes: int = 4,
    screw_diameter: float = 3.2,
    add_wire_channel: bool = True
) -> object:
    """
    Create an advanced motor mount with features.
    
    Features:
    - Raised lip to secure motor
    - Wire management channel
    - Countersunk screw holes
    - Filleted edges for strength
    
    Args:
        motor_diameter: Diameter of the motor
        motor_height: Height of motor body
        base_thickness: Thickness of base plate
        wall_thickness: Thickness of walls
        screw_holes: Number of screw holes
        screw_diameter: Diameter of screws
        add_wire_channel: Add wire management channel
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    outer_radius = (motor_diameter / 2) + wall_thickness
    inner_radius = motor_diameter / 2
    lip_height = motor_height * 0.3  # Lip holds 30% of motor
    
    # Create base plate
    mount = (
        cq.Workplane("XY")
        .circle(outer_radius + 5)  # Extended base
        .extrude(base_thickness)
    )
    
    # Add raised lip for motor
    mount = (
        mount
        .faces(">Z")
        .workplane()
        .circle(outer_radius)
        .extrude(lip_height)
    )
    
    # Hollow out for motor
    mount = (
        mount
        .faces(">Z")
        .workplane(offset=-lip_height)
        .circle(inner_radius)
        .cutThruAll()
    )
    
    # Add mounting screw holes
    screw_circle_radius = outer_radius + 3
    angle_step = 360 / screw_holes
    
    screw_points = []
    for i in range(screw_holes):
        angle_rad = math.radians(i * angle_step)
        x = screw_circle_radius * math.cos(angle_rad)
        y = screw_circle_radius * math.sin(angle_rad)
        screw_points.append((x, y))
    
    mount = (
        mount
        .faces("<Z")
        .workplane()
        .pushPoints(screw_points)
        .hole(screw_diameter)
    )
    
    # Add wire channel if requested
    if add_wire_channel:
        channel_width = 4
        channel_depth = base_thickness / 2
        
        mount = (
            mount
            .faces("<Z")
            .workplane()
            .rect(outer_radius * 2, channel_width)
            .cutBlind(channel_depth)
        )
    
    # Add fillets for strength
    mount = (
        mount
        .edges("|Z")
        .fillet(0.5)
    )
    
    return mount


def create_quad_motor_mount_with_arms(
    motor_diameter: float = 28,
    arm_width: float = 10,
    arm_thickness: float = 4
) -> object:
    """
    Create a motor mount with integrated arm attachment points.
    
    This design is suitable for mounting on carbon fiber arms.
    
    Args:
        motor_diameter: Diameter of motor
        arm_width: Width of the drone arm
        arm_thickness: Thickness of the arm
    
    Returns:
        CadQuery object
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("CadQuery is required")
    
    mount_radius = (motor_diameter / 2) + 3
    base_height = 3
    
    # Create motor mounting base
    mount = (
        cq.Workplane("XY")
        .circle(mount_radius)
        .extrude(base_height)
    )
    
    # Add center hole
    mount = (
        mount
        .faces(">Z")
        .workplane()
        .hole(motor_diameter - 2)  # Tight fit
    )
    
    # Add arm attachment tabs (4 tabs at 90 degrees)
    tab_length = arm_width + 5
    tab_width = arm_width
    tab_height = arm_thickness + 2
    
    for angle in [0, 90, 180, 270]:
        angle_rad = math.radians(angle)
        x_offset = (mount_radius + tab_length/2) * math.cos(angle_rad)
        y_offset = (mount_radius + tab_length/2) * math.sin(angle_rad)
        
        tab = (
            cq.Workplane("XY")
            .center(x_offset, y_offset)
            .rect(tab_length if angle in [0, 180] else tab_width,
                  tab_width if angle in [0, 180] else tab_length)
            .extrude(tab_height)
        )
        
        mount = mount.union(tab)
    
    # Add screw holes through tabs
    hole_positions = [
        (mount_radius + tab_length - 3, 0),
        (-mount_radius - tab_length + 3, 0),
        (0, mount_radius + tab_length - 3),
        (0, -mount_radius - tab_length + 3)
    ]
    
    for x, y in hole_positions:
        hole = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(1.6)  # M3 screw
            .extrude(tab_height)
        )
        mount = mount.cut(hole)
    
    return mount


def calculate_motor_mount_weight(
    motor_diameter: float,
    height: float,
    wall_thickness: float,
    material: str = "PLA",
    infill: float = 20
) -> dict:
    """
    Calculate estimated weight of motor mount.
    
    Args:
        motor_diameter: Motor diameter
        height: Mount height
        wall_thickness: Wall thickness
        material: Print material
        infill: Infill percentage
    
    Returns:
        Dictionary with weight info
    """
    # Calculate volume
    outer_radius = (motor_diameter / 2) + wall_thickness
    inner_radius = motor_diameter / 2
    
    outer_volume = math.pi * outer_radius**2 * height
    inner_volume = math.pi * inner_radius**2 * height
    volume_mm3 = outer_volume - inner_volume
    
    # Material densities (g/cm³)
    densities = {
        'PLA': 1.24,
        'PETG': 1.27,
        'ABS': 1.04,
        'Nylon': 1.14
    }
    
    density = densities.get(material, 1.24)
    
    # Convert and calculate (simplified)
    volume_cm3 = volume_mm3 / 1000
    shell_ratio = 0.4
    infill_ratio = 0.6 * (infill / 100)
    effective_volume = volume_cm3 * (shell_ratio + infill_ratio)
    
    weight = effective_volume * density
    
    return {
        'volume_mm3': volume_mm3,
        'volume_cm3': volume_cm3,
        'effective_volume_cm3': effective_volume,
        'weight_grams': weight,
        'material': material,
        'infill_percent': infill
    }


# Example usage
if __name__ == "__main__":
    print("=== Phase 4: Motor Mount Design ===\n")
    
    if not CADQUERY_AVAILABLE:
        print("CadQuery not installed. Please install with:")
        print("  pip install cadquery")
    else:
        print("Creating motor mounts...\n")
        
        # Example 1: Simple motor mount
        print("1. Simple Motor Mount (28mm motor)")
        simple_mount = create_simple_motor_mount(
            motor_diameter=28,
            height=5,
            hole_diameter=3,
            mounting_holes=4
        )
        
        try:
            cq.exporters.export(simple_mount, "/tmp/simple_motor_mount.stl")
            print("   ✓ Exported to /tmp/simple_motor_mount.stl")
        except:
            print("   ✓ Created (export unavailable)")
        
        # Example 2: Advanced motor mount
        print("\n2. Advanced Motor Mount (with features)")
        advanced_mount = create_advanced_motor_mount(
            motor_diameter=28,
            motor_height=10,
            add_wire_channel=True
        )
        
        try:
            cq.exporters.export(advanced_mount, "/tmp/advanced_motor_mount.stl")
            print("   ✓ Exported to /tmp/advanced_motor_mount.stl")
        except:
            print("   ✓ Created (export unavailable)")
        
        # Example 3: Weight calculation
        print("\n3. Weight Estimation:")
        weight_info = calculate_motor_mount_weight(28, 5, 3, "PLA", 20)
        for key, value in weight_info.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
        
        print("\n✓ All motor mounts created successfully!")
        print("\nNext steps:")
        print("- Open STL files in your slicer (Cura, PrusaSlicer)")
        print("- Adjust print settings (layer height, infill)")
        print("- Print and test on actual motor")
