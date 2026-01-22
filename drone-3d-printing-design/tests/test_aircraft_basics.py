"""
Tests for Phase 1: Aircraft Basics - All Aircraft Types
"""

import pytest
import math
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from phase1_aircraft_basics.aircraft_types import (
    AircraftType,
    BuildMethod,
    MaterialCost,
    FixedWingSpec,
    FlyingWingSpec,
    DeltaWingSpec,
    AutogyroSpec,
    RotorcraftSpec,
    get_aircraft_description,
    get_build_method_info
)

from phase1_aircraft_basics.flying_wing_design import (
    FlyingWingStructure,
    FlyingWingDesignRules,
    FlyingWingControlLogic,
    design_simple_flying_wing
)

from phase1_aircraft_basics.fixed_wing_design import (
    FixedWingStructure,
    FixedWingDesignRules,
    FixedWingControlLogic,
    design_simple_fixed_wing
)

from phase1_aircraft_basics.rotorcraft_design import (
    RotorcraftStructure,
    RotorcraftDesignRules,
    RotorcraftControlLogic,
    design_simple_rotorcraft
)

from phase1_aircraft_basics.autogyro_design import (
    AutogyroStructure,
    AutogyroDesignRules,
    AutogyroControlLogic,
    design_simple_autogyro
)

from phase1_aircraft_basics.delta_wing_design import (
    DeltaWingStructure,
    DeltaWingDesignRules,
    DeltaWingControlLogic,
    design_simple_delta_wing
)


class TestAircraftTypes:
    """Test aircraft type definitions and specifications."""
    
    def test_aircraft_type_enum(self):
        """Test aircraft type enumeration."""
        assert AircraftType.FIXED_WING.value == "fixed_wing"
        assert AircraftType.FLYING_WING.value == "flying_wing"
        assert AircraftType.DELTA_WING.value == "delta_wing"
        assert AircraftType.AUTOGYRO.value == "autogyro"
        assert AircraftType.ROTORCRAFT.value == "rotorcraft"
    
    def test_build_method_enum(self):
        """Test build method enumeration."""
        assert BuildMethod.HAND_BUILT.value == "hand_built"
        assert BuildMethod.THREE_D_PRINTED.value == "3d_printed"
        assert BuildMethod.HYBRID.value == "hybrid"
    
    def test_material_cost_enum(self):
        """Test material cost enumeration."""
        assert MaterialCost.LOW_COST.value == "low_cost"
        assert MaterialCost.MEDIUM_COST.value == "medium_cost"
        assert MaterialCost.HIGH_END.value == "high_end"
    
    def test_aircraft_descriptions(self):
        """Test aircraft description retrieval."""
        desc = get_aircraft_description(AircraftType.FLYING_WING)
        assert "name" in desc
        assert "description" in desc
        assert "advantages" in desc
    
    def test_build_method_info(self):
        """Test build method information."""
        info = get_build_method_info(BuildMethod.HYBRID, MaterialCost.MEDIUM_COST)
        assert "materials" in info
        assert "tools" in info
        assert "estimated_cost" in info
        assert len(info["materials"]) > 0


class TestFlyingWingSpec:
    """Test flying-wing specification."""
    
    def test_create_flying_wing_spec(self):
        """Test creating a flying-wing specification."""
        spec = FlyingWingSpec(
            name="Test Wing",
            build_method=BuildMethod.HYBRID,
            material_cost=MaterialCost.MEDIUM_COST,
            wingspan=1000,
            chord_root=200,
            chord_tip=100,
            weight_target=600
        )
        assert spec.aircraft_type == AircraftType.FLYING_WING
        assert spec.wingspan == 1000
        assert spec.wing_area > 0  # Should be calculated
    
    def test_wing_area_calculation(self):
        """Test automatic wing area calculation."""
        spec = FlyingWingSpec(
            build_method=BuildMethod.HYBRID,
            material_cost=MaterialCost.MEDIUM_COST,
            wingspan=1000,
            chord_root=200,
            chord_tip=100,
            weight_target=600
        )
        expected_area = 1000 * 150  # wingspan * average chord
        assert abs(spec.wing_area - expected_area) < 1


