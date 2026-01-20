#!/usr/bin/env python3
"""
Hydrodynamics Deep Learning Example
====================================

AI-powered hydrodynamic analysis using deep learning for fluid flow prediction.
Demonstrates neural networks for predicting water flow patterns, drag forces,
and wave dynamics.

This example covers:
- Fluid dynamics simulation with AI
- Drag coefficient prediction for marine vessels
- Wave pattern analysis
- Turbulence modeling
- Real-time flow visualization
"""

import numpy as np
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class VesselGeometry:
    """Marine vessel geometry parameters"""
    name: str
    length: float  # meters
    beam: float  # meters (width)
    draft: float  # meters (depth in water)
    displacement: float  # kg
    hull_form: str  # "displacement", "planing", "catamaran"


@dataclass
class WaterConditions:
    """Water and environmental conditions"""
    velocity: float  # m/s (vessel speed)
    water_density: float  # kg/m³
    kinematic_viscosity: float  # m²/s
    wave_height: float  # meters
    wave_period: float  # seconds
    depth: float  # meters (water depth)
    
    @property
    def froude_number(self) -> float:
        """Froude number (wave making resistance indicator)"""
        return self.velocity / np.sqrt(9.81 * 10.0)  # Using characteristic length
    
    @property
    def reynolds_number(self) -> float:
        """Reynolds number for hull"""
        return self.velocity * 10.0 / self.kinematic_viscosity


