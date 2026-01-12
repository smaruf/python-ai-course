"""Phase 0: Python Foundations"""

from .basic_concepts import (
    Point3D,
    Vector3D,
    PartProperties,
    calculate_circle_area,
    calculate_rectangle_area,
    generate_mounting_holes,
    calculate_material_volume
)

from .geometry_calc import (
    GeometryCalculator,
    calculate_motor_mount_dimensions,
    calculate_arm_dimensions,
    calculate_battery_tray,
    calculate_screw_hole_positions,
    calculate_weight_estimate,
    degrees_to_radians,
    radians_to_degrees
)

__all__ = [
    'Point3D',
    'Vector3D',
    'PartProperties',
    'GeometryCalculator',
    'calculate_circle_area',
    'calculate_rectangle_area',
    'generate_mounting_holes',
    'calculate_material_volume',
    'calculate_motor_mount_dimensions',
    'calculate_arm_dimensions',
    'calculate_battery_tray',
    'calculate_screw_hole_positions',
    'calculate_weight_estimate',
    'degrees_to_radians',
    'radians_to_degrees'
]
