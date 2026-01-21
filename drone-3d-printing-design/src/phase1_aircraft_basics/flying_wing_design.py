"""
Flying-Wing Design Module

This module provides structural parameters, design rules, and control logic
specific to flying-wing aircraft design.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from .aircraft_types import FlyingWingSpec, BuildMethod, MaterialCost


@dataclass
class FlyingWingStructure:
    """Structural parameters for flying-wing design."""
    
    # Wing geometry
    wingspan: float  # mm
    chord_root: float  # mm
    chord_tip: float  # mm
    sweep_angle: float  # degrees
    thickness_ratio: float = 0.12  # typical for flying wings
    
    # Structural elements
    spar_count: int = 1  # Number of main spars
    spar_height: float = 0  # mm (calculated if 0)
    spar_thickness: float = 3  # mm (wall thickness)
    rib_spacing: float = 50  # mm (distance between ribs)
    skin_thickness: float = 2  # mm
    
    # Control surfaces
    elevon_chord_ratio: float = 0.25  # elevon chord as ratio of wing chord
    elevon_span_ratio: float = 0.35  # elevon span as ratio of half-wingspan
    
    # Center of gravity
    cg_position: float = 0.25  # ratio from leading edge at root chord
    
    # Calculated values (filled by __post_init__)
    wing_area: float = field(default=0, init=False)
    mean_aerodynamic_chord: float = field(default=0, init=False)
    aspect_ratio: float = field(default=0, init=False)
    taper_ratio: float = field(default=0, init=False)
    estimated_weight: float = field(default=0, init=False)
    
    def __post_init__(self):
        """Calculate derived structural parameters."""
        # Calculate wing area (trapezoidal wing)
        self.wing_area = (self.chord_root + self.chord_tip) * self.wingspan / 2
        
        # Calculate mean aerodynamic chord (MAC)
        if self.chord_root > 0:
            self.mean_aerodynamic_chord = (2/3) * self.chord_root * (
                (1 + self.chord_tip/self.chord_root + (self.chord_tip/self.chord_root)**2) /
                (1 + self.chord_tip/self.chord_root)
            )
        else:
            self.mean_aerodynamic_chord = 0
        
        # Calculate aspect ratio
        if self.wing_area > 0:
            self.aspect_ratio = self.wingspan**2 / self.wing_area
        else:
            self.aspect_ratio = 0
        
        # Calculate taper ratio
        if self.chord_root > 0:
            self.taper_ratio = self.chord_tip / self.chord_root
        else:
            self.taper_ratio = 0
        
        # Calculate spar height if not specified
        if self.spar_height == 0:
            # Spar height is typically 70% of max wing thickness
            max_thickness = self.chord_root * self.thickness_ratio
            self.spar_height = max_thickness * 0.7


class FlyingWingDesignRules:
    """Design rules and constraints for flying-wing aircraft."""
    
    # Recommended ranges
    ASPECT_RATIO_RANGE = (4, 10)  # Low AR = maneuverable, High AR = efficient
    SWEEP_ANGLE_RANGE = (15, 35)  # degrees
    TAPER_RATIO_RANGE = (0.3, 0.7)
    THICKNESS_RATIO_RANGE = (0.08, 0.15)
    CG_POSITION_RANGE = (0.20, 0.30)  # ratio from leading edge
    
    @staticmethod
    def validate_design(structure: FlyingWingStructure) -> Dict[str, List[str]]:
        """
        Validate a flying-wing design against design rules.
        
        Args:
            structure: The flying-wing structure to validate
        
        Returns:
            Dictionary with 'warnings' and 'errors' lists
        """
        warnings = []
        errors = []
        
        # Check aspect ratio
        if structure.aspect_ratio < FlyingWingDesignRules.ASPECT_RATIO_RANGE[0]:
            warnings.append(
                f"Aspect ratio {structure.aspect_ratio:.2f} is low. "
                f"Wing will be less efficient but more maneuverable."
            )
        elif structure.aspect_ratio > FlyingWingDesignRules.ASPECT_RATIO_RANGE[1]:
            warnings.append(
                f"Aspect ratio {structure.aspect_ratio:.2f} is high. "
                f"Wing will be efficient but less maneuverable and structurally weaker."
            )
        
        # Check sweep angle
        if structure.sweep_angle < FlyingWingDesignRules.SWEEP_ANGLE_RANGE[0]:
            errors.append(
                f"Sweep angle {structure.sweep_angle}° is too low for a flying wing. "
                f"Minimum recommended: {FlyingWingDesignRules.SWEEP_ANGLE_RANGE[0]}°"
            )
        elif structure.sweep_angle > FlyingWingDesignRules.SWEEP_ANGLE_RANGE[1]:
            warnings.append(
                f"Sweep angle {structure.sweep_angle}° is high. "
                f"May have reduced lift and increased complexity."
            )
        
        # Check taper ratio
        if structure.taper_ratio < FlyingWingDesignRules.TAPER_RATIO_RANGE[0]:
            warnings.append(
                f"Taper ratio {structure.taper_ratio:.2f} is low. "
                f"Tip stall risk increases."
            )
        elif structure.taper_ratio > FlyingWingDesignRules.TAPER_RATIO_RANGE[1]:
            warnings.append(
                f"Taper ratio {structure.taper_ratio:.2f} is high. "
                f"Less efficient lift distribution."
            )
        
        # Check thickness ratio
        if structure.thickness_ratio < FlyingWingDesignRules.THICKNESS_RATIO_RANGE[0]:
            warnings.append(
                f"Thickness ratio {structure.thickness_ratio:.2f} is low. "
                f"May have structural issues, especially with 3D printing."
            )
        elif structure.thickness_ratio > FlyingWingDesignRules.THICKNESS_RATIO_RANGE[1]:
            warnings.append(
                f"Thickness ratio {structure.thickness_ratio:.2f} is high. "
                f"Will increase drag."
            )
        
        # Check CG position
        if structure.cg_position < FlyingWingDesignRules.CG_POSITION_RANGE[0]:
            errors.append(
                f"CG position {structure.cg_position:.2f} is too far forward. "
                f"Aircraft will be unstable."
            )
        elif structure.cg_position > FlyingWingDesignRules.CG_POSITION_RANGE[1]:
            errors.append(
                f"CG position {structure.cg_position:.2f} is too far back. "
                f"Aircraft will be unstable."
            )
        
        # Check elevon sizing
        elevon_area_ratio = structure.elevon_chord_ratio * structure.elevon_span_ratio * 2
        if elevon_area_ratio < 0.15:
            warnings.append(
                f"Elevon area ratio {elevon_area_ratio:.2f} is small. "
                f"May have insufficient control authority."
            )
        elif elevon_area_ratio > 0.30:
            warnings.append(
                f"Elevon area ratio {elevon_area_ratio:.2f} is large. "
                f"May cause control sensitivity issues."
            )
        
        return {"warnings": warnings, "errors": errors}
    
    @staticmethod
    def suggest_rib_count(wingspan: float, rib_spacing: float) -> int:
        """Calculate recommended number of ribs."""
        # Ribs per half-span
        ribs_per_side = int(wingspan / 2 / rib_spacing) + 1
        # Total ribs (including center rib)
        return ribs_per_side * 2 + 1
    
    @staticmethod
    def calculate_structural_weight(
        structure: FlyingWingStructure,
        material_density: float = 1.24  # g/cm³ (PLA default)
    ) -> float:
        """
        Estimate structural weight of the flying wing.
        
        Args:
            structure: The wing structure
            material_density: Material density in g/cm³
        
        Returns:
            Estimated weight in grams
        """
        # Convert mm to cm for volume calculation
        mm3_to_cm3 = 0.001
        
        # Spar volume
        spar_volume = (
            structure.wingspan *
            structure.spar_height *
            structure.spar_thickness *
            structure.spar_count
        ) * mm3_to_cm3
        
        # Rib volume (approximate)
        rib_count = FlyingWingDesignRules.suggest_rib_count(
            structure.wingspan,
            structure.rib_spacing
        )
        avg_chord = (structure.chord_root + structure.chord_tip) / 2
        rib_volume = (
            rib_count *
            avg_chord *
            structure.spar_height *
            structure.skin_thickness
        ) * mm3_to_cm3
        
        # Skin volume (top and bottom)
        skin_volume = (
            structure.wing_area *
            structure.skin_thickness *
            2  # top and bottom
        ) * mm3_to_cm3
        
        # Total volume
        total_volume = spar_volume + rib_volume + skin_volume
        
        # Weight calculation
        weight = total_volume * material_density
        
        # Account for infill (assume 20% infill for large surfaces)
        infill_factor = 0.3  # 30% of solid weight
        weight = weight * infill_factor
        
        return weight


class FlyingWingControlLogic:
    """Control logic for flying-wing aircraft."""
    
    @staticmethod
    def calculate_elevon_deflection(
        pitch_input: float,
        roll_input: float,
        max_deflection: float = 30.0
    ) -> Tuple[float, float]:
        """
        Calculate elevon deflections based on pilot input.
        
        Elevons combine elevator and aileron functions:
        - Both deflect same direction = pitch control
        - Deflect opposite directions = roll control
        
        Args:
            pitch_input: Pitch input (-1.0 to 1.0)
            roll_input: Roll input (-1.0 to 1.0)
            max_deflection: Maximum elevon deflection in degrees
        
        Returns:
            Tuple of (left_elevon_angle, right_elevon_angle) in degrees
        """
        # Clamp inputs
        pitch_input = max(-1.0, min(1.0, pitch_input))
        roll_input = max(-1.0, min(1.0, roll_input))
        
        # Calculate elevon positions
        # Left elevon: pitch + roll
        # Right elevon: pitch - roll
        left_elevon = (pitch_input + roll_input) * max_deflection
        right_elevon = (pitch_input - roll_input) * max_deflection
        
        # Clamp to max deflection
        left_elevon = max(-max_deflection, min(max_deflection, left_elevon))
        right_elevon = max(-max_deflection, min(max_deflection, right_elevon))
        
        return (left_elevon, right_elevon)
    
    @staticmethod
    def calculate_reflex_adjustment(
        speed: float,
        cruise_speed: float = 15.0,
        reflex_angle: float = 5.0
    ) -> float:
        """
        Calculate reflex adjustment for stability at different speeds.
        
        Flying wings use reflex (upward trailing edge bend) for stability.
        More reflex needed at higher speeds.
        
        Args:
            speed: Current speed in m/s
            cruise_speed: Design cruise speed in m/s
            reflex_angle: Maximum reflex angle in degrees
        
        Returns:
            Recommended reflex adjustment in degrees
        """
        # More reflex at higher speeds for stability
        speed_ratio = speed / cruise_speed
        
        # Limit speed ratio
        speed_ratio = max(0.5, min(1.5, speed_ratio))
        
        # Calculate reflex (increases with speed)
        reflex = reflex_angle * (0.5 + 0.5 * speed_ratio)
        
        return reflex
    
    @staticmethod
    def calculate_cg_effect(
        current_cg: float,
        target_cg: float,
        mac: float
    ) -> Dict[str, any]:
        """
        Calculate the effect of CG position on flying wing stability.
        
        Args:
            current_cg: Current CG position (ratio from leading edge)
            target_cg: Target CG position (ratio from leading edge)
            mac: Mean aerodynamic chord in mm
        
        Returns:
            Dictionary with CG analysis and recommendations
        """
        cg_diff = current_cg - target_cg
        cg_diff_mm = cg_diff * mac
        
        result = {
            "current_cg_ratio": current_cg,
            "target_cg_ratio": target_cg,
            "difference_ratio": cg_diff,
            "difference_mm": cg_diff_mm,
            "status": "OK",
            "recommendation": ""
        }
        
        if abs(cg_diff) < 0.02:  # Within 2%
            result["status"] = "OPTIMAL"
            result["recommendation"] = "CG position is optimal"
        elif cg_diff > 0.02:  # Too far back
            result["status"] = "WARNING"
            result["recommendation"] = (
                f"CG is {cg_diff_mm:.1f}mm too far back. "
                f"Move battery/components forward for stability."
            )
        elif cg_diff < -0.02:  # Too far forward
            result["status"] = "WARNING"
            result["recommendation"] = (
                f"CG is {abs(cg_diff_mm):.1f}mm too far forward. "
                f"Move battery/components backward. Aircraft may be too stable (hard to turn)."
            )
        
        # Critical errors
        if cg_diff > 0.05:
            result["status"] = "CRITICAL"
        elif cg_diff < -0.05:
            result["status"] = "CRITICAL"
        
        return result


def design_simple_flying_wing(
    wingspan: float,
    target_weight: float,
    build_method: BuildMethod,
    material_cost: MaterialCost
) -> Dict[str, any]:
    """
    Design a simple flying wing based on basic parameters.
    
    Args:
        wingspan: Desired wingspan in mm
        target_weight: Target all-up weight in grams
        build_method: Construction method
        material_cost: Material cost category
    
    Returns:
        Complete design specification
    """
    # Calculate recommended dimensions based on wingspan
    chord_root = wingspan * 0.20  # Root chord = 20% of wingspan
    chord_tip = wingspan * 0.10   # Tip chord = 10% of wingspan
    sweep_angle = 25  # degrees (good starting point)
    
    # Create structure
    structure = FlyingWingStructure(
        wingspan=wingspan,
        chord_root=chord_root,
        chord_tip=chord_tip,
        sweep_angle=sweep_angle,
        thickness_ratio=0.12
    )
    
    # Validate design
    validation = FlyingWingDesignRules.validate_design(structure)
    
    # Calculate rib count
    rib_count = FlyingWingDesignRules.suggest_rib_count(
        wingspan,
        structure.rib_spacing
    )
    
    # Estimate weight
    material_density = 1.24  # PLA
    if material_cost == MaterialCost.LOW_COST:
        material_density = 1.24  # PLA
    elif material_cost == MaterialCost.MEDIUM_COST:
        material_density = 1.27  # PETG
    else:
        material_density = 1.14  # Nylon
    
    estimated_weight = FlyingWingDesignRules.calculate_structural_weight(
        structure,
        material_density
    )
    
    # Create specification
    spec = FlyingWingSpec(
        name=f"Flying Wing {wingspan}mm",
        build_method=build_method,
        material_cost=material_cost,
        wingspan=wingspan,
        chord_root=chord_root,
        chord_tip=chord_tip,
        sweep_angle=sweep_angle,
        weight_target=target_weight
    )
    
    return {
        "specification": spec,
        "structure": structure,
        "validation": validation,
        "rib_count": rib_count,
        "estimated_structural_weight": estimated_weight,
        "weight_budget_remaining": target_weight - estimated_weight,
        "aspect_ratio": structure.aspect_ratio,
        "wing_area_dm2": structure.wing_area / 10000,  # dm² (commonly used in RC)
        "wing_loading_g_dm2": target_weight / (structure.wing_area / 10000)
    }


# Example usage
if __name__ == "__main__":
    print("=== Flying-Wing Design Module Demo ===\n")
    
    # Design a medium-sized flying wing
    print("Designing a 1000mm flying-wing...")
    design = design_simple_flying_wing(
        wingspan=1000,  # 1 meter
        target_weight=600,  # 600 grams
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.MEDIUM_COST
    )
    
    print("\n--- Specification ---")
    spec = design["specification"]
    print(f"Name: {spec.name}")
    print(f"Wingspan: {spec.wingspan}mm")
    print(f"Root Chord: {spec.chord_root}mm")
    print(f"Tip Chord: {spec.chord_tip}mm")
    print(f"Sweep Angle: {spec.sweep_angle}°")
    
    print("\n--- Aerodynamics ---")
    print(f"Wing Area: {design['wing_area_dm2']:.2f} dm²")
    print(f"Aspect Ratio: {design['aspect_ratio']:.2f}")
    print(f"Wing Loading: {design['wing_loading_g_dm2']:.1f} g/dm²")
    
    print("\n--- Structure ---")
    structure = design["structure"]
    print(f"Rib Count: {design['rib_count']}")
    print(f"Spar Height: {structure.spar_height:.1f}mm")
    print(f"Mean Aerodynamic Chord: {structure.mean_aerodynamic_chord:.1f}mm")
    
    print("\n--- Weight Budget ---")
    print(f"Estimated Structural Weight: {design['estimated_structural_weight']:.1f}g")
    print(f"Target Total Weight: {spec.weight_target}g")
    print(f"Remaining Budget (electronics, etc.): {design['weight_budget_remaining']:.1f}g")
    
    print("\n--- Validation ---")
    validation = design["validation"]
    if validation["errors"]:
        print("ERRORS:")
        for error in validation["errors"]:
            print(f"  ❌ {error}")
    if validation["warnings"]:
        print("WARNINGS:")
        for warning in validation["warnings"]:
            print(f"  ⚠️  {warning}")
    if not validation["errors"] and not validation["warnings"]:
        print("✅ Design passes all validation checks!")
    
    print("\n--- Control System Demo ---")
    # Example: Pitch up and roll right
    left_elev, right_elev = FlyingWingControlLogic.calculate_elevon_deflection(
        pitch_input=0.5,  # 50% pitch up
        roll_input=0.3    # 30% roll right
    )
    print(f"Pitch: 50% up, Roll: 30% right")
    print(f"  Left Elevon: {left_elev:.1f}°")
    print(f"  Right Elevon: {right_elev:.1f}°")
    
    print("\n--- CG Analysis ---")
    cg_analysis = FlyingWingControlLogic.calculate_cg_effect(
        current_cg=0.27,
        target_cg=0.25,
        mac=structure.mean_aerodynamic_chord
    )
    print(f"Target CG: {cg_analysis['target_cg_ratio']:.2f} (25% MAC)")
    print(f"Current CG: {cg_analysis['current_cg_ratio']:.2f}")
    print(f"Status: {cg_analysis['status']}")
    print(f"Recommendation: {cg_analysis['recommendation']}")