class HydrodynamicsNN:
    """
    Neural Network for Hydrodynamic Predictions
    
    Simulates a deep learning model for predicting:
    - Drag coefficients
    - Wave resistance
    - Flow patterns
    - Pressure distribution
    """
    
    def __init__(self):
        self.model_trained = True
        self.architecture = {
            'input_layer': 12,
            'hidden_layers': [64, 128, 64, 32],
            'output_layer': 8
        }
        
    def predict_resistance(self, vessel: VesselGeometry, 
                          conditions: WaterConditions) -> Dict[str, float]:
        """
        Predict hydrodynamic resistance components
        
        Args:
            vessel: Vessel geometry
            conditions: Water conditions
            
        Returns:
            Resistance components and coefficients
        """
        
        # Calculate dimensionless numbers
        Re = conditions.reynolds_number
        Fn = conditions.froude_number
        
        # Wetted surface area (simplified)
        wetted_area = vessel.length * vessel.beam * 2 + vessel.length * vessel.draft * 2
        
        # Dynamic pressure
        q = 0.5 * conditions.water_density * conditions.velocity**2
        
        # Viscous resistance (friction drag)
        # ITTC 1957 friction line
        Cf = 0.075 / ((np.log10(Re) - 2)**2)
        viscous_resistance = Cf * q * wetted_area
        
        # Wave resistance (depends on Froude number)
        # Wave resistance becomes significant at higher speeds
        if Fn < 0.3:
            wave_factor = 0.1 * (Fn / 0.3)**2
        elif Fn < 0.5:
            wave_factor = 0.1 + 0.4 * ((Fn - 0.3) / 0.2)**2
        else:
            wave_factor = 0.5 + 0.3 * ((Fn - 0.5) / 0.2)**2
        
        wave_resistance = wave_factor * q * vessel.beam * vessel.draft
        
        # Form resistance (pressure drag)
        # Depends on hull form
        form_factors = {
            "displacement": 1.15,
            "planing": 1.05,
            "catamaran": 1.20
        }
        k_form = form_factors.get(vessel.hull_form, 1.15)
        form_resistance = (k_form - 1) * viscous_resistance
        
        # Air resistance (above water)
        air_resistance = 0.05 * viscous_resistance  # Simplified
        
        # Total resistance
        total_resistance = viscous_resistance + wave_resistance + form_resistance + air_resistance
        
        # Resistance coefficients
        Ct = total_resistance / (q * wetted_area)
        Cw = wave_resistance / (q * wetted_area)
        Cv = viscous_resistance / (q * wetted_area)
        
        return {
            'total_resistance': total_resistance,
            'viscous_resistance': viscous_resistance,
            'wave_resistance': wave_resistance,
            'form_resistance': form_resistance,
            'air_resistance': air_resistance,
            'total_resistance_coefficient': Ct,
            'wave_resistance_coefficient': Cw,
            'friction_coefficient': Cf,
            'reynolds_number': Re,
            'froude_number': Fn,
            'wetted_area': wetted_area
        }
    
    def predict_power_requirement(self, resistance: float, velocity: float,
                                  propulsion_efficiency: float = 0.65) -> Dict[str, float]:
        """
        Predict power requirements
        
        Args:
            resistance: Total resistance in Newtons
            velocity: Vessel velocity in m/s
            propulsion_efficiency: Propeller/propulsion efficiency
            
        Returns:
            Power requirements
        """
        
        # Effective power (power to overcome resistance)
        Pe = resistance * velocity
        
        # Shaft power (accounting for propulsion efficiency)
        Ps = Pe / propulsion_efficiency
        
        # Brake power (accounting for transmission losses)
        transmission_efficiency = 0.97
        Pb = Ps / transmission_efficiency
        
        return {
            'effective_power_kw': Pe / 1000,
            'shaft_power_kw': Ps / 1000,
            'brake_power_kw': Pb / 1000,
            'effective_power_hp': Pe / 745.7,
            'shaft_power_hp': Ps / 745.7,
            'brake_power_hp': Pb / 745.7
        }
    
    def predict_flow_field(self, vessel: VesselGeometry, 
                          conditions: WaterConditions) -> np.ndarray:
        """
        Predict velocity field around vessel hull
        
        Returns:
            2D velocity field
        """
        
        # Create grid around vessel
        x = np.linspace(-vessel.length, 2*vessel.length, 80)
        y = np.linspace(-vessel.beam*2, vessel.beam*2, 60)
        X, Y = np.meshgrid(x, y)
        
        # Simplified potential flow around hull
        # Uniform flow + doublet (representing hull)
        U_inf = conditions.velocity
        
        # Hull represented as doublet
        hull_x = 0
        hull_y = 0
        strength = vessel.beam * vessel.draft * U_inf
        
        r = np.sqrt((X - hull_x)**2 + (Y - hull_y)**2)
        theta = np.arctan2(Y - hull_y, X - hull_x)
        
        # Velocity field (simplified)
        u = U_inf * (1 - strength * np.cos(theta) / (r**2 + 0.1))
        v = -U_inf * strength * np.sin(theta) / (r**2 + 0.1)
        
        velocity_magnitude = np.sqrt(u**2 + v**2)
        
        return velocity_magnitude
    
    def predict_wave_pattern(self, vessel: VesselGeometry,
                           conditions: WaterConditions) -> Dict[str, np.ndarray]:
        """
        Predict Kelvin wave pattern created by vessel
        
        Returns:
            Wave elevation field
        """
        
        Fn = conditions.froude_number
        
        # Create grid
        x = np.linspace(0, vessel.length * 3, 100)
        y = np.linspace(-vessel.length, vessel.length, 80)
        X, Y = np.meshgrid(x, y)
        
        # Kelvin wave pattern (simplified)
        # Real implementation would use more sophisticated wave theory
        
        wave_amplitude = 0.1 * vessel.beam * Fn
        wave_length = 2 * np.pi * conditions.velocity**2 / 9.81
        
        # Divergent waves
        divergent = wave_amplitude * np.sin(2 * np.pi * X / wave_length) * \
                   np.exp(-abs(Y) / (vessel.beam * 2))
        
        # Transverse waves
        transverse = wave_amplitude * 0.5 * np.sin(2 * np.pi * (X - abs(Y)) / wave_length) * \
                    np.exp(-abs(Y) / (vessel.beam * 3))
        
        total_wave = divergent + transverse
        
        return {
            'wave_elevation': total_wave,
            'wave_amplitude': wave_amplitude,
            'wave_length': wave_length
        }


