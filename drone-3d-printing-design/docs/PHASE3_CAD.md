# Phase 3: Python-Based CAD with CadQuery

## Overview

Phase 3 is the **core skill** of this entire learning path. Here you'll learn to use CadQuery, a Python library that lets you design 3D parts programmatically. Think of it as "writing code that creates CAD models" instead of clicking in a traditional CAD software.

## Duration
4-6 weeks (this is the most important phase, don't rush it!)

## Why CadQuery?

### Advantages over Traditional CAD
- ✅ **Fully Parametric**: Change one number, the whole design updates
- ✅ **Version Control**: Your designs are just Python code (Git-friendly!)
- ✅ **Automation**: Generate 100 variations with a loop
- ✅ **Reproducible**: No manual clicking, just run the script
- ✅ **Industry Used**: Real companies use it for production parts

### CadQuery vs OpenSCAD
- CadQuery uses Python (familiar syntax)
- More powerful API (workplanes, selectors)
- Better boolean operations
- Active development and community

## Installation

### Basic Installation
```bash
pip install cadquery
```

### With Visualization (Recommended)
Install CQ-Editor for visual feedback:
```bash
# Download from: https://github.com/CadQuery/CQ-editor/releases
# Available for Windows, Mac, Linux
```

### Verify Installation
```python
import cadquery as cq
print(cq.__version__)  # Should print version number
```

## Core Concepts

### 1. Workplanes

A workplane is like a drawing surface in 3D space.

```python
import cadquery as cq

# Create a workplane on the XY plane
result = cq.Workplane("XY")

# Common planes:
# "XY" - horizontal (top view)
# "XZ" - vertical front
# "YZ" - vertical side
```

**Why it matters**: All sketches are drawn on workplanes before being extruded into 3D.

### 2. Basic Shapes

#### Box
```python
box = cq.Workplane("XY").box(10, 20, 30)
# Creates a box: 10mm wide, 20mm deep, 30mm tall
```

#### Cylinder
```python
cylinder = (
    cq.Workplane("XY")
    .circle(10)      # 10mm radius
    .extrude(20)     # 20mm tall
)
```

#### Hollow Cylinder (Tube)
```python
tube = (
    cq.Workplane("XY")
    .circle(10)      # Outer circle
    .circle(8)       # Inner circle
    .extrude(20)
)
```

### 3. Extrusion Operations

#### Extrude
```python
# Extrude upward
result = cq.Workplane("XY").rect(20, 10).extrude(5)

# Extrude in both directions
result = cq.Workplane("XY").rect(20, 10).extrude(5, both=True)
```

#### Cut (Extrude and Subtract)
```python
# Create a box with a hole through it
result = (
    cq.Workplane("XY")
    .box(20, 20, 10)
    .faces(">Z")           # Select top face
    .workplane()
    .circle(3)
    .cutThruAll()          # Cut all the way through
)
```

### 4. Selectors

Selectors let you choose specific faces, edges, or vertices.

```python
# Select faces
.faces(">Z")   # Faces pointing up (positive Z)
.faces("<Z")   # Faces pointing down (negative Z)
.faces("|Z")   # Faces parallel to Z axis

# Select edges
.edges(">X")   # Edges in positive X direction
.edges("|Z")   # Edges parallel to Z axis
```

**Common use**: Select a face to add features (holes, extrusions) on it.

### 5. Boolean Operations

Combine shapes mathematically.

```python
# Union (add together)
result = box1.union(box2)

# Difference (subtract)
result = box1.cut(cylinder)

# Intersection (keep only overlap)
result = box1.intersect(cylinder)
```

### 6. Fillets and Chamfers

#### Fillet (Rounded Edge)
```python
# Round all vertical edges
result = (
    cq.Workplane("XY")
    .box(20, 20, 10)
    .edges("|Z")
    .fillet(2)  # 2mm radius
)
```

**Why fillets matter**: 
- Reduce stress concentrations
- Easier to 3D print (no sharp overhangs)
- Stronger parts

#### Chamfer (Angled Edge)
```python
# Chamfer top edges
result = (
    cq.Workplane("XY")
    .circle(10)
    .extrude(20)
    .edges(">Z")
    .chamfer(1)  # 1mm chamfer
)
```

### 7. Holes and Patterns

#### Single Hole
```python
result = (
    cq.Workplane("XY")
    .box(20, 20, 5)
    .faces(">Z")
    .workplane()
    .hole(3)  # 3mm diameter
)
```

#### Rectangular Array
```python
# 3x3 grid of holes
result = (
    cq.Workplane("XY")
    .box(30, 30, 5)
    .faces(">Z")
    .workplane()
    .rarray(10, 10, 3, 3)  # spacing, count
    .hole(2)
)
```

#### Circular Pattern
```python
import math

# 6 holes in a circle
points = []
for i in range(6):
    angle = i * (360 / 6)
    angle_rad = math.radians(angle)
    x = 15 * math.cos(angle_rad)
    y = 15 * math.sin(angle_rad)
    points.append((x, y))

result = (
    cq.Workplane("XY")
    .circle(20)
    .extrude(5)
    .faces(">Z")
    .workplane()
    .pushPoints(points)
    .hole(3)
)
```

## Practical Examples

### Example 1: Motor Mount (Simplified)

```python
import cadquery as cq

def create_motor_mount(motor_diameter=28, height=5):
    """Create a simple motor mount."""
    mount_radius = motor_diameter / 2 + 3
    
    # Base cylinder
    mount = (
        cq.Workplane("XY")
        .circle(mount_radius)
        .extrude(height)
    )
    
    # Center hole for motor
    mount = (
        mount
        .faces(">Z")
        .workplane()
        .hole(motor_diameter)
    )
    
    # 4 screw holes in circle
    import math
    screw_radius = mount_radius - 1.5
    points = []
    for i in range(4):
        angle = i * 90
        angle_rad = math.radians(angle)
        x = screw_radius * math.cos(angle_rad)
        y = screw_radius * math.sin(angle_rad)
        points.append((x, y))
    
    mount = (
        mount
        .faces(">Z")
        .workplane()
        .pushPoints(points)
        .hole(3)  # M3 screws
    )
    
    return mount

# Create and export
mount = create_motor_mount()
cq.exporters.export(mount, "motor_mount.stl")
```

### Example 2: Parametric Battery Tray

```python
import cadquery as cq

def create_battery_tray(
    battery_length=75,
    battery_width=35,
    battery_height=25,
    wall_thickness=2
):
    """Create a parametric battery tray."""
    
    # Outer dimensions
    outer_length = battery_length + 2 * wall_thickness
    outer_width = battery_width + 2 * wall_thickness
    depth = battery_height * 0.6  # Hold 60% of battery
    
    # Create outer box
    tray = (
        cq.Workplane("XY")
        .box(outer_length, outer_width, depth + wall_thickness)
    )
    
    # Hollow it out
    tray = (
        tray
        .faces(">Z")
        .workplane()
        .rect(battery_length, battery_width)
        .cutBlind(depth)
    )
    
    # Add strap slots on sides
    tray = (
        tray
        .faces(">Y")
        .workplane()
        .rect(battery_length * 0.8, 4)
        .cutBlind(wall_thickness)
    )
    
    # Round the edges for easier printing
    tray = tray.edges("|Z").fillet(1)
    
    return tray

# Create with custom battery size
tray = create_battery_tray(battery_length=100, battery_width=40)
cq.exporters.export(tray, "battery_tray.stl")
```

### Example 3: Mounting Plate with Corner Holes

```python
import cadquery as cq

def create_mounting_plate(
    length=50,
    width=40,
    thickness=3,
    hole_diameter=3.2,
    edge_distance=5
):
    """Create a mounting plate with 4 corner holes."""
    
    # Create base plate
    plate = cq.Workplane("XY").box(length, width, thickness)
    
    # Calculate corner positions
    half_length = length / 2 - edge_distance
    half_width = width / 2 - edge_distance
    
    corners = [
        (-half_length, -half_width),
        (half_length, -half_width),
        (half_length, half_width),
        (-half_length, half_width)
    ]
    
    # Add corner holes
    plate = (
        plate
        .faces(">Z")
        .workplane()
        .pushPoints(corners)
        .hole(hole_diameter)
    )
    
    # Add fillets to corners for strength
    plate = plate.edges("|Z").fillet(1)
    
    return plate

plate = create_mounting_plate()
cq.exporters.export(plate, "mounting_plate.stl")
```

## Export Options

### STL (for 3D Printing)
```python
cq.exporters.export(object, "part.stl")
```

### STEP (for CAD Interoperability)
```python
cq.exporters.export(object, "part.step")
```

### Multiple Formats
```python
# Export both
cq.exporters.export(motor_mount, "motor_mount.stl")
cq.exporters.export(motor_mount, "motor_mount.step")
```

## Best Practices

### 1. Use Variables for Dimensions
```python
# Good
motor_diameter = 28
wall_thickness = 3
mount_diameter = motor_diameter + 2 * wall_thickness

# Bad
mount_diameter = 34  # Where did this come from?
```

### 2. Add Comments
```python
# Create base cylinder for motor mount
mount = cq.Workplane("XY").circle(mount_radius).extrude(height)

# Cut center hole for motor shaft
mount = mount.faces(">Z").workplane().hole(motor_diameter)
```

### 3. Build Step by Step
```python
# Don't chain everything at once if you're learning
# Build incrementally:
result = cq.Workplane("XY")
result = result.box(20, 20, 10)
result = result.faces(">Z").workplane()
result = result.hole(5)
```

### 4. Test with Simple Shapes First
Before creating complex parts, test your logic with simple boxes/cylinders.

### 5. Use Functions for Reusability
```python
def create_mounting_holes(workplane, radius, hole_count, hole_diameter):
    """Reusable function for circular hole patterns."""
    import math
    points = []
    for i in range(hole_count):
        angle = i * (360 / hole_count)
        angle_rad = math.radians(angle)
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        points.append((x, y))
    
    return workplane.pushPoints(points).hole(hole_diameter)
```

## Common Pitfalls

### 1. Wrong Workplane Orientation
```python
# This creates a vertical cylinder (wrong for motor mount)
cq.Workplane("XZ").circle(10).extrude(20)

# This creates a horizontal cylinder (correct)
cq.Workplane("XY").circle(10).extrude(20)
```

### 2. Forgetting .workplane() After Face Selection
```python
# Wrong - won't work
result = cq.Workplane("XY").box(20, 20, 10).faces(">Z").hole(5)

# Correct - need workplane()
result = cq.Workplane("XY").box(20, 20, 10).faces(">Z").workplane().hole(5)
```

### 3. Units Confusion
CadQuery uses millimeters by default. Keep all dimensions in mm!

## Learning Exercises

### Week 1: Basics
1. Create a 20x20x10mm box
2. Create a cylinder with 15mm radius, 25mm height
3. Create a hollow tube (outer=15mm, inner=12mm, height=30mm)
4. Create a box with a hole through the center

### Week 2: Features
1. Create a box with filleted edges
2. Create a mounting plate with 4 corner holes
3. Create a circular part with 6 holes in a circular pattern
4. Create a chamfered cylinder

### Week 3: Parametric Design
1. Write a function that creates a box with any dimensions
2. Write a function that creates a motor mount for any motor size
3. Create a mounting plate generator with variable hole count
4. Create a battery tray for any battery size

### Week 4: Complex Parts
1. Combine multiple shapes (union, difference)
2. Create a motor mount with raised lip
3. Create a camera mount with angled base
4. Create your first complete drone part!

## Resources

### Official Documentation
- [CadQuery Documentation](https://cadquery.readthedocs.io/)
- [CadQuery Examples](https://cadquery.readthedocs.io/en/latest/examples.html)
- [API Reference](https://cadquery.readthedocs.io/en/latest/apireference.html)

### Community
- [CadQuery Discord](https://discord.gg/Bj9AQPsCfx)
- [CadQuery Forum](https://github.com/CadQuery/cadquery/discussions)
- [CadQuery on YouTube](https://www.youtube.com/results?search_query=cadquery+tutorial)

### Example Code
- Check `src/phase3_cad/cadquery_basics.py`
- Check `src/phase4_part_design/motor_mount.py`
- Run `examples/beginner/simple_motor_mount.py`

## Validation Checklist

Before moving to Phase 4, ensure you can:

- ✅ Install and import CadQuery
- ✅ Create basic shapes (box, cylinder)
- ✅ Use workplanes correctly
- ✅ Select faces and edges with selectors
- ✅ Add holes in patterns
- ✅ Apply fillets and chamfers
- ✅ Use boolean operations (union, cut)
- ✅ Export STL files
- ✅ Write parametric functions
- ✅ Create a simple motor mount from scratch

## Next Steps

Once you've mastered CadQuery fundamentals, proceed to:
- **Phase 4**: Design real drone parts (motor mounts, arms, etc.)
- Start with the beginner example: `examples/beginner/simple_motor_mount.py`
- Gradually increase complexity

## Summary

Phase 3 is where theory meets practice. CadQuery transforms your Python knowledge into physical parts. The power of parametric design means you can:

- **Iterate faster**: Change one number, regenerate
- **Scale easily**: Generate S/M/L versions automatically
- **Collaborate better**: Share Python code, not binary CAD files
- **Integrate**: Include CAD generation in your build pipeline

**Time Investment**: 4-6 weeks, 10-12 hours per week
**Difficulty**: 🟡 Intermediate (requires Python from Phase 0)
**Prerequisites**: Phase 0 (Python Foundations)

Take your time with this phase. Mastering CadQuery is the key to designing professional drone parts!
