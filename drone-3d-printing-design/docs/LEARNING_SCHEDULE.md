# 12-Week Learning Schedule

## Complete Roadmap: Python Foundations → Flight-Ready Drone Parts

This schedule provides a structured path to master drone part design for 3D printing using Python. Each week builds on the previous, with clear goals and milestones.

---

## 📅 Weekly Breakdown

### **Week 1-2: Python Foundations**
**Phase 0: Prerequisites**

#### Week 1: Basic Python
- **Goals:**
  - Set up Python environment
  - Learn variables, functions, basic math
  - Write first geometric calculations

- **Tasks:**
  - Install Python 3.8+
  - Run `src/phase0_foundations/basic_concepts.py`
  - Complete exercises: circle area, rectangle calculations
  - Practice: Write functions for triangles, cylinders

- **Deliverable:** 
  - Script that calculates motor mount dimensions for any motor size

#### Week 2: Classes & Math
- **Goals:**
  - Master classes and objects
  - Use math module for trigonometry
  - Create reusable geometry tools

- **Tasks:**
  - Study `Point3D` and `Vector3D` classes
  - Run `src/phase0_foundations/geometry_calc.py`
  - Create your own `Circle` class
  - Calculate mounting hole positions

- **Deliverable:**
  - Class-based geometry calculator for drone parts

---

### **Week 3: Aircraft & Drone Basics**
**Phase 1: Understanding the Domain**

- **Goals:**
  - Learn basic aerodynamics
  - Understand drone component types
  - Identify load paths in structures

- **Tasks:**
  - Research multirotor vs fixed-wing designs
  - Study motor mount requirements
  - Understand vibration issues
  - Calculate thrust-to-weight ratios

- **Resources:**
  - Watch drone building tutorials
  - Visit RCGroups forums
  - Study existing drone frames

- **Deliverable:**
  - Document with requirements for 3 different drone parts

---

### **Week 4: 3D Printing Fundamentals**
**Phase 2: Manufacturing Knowledge**

- **Goals:**
  - Understand FDM printing process
  - Learn material properties
  - Master design for manufacturing

- **Tasks:**
  - Study layer orientation effects
  - Learn about infill patterns
  - Understand tolerance requirements
  - Research material options (PLA, PETG, Nylon)

- **Practice:**
  - Download and inspect drone STL files
  - Identify design features for 3D printing
  - Calculate print times and material usage

- **Deliverable:**
  - Material selection guide for different drone parts

---

### **Week 5-6: CadQuery Mastery**
**Phase 3: Core CAD Skills**

#### Week 5: CadQuery Basics
- **Goals:**
  - Install and configure CadQuery
  - Master workplanes and sketches
  - Create basic shapes

- **Tasks:**
  - Install CadQuery: `pip install cadquery`
  - Optional: Install CQ-Editor for visualization
  - Run all examples in `src/phase3_cad/cadquery_basics.py`
  - Create: box, cylinder, hollow cylinder

- **Practice:**
  - Create 10 different basic shapes
  - Experiment with extrude, revolve
  - Learn to export STL files

- **Deliverable:**
  - Collection of 5 basic STL files

#### Week 6: Advanced CadQuery
- **Goals:**
  - Master fillets and chamfers
  - Use boolean operations
  - Create parametric designs

- **Tasks:**
  - Study `parametric_design.py`
  - Learn fillet vs chamfer trade-offs
  - Practice hole patterns
  - Master boolean operations (union, difference, intersection)

- **Practice:**
  - Create parametric box with variable dimensions
  - Design plate with hole array
  - Combine multiple shapes

- **Deliverable:**
  - Fully parametric mounting plate with 4 corner holes

---

### **Week 7-8: First Real Parts**
**Phase 4: Beginner Parts**

#### Week 7: Motor Mount
- **Goals:**
  - Design first real drone part
  - Print and test fit

- **Tasks:**
  - Study `src/phase4_part_design/motor_mount.py`
  - Run `examples/beginner/simple_motor_mount.py`
  - Customize for your motor size
  - Generate STL and print

- **Testing:**
  - Print with 30% infill
  - Test fit on actual motor
  - Iterate if needed

- **Deliverable:**
  - Working motor mount (3D printed and tested)

#### Week 8: Camera & Battery Mounts
- **Goals:**
  - Design 2 more functional parts
  - Learn about angled features

- **Tasks:**
  - Design camera mount with 30° tilt
  - Design battery tray with strap slots
  - Add fillets for strength
  - Print both parts

- **Deliverable:**
  - Camera mount and battery tray (printed)

---

### **Week 9: Intermediate Parts**
**Phase 4: Complex Designs**

- **Goals:**
  - Design multi-feature parts
  - Optimize for weight
  - Handle assembly constraints

- **Tasks:**
  - Design drone arm with taper
  - Create frame connector
  - Design landing gear with flex points
  - Calculate weight for each part

- **Advanced Features:**
  - Tapered cross-sections
  - Multiple mounting points
  - Weight optimization

- **Deliverable:**
  - Complete arm assembly (arm + motor mount)

---

### **Week 10: Engineering Validation**
**Phase 5: Make It Right**

- **Goals:**
  - Validate designs mathematically
  - Calculate weight and CG
  - Basic stress analysis

