# Phase 0: Python Foundations

## Overview

Before diving into CAD design, you need to master the Python fundamentals that will power your parametric designs. This phase focuses on practical Python skills directly applicable to 3D part design.

## Duration
2-3 weeks

## Learning Objectives

By the end of this phase, you will:
- Write Python functions for geometric calculations
- Use classes to represent 3D objects
- Work with lists and dictionaries for part properties
- Perform mathematical operations for design
- Understand virtual environments and project setup

## Topics Covered

### 1. Variables and Basic Math

Learn to work with numbers and perform calculations:

```python
# Basic calculations
radius = 10
area = 3.14159 * radius ** 2
circumference = 2 * 3.14159 * radius
```

**Why it matters:** Every parametric design relies on mathematical relationships between dimensions.

### 2. Functions

Create reusable calculation functions:

```python
def calculate_circle_area(radius):
    import math
    return math.pi * radius ** 2

area = calculate_circle_area(15)
```

**Why it matters:** Functions make your designs parametric and reusable.

### 3. Classes and Objects

Model 3D concepts with object-oriented programming:

```python
class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def distance_to(self, other):
        # Calculate distance to another point
        pass
```

**Why it matters:** CAD libraries use objects extensively to represent geometry.

### 4. Lists and Dictionaries

Store collections of data:

```python
# List of hole positions
holes = [(10, 10), (20, 10), (10, 20), (20, 20)]

# Part properties
properties = {
    'material': 'PLA',
    'weight': 25.5,
    'color': 'black'
}
```

**Why it matters:** Managing multiple features (holes, edges, faces) requires collections.

### 5. The Math Module

Python's built-in math functions:

```python
import math

# Trigonometry for circular patterns
angle = math.radians(45)
x = radius * math.cos(angle)
y = radius * math.sin(angle)
```

**Why it matters:** Essential for circular patterns, angles, and geometric calculations.

## Practical Exercises

### Exercise 1: Motor Mount Calculator

Create a function that calculates motor mount dimensions:

```python
def calculate_motor_mount_dimensions(motor_diameter, wall_thickness=3):
    """
    Calculate dimensions for a motor mount.
    
    Args:
        motor_diameter: Diameter of the motor
        wall_thickness: Thickness of the mount wall
    
    Returns:
        Dictionary with calculated dimensions
    """
    mount_diameter = motor_diameter + 2 * wall_thickness
    mount_radius = mount_diameter / 2
    
    return {
        'motor_diameter': motor_diameter,
        'mount_diameter': mount_diameter,
        'mount_radius': mount_radius,
        'wall_thickness': wall_thickness
    }
```

### Exercise 2: Mounting Hole Positions

Generate evenly-spaced hole positions:

```python
import math

def generate_mounting_holes(count, radius, hole_diameter):
    """Generate coordinates for evenly-spaced mounting holes in a circle."""
    holes = []
    angle_step = 2 * math.pi / count
    
    for i in range(count):
        angle = i * angle_step
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        holes.append((x, y))
    
    return holes

# Create 4 holes at 20mm radius
holes = generate_mounting_holes(4, 20, 3)
```

### Exercise 3: Volume and Weight

Calculate part volume and estimate weight:

```python
def calculate_hollow_cylinder_volume(outer_radius, inner_radius, height):
    """Calculate volume of a hollow cylinder."""
    import math
    outer_volume = math.pi * outer_radius ** 2 * height
    inner_volume = math.pi * inner_radius ** 2 * height
    return outer_volume - inner_volume

def estimate_weight(volume_mm3, material='PLA', infill=20):
    """Estimate weight based on volume and material."""
    densities = {
        'PLA': 1.24,    # g/cm³
        'PETG': 1.27,
        'ABS': 1.04,
        'Nylon': 1.14
    }
    
    density = densities.get(material, 1.24)
    volume_cm3 = volume_mm3 / 1000
    
    # Simplified: account for infill
    effective_volume = volume_cm3 * (0.4 + 0.6 * infill / 100)
    return effective_volume * density
```

## Resources

### Official Documentation
- [Python Tutorial](https://docs.python.org/3/tutorial/) - Official Python tutorial
- [Python Math Module](https://docs.python.org/3/library/math.html) - Math functions reference

### Books
- **Automate the Boring Stuff with Python** (first half) - Practical Python basics
- **Python Crash Course** - Beginner-friendly introduction

### Practice
- Work through `src/phase0_foundations/basic_concepts.py`
- Complete exercises in `src/phase0_foundations/geometry_calc.py`
- Write your own geometric calculation functions

## Validation Checklist

Before moving to Phase 1, ensure you can:

- ✅ Write functions with parameters and return values
- ✅ Create classes with methods
- ✅ Use lists and dictionaries effectively
- ✅ Perform trigonometric calculations
- ✅ Calculate distances, areas, and volumes
- ✅ Understand coordinate systems (2D and 3D)

## Common Pitfalls

1. **Degrees vs Radians**: Most math functions use radians, not degrees
   ```python
   # Wrong
   angle = 90
   x = math.cos(angle)  # Wrong result!
   
   # Correct
   angle = math.radians(90)
   x = math.cos(angle)  # Correct!
   ```

2. **Integer Division**: Use `/` not `//` for real division
   ```python
   # Wrong
   half = 10 // 2  # This works, but...
   half = 11 // 2  # This gives 5, not 5.5
   
   # Correct
   half = 11 / 2  # Gives 5.5
   ```

3. **Mutable Default Arguments**: Don't use mutable defaults
   ```python
   # Wrong
   def add_hole(holes=[]):  # Dangerous!
       holes.append((0, 0))
       return holes
   
   # Correct
   def add_hole(holes=None):
       if holes is None:
           holes = []
       holes.append((0, 0))
       return holes
   ```

## Next Steps

Once you've mastered these fundamentals, proceed to:
- **Phase 1**: Aircraft & Drone Basics - Understanding what you're designing for
- Start with simple scripts before moving to complex designs
- Keep practicing with real-world geometric problems

## Summary

Phase 0 lays the foundation for all parametric design work. The skills you learn here—functions, classes, math operations—will be used in every single part you design. Take your time to master these concepts!

**Time Investment**: 2-3 weeks, 5-10 hours per week
**Difficulty**: 🟢 Beginner
**Prerequisites**: None (complete beginner-friendly)
