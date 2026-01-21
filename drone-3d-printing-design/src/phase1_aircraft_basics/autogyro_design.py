"""
Autogyro Design Module

This module provides structural parameters, design rules, and control logic
for autogyro (gyroplane) aircraft design.
"""

import math
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .aircraft_types import AutogyroSpec, BuildMethod, MaterialCost


@dataclass
class AutogyroStructure:
    """Structural parameters for autogyro."""
    
    # Rotor system
    rotor_diameter: float  # mm
    rotor_blade_count: int = 2
    blade_chord: float = 0  # mm
    blade_twist: float = 8  # degrees (typical)
    rotor_rpm: float = 400  # typical for small autogyros
    
    # Rotor hub
    hub_type: str = "teetering"  # teetering, rigid, semi-rigid
    hub_diameter: float = 50  # mm
    
    # Fuselage
    fuselage_length: float = 0  # mm
    fuselage_width: float = 0  # mm
    tail_boom_length: float = 0  # mm
    
    # Propulsion (forward thrust)
    propeller_diameter: float = 0  # mm
    motor_size: int = 2212  # for electric models
    
    # Tail surfaces
    horizontal_tail_area: float = 0  # mm²
    vertical_tail_area: float = 0  # mm²
    
    # Landing gear
    main_gear_width: float = 0  # mm
    nose_gear_height: float = 0  # mm
    
    # Calculated values
    rotor_disc_area: float = field(default=0, init=False)
    rotor_solidity: float = field(default=0, init=False)
    tip_speed: float = field(default=0, init=False)  # m/s
    
    def __post_init__(self):
        """Calculate derived parameters."""
        # Rotor disc area
        self.rotor_disc_area = math.pi * (self.rotor_diameter / 2) ** 2
        
        # Auto-calculate blade chord if not provided
        if self.blade_chord == 0:
            # Typical solidity for autogyros: 0.05 to 0.08
            target_solidity = 0.065
            total_blade_area = self.rotor_disc_area * target_solidity
            single_blade_area = total_blade_area / self.rotor_blade_count
            self.blade_chord = single_blade_area / (self.rotor_diameter / 2)
        
        # Calculate rotor solidity
        total_blade_area = self.blade_chord * (self.rotor_diameter / 2) * self.rotor_blade_count
        self.rotor_solidity = total_blade_area / self.rotor_disc_area
        
        # Calculate tip speed
        rotor_radius_m = self.rotor_diameter / 2000  # Convert to meters
        rps = self.rotor_rpm / 60  # Revolutions per second
        self.tip_speed = 2 * math.pi * rotor_radius_m * rps
        
        # Auto-calculate fuselage if not provided
        if self.fuselage_length == 0:
            self.fuselage_length = self.rotor_diameter * 1.2
        if self.tail_boom_length == 0:
            self.tail_boom_length = self.rotor_diameter * 0.8


class AutogyroDesignRules:
    """Design rules for autogyro aircraft."""
    
    # Recommended ranges
    ROTOR_DISC_LOADING_RANGE = (5, 15)  # kg/m² (low loading for better autorotation)
    ROTOR_SOLIDITY_RANGE = (0.05, 0.08)
    TIP_SPEED_RANGE = (150, 220)  # m/s (Mach 0.44 to 0.65)
    BLADE_COUNT_OPTIONS = [2, 3, 4]
    
    @staticmethod
    def validate_design(structure: AutogyroStructure, target_weight_g: float) -> Dict[str, List[str]]:
        """Validate autogyro design."""
        warnings = []
        errors = []
        
        # Check blade count
        if structure.rotor_blade_count not in AutogyroDesignRules.BLADE_COUNT_OPTIONS:
            warnings.append(
                f"Unusual blade count {structure.rotor_blade_count}. "
                f"Common counts: {AutogyroDesignRules.BLADE_COUNT_OPTIONS}"
            )
        
        # Check rotor solidity
        if structure.rotor_solidity < AutogyroDesignRules.ROTOR_SOLIDITY_RANGE[0]:
            warnings.append(
                f"Low rotor solidity {structure.rotor_solidity:.3f}. "
                f"May have insufficient thrust in autorotation."
            )
        elif structure.rotor_solidity > AutogyroDesignRules.ROTOR_SOLIDITY_RANGE[1]:
            warnings.append(
                f"High rotor solidity {structure.rotor_solidity:.3f}. "
                f"Increased rotor drag and power requirements."
            )
        
        # Check disc loading
        disc_area_m2 = structure.rotor_disc_area / 1000000  # mm² to m²
        weight_kg = target_weight_g / 1000
        disc_loading = weight_kg / disc_area_m2
        
        if disc_loading < AutogyroDesignRules.ROTOR_DISC_LOADING_RANGE[0]:
            warnings.append(
                f"Very low disc loading {disc_loading:.1f} kg/m². "
                f"Rotor may be oversized."
            )
        elif disc_loading > AutogyroDesignRules.ROTOR_DISC_LOADING_RANGE[1]:
            warnings.append(
                f"High disc loading {disc_loading:.1f} kg/m². "
                f"Autorotation performance may be poor. Risk of high descent rates."
            )
        
        # Check tip speed
        if structure.tip_speed < AutogyroDesignRules.TIP_SPEED_RANGE[0]:
            warnings.append(
                f"Low tip speed {structure.tip_speed:.1f} m/s. "
                f"Rotor may not generate enough lift."
            )
        elif structure.tip_speed > AutogyroDesignRules.TIP_SPEED_RANGE[1]:
            warnings.append(
                f"High tip speed {structure.tip_speed:.1f} m/s. "
                f"Risk of compressibility effects and noise."
            )
        
        # Check hub type
        if structure.hub_type not in ["teetering", "rigid", "semi-rigid"]:
            errors.append(
                f"Unknown hub type '{structure.hub_type}'. "
                f"Valid types: teetering, rigid, semi-rigid"
            )
        
        return {"warnings": warnings, "errors": errors}
    
    @staticmethod
    def calculate_rotor_rpm(
        rotor_diameter: float,
        target_tip_speed: float = 180.0
    ) -> float:
        """
        Calculate recommended rotor RPM.
        
        Args:
            rotor_diameter: Rotor diameter in mm
            target_tip_speed: Target tip speed in m/s
        
        Returns:
            Recommended RPM
        """
        rotor_radius_m = rotor_diameter / 2000
        # v = ωr, ω = v/r (rad/s), RPM = ω * 60 / (2π)
        omega = target_tip_speed / rotor_radius_m
        rpm = omega * 60 / (2 * math.pi)
        return rpm


