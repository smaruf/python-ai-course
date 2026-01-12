"""
Beginner Example: Simple Glider Design

This example creates a basic glider design suitable for 3D printing.
Perfect for learning fixed-wing aircraft principles and integrating
with simple tools like PowerUp smartphone-controlled modules.
"""

try:
    import cadquery as cq
    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False
    print("CadQuery not installed. Install with: pip install cadquery")

import math


def create_simple_glider_wing(
    wingspan=300,
    chord_length=80,
    thickness=3,
    airfoil_height=8
):
    """
    Create a simple glider wing with a basic airfoil shape.
    
    This design can be printed and integrated with tools like:
    - PowerUp smartphone-controlled modules
    - Simple electronic stabilizers
    
    Args:
        wingspan: Total wing span in mm (default: 300mm)
        chord_length: Wing chord (front to back) in mm (default: 80mm)
        thickness: Minimum wing thickness in mm (default: 3mm)
        airfoil_height: Maximum airfoil thickness in mm (default: 8mm)
    
    Returns:
        A CadQuery object that can be exported to STL
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("Please install CadQuery first")
    
    print(f"Creating glider wing:")
    print(f"  Wingspan: {wingspan}mm")
    print(f"  Chord length: {chord_length}mm")
    print(f"  Thickness: {thickness}mm")
    print(f"  Airfoil height: {airfoil_height}mm")
    
    # Create a simple airfoil profile (approximation)
    # Using a basic curved top and flat bottom
    
    # Step 1: Create the basic wing shape using an airfoil approximation
    print("\nStep 1: Creating wing profile...")
    
    # Create points for a simple airfoil shape
    # We'll use a simplified Clark-Y style airfoil
    points = [
        (0, 0),  # Leading edge bottom
        (chord_length * 0.3, airfoil_height * 0.6),  # Max thickness point
        (chord_length * 0.7, airfoil_height * 0.3),  # Mid section
        (chord_length, thickness),  # Trailing edge
        (chord_length, 0),  # Trailing edge bottom
    ]
    
    wing_profile = (
        cq.Workplane("XZ")
        .spline(points, includeCurrent=False)
        .lineTo(0, 0)
        .close()
    )
    
    # Step 2: Extrude the profile to create the wing
    print("Step 2: Extruding wing profile...")
    wing = wing_profile.extrude(wingspan, both=True)
    
    # Step 3: Add a center slot for mounting electronics
    print("Step 3: Adding electronics mounting slot...")
    slot_width = 30
    slot_depth = airfoil_height - thickness
    
    wing = (
        wing
        .faces(">Y")
        .workplane(centerOption="CenterOfBoundBox")
        .rect(chord_length * 0.6, slot_width)
        .cutBlind(-slot_depth)
    )
    
    # Step 4: Add mounting holes for control surfaces or electronics
    print("Step 4: Adding mounting holes...")
    
    # Add holes at 25% and 75% of wingspan for attachment points
    mounting_positions = [
        (-wingspan * 0.25, chord_length * 0.5),
        (wingspan * 0.25, chord_length * 0.5)
    ]
    
    for pos in mounting_positions:
        wing = (
            wing
            .faces(">Y")
            .workplane(centerOption="CenterOfBoundBox")
            .center(pos[0], pos[1] - chord_length * 0.5)
            .hole(3)  # M3 holes for servos or attachments
        )
    
    print("\n✓ Glider wing created!")
    
    return wing


def create_simple_glider_fuselage(
    length=200,
    width=30,
    height=20
):
    """
    Create a simple fuselage for the glider.
    
    This can house electronics like:
    - PowerUp smartphone-controlled module
    - Battery compartment
    - Stabilizer electronics
    
    Args:
        length: Fuselage length in mm (default: 200mm)
        width: Fuselage width in mm (default: 30mm)
        height: Fuselage height in mm (default: 20mm)
    
    Returns:
        A CadQuery object that can be exported to STL
    """
    if not CADQUERY_AVAILABLE:
        raise ImportError("Please install CadQuery first")
    
    print(f"\nCreating glider fuselage:")
    print(f"  Length: {length}mm")
    print(f"  Width: {width}mm")
    print(f"  Height: {height}mm")
    
    # Create a streamlined fuselage
    print("\nStep 1: Creating fuselage body...")
    
    # Create an elongated body with rounded nose
    fuselage = (
        cq.Workplane("XY")
        .ellipse(length / 2, width / 2)
        .extrude(height)
    )
    
    # Add a hollow interior for electronics
    print("Step 2: Creating electronics bay...")
    wall_thickness = 2
    
    fuselage = (
        fuselage
        .faces(">Z")
        .workplane()
        .ellipse(length / 2 - wall_thickness * 2, width / 2 - wall_thickness)
        .cutBlind(-height + wall_thickness)
    )
    
    # Add a slot for the wing
    print("Step 3: Adding wing mounting slot...")
    wing_slot_width = 35
    wing_slot_thickness = 4
    
    fuselage = (
        fuselage
        .faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .center(0, 0)
        .rect(wing_slot_width, width * 1.2)
        .cutBlind(-wing_slot_thickness)
    )
    
    # Add mounting holes for wing attachment
    print("Step 4: Adding wing mounting holes...")
    hole_spacing = 20
    
    fuselage = (
        fuselage
        .faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .rect(hole_spacing, 0, forConstruction=True)
        .vertices()
        .hole(2.5)  # M2.5 holes
    )
    
    print("\n✓ Glider fuselage created!")
    
    return fuselage


# Main execution
if __name__ == "__main__":
    print("=" * 70)
    print("BEGINNER EXAMPLE: Simple Glider Design")
    print("=" * 70)
    print()
    print("This glider design can be integrated with simple tools like:")
    print("  • PowerUp smartphone-controlled paper airplane modules")
    print("    (https://www.poweruptoys.com/)")
    print("  • Smartphone-controlled gimbal stabilizers")
    print("    (Various models available on Amazon and retailers)")
    print("  • Simple RC receivers and servos")
    print()
    print("=" * 70)
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
        
        # Create the glider wing
        print("Creating glider wing...")
        print("-" * 70)
        
        glider_wing = create_simple_glider_wing(
            wingspan=300,        # 300mm wingspan (suitable for indoor/light outdoor)
            chord_length=80,     # 80mm chord
            thickness=3,         # 3mm minimum thickness
            airfoil_height=8     # 8mm max airfoil thickness
        )
        
        print("-" * 70)
        print()
        
        # Create the glider fuselage
        print("Creating glider fuselage...")
        print("-" * 70)
        
        glider_fuselage = create_simple_glider_fuselage(
            length=200,  # 200mm fuselage
            width=30,    # 30mm wide
            height=20    # 20mm tall
        )
        
        print("-" * 70)
        print()
        
        # Try to export both parts
        try:
            wing_file = "/tmp/glider_wing.stl"
            fuselage_file = "/tmp/glider_fuselage.stl"
            
            cq.exporters.export(glider_wing, wing_file)
            cq.exporters.export(glider_fuselage, fuselage_file)
            
            print(f"✓ SUCCESS! Glider parts saved:")
            print(f"  Wing: {wing_file}")
            print(f"  Fuselage: {fuselage_file}")
            print()
            print("Next steps:")
            print("1. Print both parts separately")
            print("2. Recommended print settings:")
            print("   - Layer height: 0.15-0.2mm")
            print("   - Infill: 15-20% (light for flight)")
            print("   - Material: PLA (light) or PETG (stronger)")
            print("   - Supports: Minimal, mainly for wing underside if needed")
            print("3. Assembly:")
            print("   - Slide wing into fuselage slot")
            print("   - Use M2.5 screws to secure")
            print("   - Add PowerUp module or simple electronics")
            print("4. Flight testing:")
            print("   - Start with hand launches")
            print("   - Adjust weight balance (CG at 30-35% of chord)")
            print("   - Add control surfaces if using powered module")
            print()
            print("Integration ideas:")
            print("  • PowerUp 4.0: Smartphone-controlled thrust + rudder")
            print("  • Simple RC: 2-channel receiver (requires designing control surfaces)")
            print("  • Gimbal stabilizer: For camera mounting experiments")
            print()
            print("Design variations to try:")
            print("  • Increase wingspan to 400-500mm for better glide")
            print("  • Add dihedral angle (upward wing bend) for stability")
            print("  • Design removable tail section with elevator/rudder")
            print("  • Create winglets at tips for efficiency")
            
        except Exception as e:
            print(f"✓ Glider parts created successfully!")
            print(f"  (Could not export: {e})")
        
        print()
        print("=" * 70)
        print("Congratulations! You've designed a simple glider!")
        print("=" * 70)
        print()
        print("What you learned:")
        print("  • Creating airfoil shapes with splines")
        print("  • Designing fixed-wing aircraft parts")
        print("  • Integration points for electronics")
        print("  • Practical considerations for flight")
        print()
        print("Next challenge:")
        print("  Try designing control surfaces (elevator, rudder, ailerons)")
        print("  for improved flight control!")