class TestFlyingWingDesign:
    """Test flying-wing design functionality."""
    
    def test_flying_wing_structure(self):
        """Test flying-wing structure creation."""
        structure = FlyingWingStructure(
            wingspan=1000,
            chord_root=200,
            chord_tip=100,
            sweep_angle=25
        )
        assert structure.wing_area > 0
        assert structure.mean_aerodynamic_chord > 0
        assert structure.aspect_ratio > 0
        assert 0 < structure.taper_ratio < 1
    
    def test_design_validation(self):
        """Test design validation."""
        structure = FlyingWingStructure(
            wingspan=1000,
            chord_root=200,
            chord_tip=100,
            sweep_angle=25
        )
        validation = FlyingWingDesignRules.validate_design(structure)
        assert "warnings" in validation
        assert "errors" in validation
        assert isinstance(validation["warnings"], list)
        assert isinstance(validation["errors"], list)
    
    def test_elevon_control(self):
        """Test elevon deflection calculation."""
        left, right = FlyingWingControlLogic.calculate_elevon_deflection(
            pitch_input=0.5,
            roll_input=0.3
        )
        # Left elevon should be pitch + roll
        # Right elevon should be pitch - roll
        assert left > right  # Rolling right
        assert abs(left - right) > 0  # Different deflections
    
    def test_design_simple_flying_wing(self):
        """Test automated flying-wing design."""
        design = design_simple_flying_wing(
            wingspan=1000,
            target_weight=600,
            build_method=BuildMethod.HYBRID,
            material_cost=MaterialCost.MEDIUM_COST
        )
        assert "specification" in design
        assert "structure" in design
        assert "validation" in design
        assert design["estimated_structural_weight"] > 0


class TestFixedWingDesign:
    """Test fixed-wing design functionality."""
    
    def test_fixed_wing_structure(self):
        """Test fixed-wing structure creation."""
        structure = FixedWingStructure(
            wingspan=1200,
            wing_chord=200
        )
        assert structure.wing_area > 0
        assert structure.tail_span > 0  # Auto-calculated
    
    def test_fixed_wing_validation(self):
        """Test fixed-wing validation."""
        structure = FixedWingStructure(
            wingspan=1200,
            wing_chord=200,
            fuselage_length=900
        )
        validation = FixedWingDesignRules.validate_design(structure)
        assert "warnings" in validation
        assert "errors" in validation
    
    def test_control_deflections(self):
        """Test control surface deflections."""
        controls = FixedWingControlLogic.calculate_control_deflections(
            pitch_input=0.5,
            roll_input=0.3,
            yaw_input=0.2
        )
        assert "elevator" in controls
        assert "left_aileron" in controls
        assert "right_aileron" in controls
        assert "rudder" in controls
        # Ailerons should be opposite
        assert controls["left_aileron"] == -controls["right_aileron"]
    
    def test_design_simple_fixed_wing(self):
        """Test automated fixed-wing design."""
        design = design_simple_fixed_wing(
            wingspan=1200,
            target_weight=800,
            build_method=BuildMethod.HYBRID,
            material_cost=MaterialCost.MEDIUM_COST,
            aircraft_purpose="trainer"
        )
        assert "specification" in design
        assert "structure" in design
        assert "cg_limits" in design


class TestRotorcraftDesign:
    """Test rotorcraft design functionality."""
    
    def test_rotorcraft_structure(self):
        """Test rotorcraft structure creation."""
        structure = RotorcraftStructure(
            motor_count=4,
            frame_type="X",
            motor_to_motor_distance=200,
            arm_length=100,
            motor_size=2205
        )
        assert structure.stator_diameter == 22
        assert structure.stator_height == 5
        assert structure.diagonal_size > 0
    
    def test_rotorcraft_validation(self):
        """Test rotorcraft validation."""
        structure = RotorcraftStructure(
            motor_count=4,
            frame_type="X",
            motor_to_motor_distance=200,
            arm_length=100,
            motor_size=2205,
            propeller_diameter=127  # 5 inch
        )
        validation = RotorcraftDesignRules.validate_design(structure)
        assert "warnings" in validation
        assert "errors" in validation
    
    def test_motor_mixing(self):
        """Test motor output calculation."""
        motors = RotorcraftControlLogic.calculate_motor_outputs(
            throttle=0.5,
            pitch=0.2,
            roll=0.1,
            yaw=0.0,
            motor_count=4,
            frame_type="X"
        )
        assert len(motors) == 4
        assert all(0 <= m <= 1 for m in motors)
    
    def test_design_simple_rotorcraft(self):
        """Test automated rotorcraft design."""
        design = design_simple_rotorcraft(
            motor_count=4,
            propeller_size_inch=5.0,
            target_weight=600,
            build_method=BuildMethod.THREE_D_PRINTED,
            material_cost=MaterialCost.MEDIUM_COST
        )
        assert "specification" in design
        assert "structure" in design
        assert "frame_weight" in design


