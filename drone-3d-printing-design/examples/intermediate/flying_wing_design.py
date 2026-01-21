"""
Flying-Wing Design Example

This example demonstrates how to design a flying-wing aircraft
with complete structural parameters and control logic.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from phase1_aircraft_basics.aircraft_types import (
    AircraftType,
    BuildMethod,
    MaterialCost,
    get_aircraft_description,
    get_build_method_info
)
from phase1_aircraft_basics.flying_wing_design import (
    FlyingWingStructure,
    FlyingWingDesignRules,
    FlyingWingControlLogic,
    design_simple_flying_wing
)


def main():
    print("=" * 70)
    print("FLYING-WING AIRCRAFT DESIGN EXAMPLE")
    print("=" * 70)
    print()
    
    # Display flying-wing information
    fw_desc = get_aircraft_description(AircraftType.FLYING_WING)
    print(f"Aircraft Type: {fw_desc['name']}")
    print(f"Description: {fw_desc['description']}")
    print(f"Advantages: {fw_desc['advantages']}")
    print(f"Typical Uses: {fw_desc['typical_uses']}")
    print()
    
    # Design configurations
    designs = [
        {
            "name": "Budget FPV Wing",
            "wingspan": 800,
            "weight": 400,
            "build_method": BuildMethod.HAND_BUILT,
            "material_cost": MaterialCost.LOW_COST
        },
        {
            "name": "Sport Flying Wing",
            "wingspan": 1000,
            "weight": 600,
            "build_method": BuildMethod.HYBRID,
            "material_cost": MaterialCost.MEDIUM_COST
        },
        {
            "name": "Long-Range Wing",
            "wingspan": 1500,
            "weight": 1200,
            "build_method": BuildMethod.THREE_D_PRINTED,
            "material_cost": MaterialCost.HIGH_END
        }
    ]
    
    for i, config in enumerate(designs, 1):
        print(f"\n{'='*70}")
        print(f"DESIGN {i}: {config['name']}")
        print(f"{'='*70}\n")
        
        # Design the aircraft
        design = design_simple_flying_wing(
            wingspan=config["wingspan"],
            target_weight=config["weight"],
            build_method=config["build_method"],
            material_cost=config["material_cost"]
        )
        
        spec = design["specification"]
        structure = design["structure"]
        
        # Basic specifications
        print("--- Basic Specifications ---")
        print(f"Wingspan: {spec.wingspan}mm ({spec.wingspan/1000:.2f}m)")
        print(f"Root Chord: {spec.chord_root:.1f}mm")
        print(f"Tip Chord: {spec.chord_tip:.1f}mm")
        print(f"Sweep Angle: {spec.sweep_angle}°")
        print(f"Build Method: {spec.build_method.value}")
        print(f"Material Cost: {spec.material_cost.value}")
        
        # Aerodynamics
        print("\n--- Aerodynamic Properties ---")
        print(f"Wing Area: {design['wing_area_dm2']:.2f} dm²")
        print(f"Aspect Ratio: {design['aspect_ratio']:.2f}")
        print(f"Mean Aerodynamic Chord: {structure.mean_aerodynamic_chord:.1f}mm")
        print(f"Taper Ratio: {structure.taper_ratio:.2f}")
        print(f"Wing Loading: {design['wing_loading_g_dm2']:.1f} g/dm²")
        
        # Structure
        print("\n--- Structural Details ---")
        print(f"Rib Count: {design['rib_count']}")
        print(f"Rib Spacing: {structure.rib_spacing}mm")
        print(f"Spar Height: {structure.spar_height:.1f}mm")
        print(f"Thickness Ratio: {structure.thickness_ratio:.2%}")
        
        # Weight
        print("\n--- Weight Budget ---")
        print(f"Estimated Structure: {design['estimated_structural_weight']:.1f}g")
        print(f"Target Total Weight: {spec.weight_target}g")
        print(f"Remaining for Electronics: {design['weight_budget_remaining']:.1f}g")
        
        # Build information
        print("\n--- Build Information ---")
        build_info = get_build_method_info(spec.build_method, spec.material_cost)
        print(f"Estimated Cost: {build_info['estimated_cost']}")
        print(f"Build Time: {build_info['build_time']}")
        print(f"Difficulty: {build_info['difficulty']}")
        print(f"Tools Needed: {', '.join(build_info['tools'][:3])}")
        print(f"Materials:")
        for material in build_info['materials'][:3]:
            print(f"  • {material}")
        
        # Validation
        print("\n--- Design Validation ---")
        validation = design["validation"]
        if validation["errors"]:
            print("❌ ERRORS:")
            for error in validation["errors"]:
                print(f"  • {error}")
        if validation["warnings"]:
            print("⚠️  WARNINGS:")
            for warning in validation["warnings"]:
                print(f"  • {warning}")
        if not validation["errors"] and not validation["warnings"]:
            print("✅ Design passes all validation checks!")
        
        # Control demonstration
        print("\n--- Control System Example ---")
        print("Flight scenario: Climbing right turn")
        left_elev, right_elev = FlyingWingControlLogic.calculate_elevon_deflection(
            pitch_input=-0.5,  # Pitch up (climb)
            roll_input=0.4     # Roll right
        )
        print(f"  Pitch Input: -50% (climb)")
        print(f"  Roll Input: +40% (right)")
        print(f"  → Left Elevon: {left_elev:.1f}°")
        print(f"  → Right Elevon: {right_elev:.1f}°")
        
        # CG analysis
        print("\n--- Center of Gravity Analysis ---")
        cg_analysis = FlyingWingControlLogic.calculate_cg_effect(
            current_cg=0.26,
            target_cg=0.25,
            mac=structure.mean_aerodynamic_chord
        )
        print(f"Target CG: {cg_analysis['target_cg_ratio']:.1%} MAC")
        print(f"Current CG: {cg_analysis['current_cg_ratio']:.1%} MAC")
        print(f"Difference: {cg_analysis['difference_mm']:.1f}mm")
        print(f"Status: {cg_analysis['status']}")
        print(f"Recommendation: {cg_analysis['recommendation']}")
    
    # Summary
    print(f"\n{'='*70}")
    print("DESIGN SUMMARY")
    print(f"{'='*70}\n")
    print("Three flying-wing designs have been created:")
    print("1. Budget FPV Wing - Low-cost, hand-built design for beginners")
    print("2. Sport Flying Wing - Medium-cost hybrid design for intermediate builders")
    print("3. Long-Range Wing - High-end 3D printed design for advanced users")
    print()
    print("Next Steps:")
    print("  • Choose a design based on your budget and skill level")
    print("  • Gather materials from the build information")
    print("  • Follow the structural parameters to build your wing")
    print("  • Use the control logic for flight controller setup")
    print("  • Validate your build against the design rules")
    print()
    print("Happy building! ✈️")


if __name__ == "__main__":
    main()
