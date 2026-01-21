"""
Rotorcraft Design Module

This module provides structural parameters, design rules, and control logic
for multirotor/rotorcraft aircraft (quadcopters, hexacopters, etc.).
"""

import math
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .aircraft_types import RotorcraftSpec, BuildMethod, MaterialCost


@dataclass
class RotorcraftStructure:
    """Structural parameters for rotorcraft."""
    
    # Configuration
    motor_count: int  # 4, 6, 8, etc.
    frame_type: str  # "X", "H", "+", "hybrid"
    
    # Dimensions
    motor_to_motor_distance: float  # mm (adjacent motors)
    arm_length: float  # mm
    arm_width: float = 25  # mm
    arm_height: float = 10  # mm
    
    # Motors and propellers
    motor_size: int = 2205  # stator size
    propeller_diameter: float = 0  # mm
    propeller_pitch: float = 0  # inches
    
    # Frame
    center_plate_size: float = 0  # mm (diameter or width)
    center_plate_thickness: float = 3  # mm
    
    # Calculated values
    diagonal_size: float = field(default=0, init=False)
    stator_diameter: float = field(default=0, init=False)
    stator_height: float = field(default=0, init=False)
    
    def __post_init__(self):
        """Calculate derived parameters."""
        # Parse motor size (e.g., 2205 -> 22mm diameter, 05mm height)
        self.stator_diameter = int(str(self.motor_size)[:2])
        self.stator_height = int(str(self.motor_size)[2:])
        
        # Calculate diagonal
        if self.frame_type == "X":
            self.diagonal_size = self.motor_to_motor_distance * math.sqrt(2)
        else:
            self.diagonal_size = self.motor_to_motor_distance
        
        # Auto-calculate center plate if not provided
        if self.center_plate_size == 0:
            self.center_plate_size = self.arm_width * 2.5


class RotorcraftDesignRules:
    """Design rules for rotorcraft."""
    
    # Recommended thrust-to-weight ratios
    THRUST_TO_WEIGHT_RANGES = {
        "cinematic": (1.5, 2.5),  # Smooth, stable video
        "freestyle": (4.0, 8.0),  # Acrobatic flying
        "racing": (6.0, 12.0),    # High performance
        "endurance": (1.3, 2.0),  # Long flight time
    }
    
    # Recommended propeller clearance
    MIN_PROP_CLEARANCE = 25  # mm from frame
    
    @staticmethod
    def validate_design(structure: RotorcraftStructure, purpose: str = "freestyle") -> Dict[str, List[str]]:
        """Validate rotorcraft design."""
        warnings = []
        errors = []
        
        # Check motor count
        valid_counts = [3, 4, 6, 8]
        if structure.motor_count not in valid_counts:
            errors.append(
                f"Motor count {structure.motor_count} is unusual. "
                f"Common counts: {valid_counts}"
            )
        
        # Check propeller clearance
        if structure.propeller_diameter > 0:
            max_prop_radius = structure.propeller_diameter / 2
            actual_spacing = structure.motor_to_motor_distance / 2
            clearance = actual_spacing - max_prop_radius
            
            if clearance < RotorcraftDesignRules.MIN_PROP_CLEARANCE:
                warnings.append(
                    f"Propeller clearance {clearance:.1f}mm is tight. "
                    f"Minimum recommended: {RotorcraftDesignRules.MIN_PROP_CLEARANCE}mm. "
                    f"Risk of prop strikes!"
                )
        
        # Check arm strength
        if structure.arm_height < structure.arm_width / 3:
            warnings.append(
                f"Arm height {structure.arm_height}mm may be too thin. "
                f"Consider increasing for structural strength."
            )
        
        return {"warnings": warnings, "errors": errors}
    
    @staticmethod
    def calculate_recommended_props(
        motor_size: int,
        motor_to_motor: float,
        kv_rating: int = 2400
    ) -> Dict[str, any]:
        """
        Recommend propeller size based on frame.
        
        Args:
            motor_size: Motor stator size (e.g., 2205)
            motor_to_motor: Distance between adjacent motors in mm
            kv_rating: Motor KV rating
        
        Returns:
            Propeller recommendations
        """
        # Maximum prop diameter (with safety margin)
        max_prop = (motor_to_motor - RotorcraftDesignRules.MIN_PROP_CLEARANCE * 2) * 2
        
        # Convert to inches (common prop measurement)
        max_prop_inches = max_prop / 25.4
        
        # Round down to common sizes
        common_sizes = [3, 4, 5, 6, 7, 8, 9, 10]
        valid_sizes = [s for s in common_sizes if s <= max_prop_inches]
        recommended_size = max(valid_sizes) if valid_sizes else 3
        
        # Pitch recommendations based on KV
        if kv_rating > 3000:
            pitch_range = (3.5, 4.5)
            purpose = "racing/high speed"
        elif kv_rating > 2000:
            pitch_range = (4.0, 5.0)
            purpose = "freestyle/all-around"
        else:
            pitch_range = (5.0, 6.5)
            purpose = "cruising/efficiency"
        
        return {
            "max_diameter_inch": max_prop_inches,
            "recommended_size_inch": recommended_size,
            "pitch_range_inch": pitch_range,
            "purpose": purpose,
            "common_props": [
                f"{recommended_size}x{p}" 
                for p in [4.0, 4.5, 5.0] 
                if pitch_range[0] <= p <= pitch_range[1]
            ]
        }
    
    @staticmethod
    def calculate_estimated_weight(
        structure: RotorcraftStructure,
        material_density: float = 1.24
    ) -> float:
        """Estimate frame weight."""
        mm3_to_cm3 = 0.001
        
        # Arm volume
        arm_volume = (
            structure.arm_length *
            structure.arm_width *
            structure.arm_height *
            structure.motor_count
        ) * mm3_to_cm3
        
        # Center plate volume
        center_volume = (
            math.pi * (structure.center_plate_size / 2) ** 2 *
            structure.center_plate_thickness
        ) * mm3_to_cm3
        
        # Total with 30% infill
        total_volume = (arm_volume + center_volume) * 0.3
        weight = total_volume * material_density
        
        return weight


