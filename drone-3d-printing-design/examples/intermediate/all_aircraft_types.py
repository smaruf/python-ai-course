"""
All Aircraft Types Design Example

This example demonstrates how to design all four aircraft types:
- Fixed-wing
- Flying-wing
- Autogyro
- Rotorcraft
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
from phase1_aircraft_basics.flying_wing_design import design_simple_flying_wing
from phase1_aircraft_basics.fixed_wing_design import design_simple_fixed_wing
from phase1_aircraft_basics.rotorcraft_design import design_simple_rotorcraft
from phase1_aircraft_basics.autogyro_design import design_simple_autogyro


def print_aircraft_info(aircraft_type: AircraftType):
    """Print information about an aircraft type."""
    desc = get_aircraft_description(aircraft_type)
    print(f"\n{'='*70}")
    print(f"{desc['name'].upper()}")
    print(f"{'='*70}")
    print(f"Description: {desc['description']}")
    print(f"Advantages: {desc['advantages']}")
    print(f"Disadvantages: {desc['disadvantages']}")
    print(f"Typical Uses: {desc['typical_uses']}")
    print()


def main():
    print("=" * 70)
    print("COMPLETE AIRCRAFT DESIGN SYSTEM")
    print("Covering All Four Aircraft Types")
    print("=" * 70)
    
    # ========================================================================
    # FLYING-WING DESIGN
    # ========================================================================
    print_aircraft_info(AircraftType.FLYING_WING)
    
    print("Designing a Sport Flying Wing...")
    fw_design = design_simple_flying_wing(
        wingspan=1000,
        target_weight=600,
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.MEDIUM_COST
    )
    
    fw_spec = fw_design["specification"]
    print(f"  ✓ {fw_spec.name}")
    print(f"  ✓ Wingspan: {fw_spec.wingspan}mm")
    print(f"  ✓ Wing Area: {fw_design['wing_area_dm2']:.2f} dm²")
    print(f"  ✓ Wing Loading: {fw_design['wing_loading_g_dm2']:.1f} g/dm²")
    print(f"  ✓ Estimated Cost: {get_build_method_info(fw_spec.build_method, fw_spec.material_cost)['estimated_cost']}")
    
    # ========================================================================
    # FIXED-WING DESIGN
    # ========================================================================
    print_aircraft_info(AircraftType.FIXED_WING)
    
    print("Designing a Trainer Fixed-Wing...")
    fixed_design = design_simple_fixed_wing(
        wingspan=1200,
        target_weight=800,
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.MEDIUM_COST,
        aircraft_purpose="trainer"
    )
    
    fixed_spec = fixed_design["specification"]
    print(f"  ✓ {fixed_spec.name}")
    print(f"  ✓ Wingspan: {fixed_spec.wingspan}mm")
    print(f"  ✓ Fuselage Length: {fixed_spec.fuselage_length}mm")
    print(f"  ✓ Wing Area: {fixed_design['wing_area_dm2']:.2f} dm²")
    print(f"  ✓ Aspect Ratio: {fixed_design['aspect_ratio']:.2f}")
    print(f"  ✓ Estimated Cost: {get_build_method_info(fixed_spec.build_method, fixed_spec.material_cost)['estimated_cost']}")
    
    # ========================================================================
    # ROTORCRAFT DESIGN
    # ========================================================================
    print_aircraft_info(AircraftType.ROTORCRAFT)
    
    print("Designing a 5\" Freestyle Quadcopter...")
    rc_design = design_simple_rotorcraft(
        motor_count=4,
        propeller_size_inch=5.0,
        target_weight=600,
        build_method=BuildMethod.THREE_D_PRINTED,
        material_cost=MaterialCost.MEDIUM_COST,
        purpose="freestyle"
    )
    
    rc_spec = rc_design["specification"]
    print(f"  ✓ {rc_spec.name}")
    print(f"  ✓ Diagonal Size: {rc_design['diagonal_size_mm']:.0f}mm")
    print(f"  ✓ Motor Size: {rc_spec.motor_size}")
    print(f"  ✓ Frame Weight: {rc_design['frame_weight']:.1f}g")
    print(f"  ✓ Estimated Cost: {get_build_method_info(rc_spec.build_method, rc_spec.material_cost)['estimated_cost']}")
    
    # ========================================================================
    # AUTOGYRO DESIGN
    # ========================================================================
    print_aircraft_info(AircraftType.AUTOGYRO)
    
    print("Designing a Small Autogyro...")
    ag_design = design_simple_autogyro(
        rotor_diameter=800,
        target_weight=500,
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.MEDIUM_COST
    )
    
    ag_spec = ag_design["specification"]
    print(f"  ✓ {ag_spec.name}")
    print(f"  ✓ Rotor Diameter: {ag_spec.rotor_diameter}mm")
    print(f"  ✓ Rotor RPM: {ag_design['rotor_rpm']:.0f}")
    print(f"  ✓ Tip Speed: {ag_design['tip_speed_ms']:.1f} m/s")
    print(f"  ✓ Disc Loading: {ag_design['disc_loading_kg_m2']:.1f} kg/m²")
    print(f"  ✓ Estimated Cost: {get_build_method_info(ag_spec.build_method, ag_spec.material_cost)['estimated_cost']}")
    
    # ========================================================================
    # COMPARISON
    # ========================================================================
    print(f"\n{'='*70}")
    print("DESIGN COMPARISON")
    print(f"{'='*70}\n")
    
    print(f"{'Aircraft Type':<20} {'Wingspan/Size':<15} {'Weight':<10} {'Cost':<15} {'Purpose':<20}")
    print("-" * 80)
    
    print(f"{'Flying-Wing':<20} {fw_spec.wingspan}mm{'':<9} {fw_spec.weight_target}g{'':<4} {'$40-$250':<15} {'Long-range FPV':<20}")
    print(f"{'Fixed-Wing':<20} {fixed_spec.wingspan}mm{'':<7} {fixed_spec.weight_target}g{'':<4} {'$40-$250':<15} {'Training':<20}")
    print(f"{'Rotorcraft':<20} {rc_design['diagonal_size_mm']:.0f}mm{'':<8} {rc_spec.weight_target}g{'':<4} {'$80-$200':<15} {'Freestyle/Racing':<20}")
    print(f"{'Autogyro':<20} {ag_spec.rotor_diameter}mm{'':<8} {ag_spec.weight_target}g{'':<4} {'$40-$250':<15} {'Experimental':<20}")
    
    # ========================================================================
    # BUILD METHOD COMPARISON
    # ========================================================================
    print(f"\n{'='*70}")
    print("BUILD METHOD COMPARISON")
    print(f"{'='*70}\n")
    
    for build_method in [BuildMethod.HAND_BUILT, BuildMethod.THREE_D_PRINTED, BuildMethod.HYBRID]:
        for material_cost in [MaterialCost.LOW_COST, MaterialCost.MEDIUM_COST, MaterialCost.HIGH_END]:
            info = get_build_method_info(build_method, material_cost)
            print(f"{build_method.value.upper()} - {material_cost.value.upper()}:")
            print(f"  Cost: {info['estimated_cost']}")
            print(f"  Difficulty: {info['difficulty']}")
            print(f"  Build Time: {info['build_time']}")
            print(f"  Top Materials: {', '.join(info['materials'][:2])}")
            print()
    
    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS FOR BEGINNERS")
    print(f"{'='*70}\n")
    
    print("1. START WITH: Fixed-Wing Trainer")
    print("   - Most stable and forgiving")
    print("   - Easy to build with foam or balsa")
    print("   - Good for learning flight principles")
    print()
    
    print("2. INTERMEDIATE: Flying-Wing or Rotorcraft")
    print("   - Flying-wing: Efficient, unique flying characteristics")
    print("   - Rotorcraft: Versatile, can hover and fly fast")
    print()
    
    print("3. ADVANCED: Autogyro")
    print("   - Complex mechanics with free-spinning rotor")
    print("   - Requires understanding of autorotation")
    print("   - Unique flight characteristics")
    print()
    
    print("=" * 70)
    print("All designs are ready to build!")
    print("Choose based on your skill level and intended use.")
    print("=" * 70)


if __name__ == "__main__":
    main()