class AutogyroControlLogic:
    """Control logic for autogyro aircraft."""
    
    @staticmethod
    def calculate_control_inputs(
        throttle: float,
        cyclic_pitch: float,
        cyclic_roll: float,
        rudder: float
    ) -> Dict[str, float]:
        """
        Calculate control inputs for autogyro.
        
        Autogyro controls:
        - Throttle: Controls forward propeller/motor thrust
        - Cyclic pitch: Tilts rotor disc forward/back (pitch control)
        - Cyclic roll: Tilts rotor disc left/right (roll control)
        - Rudder: Yaw control via tail
        
        Note: Rotor is NOT powered - it spins freely due to airflow
        
        Args:
            throttle: Forward thrust (0.0 to 1.0)
            cyclic_pitch: Pitch control (-1.0 to 1.0)
            cyclic_roll: Roll control (-1.0 to 1.0)
            rudder: Yaw control (-1.0 to 1.0)
        
        Returns:
            Dictionary with control outputs
        """
        # Clamp inputs
        throttle = max(0.0, min(1.0, throttle))
        cyclic_pitch = max(-1.0, min(1.0, cyclic_pitch))
        cyclic_roll = max(-1.0, min(1.0, cyclic_roll))
        rudder = max(-1.0, min(1.0, rudder))
        
        return {
            "propeller_throttle": throttle,
            "rotor_cyclic_pitch": cyclic_pitch * 10,  # degrees
            "rotor_cyclic_roll": cyclic_roll * 10,  # degrees
            "rudder_deflection": rudder * 30,  # degrees
            "note": "Rotor spins freely - no rotor throttle"
        }
    
    @staticmethod
    def calculate_rotor_state(
        airspeed: float,
        descent_rate: float,
        rotor_rpm: float,
        rotor_diameter: float
    ) -> Dict[str, any]:
        """
        Calculate rotor state during autorotation.
        
        Args:
            airspeed: Forward airspeed in m/s
            descent_rate: Vertical descent rate in m/s (positive = descending)
            rotor_rpm: Current rotor RPM
            rotor_diameter: Rotor diameter in mm
        
        Returns:
            Rotor state information
        """
        # Calculate inflow ratio
        rotor_radius_m = rotor_diameter / 2000
        tip_speed = (rotor_rpm / 60) * 2 * math.pi * rotor_radius_m
        
        # Induced velocity (simplified)
        vi = descent_rate
        
        # Advance ratio
        mu = airspeed / tip_speed if tip_speed > 0 else 0
        
        # Inflow ratio
        lambda_i = vi / tip_speed if tip_speed > 0 else 0
        
        # Autorotation status
        if rotor_rpm < 300:
            status = "LOW RPM - Risk of rotor stall"
        elif rotor_rpm > 500:
            status = "HIGH RPM - Excessive rotor speed"
        else:
            status = "NORMAL - Good autorotation"
        
        return {
            "rotor_rpm": rotor_rpm,
            "tip_speed_ms": tip_speed,
            "advance_ratio": mu,
            "inflow_ratio": lambda_i,
            "descent_rate_ms": descent_rate,
            "status": status
        }


