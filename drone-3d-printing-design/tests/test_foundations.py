"""
Tests for Phase 0: Python Foundations
"""

import pytest
import math
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from phase0_foundations.basic_concepts import (
    Point3D,
    Vector3D,
    PartProperties,
    calculate_circle_area,
    calculate_rectangle_area,
    generate_mounting_holes,
    calculate_material_volume
)

from phase0_foundations.geometry_calc import (
    GeometryCalculator,
    calculate_motor_mount_dimensions,
    calculate_arm_dimensions,
    calculate_battery_tray,
    calculate_screw_hole_positions,
    calculate_weight_estimate,
    degrees_to_radians,
    radians_to_degrees
)


class TestBasicConcepts:
    """Test basic Python concepts and geometry."""
    
    def test_calculate_circle_area(self):
        """Test circle area calculation."""
        area = calculate_circle_area(10)
        expected = math.pi * 100
        assert abs(area - expected) < 0.01
    
    def test_calculate_rectangle_area(self):
        """Test rectangle area calculation."""
        area = calculate_rectangle_area(20, 15)
        assert area == 300
    
    def test_point3d_distance(self):
        """Test 3D point distance calculation."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(3, 4, 0)
        distance = p1.distance_to(p2)
        assert abs(distance - 5.0) < 0.01
    
    def test_point3d_3d_distance(self):
        """Test 3D point distance in 3D space."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(1, 1, 1)
        distance = p1.distance_to(p2)
        expected = math.sqrt(3)
        assert abs(distance - expected) < 0.01
    
    def test_vector3d_magnitude(self):
        """Test vector magnitude calculation."""
        v = Vector3D(3, 4, 0)
        assert abs(v.magnitude() - 5.0) < 0.01
    
    def test_vector3d_normalize(self):
        """Test vector normalization."""
        v = Vector3D(3, 4, 0)
        normalized = v.normalize()
        assert abs(normalized.magnitude() - 1.0) < 0.01
    
    def test_vector3d_dot_product(self):
        """Test vector dot product."""
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        dot = v1.dot(v2)
        assert abs(dot) < 0.01  # Perpendicular vectors
    
    def test_vector3d_cross_product(self):
        """Test vector cross product."""
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        cross = v1.cross(v2)
        assert abs(cross.x) < 0.01
        assert abs(cross.y) < 0.01
        assert abs(cross.z - 1.0) < 0.01
    
    def test_part_properties(self):
        """Test part properties management."""
        part = PartProperties()
        part.add_property("material", "PLA")
        part.add_property("weight", 25.5)
        
        assert part.get_property("material") == "PLA"
        assert part.get_property("weight") == 25.5
        assert part.get_property("nonexistent", "default") == "default"
    
    def test_generate_mounting_holes(self):
        """Test mounting hole generation."""
        holes = generate_mounting_holes(4, 20, 3)
        assert len(holes) == 4
        
        # Check that holes are evenly spaced (90 degrees apart)
        for i, (x, y) in enumerate(holes):
            radius = math.sqrt(x**2 + y**2)
            assert abs(radius - 20) < 0.01
    
    def test_calculate_material_volume(self):
        """Test hollow cylinder volume calculation."""
        volume = calculate_material_volume(10, 8, 5)
        expected = math.pi * (10**2 - 8**2) * 5
        assert abs(volume - expected) < 0.01


class TestGeometryCalculator:
    """Test geometry calculation utilities."""
    
    def test_cylinder_volume(self):
        """Test cylinder volume calculation."""
        volume = GeometryCalculator.cylinder_volume(10, 20)
        expected = math.pi * 100 * 20
        assert abs(volume - expected) < 0.01
    
    def test_box_volume(self):
        """Test box volume calculation."""
        volume = GeometryCalculator.box_volume(10, 20, 30)
        assert volume == 6000
    
    def test_sphere_volume(self):
        """Test sphere volume calculation."""
        volume = GeometryCalculator.sphere_volume(10)
        expected = (4/3) * math.pi * 1000
        assert abs(volume - expected) < 0.01


