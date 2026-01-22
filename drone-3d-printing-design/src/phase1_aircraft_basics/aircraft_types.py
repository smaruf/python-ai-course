"""
Phase 1: Aircraft Types and Basic Definitions

This module defines the different types of aircraft that can be designed:
- Fixed-wing
- Flying-wing
- Delta-wing
- Autogyro
- Rotorcraft (multirotor)
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field


class AircraftType(Enum):
    """Types of aircraft supported by the design system."""
    FIXED_WING = "fixed_wing"
    FLYING_WING = "flying_wing"
    DELTA_WING = "delta_wing"
    AUTOGYRO = "autogyro"
    ROTORCRAFT = "rotorcraft"


class BuildMethod(Enum):
    """Methods for building aircraft."""
    HAND_BUILT = "hand_built"  # Built by hand with traditional materials
    THREE_D_PRINTED = "3d_printed"  # 3D printed parts
    HYBRID = "hybrid"  # Combination of both


class MaterialCost(Enum):
    """Material cost categories."""
    LOW_COST = "low_cost"  # Budget materials (foam, balsa, basic PLA)
    MEDIUM_COST = "medium_cost"  # Mid-range materials (PETG, lite-ply, carbon tubes)
    HIGH_END = "high_end"  # Premium materials (carbon fiber, nylon, advanced composites)


@dataclass
class AircraftSpecification:
    """Base specification for aircraft design."""
    build_method: BuildMethod
    material_cost: MaterialCost
    wingspan: float  # mm
    weight_target: float  # grams
    aircraft_type: AircraftType = None  # Set by subclasses
    name: str = "Unnamed Aircraft"
    description: str = ""
    
    def __post_init__(self):
        """Validate specifications."""
        if self.wingspan <= 0:
            raise ValueError("Wingspan must be positive")
        if self.weight_target <= 0:
            raise ValueError("Weight target must be positive")


@dataclass
class FixedWingSpec(AircraftSpecification):
    """Specification for fixed-wing aircraft."""
    fuselage_length: float = 0  # mm
    wing_area: float = 0  # mm²
    tail_span: float = 0  # mm
    chord_length: float = 0  # mm (average)
    dihedral_angle: float = 0  # degrees
    sweep_angle: float = 0  # degrees
    
    def __post_init__(self):
        """Initialize and calculate missing values."""
        super().__post_init__()
        self.aircraft_type = AircraftType.FIXED_WING
        
        # Calculate wing area if not provided
        if self.wing_area == 0 and self.chord_length > 0:
            self.wing_area = self.wingspan * self.chord_length


@dataclass
class FlyingWingSpec(AircraftSpecification):
    """Specification for flying-wing aircraft."""
    chord_root: float = 0  # mm (root chord)
    chord_tip: float = 0  # mm (tip chord)
    sweep_angle: float = 20  # degrees (typical for flying wings)
    wing_area: float = 0  # mm²
    center_of_gravity: float = 0.25  # ratio from leading edge (25% is typical)
    elevon_size: float = 0  # mm² (control surface area)
    thickness_ratio: float = 0.12  # airfoil thickness to chord ratio
    
    def __post_init__(self):
        """Initialize and calculate missing values."""
        super().__post_init__()
        self.aircraft_type = AircraftType.FLYING_WING
        
        # Calculate average chord
        avg_chord = (self.chord_root + self.chord_tip) / 2
        
        # Calculate wing area if not provided
        if self.wing_area == 0 and avg_chord > 0:
            self.wing_area = self.wingspan * avg_chord


@dataclass
class DeltaWingSpec(AircraftSpecification):
    """Specification for delta-wing aircraft."""
    chord_root: float = 0  # mm (root chord at fuselage)
    chord_tip: float = 0  # mm (tip chord, often very small or zero)
    sweep_angle: float = 45  # degrees (leading edge sweep, typical 40-60° for delta)
    wing_area: float = 0  # mm²
    center_of_gravity: float = 0.35  # ratio from apex (35-40% is typical for delta)
    control_surface_type: str = "elevons"  # elevons or canards
    vertical_tail: bool = True  # Most deltas have vertical stabilizers
    aspect_ratio_target: float = 2.0  # Low aspect ratio typical for deltas
    thickness_ratio: float = 0.06  # Thin airfoil typical for delta wings
    
    def __post_init__(self):
        """Initialize and calculate missing values."""
        super().__post_init__()
        self.aircraft_type = AircraftType.DELTA_WING
        
        # Calculate wing area if not provided (triangular/delta planform)
        # For delta wing: Area = 0.5 * wingspan * root_chord
        if self.wing_area == 0 and self.chord_root > 0:
            self.wing_area = 0.5 * self.wingspan * self.chord_root


@dataclass
class AutogyroSpec(AircraftSpecification):
    """Specification for autogyro aircraft."""
    rotor_diameter: float = 0  # mm
    rotor_blade_count: int = 2
    blade_chord: float = 0  # mm
    fuselage_length: float = 0  # mm
    propeller_diameter: float = 0  # mm (forward thrust)
    tail_surface_area: float = 0  # mm²
    
    def __post_init__(self):
        """Initialize specification."""
        super().__post_init__()
        self.aircraft_type = AircraftType.AUTOGYRO
        # For autogyro, wingspan is rotor diameter
        if self.rotor_diameter > 0:
            self.wingspan = self.rotor_diameter


@dataclass
class RotorcraftSpec(AircraftSpecification):
    """Specification for rotorcraft (multirotor/drone)."""
    motor_count: int = 4  # 4 = quadcopter, 6 = hexacopter, 8 = octocopter
    motor_to_motor_distance: float = 0  # mm
    motor_size: int = 2205  # motor stator size (e.g., 2205, 2306)
    arm_length: float = 0  # mm
    frame_type: str = "X"  # X, H, +, etc.
    propeller_diameter: float = 0  # mm
    
    def __post_init__(self):
        """Initialize and calculate missing values."""
        super().__post_init__()
        self.aircraft_type = AircraftType.ROTORCRAFT
        
        # Calculate wingspan (motor to motor diagonal)
        if self.wingspan == 0 and self.motor_to_motor_distance > 0:
            import math
            if self.frame_type == "X":
                # Diagonal distance for X frame
                self.wingspan = self.motor_to_motor_distance * math.sqrt(2)
            else:
                self.wingspan = self.motor_to_motor_distance


def get_aircraft_description(aircraft_type: AircraftType) -> Dict[str, str]:
    """
    Get a description of an aircraft type.
    
    Args:
        aircraft_type: The type of aircraft
    
    Returns:
        Dictionary with description and characteristics
    """
    descriptions = {
        AircraftType.FIXED_WING: {
            "name": "Fixed-Wing Aircraft",
            "description": "Traditional aircraft with separate wing and fuselage. "
                          "Includes tail surfaces for stability and control.",
            "advantages": "Efficient cruise flight, long endurance, stable platform",
            "disadvantages": "Requires runway or launcher, harder to hover",
            "typical_uses": "Long-range missions, aerial mapping, FPV cruising",
            "key_components": "Wing, fuselage, tail (horizontal and vertical), control surfaces"
        },
        AircraftType.FLYING_WING: {
            "name": "Flying-Wing Aircraft",
            "description": "Aircraft with no separate fuselage or tail. "
                          "All components integrated into the wing structure.",
            "advantages": "Low drag, high efficiency, sleek design, good stealth",
            "disadvantages": "More challenging to design and control, less stable",
            "typical_uses": "Long-range FPV, aerial photography, racing",
            "key_components": "Main wing structure, elevons (combined elevator and ailerons), "
                             "integrated fuselage bay"
        },
        AircraftType.DELTA_WING: {
            "name": "Delta-Wing Aircraft",
            "description": "Triangular wing planform with high sweep angle. "
                          "Inspired by supersonic fighters, adapted for RC/FPV use.",
            "advantages": "High speed capability, excellent high-alpha performance, stable at speed, "
                         "simple structure, good roll rate",
            "disadvantages": "High drag at low speed, higher landing speed, less efficient cruise, "
                            "larger wing area needed",
            "typical_uses": "High-speed FPV, aerobatic flying, scale military models, jet-powered aircraft",
            "key_components": "Triangular wing with high sweep, elevons or trailing edge controls, "
                             "vertical stabilizer(s), often includes canards for pitch control"
        },
        AircraftType.AUTOGYRO: {
            "name": "Autogyro (Gyroplane)",
            "description": "Aircraft with unpowered rotor for lift and powered propeller for thrust. "
                          "Rotor spins freely due to airflow.",
            "advantages": "Short takeoff, can't stall, simple mechanics, stable flight",
            "disadvantages": "Cannot hover, complex rotor mechanics, less common",
            "typical_uses": "Experimental projects, unique flight characteristics, education",
            "key_components": "Free-spinning rotor, forward propeller/motor, fuselage, tail"
        },
        AircraftType.ROTORCRAFT: {
            "name": "Rotorcraft (Multirotor/Drone)",
            "description": "Aircraft with multiple powered rotors for vertical flight. "
                          "Most common: quadcopter (4 rotors), hexacopter (6), octocopter (8).",
            "advantages": "VTOL capability, stable hover, easy to control, highly maneuverable",
            "disadvantages": "Limited endurance, complex electronics, vibration issues",
            "typical_uses": "Aerial photography, racing, inspection, delivery",
            "key_components": "Motors, propellers, arms, frame, flight controller, ESCs"
        }
    }
    
    return descriptions.get(aircraft_type, {})


def get_build_method_info(build_method: BuildMethod, material_cost: MaterialCost) -> Dict[str, any]:
    """
    Get information about build methods and materials.
    
    Args:
        build_method: The method of construction
        material_cost: Cost category of materials
    
    Returns:
        Dictionary with materials, tools, and cost information
    """
    info = {
        "build_method": build_method.value,
        "material_cost": material_cost.value,
        "materials": [],
        "tools": [],
        "estimated_cost": "",
        "difficulty": "",
        "build_time": ""
    }
    
    # Hand-built options
    if build_method == BuildMethod.HAND_BUILT:
        if material_cost == MaterialCost.LOW_COST:
            info["materials"] = [
                "EPP/EPO foam (cheap, durable)",
                "Balsa wood",
                "Carbon fiber rods (3mm-6mm)",
                "Hot glue, CA glue",
                "Packing tape for reinforcement"
            ]
            info["tools"] = ["Hot wire cutter", "Hobby knife", "Ruler", "Sandpaper"]
            info["estimated_cost"] = "$10-$30"
            info["difficulty"] = "Beginner-friendly"
            info["build_time"] = "2-4 hours"
        elif material_cost == MaterialCost.MEDIUM_COST:
            info["materials"] = [
                "Depron foam sheets",
                "Lite-ply or aircraft plywood",
                "Carbon fiber tubes and sheets",
                "Fiberglass cloth",
                "Epoxy resin"
            ]
            info["tools"] = ["Hot wire cutter", "Dremel tool", "Clamps", "Mixing tools"]
            info["estimated_cost"] = "$50-$150"
            info["difficulty"] = "Intermediate"
            info["build_time"] = "8-16 hours"
        else:  # HIGH_END
            info["materials"] = [
                "Carbon fiber prepreg",
                "Kevlar reinforcement",
                "Advanced composites",
                "Vacuum bagging materials",
                "Premium epoxy systems"
            ]
            info["tools"] = ["Vacuum pump", "Heat gun", "Advanced layup tools"]
            info["estimated_cost"] = "$200-$500+"
            info["difficulty"] = "Advanced"
            info["build_time"] = "20-40 hours"
    
    # 3D printed options
    elif build_method == BuildMethod.THREE_D_PRINTED:
        if material_cost == MaterialCost.LOW_COST:
            info["materials"] = [
                "PLA filament (basic, cheap)",
                "PLA+ (stronger variant)",
                "Basic support material"
            ]
            info["tools"] = ["FDM 3D printer (budget)", "Calipers", "File/sandpaper"]
            info["estimated_cost"] = "$20-$50"
            info["difficulty"] = "Beginner (if familiar with 3D printing)"
            info["build_time"] = "4-8 hours (print) + 1-2 hours (assembly)"
        elif material_cost == MaterialCost.MEDIUM_COST:
            info["materials"] = [
                "PETG filament (stronger, flexible)",
                "TPU for flexible parts",
                "Carbon fiber PLA/PETG",
                "Support material (PVA/HIPS)"
            ]
            info["tools"] = ["Quality FDM printer", "Post-processing tools", "Acetone (for ABS)"]
            info["estimated_cost"] = "$80-$200"
            info["difficulty"] = "Intermediate"
            info["build_time"] = "8-16 hours (print) + 2-4 hours (assembly)"
        else:  # HIGH_END
            info["materials"] = [
                "Nylon filament (high strength)",
                "Carbon fiber reinforced nylon",
                "PC (polycarbonate) for extreme strength",
                "ASA for UV resistance"
            ]
            info["tools"] = [
                "High-temp FDM printer (enclosure required)",
                "Drying chamber for filament",
                "Advanced post-processing"
            ]
            info["estimated_cost"] = "$150-$400"
            info["difficulty"] = "Advanced"
            info["build_time"] = "12-24 hours (print) + 4-6 hours (assembly)"
    
    # Hybrid approach
    else:  # HYBRID
        info["materials"] = [
            "Combination of 3D printed connectors and hand-built surfaces",
            "3D printed: motor mounts, frame connectors, hinges",
            "Hand-built: wings, fuselage (foam/balsa)"
        ]
        info["tools"] = ["3D printer", "Hand tools", "Adhesives"]
        info["estimated_cost"] = "$40-$250 (depending on mix)"
        info["difficulty"] = "Intermediate"
        info["build_time"] = "6-20 hours"
    
    return info


# Example usage
if __name__ == "__main__":
    print("=== Aircraft Types Demo ===\n")
    
    # Display information for each aircraft type
    for aircraft_type in AircraftType:
        desc = get_aircraft_description(aircraft_type)
        print(f"{'='*60}")
        print(f"{desc.get('name', 'Unknown')}")
        print(f"{'='*60}")
        print(f"Description: {desc.get('description', 'N/A')}")
        print(f"Advantages: {desc.get('advantages', 'N/A')}")
        print(f"Disadvantages: {desc.get('disadvantages', 'N/A')}")
        print(f"Typical Uses: {desc.get('typical_uses', 'N/A')}")
        print(f"Key Components: {desc.get('key_components', 'N/A')}")
        print()
    
    # Example: Flying wing specification
    print("=== Example: Flying Wing Specification ===\n")
    flying_wing = FlyingWingSpec(
        name="FPV Flying Wing",
        build_method=BuildMethod.HYBRID,
        material_cost=MaterialCost.MEDIUM_COST,
        wingspan=1000,  # 1000mm = 1 meter
        chord_root=200,  # 200mm root chord
        chord_tip=100,   # 100mm tip chord
        weight_target=600,  # 600 grams
        sweep_angle=25,
        description="Fast FPV flying wing for long-range cruising"
    )
    
    print(f"Aircraft: {flying_wing.name}")
    print(f"Type: {flying_wing.aircraft_type.value}")
    print(f"Wingspan: {flying_wing.wingspan}mm")
    print(f"Wing Area: {flying_wing.wing_area}mm²")
    print(f"Weight Target: {flying_wing.weight_target}g")
    print(f"Build Method: {flying_wing.build_method.value}")
    print(f"Material Cost: {flying_wing.material_cost.value}")
    print()
    
    # Build method info
    build_info = get_build_method_info(flying_wing.build_method, flying_wing.material_cost)
    print("Build Information:")
    print(f"  Estimated Cost: {build_info['estimated_cost']}")
    print(f"  Difficulty: {build_info['difficulty']}")
    print(f"  Build Time: {build_info['build_time']}")
    print(f"  Materials: {', '.join(build_info['materials'][:3])}")
