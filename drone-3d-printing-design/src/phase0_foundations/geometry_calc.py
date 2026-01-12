"""
Phase 0: Python Foundations - Geometry Calculations

This module provides geometry calculations commonly used in drone part design.
"""

import math
from typing import Tuple, List


class GeometryCalculator:
    """Helper class for common geometry calculations."""
    
    @staticmethod
    def circle_circumference(radius: float) -> float:
        """Calculate circumference of a circle."""
        return 2 * math.pi * radius
    
    @staticmethod
    def cylinder_volume(radius: float, height: float) -> float:
        """Calculate volume of a cylinder."""
        return math.pi * radius ** 2 * height
    
    @staticmethod
    def cylinder_surface_area(radius: float, height: float) -> float:
        """Calculate surface area of a cylinder."""
        lateral_area = 2 * math.pi * radius * height
        end_areas = 2 * math.pi * radius ** 2
        return lateral_area + end_areas
    
    @staticmethod
    def box_volume(length: float, width: float, height: float) -> float:
        """Calculate volume of a box."""
        return length * width * height
    
    @staticmethod
    def sphere_volume(radius: float) -> float:
        """Calculate volume of a sphere."""
        return (4/3) * math.pi * radius ** 3
    
    @staticmethod
    def cone_volume(radius: float, height: float) -> float:
        """Calculate volume of a cone."""
        return (1/3) * math.pi * radius ** 2 * height


def calculate_motor_mount_dimensions(
    motor_diameter: float,
    wall_thickness: float = 3.0,
    mounting_holes: int = 4
) -> dict:
    """
    Calculate dimensions for a motor mount.
    
    Args:
        motor_diameter: Diameter of the motor
        wall_thickness: Thickness of the mount wall
        mounting_holes: Number of mounting holes
    
    Returns:
        Dictionary with calculated dimensions
    """
    mount_diameter = motor_diameter + 2 * wall_thickness
    mount_radius = mount_diameter / 2
    hole_circle_radius = mount_radius + 5  # 5mm beyond mount edge
    
    return {
        'motor_diameter': motor_diameter,
        'mount_diameter': mount_diameter,
        'mount_radius': mount_radius,
        'wall_thickness': wall_thickness,
        'hole_circle_radius': hole_circle_radius,
        'mounting_holes': mounting_holes
    }