class TestMotorMountCalculations:
    """Test motor mount dimension calculations."""
    
    def test_calculate_motor_mount_dimensions(self):
        """Test motor mount dimension calculation."""
        dims = calculate_motor_mount_dimensions(28, wall_thickness=3)
        
        assert dims['motor_diameter'] == 28
        assert dims['mount_diameter'] == 34
        assert dims['mount_radius'] == 17
        assert dims['wall_thickness'] == 3
        assert dims['mounting_holes'] == 4
    
    def test_calculate_motor_mount_default_thickness(self):
        """Test motor mount with default wall thickness."""
        dims = calculate_motor_mount_dimensions(28)
        assert dims['wall_thickness'] == 3.0


class TestArmCalculations:
    """Test drone arm dimension calculations."""
    
    def test_calculate_arm_dimensions(self):
        """Test arm dimension calculation."""
        arm = calculate_arm_dimensions(180, 2205)
        
        assert arm['length'] == 180
        assert arm['motor_size'] == 2205
        assert arm['stator_diameter'] == 22
        assert arm['base_width'] == 32
        assert arm['tip_width'] == 32 * 0.7
    
    def test_calculate_arm_different_motor(self):
        """Test arm calculation with different motor size."""
        arm = calculate_arm_dimensions(220, 2306)
        assert arm['stator_diameter'] == 23
        assert arm['length'] == 220


class TestBatteryTray:
    """Test battery tray calculations."""
    
    def test_calculate_battery_tray(self):
        """Test battery tray dimension calculation."""
        tray = calculate_battery_tray(75, 35, 25, clearance=2)
        
        assert tray['battery_length'] == 75
        assert tray['tray_length'] == 79
        assert tray['tray_width'] == 39
        assert tray['clearance'] == 2


class TestScrewHoles:
    """Test screw hole position calculations."""
    
    def test_calculate_screw_hole_positions(self):
        """Test screw hole position calculation."""
        holes = calculate_screw_hole_positions(50, 40, edge_distance=5)
        
        assert len(holes) == 4
        
        # Check positions
        expected = [
            (-20, -15),  # Bottom-left
            (20, -15),   # Bottom-right
            (20, 15),    # Top-right
            (-20, 15)    # Top-left
        ]
        
        for (x, y), (ex, ey) in zip(holes, expected):
            assert abs(x - ex) < 0.01
            assert abs(y - ey) < 0.01


class TestWeightEstimation:
    """Test weight estimation calculations."""
    
    def test_calculate_weight_estimate_pla(self):
        """Test weight estimation for PLA."""
        weight = calculate_weight_estimate(5000, "PLA", 20)
        assert weight > 0
        assert weight < 10  # Should be a few grams
    
    def test_calculate_weight_estimate_different_materials(self):
        """Test weight estimation for different materials."""
        volume = 5000
        infill = 30
        
        weight_pla = calculate_weight_estimate(volume, "PLA", infill)
        weight_petg = calculate_weight_estimate(volume, "PETG", infill)
        weight_abs = calculate_weight_estimate(volume, "ABS", infill)
        
        # PETG should be slightly heavier than PLA
        assert weight_petg > weight_pla
        # ABS should be lighter than PLA
        assert weight_abs < weight_pla


class TestAngleConversions:
    """Test angle conversion utilities."""
    
    def test_degrees_to_radians(self):
        """Test degree to radian conversion."""
        rad = degrees_to_radians(180)
        assert abs(rad - math.pi) < 0.01
        
        rad = degrees_to_radians(90)
        assert abs(rad - math.pi/2) < 0.01
    
    def test_radians_to_degrees(self):
        """Test radian to degree conversion."""
        deg = radians_to_degrees(math.pi)
        assert abs(deg - 180) < 0.01
        
        deg = radians_to_degrees(math.pi/2)
        assert abs(deg - 90) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
