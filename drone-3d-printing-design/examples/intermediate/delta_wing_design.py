"""
Delta-Wing Aircraft Design Example

This example demonstrates how to design a delta-wing aircraft using
the drone-3d-printing-design framework.

Delta wings are characterized by their triangular planform and are
commonly used in high-speed RC aircraft and scale military models.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from phase1_aircraft_basics.aircraft_types import (
    AircraftType,
    BuildMethod,
    MaterialCost,
    DeltaWingSpec,
    get_aircraft_description
)

from phase1_aircraft_basics.delta_wing_design import (
    DeltaWingStructure,
    DeltaWingDesignRules,
    DeltaWingControlLogic,
    design_simple_delta_wing
)


def main():
    """Main demonstration of delta-wing design."""
    
    print("=" * 80)
    print("DELTA-WING AIRCRAFT DESIGN DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Display delta-wing characteristics
    print("--- What is a Delta-Wing Aircraft? ---")
    desc = get_aircraft_description(AircraftType.DELTA_WING)
    print(f"Name: {desc['name']}")
    print(f"\nDescription:")
    print(f"  {desc['description']}")
    print(f"\nAdvantages:")
    print(f"  {desc['advantages']}")
    print(f"\nDisadvantages:")
    print(f"  {desc['disadvantages']}")
    print(f"\nTypical Uses:")
    print(f"  {desc['typical_uses']}")
    print(f"\nKey Components:")
    print(f"  {desc['key_components']}")
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Design Example 1: Small FPV Delta Wing
    print("=" * 80)
    print("EXAMPLE 1: Small FPV Delta Wing (750mm)")
    print("=" * 80)
    print()
    
    small_delta = design_simple_delta_wing(
        wingspan=750,  # 750mm wingspan
        target_weight=400,  # 400 grams total
        build_method=BuildMethod.THREE_D_PRINTED,
        material_cost=MaterialCost.LOW_COST,
        sweep_angle=48  # 48 degree sweep
    )
    
    print_design_summary(small_delta)
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Design Example 2: Medium High-Speed Delta
    print("=" * 80)
    print("EXAMPLE 2: Medium High-Speed Delta (1000mm)")
    print("=" * 80)
    print()
    
    medium_delta = design_simple_delta_wing(
        wingspan=1000,  # 1 meter wingspan
        target_weight=650,  # 650 grams total
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.MEDIUM_COST,
        sweep_angle=52  # 52 degree sweep (higher speed)
    )
    
    print_design_summary(medium_delta)
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Design Example 3: Large Scale Delta (like a Mirage or Vulcan)
    print("=" * 80)
    print("EXAMPLE 3: Large Scale Military Delta (1500mm)")
    print("=" * 80)
    print()
    
    large_delta = design_simple_delta_wing(
        wingspan=1500,  # 1.5 meter wingspan
        target_weight=1200,  # 1200 grams total
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.HIGH_END,
        sweep_angle=55  # 55 degree sweep (scale fighter)
    )
    
    print_design_summary(large_delta)
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Control demonstration
    print("=" * 80)
    print("DELTA-WING CONTROL SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()
    
    demonstrate_control_system(medium_delta["structure"])
    print()
    
    input("Press Enter to continue...")
    print()
    
    # High-alpha performance demonstration
    print("=" * 80)
    print("HIGH ANGLE-OF-ATTACK PERFORMANCE")
    print("=" * 80)
    print()
    
    demonstrate_high_alpha_performance(medium_delta["structure"])
    print()
    
    input("Press Enter to continue...")
    print()
    
    # Final summary
    print("=" * 80)
    print("DELTA-WING DESIGN SUMMARY")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print()
    print("1. Delta wings have low aspect ratio (1.5-3.5) and high sweep (40-65°)")
    print("2. They excel at high speeds and high angle-of-attack flight")
    print("3. Vortex lift provides extra lift at high AoA (above ~15°)")
    print("4. They require larger wing area than conventional designs")
    print("5. CG should be 30-40% from the apex for stability")
    print("6. Most deltas need vertical stabilizers for directional control")
    print("7. Landing speeds are higher due to delta wing characteristics")
    print()
    print("Design Considerations for 3D Printing:")
    print()
    print("✓ Thin airfoils (4-8% thickness) are typical")
    print("✓ Print ribs vertically for strength")
    print("✓ Use carbon fiber spars for main load paths")
    print("✓ Skin can be 3D printed or covered with film")
    print("✓ Consider hybrid build: 3D print structure, cover with foam or film")
    print()
    print("Ready to build your delta wing! ✈️")
    print("=" * 80)


def print_design_summary(design: dict):
    """Print a formatted summary of a delta-wing design."""
    spec = design["specification"]
    structure = design["structure"]
    
    print(f"Aircraft: {spec.name}")
    print(f"Build Method: {spec.build_method.value}")
    print(f"Material Cost: {spec.material_cost.value}")
    print()
    
    print("--- Geometry ---")
    print(f"Wingspan: {spec.wingspan}mm")
    print(f"Root Chord: {structure.chord_root:.1f}mm")
    print(f"Sweep Angle: {structure.sweep_angle}°")
    print(f"Wing Area: {design['wing_area_dm2']:.2f} dm²")
    print(f"Aspect Ratio: {design['aspect_ratio']:.2f}")
    print()
    
    print("--- Performance ---")
    print(f"Wing Loading: {design['wing_loading_g_dm2']:.1f} g/dm²")
    print(f"Estimated Stall Speed: {design['estimated_stall_speed_ms']:.1f} m/s "
          f"({design['estimated_stall_speed_ms'] * 3.6:.1f} km/h)")
    print(f"Estimated Cruise Speed: {design['estimated_cruise_speed_ms']:.1f} m/s "
          f"({design['estimated_cruise_speed_ms'] * 3.6:.1f} km/h)")
    print(f"Max Angle of Attack: ~{design['max_angle_of_attack']}° (vortex burst)")
    print()
    
    print("--- Weight Budget ---")
    print(f"Structural Weight: {design['estimated_structural_weight']:.1f}g")
    print(f"Total Weight Target: {spec.weight_target}g")
    print(f"Available for Electronics: {design['weight_budget_remaining']:.1f}g")
    print()
    
    print("--- Structure ---")
    print(f"Ribs: {design['rib_count']} ribs")
    print(f"Spar Height: {structure.spar_height:.1f}mm")
    print(f"Vertical Tail: {'Yes' if structure.has_vertical_tail else 'No'}")
    if structure.has_vertical_tail:
        print(f"  Height: {structure.vertical_tail_height:.1f}mm")
        print(f"  Area: {structure.vertical_tail_area:.0f}mm²")
    print()
    
    # Validation
    validation = design["validation"]
    if validation["errors"]:
        print("❌ ERRORS:")
        for error in validation["errors"]:
            print(f"   {error}")
        print()
    
    if validation["warnings"]:
        print("⚠️  WARNINGS:")
        for warning in validation["warnings"]:
            print(f"   {warning}")
        print()
    
    if not validation["errors"] and not validation["warnings"]:
        print("✅ Design passes all validation checks!")
        print()


def demonstrate_control_system(structure: DeltaWingStructure):
    """Demonstrate delta-wing control system."""
    print("Delta wings use elevons for pitch and roll control.")
    print("(Similar to flying wings but with different characteristics)")
    print()
    
    test_cases = [
        ("Level Flight", 0.0, 0.0),
        ("Pitch Up", 0.5, 0.0),
        ("Pitch Down", -0.5, 0.0),
        ("Roll Left", 0.0, -0.5),
        ("Roll Right", 0.0, 0.5),
        ("Pitch Up + Roll Right", 0.5, 0.5),
        ("Pitch Down + Roll Left", -0.5, -0.5),
    ]
    
    print("Control Input Test Cases:")
    print("-" * 70)
    print(f"{'Maneuver':<25} {'Pitch':>8} {'Roll':>8} {'Left Elev':>12} {'Right Elev':>12}")
    print("-" * 70)
    
    for name, pitch, roll in test_cases:
        left_elev, right_elev = DeltaWingControlLogic.calculate_elevon_deflection(
            pitch_input=pitch,
            roll_input=roll,
            max_deflection=25.0
        )
        print(f"{name:<25} {pitch:>7.1f}  {roll:>7.1f}  {left_elev:>10.1f}°  {right_elev:>10.1f}°")
    
    print()
    
    # Roll-yaw coupling
    print("Roll-Yaw Coupling (Proverse Yaw):")
    print("Delta wings naturally yaw into the turn due to differential drag.")
    print()
    print("Speed (m/s) | Roll Input | Induced Yaw Rate (°/s)")
    print("-" * 50)
    
    for speed in [5, 10, 15, 20]:
        for roll in [-0.5, 0.5]:
            yaw_rate = DeltaWingControlLogic.calculate_yaw_from_roll(
                roll_input=roll,
                speed=speed,
                coupling_factor=0.3
            )
            direction = "Left" if roll < 0 else "Right"
            print(f"{speed:>10}  | {direction:>10} | {yaw_rate:>20.1f}")


def demonstrate_high_alpha_performance(structure: DeltaWingStructure):
    """Demonstrate high angle-of-attack capabilities."""
    print("Delta wings can operate at very high angles of attack using vortex lift.")
    print("This is what makes them excellent for low-speed maneuvering despite their design.")
    print()
    
    print("Lift Coefficient vs Angle of Attack:")
    print("-" * 80)
    print(f"{'AoA (°)':>8} {'Vortex CL':>12} {'Total CL':>12} {'Flight Regime':>20} {'Notes':>25}")
    print("-" * 80)
    
    for aoa in range(0, 41, 5):
        cl_vortex = DeltaWingDesignRules.calculate_vortex_lift_coefficient(
            aoa, structure.sweep_angle
        )
        cl_total = DeltaWingDesignRules.calculate_total_lift_coefficient(
            aoa, structure.sweep_angle, structure.aspect_ratio
        )
        
        # Determine flight regime
        if aoa < 15:
            regime = "Normal"
            notes = "Attached flow"
        elif aoa < 25:
            regime = "High Alpha"
            notes = "Vortex lift building"
        elif aoa < 35:
            regime = "Very High Alpha"
            notes = "Strong vortex lift"
        else:
            regime = "Post Vortex Burst"
            notes = "Loss of lift!"
        
        print(f"{aoa:>8}  {cl_vortex:>12.3f} {cl_total:>12.3f} {regime:>20} {notes:>25}")
    
    print()
    print("Key Observations:")
    print("• Vortex lift kicks in above 10-15° AoA")
    print("• Peak CL occurs around 30-35° before vortex burst")
    print("• Delta can maintain control well beyond conventional stall angle")
    print("• This allows slow-speed landing and takeoff despite high wing loading")
    print()
    
    # Control effectiveness
    print("Control Effectiveness at High AoA:")
    print("-" * 60)
    
    for aoa in [10, 20, 30, 37]:
        high_alpha = DeltaWingControlLogic.calculate_high_alpha_control(
            angle_of_attack=aoa,
            pitch_input=0.5
        )
        print(f"\nAoA: {aoa}°")
        print(f"  Flight Regime: {high_alpha['flight_regime']}")
        print(f"  Control Effectiveness: {high_alpha['control_effectiveness'] * 100:.0f}%")
        
        if high_alpha['warnings']:
            for warning in high_alpha['warnings']:
                print(f"  ⚠️  {warning}")


if __name__ == "__main__":
    main()
