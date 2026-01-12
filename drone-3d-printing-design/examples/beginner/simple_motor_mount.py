"""
Beginner Example: Simple Motor Mount

This is your first drone part design! This creates a basic motor mount
suitable for 3D printing.
"""

try:
    import cadquery as cq
    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False
    print("CadQuery not installed. Install with: pip install cadquery")

import math


def create_beginner_motor_mount(
    motor_diameter=28,
    mount_height=5,
    screw_diameter=3
):
    """
    Create a simple motor mount - your first drone part!
    
    This design features:
    - Circular base to fit the motor
    - Center hole for motor shaft
    - 4 mounting holes for screws
    
    Args:
        motor_diameter: Diameter of your motor (default: 28mm)
        mount_height: How thick the mount should be (default: 5mm)
        screw_diameter: Diameter of mounting screws (default: 3mm)
    
    Returns:
        A CadQuery object that can be exported to STL
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("Please install CadQuery first")
    
    # Step 1: Calculate the size of our mount
    # We want it to be 3mm larger than the motor on each side
    wall_thickness = 3
    mount_radius = (motor_diameter / 2) + wall_thickness
    
    print(f"Motor diameter: {motor_diameter}mm")
    print(f"Mount radius: {mount_radius}mm")
    
    # Step 2: Create the base circle and extrude it
    motor_mount = (
        cq.Workplane("XY")          # Start on the XY plane
        .circle(mount_radius)       # Draw a circle
        .extrude(mount_height)      # Pull it up to create a cylinder
    )
    
    print(f"Created base cylinder: {mount_radius}mm radius, {mount_height}mm tall")
    
    # Step 3: Cut a hole in the center for the motor
    motor_mount = (
        motor_mount
        .faces(">Z")                # Select the top face
        .workplane()                # Create a new workplane on it
        .hole(motor_diameter)       # Cut a hole through
    )
    
    print(f"Added center hole: {motor_diameter}mm diameter")
    
    # Step 4: Add 4 screw holes in a circular pattern
    # These will be evenly spaced around the mount
    screw_circle_radius = mount_radius - (wall_thickness / 2)
    
    # Calculate positions for 4 holes at 0°, 90°, 180°, 270°
    hole_positions = []
    for i in range(4):
        angle = i * 90  # 0, 90, 180, 270 degrees
        angle_rad = math.radians(angle)
        x = screw_circle_radius * math.cos(angle_rad)
        y = screw_circle_radius * math.sin(angle_rad)
        hole_positions.append((x, y))
        print(f"Screw hole {i+1}: x={x:.1f}mm, y={y:.1f}mm")
    
    # Add the holes
    motor_mount = (
        motor_mount
        .faces(">Z")
        .workplane()
        .pushPoints(hole_positions)  # Position for each hole
        .hole(screw_diameter)        # Cut the holes
    )
    
    print(f"Added 4 screw holes: {screw_diameter}mm diameter")
    
    # Done!
    return motor_mount


# Main execution
if __name__ == "__main__":
    print("=" * 50)
    print("BEGINNER EXAMPLE: Simple Motor Mount")
    print("=" * 50)
    print()
    
    if not CADQUERY_AVAILABLE:
        print("⚠️  CadQuery is not installed!")
        print()
        print("To install CadQuery, run:")
        print("  pip install cadquery")
        print()
        print("For detailed instructions, visit:")
        print("  https://cadquery.readthedocs.io/en/latest/installation.html")
    else:
        print("✓ CadQuery is available!")
        print()
        
        # Create the motor mount
        print("Creating motor mount...")
        print("-" * 50)
        
        motor_mount = create_beginner_motor_mount(
            motor_diameter=28,  # Standard size for many drone motors
            mount_height=5,     # 5mm is strong enough
            screw_diameter=3    # M3 screws
        )
        
        print("-" * 50)
        print()
        
        # Try to export it
        output_file = "/tmp/beginner_motor_mount.stl"
        try:
            cq.exporters.export(motor_mount, output_file)
            print(f"✓ SUCCESS! Motor mount saved to:")
            print(f"  {output_file}")
            print()
            print("Next steps:")
            print("1. Open the STL file in your slicer (Cura, PrusaSlicer, etc.)")
            print("2. Recommended settings:")
            print("   - Layer height: 0.2mm")
            print("   - Infill: 30-50%")
            print("   - Material: PLA or PETG")
            print("3. Print and test fit on your motor!")
            print()
            print("Pro tip: Print one first to check the fit before printing 4!")
        except Exception as e:
            print(f"✓ Motor mount created successfully!")
            print(f"  (Could not export: {e})")
        
        print()
        print("=" * 50)
        print("Congratulations! You've created your first drone part!")
        print("=" * 50)