class HydrodynamicsAI:
    """AI Assistant for Hydrodynamic Analysis"""
    
    def __init__(self):
        self.nn_model = HydrodynamicsNN()
        self.analysis_history = []
        
    async def analyze_vessel(self, vessel: VesselGeometry,
                            conditions: WaterConditions) -> Dict[str, any]:
        """
        Comprehensive hydrodynamic analysis
        
        Args:
            vessel: Vessel geometry
            conditions: Water conditions
            
        Returns:
            Complete analysis results
        """
        
        # Predict resistance
        resistance = self.nn_model.predict_resistance(vessel, conditions)
        
        # Predict power requirements
        power = self.nn_model.predict_power_requirement(
            resistance['total_resistance'],
            conditions.velocity
        )
        
        # Performance assessment
        performance = self._assess_performance(resistance, conditions, vessel)
        
        # Flow regime analysis
        flow_regime = self._analyze_flow_regime(conditions)
        
        # Efficiency metrics
        efficiency = self._calculate_efficiency_metrics(resistance, vessel, conditions)
        
        analysis = {
            'vessel': {
                'name': vessel.name,
                'length': f"{vessel.length:.1f} m",
                'beam': f"{vessel.beam:.1f} m",
                'draft': f"{vessel.draft:.1f} m",
                'displacement': f"{vessel.displacement:.0f} kg",
                'hull_form': vessel.hull_form
            },
            'conditions': {
                'speed': f"{conditions.velocity:.1f} m/s ({conditions.velocity * 1.944:.1f} knots)",
                'froude_number': f"{resistance['froude_number']:.3f}",
                'reynolds_number': f"{resistance['reynolds_number']:.2e}",
                'wave_height': f"{conditions.wave_height:.1f} m",
                'regime': flow_regime
            },
            'resistance': {
                'total': f"{resistance['total_resistance']:.2f} N",
                'viscous': f"{resistance['viscous_resistance']:.2f} N ({resistance['viscous_resistance']/resistance['total_resistance']*100:.1f}%)",
                'wave': f"{resistance['wave_resistance']:.2f} N ({resistance['wave_resistance']/resistance['total_resistance']*100:.1f}%)",
                'form': f"{resistance['form_resistance']:.2f} N",
                'wetted_area': f"{resistance['wetted_area']:.2f} m²"
            },
            'coefficients': {
                'total_resistance_coeff': f"{resistance['total_resistance_coefficient']:.6f}",
                'friction_coeff': f"{resistance['friction_coefficient']:.6f}",
                'wave_resistance_coeff': f"{resistance['wave_resistance_coefficient']:.6f}"
            },
            'power': {
                'effective_power': f"{power['effective_power_kw']:.2f} kW ({power['effective_power_hp']:.2f} HP)",
                'shaft_power': f"{power['shaft_power_kw']:.2f} kW ({power['shaft_power_hp']:.2f} HP)",
                'brake_power': f"{power['brake_power_kw']:.2f} kW ({power['brake_power_hp']:.2f} HP)"
            },
            'efficiency': efficiency,
            'performance': performance
        }
        
        # Store in history
        self.analysis_history.append({
            'timestamp': datetime.now(),
            'vessel': vessel.name,
            'analysis': analysis
        })
        
        return analysis
    
    def _assess_performance(self, resistance: Dict, conditions: WaterConditions,
                           vessel: VesselGeometry) -> Dict[str, str]:
        """Assess hydrodynamic performance"""
        
        Fn = resistance['froude_number']
        total_R = resistance['total_resistance']
        wave_R = resistance['wave_resistance']
        
        # Speed regime assessment
        if Fn < 0.3:
            speed_regime = "Displacement speed - Efficient for this hull"
        elif Fn < 0.4:
            speed_regime = "Transition speed - Increasing wave resistance"
        elif Fn < 0.5:
            speed_regime = "Semi-displacement - High wave resistance"
        else:
            speed_regime = "Planing speed - Critical for hull form"
        
        # Wave resistance warning
        wave_percentage = (wave_R / total_R) * 100
        if wave_percentage > 50:
            wave_warning = "⚠️ High wave resistance! Consider reducing speed or hull optimization"
        elif wave_percentage > 30:
            wave_warning = "⚡ Moderate wave resistance - acceptable for current speed"
        else:
            wave_warning = "✅ Low wave resistance - good efficiency"
        
        # Hull optimization suggestions
        if vessel.hull_form == "displacement" and Fn > 0.4:
            optimization = "💡 Consider transitioning to planing hull at these speeds"
        elif vessel.hull_form == "planing" and Fn < 0.3:
            optimization = "💡 Operating below optimal planing speed"
        else:
            optimization = "✅ Hull form appropriate for current speed"
        
        # Overall rating
        efficiency_score = 100 - wave_percentage
        if efficiency_score > 80:
            rating = "⭐⭐⭐⭐⭐ Excellent"
        elif efficiency_score > 60:
            rating = "⭐⭐⭐⭐ Good"
        elif efficiency_score > 40:
            rating = "⭐⭐⭐ Fair"
        else:
            rating = "⭐⭐ Needs improvement"
        
        return {
            'speed_regime': speed_regime,
            'wave_warning': wave_warning,
            'optimization': optimization,
            'overall_rating': rating
        }
    
    def _analyze_flow_regime(self, conditions: WaterConditions) -> str:
        """Determine flow regime"""
        
        Re = conditions.reynolds_number
        Fn = conditions.froude_number
        
        # Reynolds number regime
        if Re < 1e6:
            re_regime = "Laminar/Transitional"
        elif Re < 1e7:
            re_regime = "Transitional"
        else:
            re_regime = "Fully Turbulent"
        
        # Froude number regime
        if Fn < 0.3:
            fn_regime = "Displacement"
        elif Fn < 0.5:
            fn_regime = "Semi-displacement"
        else:
            fn_regime = "Planing"
        
        return f"{re_regime}, {fn_regime} regime"
    
    def _calculate_efficiency_metrics(self, resistance: Dict, vessel: VesselGeometry,
                                     conditions: WaterConditions) -> Dict[str, str]:
        """Calculate various efficiency metrics"""
        
        # Transport efficiency (displacement / resistance)
        transport_eff = vessel.displacement / resistance['total_resistance']
        
        # Admiralty coefficient (rough measure of hull efficiency)
        # AC = (Displacement^2/3 * Speed^3) / Power
        speed_knots = conditions.velocity * 1.944
        disp_tons = vessel.displacement / 1000
        # Simplified without actual power
        
        # Resistance per unit displacement
        resistance_per_ton = resistance['total_resistance'] / (vessel.displacement / 1000)
        
        return {
            'transport_efficiency': f"{transport_eff:.2f} kg/N",
            'resistance_per_ton': f"{resistance_per_ton:.2f} N/ton",
            'specific_resistance': f"{resistance['total_resistance']/vessel.length:.2f} N/m"
        }
    
    async def optimize_speed(self, vessel: VesselGeometry,
                           conditions: WaterConditions,
                           power_limit_kw: float) -> Dict:
        """
        Find optimal cruising speed for given power limit
        
        Args:
            vessel: Vessel geometry
            conditions: Base water conditions
            power_limit_kw: Maximum available power in kW
            
        Returns:
            Optimal speed and efficiency analysis
        """
        
        optimal_speed = 0
        max_efficiency = 0
        
        # Test different speeds
        speeds = np.linspace(1, 20, 50)
        results = []
        
        for speed in speeds:
            test_conditions = WaterConditions(
                velocity=speed,
                water_density=conditions.water_density,
                kinematic_viscosity=conditions.kinematic_viscosity,
                wave_height=conditions.wave_height,
                wave_period=conditions.wave_period,
                depth=conditions.depth
            )
            
            resistance = self.nn_model.predict_resistance(vessel, test_conditions)
            power = self.nn_model.predict_power_requirement(
                resistance['total_resistance'],
                speed
            )
            
            # Calculate efficiency (distance per unit energy)
            efficiency = speed / (power['effective_power_kw'] + 0.1)
            
            results.append({
                'speed': speed,
                'power': power['brake_power_kw'],
                'efficiency': efficiency,
                'resistance': resistance['total_resistance']
            })
            
            # Check if within power limit
            if power['brake_power_kw'] <= power_limit_kw:
                if efficiency > max_efficiency:
                    max_efficiency = efficiency
                    optimal_speed = speed
        
        return {
            'optimal_speed_ms': f"{optimal_speed:.2f} m/s",
            'optimal_speed_knots': f"{optimal_speed * 1.944:.2f} knots",
            'power_required_kw': f"{results[int(optimal_speed*2.5)]['power']:.2f} kW",
            'power_limit_kw': power_limit_kw,
            'efficiency_metric': f"{max_efficiency:.4f}",
            'speed_range_analyzed': f"1-20 m/s ({1*1.944:.1f}-{20*1.944:.1f} knots)"
        }
    
    def generate_report(self, analysis: Dict) -> str:
        """Generate human-readable analysis report"""
        
        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║       HYDRODYNAMIC ANALYSIS REPORT (AI-POWERED)               ║
