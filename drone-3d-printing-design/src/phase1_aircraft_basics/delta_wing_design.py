"""
Delta-Wing Design Module

This module provides structural parameters, design rules, aerodynamic calculations,
and control logic specific to delta-wing aircraft design.

Delta wings are characterized by:
- Triangular planform
- High leading-edge sweep (typically 40-60°)
- Low aspect ratio (typically 1.5-3.0)
- High angle-of-attack capability
- Vortex lift generation at high alpha
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from .aircraft_types import DeltaWingSpec, BuildMethod, MaterialCost


@dataclass
class DeltaWingStructure:
    """Structural parameters for delta-wing design."""
    
    # Wing geometry
    wingspan: float  # mm
    chord_root: float  # mm (chord at centerline/fuselage)
    sweep_angle: float  # degrees (leading edge sweep)
    thickness_ratio: float = 0.06  # thin airfoil typical for deltas
    
    # Structural elements
    spar_count: int = 2  # Main spars (typically 2 for delta wings)
    spar_height: float = 0  # mm (calculated if 0)
    spar_thickness: float = 3  # mm (wall thickness)
    rib_spacing: float = 60  # mm (distance between ribs)
    skin_thickness: float = 2  # mm
    
    # Control surfaces
    elevon_chord_ratio: float = 0.20  # elevon chord as ratio of local chord
    elevon_span_start: float = 0.15  # where elevons start (ratio of semi-span)
    elevon_span_end: float = 0.90  # where elevons end (ratio of semi-span)
    
    # Vertical stabilizer
    has_vertical_tail: bool = True
    vertical_tail_height: float = 0  # mm (calculated based on design)
    vertical_tail_area: float = 0  # mm²
    
    # Center of gravity
    cg_position: float = 0.35  # ratio from apex (30-40% is typical)
    
    # Optional canards for pitch control
    has_canards: bool = False
    canard_area: float = 0  # mm²
    canard_position: float = 0  # mm from nose
    
    # Calculated values (filled by __post_init__)
    wing_area: float = field(default=0, init=False)
    mean_aerodynamic_chord: float = field(default=0, init=False)
    aspect_ratio: float = field(default=0, init=False)
    taper_ratio: float = field(default=0, init=False)  # Always 0 for pure delta
    chord_tip: float = field(default=0, init=False)
    estimated_weight: float = field(default=0, init=False)
    
    def __post_init__(self):
        """Calculate derived structural parameters."""
        # For a pure delta wing, tip chord is effectively zero
        # But for practical RC delta, we often have a small tip chord
        # Calculate from sweep angle and wingspan
        self.chord_tip = 0  # Pure delta has zero tip chord
        
        # Calculate wing area for triangular delta planform
        # Area = 0.5 * wingspan * root_chord
        self.wing_area = 0.5 * self.wingspan * self.chord_root
        
        # Calculate mean aerodynamic chord (MAC) for delta wing
        # For a pure delta (taper ratio = 0): MAC = 2/3 * root_chord
        self.mean_aerodynamic_chord = (2.0 / 3.0) * self.chord_root
        
        # Calculate aspect ratio
        if self.wing_area > 0:
            self.aspect_ratio = self.wingspan**2 / self.wing_area
        else:
            self.aspect_ratio = 0
        
        # Taper ratio is 0 for pure delta
        self.taper_ratio = 0
        
        # Calculate spar height if not specified
        if self.spar_height == 0:
            # Spar height is typically 60-70% of max wing thickness for thin delta airfoils
            max_thickness = self.chord_root * self.thickness_ratio
            self.spar_height = max_thickness * 0.65
        
        # Calculate vertical tail dimensions if not specified
        if self.has_vertical_tail:
            if self.vertical_tail_height == 0:
                # Typical vertical tail height is 15-20% of wingspan
                self.vertical_tail_height = self.wingspan * 0.17
            
            if self.vertical_tail_area == 0:
                # Vertical tail area typically 8-12% of wing area
                self.vertical_tail_area = self.wing_area * 0.10
        
        # Verify sweep angle is consistent with geometry
        # tan(sweep) = (wingspan/2) / chord_root
        calculated_sweep = math.degrees(math.atan((self.wingspan / 2) / self.chord_root))
        if abs(calculated_sweep - self.sweep_angle) > 5:  # 5 degree tolerance
            # Adjust chord_root to match specified sweep angle
            self.chord_root = (self.wingspan / 2) / math.tan(math.radians(self.sweep_angle))
            # Recalculate dependent values
            self.wing_area = 0.5 * self.wingspan * self.chord_root
            self.mean_aerodynamic_chord = (2.0 / 3.0) * self.chord_root
            if self.wing_area > 0:
                self.aspect_ratio = self.wingspan**2 / self.wing_area


class DeltaWingDesignRules:
    """Design rules and constraints for delta-wing aircraft."""
    
    # Recommended ranges for delta wings
    ASPECT_RATIO_RANGE = (1.5, 6.0)  # Low to medium AR for deltas (pure delta to cropped delta)
    SWEEP_ANGLE_RANGE = (40, 65)  # degrees (high sweep for deltas)
    THICKNESS_RATIO_RANGE = (0.04, 0.08)  # Thin airfoils for deltas
    CG_POSITION_RANGE = (0.30, 0.42)  # ratio from apex
    WING_LOADING_RANGE = (30, 80)  # g/dm² (deltas can handle higher loading)
    
    @staticmethod
    def validate_design(structure: DeltaWingStructure) -> Dict[str, List[str]]:
        """
        Validate a delta-wing design against design rules.
        
        Args:
            structure: The delta-wing structure to validate
        
        Returns:
            Dictionary with 'warnings' and 'errors' lists
        """
        warnings = []
        errors = []
        
        # Check aspect ratio
        if structure.aspect_ratio < DeltaWingDesignRules.ASPECT_RATIO_RANGE[0]:
            warnings.append(
                f"Aspect ratio {structure.aspect_ratio:.2f} is very low. "
                f"Wing will have high induced drag but excellent high-alpha performance."
            )
        elif structure.aspect_ratio > DeltaWingDesignRules.ASPECT_RATIO_RANGE[1]:
            warnings.append(
                f"Aspect ratio {structure.aspect_ratio:.2f} is high for a delta wing. "
                f"Consider a swept wing or flying wing design instead."
            )
        
        # Check sweep angle
        if structure.sweep_angle < DeltaWingDesignRules.SWEEP_ANGLE_RANGE[0]:
            errors.append(
                f"Sweep angle {structure.sweep_angle}° is too low for a delta wing. "
                f"Minimum recommended: {DeltaWingDesignRules.SWEEP_ANGLE_RANGE[0]}°"
            )
        elif structure.sweep_angle > DeltaWingDesignRules.SWEEP_ANGLE_RANGE[1]:
            warnings.append(
                f"Sweep angle {structure.sweep_angle}° is very high. "
                f"Will have excellent supersonic characteristics but poor subsonic efficiency."
            )
        
        # Check thickness ratio
        if structure.thickness_ratio < DeltaWingDesignRules.THICKNESS_RATIO_RANGE[0]:
            warnings.append(
                f"Thickness ratio {structure.thickness_ratio:.3f} is very low. "
                f"May have structural issues, especially with 3D printing."
            )
        elif structure.thickness_ratio > DeltaWingDesignRules.THICKNESS_RATIO_RANGE[1]:
            warnings.append(
                f"Thickness ratio {structure.thickness_ratio:.3f} is high for a delta wing. "
                f"Will increase drag and reduce top speed."
            )
        
        # Check CG position
        if structure.cg_position < DeltaWingDesignRules.CG_POSITION_RANGE[0]:
            errors.append(
                f"CG position {structure.cg_position:.2f} is too far forward. "
                f"Aircraft will be pitch-unstable and nose-heavy."
            )
        elif structure.cg_position > DeltaWingDesignRules.CG_POSITION_RANGE[1]:
            errors.append(
                f"CG position {structure.cg_position:.2f} is too far back. "
                f"Aircraft will be unstable and difficult to control."
            )
        
        # Check elevon sizing
        elevon_span_ratio = structure.elevon_span_end - structure.elevon_span_start
        elevon_area_ratio = structure.elevon_chord_ratio * elevon_span_ratio
        
        if elevon_area_ratio < 0.10:
            warnings.append(
                f"Elevon area ratio {elevon_area_ratio:.2f} is small. "
                f"May have insufficient control authority at low speeds."
            )
        elif elevon_area_ratio > 0.25:
            warnings.append(
                f"Elevon area ratio {elevon_area_ratio:.2f} is large. "
                f"May cause excessive control sensitivity."
            )
        
        # Vertical stabilizer check
        if structure.has_vertical_tail:
            vtail_ratio = structure.vertical_tail_area / structure.wing_area
            if vtail_ratio < 0.08:
                warnings.append(
                    f"Vertical tail area ratio {vtail_ratio:.2f} is small. "
                    f"May have poor directional stability."
                )
            elif vtail_ratio > 0.15:
                warnings.append(
                    f"Vertical tail area ratio {vtail_ratio:.2f} is large. "
                    f"Will increase drag."
                )
        else:
            warnings.append(
                "No vertical tail specified. Delta wings typically need vertical "
                "stabilizers for directional stability."
            )
        
        return {"warnings": warnings, "errors": errors}
    
    @staticmethod
    def suggest_rib_count(chord_root: float, rib_spacing: float) -> int:
        """Calculate recommended number of ribs for delta wing."""
        # Ribs are arranged radially from apex to trailing edge
        # Number of ribs depends on root chord
        rib_count = int(chord_root / rib_spacing) + 1
        # Add extra ribs for structural integrity
        return max(rib_count, 5)  # Minimum 5 ribs
    
    @staticmethod
    def calculate_structural_weight(
        structure: DeltaWingStructure,
        material_density: float = 1.24  # g/cm³ (PLA default)
    ) -> float:
        """
        Estimate structural weight of the delta wing.
        
        Args:
            structure: The wing structure
            material_density: Material density in g/cm³
        
        Returns:
            Estimated weight in grams
        """
        # Convert mm to cm for volume calculation
        mm3_to_cm3 = 0.001
        
        # Main spar volume (2 spars running from apex to wing tips)
        # Each spar length is approximately: sqrt((wingspan/2)^2 + chord_root^2)
        spar_length = math.sqrt((structure.wingspan / 2)**2 + structure.chord_root**2)
        spar_volume = (
            spar_length *
            structure.spar_height *
            structure.spar_thickness *
            structure.spar_count
        ) * mm3_to_cm3
        
        # Rib volume (ribs run from leading edge to trailing edge)
        rib_count = DeltaWingDesignRules.suggest_rib_count(
            structure.chord_root,
            structure.rib_spacing
        )
        # Average rib length (gets shorter toward tip)
        avg_rib_length = structure.chord_root * 0.6
        rib_volume = (
            rib_count *
            avg_rib_length *
            structure.spar_height *
            structure.skin_thickness
        ) * mm3_to_cm3
        
        # Skin volume (top and bottom surfaces)
        skin_volume = (
            structure.wing_area *
            structure.skin_thickness *
            2  # top and bottom
        ) * mm3_to_cm3
        
        # Vertical tail volume (if present)
        vtail_volume = 0
        if structure.has_vertical_tail:
            vtail_volume = (
                structure.vertical_tail_area *
                structure.skin_thickness *
                2  # both sides
            ) * mm3_to_cm3
        
        # Total volume
        total_volume = spar_volume + rib_volume + skin_volume + vtail_volume
        
        # Weight calculation
        weight = total_volume * material_density
        
        # Account for infill (assume 25% infill for delta wings)
        infill_factor = 0.35  # 35% of solid weight
        weight = weight * infill_factor
        
        return weight
    
    @staticmethod
    def calculate_vortex_lift_coefficient(
        angle_of_attack: float,
        sweep_angle: float
    ) -> float:
        """
        Calculate additional lift coefficient from leading-edge vortices.
        
        Delta wings generate vortex lift at high angles of attack.
        
        Args:
            angle_of_attack: Angle of attack in degrees
            sweep_angle: Leading edge sweep angle in degrees
        
        Returns:
            Additional vortex lift coefficient
        """
        # Vortex lift becomes significant above ~10° AoA
        if angle_of_attack < 10:
            return 0.0
        
        # Vortex lift increases with sweep angle and AoA
        # Empirical formula for slender delta wings
        alpha_rad = math.radians(angle_of_attack)
        sweep_rad = math.radians(sweep_angle)
        
        # Vortex lift coefficient
        # K_v depends on sweep angle (higher sweep = stronger vortices)
        K_v = 0.8 * math.sin(sweep_rad)
        
        # Vortex CL = K_v * sin(alpha) * cos(alpha) * sin(alpha)
        CL_vortex = K_v * (math.sin(alpha_rad)**2) * math.cos(alpha_rad)
        
        return CL_vortex
    
    @staticmethod
    def calculate_total_lift_coefficient(
        angle_of_attack: float,
        sweep_angle: float,
        aspect_ratio: float
    ) -> float:
        """
        Calculate total lift coefficient including vortex lift.
        
        Args:
            angle_of_attack: Angle of attack in degrees
            sweep_angle: Leading edge sweep angle in degrees
            aspect_ratio: Wing aspect ratio
        
        Returns:
            Total lift coefficient
        """
        # Potential flow lift (basic wing theory)
        alpha_rad = math.radians(angle_of_attack)
        
        # Lift curve slope for delta wing
        # a_0 = 2*pi*AR / (2 + sqrt(4 + AR^2))
        a_0 = (2 * math.pi * aspect_ratio) / (2 + math.sqrt(4 + aspect_ratio**2))
        
        # Basic lift coefficient
        CL_basic = a_0 * alpha_rad
        
        # Add vortex lift
        CL_vortex = DeltaWingDesignRules.calculate_vortex_lift_coefficient(
            angle_of_attack,
            sweep_angle
        )
        
        # Total lift
        CL_total = CL_basic + CL_vortex
        
        # Clamp to realistic values (max CL around 1.5-2.0 for deltas)
        CL_total = min(CL_total, 2.0)
        
        return CL_total


class DeltaWingControlLogic:
    """Control logic for delta-wing aircraft."""
    
    @staticmethod
    def calculate_elevon_deflection(
        pitch_input: float,
        roll_input: float,
        max_deflection: float = 25.0
    ) -> Tuple[float, float]:
        """
        Calculate elevon deflections based on pilot input.
        
        Delta wings typically use elevons for pitch and roll control,
        similar to flying wings but with different mixing ratios.
        
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
    def calculate_yaw_from_roll(
        roll_input: float,
        speed: float,
        coupling_factor: float = 0.3
    ) -> float:
        """
        Calculate induced yaw from roll input (proverse yaw).
        
        Delta wings exhibit strong roll-yaw coupling due to differential drag.
        
        Args:
            roll_input: Roll input (-1.0 to 1.0)
            speed: Airspeed in m/s
            coupling_factor: Roll-yaw coupling strength (0.2-0.4 typical)
        
        Returns:
            Yaw rate in degrees/second
        """
        # Roll-yaw coupling increases with speed
        # At low speeds, coupling is weaker
        speed_factor = min(speed / 10.0, 1.0)  # Normalize to 10 m/s
        
        # Calculate induced yaw
        yaw_rate = roll_input * coupling_factor * speed_factor * 60  # degrees/second
        
        return yaw_rate
    
    @staticmethod
    def calculate_high_alpha_control(
        angle_of_attack: float,
        pitch_input: float,
        vortex_burst_aoa: float = 35.0
    ) -> Dict[str, Any]:
        """
        Calculate control effectiveness at high angle of attack.
        
        Delta wings can fly at very high AoA using vortex lift,
        but control effectiveness changes.
        
        Args:
            angle_of_attack: Current angle of attack in degrees
            pitch_input: Desired pitch input (-1.0 to 1.0)
            vortex_burst_aoa: AoA where vortices burst (loss of lift)
        
        Returns:
            Dictionary with control parameters and warnings
        """
        result = {
            "angle_of_attack": angle_of_attack,
            "control_effectiveness": 1.0,
            "recommended_input": pitch_input,
            "warnings": []
        }
        
        # Normal flight regime (AoA < 20°)
        if angle_of_attack < 20:
            result["control_effectiveness"] = 1.0
            result["flight_regime"] = "normal"
        
        # High alpha regime (20° < AoA < vortex_burst_aoa)
        elif angle_of_attack < vortex_burst_aoa:
            result["flight_regime"] = "high_alpha"
            # Control effectiveness reduces but remains good
            result["control_effectiveness"] = 0.8
            result["warnings"].append(
                f"High angle of attack ({angle_of_attack:.1f}°). "
                "Vortex lift active. Reduce AoA for better efficiency."
            )
        
        # Post-vortex-burst regime (AoA > vortex_burst_aoa)
        else:
            result["flight_regime"] = "post_stall"
            result["control_effectiveness"] = 0.3
            result["warnings"].append(
                f"WARNING: Angle of attack ({angle_of_attack:.1f}°) exceeds vortex burst limit "
                f"({vortex_burst_aoa:.1f}°). Reduce nose attitude immediately!"
            )
            # Limit pitch-up input
            if pitch_input > 0:
                result["recommended_input"] = 0
        
        return result
    
    @staticmethod
    def calculate_cg_effect(
        current_cg: float,
        target_cg: float,
        mac: float
    ) -> Dict[str, Any]:
        """
        Calculate the effect of CG position on delta wing stability.
        
        Args:
            current_cg: Current CG position (ratio from apex)
            target_cg: Target CG position (ratio from apex)
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
                f"Move battery/payload forward. Aircraft may be unstable."
            )
        elif cg_diff < -0.02:  # Too far forward
            result["status"] = "WARNING"
            result["recommendation"] = (
                f"CG is {abs(cg_diff_mm):.1f}mm too far forward. "
                f"Move battery/payload backward. High-alpha capability reduced."
            )
        
        # Critical errors
        if cg_diff > 0.05:
            result["status"] = "CRITICAL"
            result["recommendation"] += " DO NOT FLY until CG is corrected!"
        elif cg_diff < -0.05:
            result["status"] = "CRITICAL"
        
        return result


def design_simple_delta_wing(
    wingspan: float,
    target_weight: float,
    build_method: BuildMethod,
    material_cost: MaterialCost,
    sweep_angle: float = 50.0
) -> Dict[str, Any]:
    """
    Design a simple delta wing based on basic parameters.
    
    Args:
        wingspan: Desired wingspan in mm
        target_weight: Target all-up weight in grams
        build_method: Construction method
        material_cost: Material cost category
        sweep_angle: Leading edge sweep angle in degrees (default 50°)
    
    Returns:
        Complete design specification
    """
    # Calculate root chord from wingspan and sweep angle
    # For delta: chord_root = (wingspan/2) / tan(sweep_angle)
    chord_root = (wingspan / 2) / math.tan(math.radians(sweep_angle))
    
    # Create structure
    structure = DeltaWingStructure(
        wingspan=wingspan,
        chord_root=chord_root,
        sweep_angle=sweep_angle,
        thickness_ratio=0.06,
        has_vertical_tail=True
    )
    
    # Validate design
    validation = DeltaWingDesignRules.validate_design(structure)
    
    # Calculate rib count
    rib_count = DeltaWingDesignRules.suggest_rib_count(
        chord_root,
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
    
    estimated_weight = DeltaWingDesignRules.calculate_structural_weight(
        structure,
        material_density
    )
    
    # Create specification
    spec = DeltaWingSpec(
        name=f"Delta Wing {wingspan}mm",
        build_method=build_method,
        material_cost=material_cost,
        wingspan=wingspan,
        chord_root=chord_root,
        sweep_angle=sweep_angle,
        weight_target=target_weight
    )
    
    # Calculate performance metrics
    wing_area_dm2 = structure.wing_area / 10000  # dm²
    wing_loading = target_weight / wing_area_dm2 if wing_area_dm2 > 0 else 0
    
    # Estimate stall speed (rough approximation)
    # V_stall = sqrt(2 * W / (rho * S * CL_max))
    # Assuming sea level density and CL_max ~ 1.5 for delta
    CL_max = 1.5
    rho = 1.225  # kg/m³
    weight_n = (target_weight / 1000) * 9.81  # Convert to Newtons
    wing_area_m2 = structure.wing_area / 1000000  # Convert to m²
    
    if wing_area_m2 > 0:
        stall_speed = math.sqrt((2 * weight_n) / (rho * wing_area_m2 * CL_max))
    else:
        stall_speed = 0
    
    return {
        "specification": spec,
        "structure": structure,
        "validation": validation,
        "rib_count": rib_count,
        "estimated_structural_weight": estimated_weight,
        "weight_budget_remaining": target_weight - estimated_weight,
        "aspect_ratio": structure.aspect_ratio,
        "wing_area_dm2": wing_area_dm2,
        "wing_loading_g_dm2": wing_loading,
        "estimated_stall_speed_ms": stall_speed,
        "estimated_cruise_speed_ms": stall_speed * 1.5,  # Typical cruise at 1.5x stall
        "max_angle_of_attack": 35  # Typical vortex burst AoA
    }


# Example usage
if __name__ == "__main__":
    print("=== Delta-Wing Design Module Demo ===\n")
    
    # Design a medium-sized delta wing
    print("Designing a 1000mm delta-wing...")
    design = design_simple_delta_wing(
        wingspan=1000,  # 1 meter
        target_weight=550,  # 550 grams
        build_method=BuildMethod.THREE_D_PRINTED,
        material_cost=MaterialCost.MEDIUM_COST,
        sweep_angle=55  # 55 degree sweep (more typical for delta)
    )
    
    print("\n--- Specification ---")
    spec = design["specification"]
    print(f"Name: {spec.name}")
    print(f"Wingspan: {spec.wingspan}mm")
    print(f"Root Chord: {spec.chord_root:.1f}mm")
    print(f"Sweep Angle: {spec.sweep_angle}°")
    print(f"Aircraft Type: {spec.aircraft_type.value}")
    
    print("\n--- Aerodynamics ---")
    print(f"Wing Area: {design['wing_area_dm2']:.2f} dm²")
    print(f"Aspect Ratio: {design['aspect_ratio']:.2f}")
    print(f"Wing Loading: {design['wing_loading_g_dm2']:.1f} g/dm²")
    print(f"Estimated Stall Speed: {design['estimated_stall_speed_ms']:.1f} m/s")
    print(f"Estimated Cruise Speed: {design['estimated_cruise_speed_ms']:.1f} m/s")
    
    print("\n--- Structure ---")
    structure = design["structure"]
    print(f"Rib Count: {design['rib_count']}")
    print(f"Spar Height: {structure.spar_height:.1f}mm")
    print(f"Mean Aerodynamic Chord: {structure.mean_aerodynamic_chord:.1f}mm")
    print(f"Vertical Tail Height: {structure.vertical_tail_height:.1f}mm")
    print(f"Vertical Tail Area: {structure.vertical_tail_area:.0f}mm²")
    
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
    
    print("\n--- Vortex Lift Analysis ---")
    # Calculate lift at various angles of attack
    print("Angle of Attack | Vortex CL | Total CL")
    print("-" * 45)
    for aoa in [0, 10, 20, 30, 35]:
        cl_vortex = DeltaWingDesignRules.calculate_vortex_lift_coefficient(
            aoa, structure.sweep_angle
        )
        cl_total = DeltaWingDesignRules.calculate_total_lift_coefficient(
            aoa, structure.sweep_angle, structure.aspect_ratio
        )
        print(f"{aoa:3d}°            | {cl_vortex:5.3f}     | {cl_total:5.3f}")
    
    print("\n--- Control System Demo ---")
    # Example: Pitch up and roll right
    left_elev, right_elev = DeltaWingControlLogic.calculate_elevon_deflection(
        pitch_input=0.5,  # 50% pitch up
        roll_input=0.3    # 30% roll right
    )
    print(f"Pitch: 50% up, Roll: 30% right")
    print(f"  Left Elevon: {left_elev:.1f}°")
    print(f"  Right Elevon: {right_elev:.1f}°")
    
    # High alpha control
    print("\n--- High Alpha Performance ---")
    for aoa in [15, 25, 37]:
        high_alpha = DeltaWingControlLogic.calculate_high_alpha_control(
            angle_of_attack=aoa,
            pitch_input=0.5
        )
        print(f"AoA {aoa}°: {high_alpha['flight_regime']} regime, "
              f"control effectiveness: {high_alpha['control_effectiveness']:.1f}")
        if high_alpha['warnings']:
            for warning in high_alpha['warnings']:
                print(f"  ⚠️  {warning}")
    
    print("\n--- CG Analysis ---")
    cg_analysis = DeltaWingControlLogic.calculate_cg_effect(
        current_cg=0.37,
        target_cg=0.35,
        mac=structure.mean_aerodynamic_chord
    )
    print(f"Target CG: {cg_analysis['target_cg_ratio']:.2f} (35% from apex)")
    print(f"Current CG: {cg_analysis['current_cg_ratio']:.2f}")
    print(f"Status: {cg_analysis['status']}")
    print(f"Recommendation: {cg_analysis['recommendation']}")
