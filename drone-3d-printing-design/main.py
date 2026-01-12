"""
Drone 3D Printing Design Project - Main Demo

This demo showcases the capabilities of the drone part design system.
Run this file to see examples from each phase of the learning path.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 70)
print("DRONE 3D PRINTING DESIGN PROJECT - DEMO")
print("=" * 70)
print()
print("This demo will walk you through the 7 phases of learning to design")
print("drone parts for 3D printing using Python.")
print()

# Check for CadQuery
try:
    import cadquery as cq
    CADQUERY_AVAILABLE = True
    print("✓ CadQuery is installed - Full demo available!")
except ImportError:
    CADQUERY_AVAILABLE = False
    print("⚠️  CadQuery not installed - Running limited demo")
    print("   Install with: pip install cadquery")

print()
input("Press Enter to continue...")
print()

# ============================================================================
# PHASE 0: Python Foundations
# ============================================================================
print("=" * 70)
print("PHASE 0: Python Foundations")
print("=" * 70)
print()

from phase0_foundations.basic_concepts import Point3D, Vector3D, generate_mounting_holes
from phase0_foundations.geometry_calc import (
    calculate_motor_mount_dimensions,
    calculate_weight_estimate
)

print("Demonstrating basic 3D geometry...")
p1 = Point3D(0, 0, 0)
p2 = Point3D(10, 10, 10)
print(f"Point 1: {p1}")
print(f"Point 2: {p2}")
print(f"Distance: {p1.distance_to(p2):.2f}mm")
print()

print("Calculating motor mount dimensions...")
dims = calculate_motor_mount_dimensions(motor_diameter=28)
print(f"Motor diameter: {dims['motor_diameter']}mm")
print(f"Mount diameter: {dims['mount_diameter']:.1f}mm")
print(f"Mounting holes: {dims['mounting_holes']}")
print()

print("Generating mounting hole positions...")
holes = generate_mounting_holes(4, 20, 3)
for i, (x, y) in enumerate(holes):
    print(f"  Hole {i+1}: x={x:.1f}mm, y={y:.1f}mm")
print()

input("Press Enter to continue to Phase 1...")
print()

# ============================================================================
# PHASE 1: Aircraft & Drone Basics
# ============================================================================
print("=" * 70)
print("PHASE 1: Aircraft & Drone Basics")
print("=" * 70)
print()

print("Understanding drone components and their requirements:")
print()
print("Common Drone Parts to Design:")
print("  • Motor mounts - Secure motors to arms")
print("  • Frame connectors - Join arms to body")
print("  • Battery trays - Hold and protect batteries")
print("  • Camera mounts - Position camera at correct angle")
print("  • Landing gear - Protect drone on landing")
print()
print("Key Design Considerations:")
print("  ✓ Weight vs Strength tradeoff")
print("  ✓ Vibration dampening")
print("  ✓ Load path distribution")
print("  ✓ Easy assembly/disassembly")
print()

input("Press Enter to continue to Phase 2...")
print()

# ============================================================================
# PHASE 2: 3D Printing Fundamentals
# ============================================================================
print("=" * 70)
print("PHASE 2: 3D Printing Fundamentals")
print("=" * 70)
print()

print("3D Printing Best Practices for Drone Parts:")
print()
print("Material Selection:")
print("  • PLA/PLA+ - Prototypes and testing")
print("  • PETG - Flexible mounts, better layer adhesion")
print("  • ABS - Heat resistance")
print("  • Nylon/CF-Nylon - Flight-ready, high strength")
print()
print("Print Settings:")
print("  • Layer height: 0.2mm (0.15mm for small parts)")
print("  • Infill: 30-50% for structural parts")
print("  • Perimeters: 3-4 walls minimum")
print("  • Layer orientation: Consider stress direction")
print()

print("Estimating part weight...")
volume = 5000  # mm³
for material in ['PLA', 'PETG', 'Nylon']:
    weight = calculate_weight_estimate(volume, material, 30)
    print(f"  {material}: {weight:.2f}g (30% infill)")
print()

input("Press Enter to continue to Phase 3...")
print()

# ============================================================================
# PHASE 3: Python-Based CAD (Core)
# ============================================================================
print("=" * 70)
print("PHASE 3: Python-Based CAD with CadQuery")
print("=" * 70)
print()

if CADQUERY_AVAILABLE:
    from phase3_cad.cadquery_basics import (
        create_simple_box,
        create_cylinder,
        create_mounting_plate
    )
    
    print("Creating basic CAD objects...")
    print()
    
    print("1. Simple Box (20x15x10mm)")
    box = create_simple_box(20, 15, 10)
    print("   ✓ Created")
    
    print("2. Cylinder (radius=10mm, height=20mm)")
    cylinder = create_cylinder(10, 20)
    print("   ✓ Created")
    
    print("3. Mounting Plate (50x40x3mm with corner holes)")
    plate = create_mounting_plate(50, 40, 3, 3.2)
    print("   ✓ Created")
    
    # Try to export one
    try:
        output_file = "/tmp/demo_mounting_plate.stl"
        cq.exporters.export(plate, output_file)
        print(f"\n✓ Sample exported to: {output_file}")
    except Exception as e:
        print(f"\n⚠ Export not available: {e}")
else:
    print("CadQuery not available - skipping CAD demonstrations")
    print("Install CadQuery to see the full CAD capabilities!")

print()
input("Press Enter to continue to Phase 4...")
print()

# ============================================================================
# PHASE 4: Aircraft Part Design
# ============================================================================
print("=" * 70)
print("PHASE 4: Aircraft Part Design Projects")
print("=" * 70)
print()

if CADQUERY_AVAILABLE:
    from phase4_part_design.motor_mount import (
        create_simple_motor_mount,
        calculate_motor_mount_weight
    )
    
    print("Creating a Motor Mount (the most important drone part!)...")
    print()
    
    motor_mount = create_simple_motor_mount(
        motor_diameter=28,
        height=5,
        hole_diameter=3,
        mounting_holes=4
    )
    print("✓ Motor mount created!")
    print()
    
    print("Calculating motor mount specifications...")
    weight_info = calculate_motor_mount_weight(28, 5, 3, "PLA", 30)
    print(f"  Volume: {weight_info['volume_mm3']:.0f} mm³")
    print(f"  Estimated weight: {weight_info['weight_grams']:.2f}g")
    print(f"  Material: {weight_info['material']}")
    print(f"  Infill: {weight_info['infill_percent']}%")
    print()
    
    try:
        output_file = "/tmp/demo_motor_mount.stl"
        cq.exporters.export(motor_mount, output_file)
        print(f"✓ Motor mount exported to: {output_file}")
        print()
        print("Open this file in your slicer to see the 3D model!")
    except Exception as e:
        print(f"⚠ Export not available: {e}")
else:
    print("Example: Motor Mount Design")
    print("  - 28mm motor diameter")
    print("  - 5mm height")
    print("  - 4 mounting holes")
    print("  - Estimated weight: ~2.5g")
    print()
    print("Install CadQuery to actually generate the STL file!")

print()
input("Press Enter to continue to Phase 5...")
print()

# ============================================================================
# PHASE 5: Engineering Validation
# ============================================================================
print("=" * 70)
print("PHASE 5: Engineering Validation")
print("=" * 70)
print()

print("Engineering validation ensures your parts will work in real flight!")
print()
print("Key Validation Steps:")
print("  1. Weight & Center of Gravity calculation")
print("  2. Structural stress analysis")
print("  3. Vibration frequency analysis")
print("  4. Material selection validation")
print()
print("Example: Drone Arm Analysis")
print("  • Arm length: 180mm")
print("  • Motor weight: 35g")
print("  • Thrust: 1000g per motor")
print("  • Bending stress: Calculate using beam theory")
print("  • Safety factor: 2.0 minimum")
print()

input("Press Enter to continue to Phase 6...")
print()

# ============================================================================
# PHASE 6: Automation & Optimization
# ============================================================================
print("=" * 70)
print("PHASE 6: Automation & Optimization")
print("=" * 70)
print()

print("Automating design generation for multiple configurations...")
print()
print("Example: Generate motor mounts for different sizes:")
print()

motor_sizes = [22, 28, 32, 36]
for size in motor_sizes:
    dims = calculate_motor_mount_dimensions(size)
    volume = 3.14159 * ((dims['mount_diameter']/2)**2 - (size/2)**2) * 5
    weight = calculate_weight_estimate(volume, "PLA", 30)
    print(f"  {size}mm motor:")
    print(f"    Mount diameter: {dims['mount_diameter']:.1f}mm")
    print(f"    Weight: {weight:.2f}g")

print()
print("This automation allows you to:")
print("  ✓ Generate entire part families quickly")
print("  ✓ Optimize for different weight/strength requirements")
print("  ✓ A/B test different designs")
print()

input("Press Enter to continue to Phase 7...")
print()

# ============================================================================
# PHASE 7: Real-World Integration
# ============================================================================
print("=" * 70)
print("PHASE 7: Real-World Integration")
print("=" * 70)
print()

print("Integrating your designs into complete drone systems:")
print()
print("Flight Controller Integration:")
print("  • ArduPilot / PX4 mounts")
print("  • Vibration dampening mounts")
print("  • GPS antenna holders")
print()
print("FPV System:")
print("  • Camera mounts (adjustable angle)")
print("  • VTX (video transmitter) housing")
print("  • Antenna mounts")
print()
print("Version Control:")
print("  • Store CAD scripts in Git")
print("  • Track design changes")
print("  • Share with community")
print()

input("Press Enter to see final summary...")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print("DEMO COMPLETE - SUMMARY")
print("=" * 70)
print()

print("🎯 What You've Learned:")
print()
print("✓ Phase 0: Python foundations for parametric design")
print("✓ Phase 1: Understanding drone components and requirements")
print("✓ Phase 2: 3D printing best practices and materials")
print("✓ Phase 3: CadQuery for Python-based CAD design")
print("✓ Phase 4: Designing real drone parts (motor mounts, etc.)")
print("✓ Phase 5: Engineering validation and analysis")
print("✓ Phase 6: Design automation and optimization")
print("✓ Phase 7: Real-world system integration")
print()

print("📚 Next Steps:")
print()
print("1. Try the beginner example:")
print("   python examples/beginner/simple_motor_mount.py")
print()
print("2. Read the phase documentation:")
print("   docs/PHASE0_FOUNDATIONS.md")
print("   docs/PHASE3_CAD.md")
print("   docs/PHASE4_PART_DESIGN.md")
print()
print("3. Run the tests:")
print("   python -m pytest tests/ -v")
print()
print("4. Design your own parts:")
print("   - Modify examples")
print("   - Create custom designs")
print("   - Print and test!")
print()

if not CADQUERY_AVAILABLE:
    print("⚠️  To unlock full functionality:")
    print("   pip install cadquery")
    print("   Visit: https://cadquery.readthedocs.io/")
    print()

print("=" * 70)
print("Happy Designing! 🚁✨")
print("=" * 70)