def design_simple_autogyro(
    rotor_diameter: float,
    target_weight: float,
    build_method: BuildMethod,
    material_cost: MaterialCost
) -> Dict[str, any]:
    """
    Design a simple autogyro.
    
    Args:
        rotor_diameter: Main rotor diameter in mm
        target_weight: Target all-up weight in grams
        build_method: Construction method
        material_cost: Material cost category
    
    Returns:
        Complete design specification
    """
    # Calculate propeller size (typically 1/4 to 1/3 of rotor diameter)
    propeller_diameter = rotor_diameter * 0.30
    
    # Calculate optimal rotor RPM
    rotor_rpm = AutogyroDesignRules.calculate_rotor_rpm(rotor_diameter, 180)
    
    # Create structure
    structure = AutogyroStructure(
        rotor_diameter=rotor_diameter,
        rotor_blade_count=2,
        rotor_rpm=rotor_rpm,
        propeller_diameter=propeller_diameter,
        fuselage_length=rotor_diameter * 1.2,
        tail_boom_length=rotor_diameter * 0.8
    )
    
    # Validate
    validation = AutogyroDesignRules.validate_design(structure, target_weight)
    
    # Create specification
    spec = AutogyroSpec(
        name=f"Autogyro {rotor_diameter}mm",
        build_method=build_method,
        material_cost=material_cost,
        wingspan=rotor_diameter,  # For autogyro, wingspan = rotor diameter
        rotor_diameter=rotor_diameter,
        rotor_blade_count=structure.rotor_blade_count,
        propeller_diameter=propeller_diameter,
        weight_target=target_weight
    )
    
    # Calculate disc loading
    disc_area_m2 = structure.rotor_disc_area / 1000000
    disc_loading = (target_weight / 1000) / disc_area_m2
    
    return {
        "specification": spec,
        "structure": structure,
        "validation": validation,
        "rotor_rpm": rotor_rpm,
        "tip_speed_ms": structure.tip_speed,
        "disc_loading_kg_m2": disc_loading,
        "rotor_solidity": structure.rotor_solidity,
        "disc_area_m2": disc_area_m2
    }


# Example usage
if __name__ == "__main__":
    print("=== Autogyro Design Module Demo ===\n")
    
    # Design a small autogyro
    design = design_simple_autogyro(
        rotor_diameter=800,  # 800mm rotor
        target_weight=500,   # 500 grams
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.MEDIUM_COST
    )
    
    print("--- Specification ---")
    spec = design["specification"]
    print(f"Name: {spec.name}")
    print(f"Rotor Diameter: {spec.rotor_diameter}mm")
    print(f"Blade Count: {spec.rotor_blade_count}")
    print(f"Propeller: {spec.propeller_diameter:.0f}mm")
    
    print("\n--- Rotor Performance ---")
    print(f"Rotor RPM: {design['rotor_rpm']:.0f}")
    print(f"Tip Speed: {design['tip_speed_ms']:.1f} m/s")
    print(f"Disc Area: {design['disc_area_m2']:.3f} m²")
    print(f"Disc Loading: {design['disc_loading_kg_m2']:.1f} kg/m²")
    print(f"Rotor Solidity: {design['rotor_solidity']:.3f}")
    
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
    controls = AutogyroControlLogic.calculate_control_inputs(
        throttle=0.7,       # 70% forward thrust
        cyclic_pitch=-0.3,  # Pitch forward
        cyclic_roll=0.2,    # Roll right
        rudder=0.1          # Slight right turn
    )
    print("Input: 70% throttle, pitch forward, roll right")
    print(f"  Propeller: {controls['propeller_throttle']*100:.0f}%")
    print(f"  Cyclic Pitch: {controls['rotor_cyclic_pitch']:.1f}°")
    print(f"  Cyclic Roll: {controls['rotor_cyclic_roll']:.1f}°")
    print(f"  Rudder: {controls['rudder_deflection']:.1f}°")
    print(f"  Note: {controls['note']}")
    
    print("\n--- Autorotation State ---")
    rotor_state = AutogyroControlLogic.calculate_rotor_state(
        airspeed=12.0,      # 12 m/s forward
        descent_rate=3.0,   # 3 m/s descent
        rotor_rpm=design['rotor_rpm'],
        rotor_diameter=spec.rotor_diameter
    )
    print(f"Descent Rate: {rotor_state['descent_rate_ms']} m/s")
    print(f"Rotor RPM: {rotor_state['rotor_rpm']:.0f}")
    print(f"Status: {rotor_state['status']}")