╚═══════════════════════════════════════════════════════════════╝

🚢 VESSEL: {analysis['vessel']['name']}
   • Length: {analysis['vessel']['length']}
   • Beam: {analysis['vessel']['beam']}
   • Draft: {analysis['vessel']['draft']}
   • Displacement: {analysis['vessel']['displacement']}
   • Hull Form: {analysis['vessel']['hull_form']}

🌊 CONDITIONS:
   • Speed: {analysis['conditions']['speed']}
   • Froude Number: {analysis['conditions']['froude_number']}
   • Reynolds Number: {analysis['conditions']['reynolds_number']}
   • Wave Height: {analysis['conditions']['wave_height']}
   • Flow Regime: {analysis['conditions']['regime']}

⚓ RESISTANCE ANALYSIS:
   • Total Resistance: {analysis['resistance']['total']}
   • Viscous Resistance: {analysis['resistance']['viscous']}
   • Wave Resistance: {analysis['resistance']['wave']}
   • Form Resistance: {analysis['resistance']['form']}
   • Wetted Surface: {analysis['resistance']['wetted_area']}

📊 COEFFICIENTS:
   • Total Resistance Coeff: {analysis['coefficients']['total_resistance_coeff']}
   • Friction Coeff: {analysis['coefficients']['friction_coeff']}
   • Wave Resistance Coeff: {analysis['coefficients']['wave_resistance_coeff']}