def calculate_arm_dimensions(
    arm_length: float,
    motor_size: int,
    thickness: float = 4.0
) -> dict:
    """
    Calculate dimensions for a drone arm.
    
    Args:
        arm_length: Length of the arm in mm
        motor_size: Motor size (e.g., 2205, 2306)
        thickness: Arm thickness in mm
    
    Returns:
        Dictionary with calculated dimensions
    """
    # Motor size encoding: XXYY where XX is stator diameter, YY is height
    stator_diameter = (motor_size // 100)
    
    # Width should accommodate motor and provide mounting
    width = stator_diameter + 10
    
    # Calculate taper (wider at base, narrower at tip)
    base_width = width
    tip_width = width * 0.7  # 70% of base width
    
    # Calculate weight estimate (rough)
    avg_width = (base_width + tip_width) / 2
    volume = arm_length * avg_width * thickness  # mm³
    
    return {
        'length': arm_length,
        'base_width': base_width,
        'tip_width': tip_width,
        'thickness': thickness,
        'volume': volume,
        'motor_size': motor_size,
        'stator_diameter': stator_diameter
    }


def calculate_battery_tray(
    battery_length: float,
    battery_width: float,
    battery_height: float,
    clearance: float = 2.0
) -> dict:
    """
    Calculate dimensions for a battery tray.
    
    Args:
        battery_length: Length of battery
        battery_width: Width of battery
        battery_height: Height of battery
        clearance: Clearance around battery
    
    Returns:
        Dictionary with tray dimensions
    """
    tray_length = battery_length + 2 * clearance
    tray_width = battery_width + 2 * clearance
    tray_depth = battery_height * 0.6  # Hold 60% of battery height
    wall_thickness = 2.0
    
    return {
        'battery_length': battery_length,
        'battery_width': battery_width,
        'battery_height': battery_height,
        'tray_length': tray_length,
        'tray_width': tray_width,
        'tray_depth': tray_depth,
        'wall_thickness': wall_thickness,
        'clearance': clearance
    }


def calculate_screw_hole_positions(
    width: float,
    height: float,
    edge_distance: float = 5.0
) -> List[Tuple[float, float]]:
    """
    Calculate positions for corner screw holes.
    
    Args:
        width: Width of the part
        height: Height of the part
        edge_distance: Distance from edge to hole center
    
    Returns:
        List of (x, y) coordinates for holes
    """
    half_width = width / 2
    half_height = height / 2
    
    positions = [
        (-half_width + edge_distance, -half_height + edge_distance),  # Bottom-left
        (half_width - edge_distance, -half_height + edge_distance),   # Bottom-right
        (half_width - edge_distance, half_height - edge_distance),    # Top-right
        (-half_width + edge_distance, half_height - edge_distance)    # Top-left
    ]
    
    return positions


def calculate_weight_estimate(
    volume_mm3: float,
    material: str = "PLA",
    infill_percent: float = 20
) -> float:
    """
    Estimate weight of a 3D printed part.
    
    Args:
        volume_mm3: Volume in cubic millimeters
        material: Material type
        infill_percent: Infill percentage (0-100)
    
    Returns:
        Weight in grams
    """
    # Material densities in g/cm³
    densities = {
        'PLA': 1.24,
        'PLA+': 1.24,
        'PETG': 1.27,
        'ABS': 1.04,
        'Nylon': 1.14,
        'TPU': 1.21
    }
    
    density = densities.get(material, 1.24)  # Default to PLA
    
    # Convert mm³ to cm³
    volume_cm3 = volume_mm3 / 1000
    
    # Account for infill (simplified model)
    # Assume 2 perimeters (shells) = ~40% of volume
    shell_volume = volume_cm3 * 0.4
    infill_volume = volume_cm3 * 0.6 * (infill_percent / 100)
    
    effective_volume = shell_volume + infill_volume
    weight = effective_volume * density
    
    return weight


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180 / math.pi


# Example usage
if __name__ == "__main__":
    print("=== Phase 0: Geometry Calculations ===\n")
    
    # Example 1: Motor mount
    print("1. Motor Mount Dimensions:")
    motor_mount = calculate_motor_mount_dimensions(28)
    for key, value in motor_mount.items():
        print(f"   {key}: {value}")
    
    # Example 2: Drone arm
    print("\n2. Drone Arm Dimensions:")
    arm = calculate_arm_dimensions(180, 2205)
    for key, value in arm.items():
        print(f"   {key}: {value:.2f}")
    
    # Example 3: Battery tray
    print("\n3. Battery Tray Dimensions:")
    tray = calculate_battery_tray(75, 35, 25)
    for key, value in tray.items():
        print(f"   {key}: {value:.2f}")
    
    # Example 4: Weight estimate
    print("\n4. Weight Estimate:")
    volume = 5000  # 5000 mm³
    weight_pla = calculate_weight_estimate(volume, "PLA", 20)
    weight_petg = calculate_weight_estimate(volume, "PETG", 20)
    print(f"   Volume: {volume} mm³")
    print(f"   Weight (PLA, 20% infill): {weight_pla:.2f}g")
    print(f"   Weight (PETG, 20% infill): {weight_petg:.2f}g")
    
    # Example 5: Screw holes
    print("\n5. Screw Hole Positions:")
    holes = calculate_screw_hole_positions(50, 40)
    for i, (x, y) in enumerate(holes):
        print(f"   Hole {i+1}: x={x:.1f}, y={y:.1f}")
