"""
Fixed-Wing Aircraft Design Module

This module provides structural parameters, design rules, and control logic
for traditional fixed-wing aircraft design.
"""

import math
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .aircraft_types import FixedWingSpec, BuildMethod, MaterialCost


@dataclass
class FixedWingStructure:
    """Structural parameters for fixed-wing aircraft."""
    
    # Main wing
    wingspan: float  # mm
    wing_chord: float  # mm (mean)
    wing_area: float = field(default=0, init=False)
    
    # Fuselage
    fuselage_length: float = 0  # mm
    fuselage_width: float = 0  # mm
    fuselage_height: float = 0  # mm
    
    # Tail surfaces
    tail_span: float = 0  # mm (horizontal stabilizer)
    tail_chord: float = 0  # mm
    vertical_tail_height: float = 0  # mm
    vertical_tail_chord: float = 0  # mm
    
    # Wing structure
    dihedral_angle: float = 3  # degrees (typical)
    wing_thickness_ratio: float = 0.10
    
    # Control surfaces
    aileron_chord_ratio: float = 0.25  # aileron chord as % of wing chord
    elevator_chord_ratio: float = 0.30  # elevator as % of tail chord
    rudder_chord_ratio: float = 0.30  # rudder as % of vertical tail chord
    
    def __post_init__(self):
        """Calculate derived parameters."""
        self.wing_area = self.wingspan * self.wing_chord
        
        # Auto-calculate tail surfaces if not provided
        if self.tail_span == 0:
            self.tail_span = self.wingspan * 0.35  # 35% of wingspan
        if self.tail_chord == 0:
            self.tail_chord = self.wing_chord * 0.4  # 40% of wing chord
        if self.vertical_tail_height == 0:
            self.vertical_tail_height = self.wingspan * 0.15
        if self.vertical_tail_chord == 0:
            self.vertical_tail_chord = self.wing_chord * 0.5


class FixedWingDesignRules:
    """Design rules for fixed-wing aircraft."""
    
    # Recommended ratios
    TAIL_VOLUME_COEFFICIENT_H = (0.4, 0.6)  # Horizontal tail volume coefficient
    TAIL_VOLUME_COEFFICIENT_V = (0.03, 0.05)  # Vertical tail volume coefficient
    WING_LOADING_RANGE = (20, 60)  # g/dm²
    ASPECT_RATIO_RANGE = (5, 12)
    
    @staticmethod
    def validate_design(structure: FixedWingStructure) -> Dict[str, List[str]]:
        """Validate fixed-wing design."""
        warnings = []
        errors = []
        
        # Calculate tail volume coefficients
        if structure.fuselage_length > 0:
            # Horizontal tail volume coefficient
            tail_area = structure.tail_span * structure.tail_chord
            tail_arm = structure.fuselage_length * 0.7  # Approximate
            vh = (tail_area * tail_arm) / (structure.wing_area * structure.wing_chord)
            
            if vh < FixedWingDesignRules.TAIL_VOLUME_COEFFICIENT_H[0]:
                warnings.append(
                    f"Horizontal tail volume coefficient {vh:.2f} is low. "
                    f"Aircraft may lack pitch stability."
                )
            elif vh > FixedWingDesignRules.TAIL_VOLUME_COEFFICIENT_H[1]:
                warnings.append(
                    f"Horizontal tail volume coefficient {vh:.2f} is high. "
                    f"Tail is oversized, adding unnecessary weight."
                )
        
        # Check wing aspect ratio
        aspect_ratio = structure.wingspan**2 / structure.wing_area
        if aspect_ratio < FixedWingDesignRules.ASPECT_RATIO_RANGE[0]:
            warnings.append(
                f"Low aspect ratio {aspect_ratio:.1f}. "
                f"Wing will be less efficient but more maneuverable."
            )
        elif aspect_ratio > FixedWingDesignRules.ASPECT_RATIO_RANGE[1]:
            warnings.append(
                f"High aspect ratio {aspect_ratio:.1f}. "
                f"Wing is efficient but may be structurally weak."
            )
        
        # Check dihedral
        if structure.dihedral_angle < 0:
            warnings.append("Negative dihedral (anhedral) reduces stability.")
        elif structure.dihedral_angle > 8:
            warnings.append(
                f"High dihedral angle {structure.dihedral_angle}° "
                f"may cause excessive roll-yaw coupling."
            )
        
        return {"warnings": warnings, "errors": errors}
    
    @staticmethod
    def calculate_cg_limits(
        wing_chord: float,
        fuselage_length: float
    ) -> Dict[str, float]:
        """
        Calculate recommended CG range.
        
        Returns:
            Dictionary with forward and aft CG limits
        """
        # CG typically 25-35% of wing chord from leading edge
        return {
            "forward_limit_mm": wing_chord * 0.25,
            "aft_limit_mm": wing_chord * 0.35,
            "forward_limit_ratio": 0.25,
            "aft_limit_ratio": 0.35,
            "reference": "from wing leading edge"
        }