class TestAutogyroDesign:
    """Test autogyro design functionality."""
    
    def test_autogyro_structure(self):
        """Test autogyro structure creation."""
        structure = AutogyroStructure(
            rotor_diameter=800,
            rotor_blade_count=2,
            rotor_rpm=400
        )
        assert structure.rotor_disc_area > 0
        assert structure.rotor_solidity > 0
        assert structure.tip_speed > 0
    
    def test_autogyro_validation(self):
        """Test autogyro validation."""
        structure = AutogyroStructure(
            rotor_diameter=800,
            rotor_blade_count=2
        )
        validation = AutogyroDesignRules.validate_design(structure, 500)
        assert "warnings" in validation
        assert "errors" in validation
    
    def test_autogyro_controls(self):
        """Test autogyro control inputs."""
        controls = AutogyroControlLogic.calculate_control_inputs(
            throttle=0.7,
            cyclic_pitch=-0.3,
            cyclic_roll=0.2,
            rudder=0.1
        )
        assert "propeller_throttle" in controls
        assert "rotor_cyclic_pitch" in controls
        assert "rotor_cyclic_roll" in controls
        assert "rudder_deflection" in controls
    
    def test_design_simple_autogyro(self):
        """Test automated autogyro design."""
        design = design_simple_autogyro(
            rotor_diameter=800,
            target_weight=500,
            build_method=BuildMethod.HYBRID,
            material_cost=MaterialCost.MEDIUM_COST
        )
        assert "specification" in design
        assert "structure" in design
        assert "rotor_rpm" in design
        assert "disc_loading_kg_m2" in design


class TestDeltaWingSpec:
    """Test delta-wing specification."""
    
    def test_create_delta_wing_spec(self):
        """Test creating a delta-wing specification."""
        spec = DeltaWingSpec(
            name="Test Delta",
            build_method=BuildMethod.THREE_D_PRINTED,
            material_cost=MaterialCost.MEDIUM_COST,
            wingspan=1000,
            chord_root=350,
            sweep_angle=55,
            weight_target=550
        )
        assert spec.name == "Test Delta"
        assert spec.aircraft_type == AircraftType.DELTA_WING
        assert spec.wingspan == 1000
        assert spec.sweep_angle == 55
        # Wing area should be calculated (triangular planform)
        assert spec.wing_area > 0
    
    def test_delta_wing_area_calculation(self):
        """Test automatic wing area calculation for delta wing."""
        spec = DeltaWingSpec(
            name="Area Test",
            build_method=BuildMethod.THREE_D_PRINTED,
            material_cost=MaterialCost.LOW_COST,
            wingspan=1000,
            chord_root=400,
            sweep_angle=50,
            weight_target=500
        )
        # For delta: area = 0.5 * wingspan * chord_root
        expected_area = 0.5 * 1000 * 400
        assert abs(spec.wing_area - expected_area) < 1


class TestDeltaWingDesign:
    """Test delta-wing design functionality."""
    
    def test_delta_wing_structure(self):
        """Test delta-wing structure creation."""
        structure = DeltaWingStructure(
            wingspan=1000,
            chord_root=350,
            sweep_angle=55,
            thickness_ratio=0.06
        )
        assert structure.wingspan == 1000
        assert structure.wing_area > 0
        assert structure.aspect_ratio > 0
        assert structure.mean_aerodynamic_chord > 0
        # MAC for pure delta should be 2/3 of root chord
        expected_mac = (2.0 / 3.0) * structure.chord_root
        assert abs(structure.mean_aerodynamic_chord - expected_mac) < 1
    
    def test_delta_wing_aspect_ratio(self):
        """Test aspect ratio calculation."""
        structure = DeltaWingStructure(
            wingspan=1000,
            chord_root=350,
            sweep_angle=55
        )
        # AR = wingspan^2 / area
        expected_ar = (1000 ** 2) / structure.wing_area
        assert abs(structure.aspect_ratio - expected_ar) < 0.1
    
    def test_delta_wing_validation(self):
        """Test delta-wing design validation."""
        structure = DeltaWingStructure(
            wingspan=1000,
            chord_root=350,
            sweep_angle=55
        )
        validation = DeltaWingDesignRules.validate_design(structure)
        assert "warnings" in validation
        assert "errors" in validation
        assert isinstance(validation["warnings"], list)
        assert isinstance(validation["errors"], list)
    
    def test_delta_wing_vortex_lift(self):
        """Test vortex lift coefficient calculation."""
        # At low AoA, vortex lift should be minimal
        cl_vortex_low = DeltaWingDesignRules.calculate_vortex_lift_coefficient(
            angle_of_attack=5,
            sweep_angle=55
        )
        assert cl_vortex_low >= 0
        assert cl_vortex_low < 0.01
        
        # At high AoA, vortex lift should be significant
        cl_vortex_high = DeltaWingDesignRules.calculate_vortex_lift_coefficient(
            angle_of_attack=25,
            sweep_angle=55
        )
        assert cl_vortex_high > 0.05
        assert cl_vortex_high > cl_vortex_low
    
    def test_delta_wing_total_lift(self):
        """Test total lift coefficient calculation."""
        cl_total = DeltaWingDesignRules.calculate_total_lift_coefficient(
            angle_of_attack=20,
            sweep_angle=55,
            aspect_ratio=2.5
        )
        assert cl_total > 0
        # Should be reasonable value (not exceeding ~2.0)
        assert cl_total <= 2.0
    
    def test_delta_wing_structural_weight(self):
        """Test structural weight estimation."""
        structure = DeltaWingStructure(
            wingspan=1000,
            chord_root=350,
            sweep_angle=55
        )
        weight = DeltaWingDesignRules.calculate_structural_weight(
            structure,
            material_density=1.24  # PLA
        )
        assert weight > 0
        # Should be reasonable for this size
        assert 200 < weight < 1000