- **Tasks:**
  - Study `src/phase5_validation/weight_cg.py`
  - Calculate CG for quadcopter frame
  - Learn basic beam bending equations
  - Estimate stress in drone arm

- **Tools:**
  - NumPy for matrix calculations
  - SciPy for engineering functions
  - Optional: FreeCAD FEM

- **Deliverable:**
  - Weight and CG report for complete drone frame

---

### **Week 11: Automation & Optimization**
**Phase 6: Scale Up**

- **Goals:**
  - Automate design generation
  - Create design families
  - Optimize parameters

- **Tasks:**
  - Write script to generate 5 motor mount sizes
  - Create arm generator for different wingspans
  - Implement weight optimization loop
  - Batch generate STL files

- **Advanced:**
  - Genetic algorithm for optimization
  - Multi-objective optimization (weight vs strength)

- **Deliverable:**
  - Auto-generator for complete quadcopter frame family (3", 5", 7", 10")

---

### **Week 12: Final Project**
**Integration & Real Flight**

- **Goals:**
  - Complete integrated system
  - Print and assemble
  - Prepare for flight

- **Tasks:**
  - Design complete quadcopter frame
  - Include all mounts (motor, camera, FC, battery)
  - Generate all STL files
  - Print complete kit
  - Assemble and bench test

- **Components:**
  - 4x motor mounts
  - 4x arms
  - 1x center plate
  - 1x camera mount
  - 1x battery tray
  - Landing gear

- **Final Deliverable:**
  - Complete 3D-printed quadcopter frame
  - GitHub repository with all CAD scripts
  - Documentation with assembly instructions
  - (Optional) First test flight video!

---

## 📊 Time Commitment

| Phase | Weeks | Hours/Week | Total Hours |
|-------|-------|------------|-------------|
| Phase 0 | 2 | 8-10 | 16-20 |
| Phase 1 | 1 | 6-8 | 6-8 |
| Phase 2 | 1 | 6-8 | 6-8 |
| Phase 3 | 2 | 10-12 | 20-24 |
| Phase 4 | 3 | 8-10 | 24-30 |
| Phase 5 | 1 | 6-8 | 6-8 |
| Phase 6 | 1 | 8-10 | 8-10 |
| Phase 7 | 1 | 10-15 | 10-15 |
| **Total** | **12** | **8-10 avg** | **96-123** |

---

## 🎯 Milestones & Checkpoints

### Month 1 (Weeks 1-4)
- ✅ Python fundamentals mastered
- ✅ Understanding of drone components
- ✅ 3D printing knowledge acquired
- **Checkpoint:** Can write geometric calculation scripts

### Month 2 (Weeks 5-8)
- ✅ CadQuery basics mastered
- ✅ First motor mount printed
- ✅ 3+ functional parts designed
- **Checkpoint:** Can design and print basic parts

### Month 3 (Weeks 9-12)
- ✅ Complex multi-feature parts
- ✅ Engineering validation
- ✅ Design automation
- ✅ Complete frame assembly
- **Checkpoint:** Flight-ready quadcopter frame

---

## 💡 Study Tips

### Daily Routine
- **30 min**: Read documentation/tutorials
- **60-90 min**: Hands-on coding/design
- **30 min**: Review and testing

### Weekly Goals
- Set specific deliverable for each week
- Print at least one part per week (after Week 7)
- Document your learning journey
- Join online communities for questions

### Resources to Use Concurrently
- CadQuery documentation
- Drone building forums (RCGroups, IntFPV)
- 3D printing communities (r/3Dprinting)
- YouTube tutorials for specific techniques

---

## 🚀 Accelerated Path (8 Weeks)

If you have prior Python experience:

| Week | Focus |
|------|-------|
| 1 | Phase 0 + 1 (Python + Aircraft basics) |
| 2 | Phase 2 + 3 (Printing + CadQuery basics) |
| 3 | Phase 3 (Advanced CadQuery) |
| 4-5 | Phase 4 (Motor mount, camera, battery, arm) |
| 6 | Phase 4 (Advanced parts + validation) |
| 7 | Phase 5 + 6 (Validation + optimization) |
| 8 | Phase 7 (Final project) |

---

## 🎓 After Completion

Once you finish the 12 weeks, you can:

1. **Contribute to open-source drone projects**
   - Share your designs on Thingiverse/Printables
   - Collaborate on GitHub

2. **Start selling designs**
   - Custom drone frames on Etsy
   - Specialized part designs

3. **Advanced topics**
   - Composite material integration
   - FEA simulation mastery
   - Aerodynamic optimization

4. **Other applications**
   - RC aircraft (fixed-wing)
   - RC cars/boats
   - Robotics parts
   - General mechanical design

---

## 📝 Progress Tracking

Create a checklist and mark off as you complete:

```markdown
## Week 1
- [ ] Python environment set up
- [ ] basic_concepts.py completed
- [ ] Motor mount calculator written
- [ ] Passed Phase 0 checkpoint

## Week 2
- [ ] Classes and OOP mastered
- [ ] geometry_calc.py completed
- [ ] Geometry calculator created
- [ ] Ready for Phase 1
...
```

---

**Good luck on your learning journey! 🚁✨**

Remember: The goal is not speed, but solid understanding. Take your time, experiment, and enjoy the process of creating!