class RotorcraftControlLogic:
    """Control logic for rotorcraft."""
    
    @staticmethod
    def calculate_motor_outputs(
        throttle: float,
        pitch: float,
        roll: float,
        yaw: float,
        motor_count: int = 4,
        frame_type: str = "X"
    ) -> List[float]:
        """
        Calculate individual motor outputs for quadcopter.
        
        Args:
            throttle: Throttle input (0.0 to 1.0)
            pitch: Pitch input (-1.0 to 1.0)
            roll: Roll input (-1.0 to 1.0)
            yaw: Yaw input (-1.0 to 1.0)
            motor_count: Number of motors
            frame_type: Frame configuration
        
        Returns:
            List of motor output values (0.0 to 1.0)
        """
        # Clamp inputs
        throttle = max(0.0, min(1.0, throttle))
        pitch = max(-1.0, min(1.0, pitch))
        roll = max(-1.0, min(1.0, roll))
        yaw = max(-1.0, min(1.0, yaw))
        
        if motor_count == 4 and frame_type == "X":
            # Quadcopter X configuration
            # Motor layout:
            #     1   2
            #      \ /
            #       X
            #      / \
            #     4   3
            motors = [
                throttle + pitch + roll + yaw,  # Front-left
                throttle + pitch - roll - yaw,  # Front-right
                throttle - pitch - roll + yaw,  # Rear-right
                throttle - pitch + roll - yaw,  # Rear-left
            ]
        else:
            # Generic: equal throttle to all motors (no control mixing)
            motors = [throttle] * motor_count
        
        # Clamp and normalize
        motors = [max(0.0, min(1.0, m)) for m in motors]
        
        return motors