class TestDeltaWingControl:
    """Test delta-wing control logic."""
    
    def test_elevon_deflection(self):
        """Test elevon deflection calculation."""
        left, right = DeltaWingControlLogic.calculate_elevon_deflection(
            pitch_input=0.5,
            roll_input=0.0,
            max_deflection=25
        )
        # Pure pitch - both elevons should deflect equally
        assert left == right
        assert abs(left - 12.5) < 0.1  # 50% of 25 degrees
    
    def test_elevon_roll_control(self):
        """Test elevon roll control."""
        left, right = DeltaWingControlLogic.calculate_elevon_deflection(
            pitch_input=0.0,
            roll_input=0.5,
            max_deflection=25
        )
        # Pure roll - elevons should deflect opposite
        assert left == -right
        assert abs(left - 12.5) < 0.1
    
    def test_elevon_mixed_control(self):
        """Test elevon mixed pitch and roll."""
        left, right = DeltaWingControlLogic.calculate_elevon_deflection(
            pitch_input=0.5,
            roll_input=0.3,
            max_deflection=25
        )
        # Mixed control
        assert left != right  # Should be different
        assert abs(left) <= 25  # Within limits
        assert abs(right) <= 25
    
    def test_yaw_from_roll_coupling(self):
        """Test roll-yaw coupling (proverse yaw)."""
        yaw_rate = DeltaWingControlLogic.calculate_yaw_from_roll(
            roll_input=0.5,
            speed=10,
            coupling_factor=0.3
        )
        assert yaw_rate > 0  # Positive roll should induce yaw
    
    def test_high_alpha_control_normal(self):
        """Test control at normal AoA."""
        result = DeltaWingControlLogic.calculate_high_alpha_control(
            angle_of_attack=15,
            pitch_input=0.5
        )
        assert result["flight_regime"] == "normal"
        assert result["control_effectiveness"] == 1.0
    
    def test_high_alpha_control_vortex(self):
        """Test control at high AoA with vortex lift."""
        result = DeltaWingControlLogic.calculate_high_alpha_control(
            angle_of_attack=25,
            pitch_input=0.5
        )
        assert result["flight_regime"] == "high_alpha"
        assert 0 < result["control_effectiveness"] < 1
    
    def test_high_alpha_control_post_burst(self):
        """Test control post vortex burst."""
        result = DeltaWingControlLogic.calculate_high_alpha_control(
            angle_of_attack=37,
            pitch_input=0.5
        )
        assert result["flight_regime"] == "post_stall"
        assert result["control_effectiveness"] < 0.5
        assert len(result["warnings"]) > 0
    
    def test_cg_effect(self):
        """Test CG effect calculation."""
        result = DeltaWingControlLogic.calculate_cg_effect(
            current_cg=0.35,
            target_cg=0.35,
            mac=250
        )
        assert result["status"] == "OPTIMAL"
        assert abs(result["difference_mm"]) < 1
    
    def test_design_simple_delta_wing(self):
        """Test automated delta-wing design."""
        design = design_simple_delta_wing(
            wingspan=1000,
            target_weight=550,
            build_method=BuildMethod.THREE_D_PRINTED,
            material_cost=MaterialCost.MEDIUM_COST,
            sweep_angle=55
        )
        assert "specification" in design
        assert "structure" in design
        assert "validation" in design
        assert "wing_area_dm2" in design
        assert "wing_loading_g_dm2" in design
        assert "estimated_stall_speed_ms" in design
        
        # Check that calculations are reasonable
        spec = design["specification"]
        assert spec.aircraft_type == AircraftType.DELTA_WING
        assert design["aspect_ratio"] > 0
        assert design["estimated_structural_weight"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