class FixedWingControlLogic:
    """Control logic for fixed-wing aircraft."""
    
    @staticmethod
    def calculate_control_deflections(
        pitch_input: float,
        roll_input: float,
        yaw_input: float,
        max_deflection: float = 30.0
    ) -> Dict[str, float]:
        """
        Calculate control surface deflections.
        
        Args:
            pitch_input: Pitch input (-1.0 to 1.0)
            roll_input: Roll input (-1.0 to 1.0)
            yaw_input: Yaw input (-1.0 to 1.0)
            max_deflection: Maximum deflection in degrees
        
        Returns:
            Dictionary with all control surface angles
        """
        # Clamp inputs
        pitch_input = max(-1.0, min(1.0, pitch_input))
        roll_input = max(-1.0, min(1.0, roll_input))
        yaw_input = max(-1.0, min(1.0, yaw_input))
        
        return {
            "elevator": pitch_input * max_deflection,
            "left_aileron": roll_input * max_deflection,
            "right_aileron": -roll_input * max_deflection,  # Opposite of left
            "rudder": yaw_input * max_deflection
        }


def design_simple_fixed_wing(
    wingspan: float,
    target_weight: float,
    build_method: BuildMethod,
    material_cost: MaterialCost,
    aircraft_purpose: str = "trainer"
) -> Dict[str, any]:
    """
    Design a simple fixed-wing aircraft.
    
    Args:
        wingspan: Wingspan in mm
        target_weight: Target weight in grams
        build_method: Construction method
        material_cost: Material cost category
        aircraft_purpose: "trainer", "sport", "racer", or "glider"
    
    Returns:
        Complete design specification
    """
    # Calculate dimensions based on purpose
    if aircraft_purpose == "trainer":
        wing_chord = wingspan * 0.18
        fuselage_length = wingspan * 0.75
        aspect_ratio_target = 6
    elif aircraft_purpose == "sport":
        wing_chord = wingspan * 0.16
        fuselage_length = wingspan * 0.70
        aspect_ratio_target = 7
    elif aircraft_purpose == "racer":
        wing_chord = wingspan * 0.15
        fuselage_length = wingspan * 0.65
        aspect_ratio_target = 8
    else:  # glider
        wing_chord = wingspan * 0.12
        fuselage_length = wingspan * 0.85
        aspect_ratio_target = 10
    
    # Create structure
    structure = FixedWingStructure(
        wingspan=wingspan,
        wing_chord=wing_chord,
        fuselage_length=fuselage_length,
        fuselage_width=wing_chord * 0.4,
        fuselage_height=wing_chord * 0.3
    )
    
    # Validate
    validation = FixedWingDesignRules.validate_design(structure)
    
    # Calculate CG limits
    cg_limits = FixedWingDesignRules.calculate_cg_limits(
        wing_chord,
        fuselage_length
    )
    
    # Create specification
    spec = FixedWingSpec(
        name=f"Fixed-Wing {aircraft_purpose.title()} {wingspan}mm",
        build_method=build_method,
        material_cost=material_cost,
        wingspan=wingspan,
        fuselage_length=fuselage_length,
        chord_length=wing_chord,
        weight_target=target_weight
    )
    
    aspect_ratio = wingspan**2 / structure.wing_area
    wing_area_dm2 = structure.wing_area / 10000
    
    return {
        "specification": spec,
        "structure": structure,
        "validation": validation,
        "cg_limits": cg_limits,
        "aspect_ratio": aspect_ratio,
        "wing_area_dm2": wing_area_dm2,
        "wing_loading_g_dm2": target_weight / wing_area_dm2,
        "purpose": aircraft_purpose
    }


# Example usage
if __name__ == "__main__":
    print("=== Fixed-Wing Design Module Demo ===\n")
    
    # Design a trainer aircraft
    design = design_simple_fixed_wing(
        wingspan=1200,  # 1.2 meters
        target_weight=800,  # 800 grams
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.MEDIUM_COST,
        aircraft_purpose="trainer"
    )
    
    print("--- Specification ---")
    spec = design["specification"]
    print(f"Name: {spec.name}")
    print(f"Wingspan: {spec.wingspan}mm")
    print(f"Fuselage Length: {spec.fuselage_length}mm")
    print(f"Wing Chord: {spec.chord_length}mm")
    
    print("\n--- Performance ---")
    print(f"Wing Area: {design['wing_area_dm2']:.2f} dm²")
    print(f"Aspect Ratio: {design['aspect_ratio']:.2f}")
    print(f"Wing Loading: {design['wing_loading_g_dm2']:.1f} g/dm²")
    
    print("\n--- CG Requirements ---")
    cg = design["cg_limits"]
    print(f"Forward Limit: {cg['forward_limit_mm']:.1f}mm ({cg['forward_limit_ratio']:.0%})")
    print(f"Aft Limit: {cg['aft_limit_mm']:.1f}mm ({cg['aft_limit_ratio']:.0%})")
    print(f"Reference: {cg['reference']}")
    
    print("\n--- Control System Demo ---")
    controls = FixedWingControlLogic.calculate_control_deflections(
        pitch_input=-0.5,  # Nose up
        roll_input=0.3,    # Roll right
        yaw_input=0.2      # Yaw right
    )
    print("Input: Pitch -50%, Roll +30%, Yaw +20%")
    print(f"  Elevator: {controls['elevator']:.1f}°")
    print(f"  Left Aileron: {controls['left_aileron']:.1f}°")
    print(f"  Right Aileron: {controls['right_aileron']:.1f}°")
    print(f"  Rudder: {controls['rudder']:.1f}°")