def design_simple_rotorcraft(
    motor_count: int,
    propeller_size_inch: float,
    target_weight: float,
    build_method: BuildMethod,
    material_cost: MaterialCost,
    purpose: str = "freestyle"
) -> Dict[str, any]:
    """
    Design a simple rotorcraft frame.
    
    Args:
        motor_count: Number of motors (4, 6, 8)
        propeller_size_inch: Propeller size in inches
        target_weight: Target all-up weight in grams
        build_method: Construction method
        material_cost: Material cost category
        purpose: "racing", "freestyle", "cinematic", or "endurance"
    
    Returns:
        Complete design specification
    """
    # Convert prop size to mm
    propeller_diameter = propeller_size_inch * 25.4
    
    # Calculate motor spacing (prop diameter + clearance)
    motor_spacing = (propeller_diameter / 2 + RotorcraftDesignRules.MIN_PROP_CLEARANCE) * 2
    
    # Arm length
    arm_length = motor_spacing / 2
    
    # Motor size based on prop size
    if propeller_size_inch <= 4:
        motor_size = 1408
        arm_dims = (20, 8)
    elif propeller_size_inch <= 5:
        motor_size = 2205
        arm_dims = (25, 10)
    elif propeller_size_inch <= 6:
        motor_size = 2306
        arm_dims = (30, 12)
    else:
        motor_size = 2408
        arm_dims = (35, 14)
    
    # Create structure
    structure = RotorcraftStructure(
        motor_count=motor_count,
        frame_type="X",
        motor_to_motor_distance=motor_spacing,
        arm_length=arm_length,
        arm_width=arm_dims[0],
        arm_height=arm_dims[1],
        motor_size=motor_size,
        propeller_diameter=propeller_diameter
    )
    
    # Validate
    validation = RotorcraftDesignRules.validate_design(structure, purpose)
    
    # Estimate weight
    material_density = 1.24 if material_cost == MaterialCost.LOW_COST else 1.27
    frame_weight = RotorcraftDesignRules.calculate_estimated_weight(structure, material_density)
    
    # Create specification
    spec = RotorcraftSpec(
        name=f"{motor_count}-motor {purpose.title()} Drone",
        build_method=build_method,
        material_cost=material_cost,
        wingspan=structure.diagonal_size,
        motor_count=motor_count,
        motor_size=motor_size,
        propeller_diameter=propeller_diameter,
        weight_target=target_weight
    )
    
    return {
        "specification": spec,
        "structure": structure,
        "validation": validation,
        "frame_weight": frame_weight,
        "diagonal_size_mm": structure.diagonal_size,
        "purpose": purpose
    }


# Example usage
if __name__ == "__main__":
    print("=== Rotorcraft Design Module Demo ===\n")
    
    # Design a 5" freestyle quadcopter
    design = design_simple_rotorcraft(
        motor_count=4,
        propeller_size_inch=5.0,
        target_weight=600,
        build_method=BuildMethod.THREE_D_PRINTED,
        material_cost=MaterialCost.MEDIUM_COST,
        purpose="freestyle"
    )
    
    print("--- Specification ---")
    spec = design["specification"]
    print(f"Name: {spec.name}")
    print(f"Motor Count: {spec.motor_count}")
    print(f"Motor Size: {spec.motor_size}")
    print(f"Propeller: {spec.propeller_diameter / 25.4:.1f} inches")
    
    print("\n--- Frame Dimensions ---")
    structure = design["structure"]
    print(f"Diagonal Size: {design['diagonal_size_mm']:.0f}mm")
    print(f"Motor-to-Motor: {structure.motor_to_motor_distance:.0f}mm")
    print(f"Arm Length: {structure.arm_length:.0f}mm")
    print(f"Arm Size: {structure.arm_width}x{structure.arm_height}mm")
    
    print("\n--- Weight ---")
    print(f"Frame Weight: {design['frame_weight']:.1f}g")
    print(f"Target Total: {spec.weight_target}g")
    
    print("\n--- Motor Control Demo ---")
    # Example: 50% throttle, pitch forward, roll right
    motors = RotorcraftControlLogic.calculate_motor_outputs(
        throttle=0.5,
        pitch=0.3,
        roll=0.2,
        yaw=0.0
    )
    print("Input: 50% throttle, 30% pitch forward, 20% roll right")
    for i, power in enumerate(motors, 1):
        print(f"  Motor {i}: {power*100:.1f}%")
