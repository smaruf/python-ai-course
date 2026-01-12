"""
Beginner Example: Camera Mount

This example creates a simple camera mount for FPV drones.
It demonstrates angled features and practical drone part design.
"""

try:
    import cadquery as cq
    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False
    print("CadQuery not installed. Install with: pip install cadquery")

import math


def create_simple_camera_mount(
    camera_width=28,
    camera_height=28,
    mount_angle=30,
    thickness=3
):
    """
    Create a simple camera mount with adjustable angle.
    
    This mount allows you to tilt your FPV camera for forward flight.
    Common angles are 20-40 degrees.
    
    Args:
        camera_width: Width of camera board (default: 28mm for typical FPV cam)
        camera_height: Height of camera board
        mount_angle: Angle to tilt camera (default: 30 degrees)
        thickness: Wall thickness (default: 3mm)
    
    Returns:
        A CadQuery object that can be exported to STL
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("Please install CadQuery first")
    
    print(f"Creating camera mount:")
    print(f"  Camera size: {camera_width}x{camera_height}mm")
    print(f"  Mount angle: {mount_angle}°")
    print(f"  Thickness: {thickness}mm")
    
    # Calculate dimensions
    base_width = camera_width + 2 * thickness
    base_depth = 15  # Enough for mounting holes
    base_height = thickness
    
    # Camera holder dimensions
    holder_height = camera_height + thickness
    
    # Step 1: Create the base plate
    print("\nStep 1: Creating base plate...")
    mount = (
        cq.Workplane("XY")
        .box(base_width, base_depth, base_height)
    )
    
    # Step 2: Add mounting holes to base
    print("Step 2: Adding mounting holes...")
    hole_spacing = base_width - 10
    mount = (
        mount
        .faces(">Z")
        .workplane()
        .rect(hole_spacing, 0, forConstruction=True)
        .vertices()
        .hole(3)  # M3 screw holes
    )
    
    # Step 3: Create the angled camera holder
    print(f"Step 3: Creating {mount_angle}° angled holder...")
    
    # Calculate the position offset due to angle
    angle_rad = math.radians(mount_angle)
    
    # Create camera holder box
    holder = (
        cq.Workplane("XY")
        .transformed(rotate=(mount_angle, 0, 0))  # Rotate around X axis
        .center(0, holder_height/2)
        .box(camera_width, holder_height, thickness)
    )
    
    # Combine base and holder
    mount = mount.union(holder)
    
    # Step 4: Add camera mounting holes
    print("Step 4: Adding camera mounting holes...")
    
    # Standard FPV camera hole pattern (20mm spacing)
    cam_hole_spacing = 20
    
    holder_with_holes = (
        cq.Workplane("XY")
        .transformed(rotate=(mount_angle, 0, 0))
        .center(0, holder_height/2)
        .rect(cam_hole_spacing, cam_hole_spacing, forConstruction=True)
        .vertices()
        .circle(1.5)  # M2 holes for camera
        .extrude(thickness, combine=False)
    )
    
    # Cut the holes
    mount = mount.cut(holder_with_holes)
    
    # Step 5: Add fillets for strength and easier printing
    print("Step 5: Adding fillets...")
    try:
        mount = mount.edges("|Z and >Y").fillet(1)
    except:
        print("  (Some fillets skipped - complex geometry)")
    
    print("\n✓ Camera mount created!")
    
    return mount


# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("BEGINNER EXAMPLE: Simple Camera Mount")
    print("=" * 60)
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
        
        # Create the camera mount
        print("Creating camera mount for typical FPV camera...")
        print("-" * 60)
        
        camera_mount = create_simple_camera_mount(
            camera_width=28,      # Standard FPV camera
            camera_height=28,
            mount_angle=30,       # 30° angle for racing
            thickness=3
        )
        
        print("-" * 60)
        print()
        
        # Try to export it
        output_file = "/tmp/camera_mount.stl"
        try:
            cq.exporters.export(camera_mount, output_file)
            print(f"✓ SUCCESS! Camera mount saved to:")
            print(f"  {output_file}")
            print()
            print("Next steps:")
            print("1. Open the STL file in your slicer")
            print("2. Recommended settings:")
            print("   - Layer height: 0.2mm")
            print("   - Infill: 40-50% (needs to be strong)")
            print("   - Supports: May need support for angled part")
            print("   - Material: PETG or Nylon (impact resistance)")
            print("3. Print orientation: Base flat on bed")
            print()
            print("Pro tip: Try different angles (20°, 30°, 40°)")
            print("         to see what works best for your flying style!")
            print()
            
            # Create variations
            print("Creating additional angle variations...")
            for angle in [20, 40]:
                variant = create_simple_camera_mount(mount_angle=angle)
                variant_file = f"/tmp/camera_mount_{angle}deg.stl"
                cq.exporters.export(variant, variant_file)
                print(f"  ✓ {angle}° version: {variant_file}")
            
        except Exception as e:
            print(f"✓ Camera mount created successfully!")
            print(f"  (Could not export: {e})")
        
        print()
        print("=" * 60)
        print("Great job! You've created a functional camera mount!")
        print("=" * 60)
        print()
        print("What you learned:")
        print("  • Creating angled features with .transformed()")
        print("  • Combining multiple parts with .union()")
        print("  • Adding hole patterns")
        print("  • Practical drone part design")