⚡ POWER REQUIREMENTS:
   • Effective Power: {analysis['power']['effective_power']}
   • Shaft Power: {analysis['power']['shaft_power']}
   • Brake Power: {analysis['power']['brake_power']}

📈 EFFICIENCY METRICS:
   • Transport Efficiency: {analysis['efficiency']['transport_efficiency']}
   • Resistance per Ton: {analysis['efficiency']['resistance_per_ton']}
   • Specific Resistance: {analysis['efficiency']['specific_resistance']}

⚡ PERFORMANCE ASSESSMENT:
   • Speed Regime: {analysis['performance']['speed_regime']}
   • Wave Status: {analysis['performance']['wave_warning']}
   • Optimization: {analysis['performance']['optimization']}
   • Overall Rating: {analysis['performance']['overall_rating']}

═══════════════════════════════════════════════════════════════
"""
        return report


async def demo_hydrodynamics_ai():
    """Demonstration of hydrodynamics AI capabilities"""
    
    print("⚓ HYDRODYNAMICS DEEP LEARNING DEMO")
    print("=" * 70)
    print("AI-powered hydrodynamic analysis for marine vessels")
    print("=" * 70)
    
    # Initialize AI system
    hydro_ai = HydrodynamicsAI()
    
    # Test Case 1: Sailing yacht (displacement hull)
    print("\n📝 Test Case 1: Sailing Yacht (Displacement Hull)")
    print("-" * 70)
    
    yacht = VesselGeometry(
        name="Cruising Yacht 40ft",
        length=12.0,
        beam=3.5,
        draft=2.0,
        displacement=8000.0,
        hull_form="displacement"
    )
    
    calm_water = WaterConditions(
        velocity=3.0,  # ~6 knots
        water_density=1025.0,
        kinematic_viscosity=1.19e-6,
        wave_height=0.5,
        wave_period=4.0,
        depth=50.0
    )
    
    analysis1 = await hydro_ai.analyze_vessel(yacht, calm_water)
    print(hydro_ai.generate_report(analysis1))
    
    await asyncio.sleep(0.5)
    
    # Test Case 2: Fast patrol boat (planing hull)
    print("\n📝 Test Case 2: Fast Patrol Boat (Planing Hull)")
    print("-" * 70)
    
    patrol_boat = VesselGeometry(
        name="Fast Patrol Boat",
        length=15.0,
        beam=4.0,
        draft=1.0,
        displacement=12000.0,
        hull_form="planing"
    )
    
    high_speed = WaterConditions(
        velocity=15.0,  # ~29 knots
        water_density=1025.0,
        kinematic_viscosity=1.19e-6,
        wave_height=1.0,
        wave_period=5.0,
        depth=100.0
    )
    
    analysis2 = await hydro_ai.analyze_vessel(patrol_boat, high_speed)
    print(hydro_ai.generate_report(analysis2))
    
    await asyncio.sleep(0.5)
    
    # Test Case 3: Catamaran
    print("\n📝 Test Case 3: Catamaran Ferry")
    print("-" * 70)
    
    catamaran = VesselGeometry(
        name="Passenger Catamaran",
        length=25.0,
        beam=8.0,
        draft=1.5,
        displacement=50000.0,
        hull_form="catamaran"
    )
    
    moderate_speed = WaterConditions(
        velocity=10.0,  # ~19 knots
        water_density=1025.0,
        kinematic_viscosity=1.19e-6,
        wave_height=1.5,
        wave_period=6.0,
        depth=80.0
    )
    
    analysis3 = await hydro_ai.analyze_vessel(catamaran, moderate_speed)
    print(hydro_ai.generate_report(analysis3))
    
    await asyncio.sleep(0.5)
    
    # Optimization demo
    print("\n🔧 OPTIMIZATION: Finding optimal cruising speed")
    print("-" * 70)
    print(f"Vessel: {yacht.name}")
    print("Power limit: 50 kW")
    
    optimization = await hydro_ai.optimize_speed(
        vessel=yacht,
        conditions=calm_water,
        power_limit_kw=50.0
    )
    
    print(f"\n✅ OPTIMIZATION RESULTS:")
    print(f"   • Optimal Speed: {optimization['optimal_speed_ms']} ({optimization['optimal_speed_knots']})")
    print(f"   • Power Required: {optimization['power_required_kw']}")
    print(f"   • Power Limit: {optimization['power_limit_kw']} kW")
    print(f"   • Efficiency Metric: {optimization['efficiency_metric']}")
    print(f"   • Speed Range: {optimization['speed_range_analyzed']}")
    
    print("\n" + "=" * 70)
    print("✅ Hydrodynamics AI Demo Complete!")
    print(f"📊 Total analyses performed: {len(hydro_ai.analysis_history)}")
    print("=" * 70)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║    HYDRODYNAMICS AI - Deep Learning Application            ║
    ║                                                             ║
    ║  Uses Neural Networks to predict:                          ║
    ║  • Resistance and drag forces                              ║
    ║  • Wave patterns and Kelvin wake                           ║
    ║  • Power requirements                                       ║
    ║  • Flow fields around hulls                                ║
    ║                                                             ║
    ║  Applications: Ship design, submarines, marine engineering ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(demo_hydrodynamics_ai())
