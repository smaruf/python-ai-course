# RC Aircraft & Autonomous Drone Implementation Guide ✈️🤖

> **Part of [Python AI Course](../README.md)** — A comprehensive implementation reference for building full RC aircraft and fully autonomous drones, from hobby-grade to production-grade systems.  
> See also: [README.md](README.md) | [Learning Schedule](docs/LEARNING_SCHEDULE.md)

This guide covers the full stack: **structural design → active/passive components → firmware → AI autonomy**, across four production tiers from a $50 foam glider to a $50,000+ industrial BVLOS platform.

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Structural Implementation](#2-structural-implementation)
3. [Active and Passive Components](#3-active-and-passive-components)
4. [Firmware Levels](#4-firmware-levels)
5. [Production Tiers](#5-production-tiers)
6. [Multi-Language Firmware](#6-multi-language-firmware)
7. [AI-Based Autonomous Firmware](#7-ai-based-autonomous-firmware)
8. [Getting Started](#8-getting-started)
9. [Safety & Legal](#9-safety--legal)

---

## 1. Overview

Modern unmanned aircraft fall into two broad categories:

| Category | Control Source | Example Use Cases |
|---|---|---|
| **RC Aircraft** | Human pilot via radio link | Sport flying, FPV racing, training |
| **Autonomous Drone** | On-board flight computer + sensors | Mapping, delivery, inspection, swarm ops |

Most production platforms support **both modes simultaneously** — a human can always override an autonomous mission. This guide covers how to design, build, and program both modes from first principles, using open-source toolchains (ArduPilot, PX4, MicroPython) all the way up to DJI-style proprietary stacks.

---

## 2. Structural Implementation

### 2.1 Fixed-Wing RC Aircraft 🛩️

A conventional fixed-wing has a fuselage, separate left/right wings, a horizontal stabilizer, and a vertical stabilizer. Control surfaces are **ailerons** (roll), **elevator** (pitch), and **rudder** (yaw).

**Key structural zones:**

```
[Nose/Spinner] → [Motor Firewall] → [Fuselage Spine] → [Wing Spar Junction]
                                                      ↘ [Tail Boom] → [Stabilizers]
```

- **Wing spar** carries the primary bending load — design in PETG or carbon-fiber-reinforced PLA
- **Firewall** must handle motor thrust + torque reaction; use 4–6 perimeter walls in slicer
- **Servo pockets** are precision-fit; use `tolerances.py` to adjust for your printer

**3D printing notes:**
- Print fuselage halves flat (split along centerline), bond with CA glue + fiberglass tape
- Infill 20–30% gyroid for fuselage, 40–60% rectilinear for structural bulkheads
- See `src/phase4_part_design/drone_arm.py` for a reusable spar socket pattern

---

### 2.2 Flying-Wing RC Aircraft 🪁

A flying-wing has **no separate tail**; pitch and roll are both controlled by **elevons** (combined aileron + elevator). Higher efficiency, lower part count, ideal for FPV and mapping.

**Critical parameters:**

| Parameter | Typical Range | Notes |
|---|---|---|
| Sweep angle | 20°–35° | Stability vs. efficiency trade-off |
| Wash-out (twist) | 2°–4° tip-down | Prevents tip stall |
| Reflexed airfoil | 2–4% reflex | Required for pitch stability without tail |
| CG position | 25–30% MAC | Measure from leading edge of mean chord |

**Design source:** `src/phase1_aircraft_basics/flying_wing_design.py`

---

### 2.3 Quadcopter / Multirotor 🚁

Multirotors achieve 6-DOF control purely through differential motor thrust — **no moving aerodynamic surfaces**. This simplifies mechanical design but demands a fast flight controller loop (≥500 Hz PID).

**Common frame configurations:**

| Config | Arm Count | Motor Layout | Best For |
|---|---|---|---|
| Quad X | 4 | X pattern | FPV racing, general use |
| Quad + | 4 | + pattern | Stable video, legacy |
| Hex X | 6 | X pattern | Payload, redundancy |
| Octo | 8 | X or coaxial | Heavy lift, industrial |
| Tricopter | 3 | Y + tail servo | Efficient, complex |

**Arm sizing rule of thumb:**

```python
# From src/phase4_part_design/drone_arm.py
# 20 mm = minimum clearance (mm) between propeller tip and arm mounting point
arm_length_mm = (prop_diameter_inches * 25.4) / 2 + motor_mount_diameter_mm / 2 + 20
```

**3D printing materials by stress zone:**

| Zone | Recommended Material | Infill |
|---|---|---|
| Motor mount (high vibration) | PETG or CF-PLA | 60–80% |
| Arm tube | CF-PETG or aluminum tube | N/A (solid) |
| Center plate | CF-Nylon or PLA + CF wrap | 40% |
| Landing gear | TPU 95A | 30% gyroid |
| Camera/FPV mount | TPU 85A | 20% |

---

### 2.4 3D Printing Methods & Materials 🖨️

| Material | Strength | Weight | Print Difficulty | Best Use |
|---|---|---|---|---|
| PLA | Medium | Light | Easy | Prototyping, indoor |
| PETG | High | Medium | Easy-Medium | Outdoor frames |
| CF-PLA | High+ | Light | Medium | Motor mounts, arms |
| CF-Nylon | Very High | Medium | Hard | Production structural |
| TPU 85A | Flexible | Medium | Medium | Vibration damping, gear |
| Carbon Fiber (pre-preg) | Extreme | Very Light | Expert | Industrial grade |

---

## 3. Active and Passive Components

### 3.1 Active Components ⚡

| Component | Function | Key Specs |
|---|---|---|
| **Brushless Motor** | Thrust generation | KV rating, stator size (e.g., 2306) |
| **ESC** | Motor speed control | Continuous/burst amps, BLHeli_32/AM32 FW |
| **Servo** | Control surface actuation | Torque (kg·cm), speed (s/60°), digital vs analog |
| **Flight Controller** | Sensor fusion + PID control | CPU (F4/F7/H7), IMU count, barometer |
| **GPS/GNSS** | Position fix | Constellation support, RTK option |
| **Telemetry Radio** | Ground link | SiK 433/915 MHz, DroneCAN, MAVLink |
| **FPV Camera** | Pilot video | NTSC/PAL latency, WDR sensor |
| **FPV VTX** | Video transmission | Power (mW), frequency (5.8 GHz), SmartAudio |
| **RC Receiver** | Pilot command input | SBUS, CRSF, ELRS protocols |
| **LiDAR / Sonar** | Terrain following, obstacle avoidance | Range (m), update rate (Hz) |
| **Optical Flow** | GPS-denied positioning | Frame rate, lens FOV |
| **Companion Computer** | AI inference, mission logic | Raspberry Pi, Jetson Nano, Orange Pi |

---

### 3.2 Passive Components 🔩

| Component | Function | Material Options |
|---|---|---|
| **Frame** | Structural backbone | CF sheet, 3D-printed PLA/PETG/Nylon |
| **Landing Gear** | Ground support | 3D-printed TPU, aluminum rods |
| **Propellers** | Thrust generation | APC, T-Motor, 3D-printed nylon |
| **Battery Mount** | Secure LiPo/Li-Ion pack | Velcro + 3D-printed tray |
| **Wiring Harness** | Power distribution | 12–18 AWG silicone wire + PDB |
| **Connectors** | Modular electrical connections | XT30/XT60 (power), JST-GH (signal) |
| **Vibration Dampers** | Isolate FC from motor noise | TPU printed, M3 rubber standoffs |
| **Antenna Mounts** | GPS/telemetry antenna positioning | 3D-printed PETG |

---

### 3.3 Component Selection by Production Tier

| Component | 🟢 Simple / Hobby | 🟡 Medium / Prosumer | 🔴 Production / Industrial |
|---|---|---|---|
| **Flight Controller** | Betaflight F4 | Pixhawk 4 / Cube Orange | Cube Orange+ / custom H7 |
| **Motor** | Generic 2306 2300KV | T-Motor F60 Pro | T-Motor U8 Lite / Maxon |
| **ESC** | BLHeli_S 35A | BLHeli_32 50A | Zubax Myxa (FOC CAN) |
| **GPS** | BN-220 | Here3 CAN | Here4 RTK |
| **Telemetry** | SiK 100mW | SiK 500mW / RFD900x | RFD900x + LTE modem |
| **Frame** | 3D-printed PLA | 3D-printed CF-PETG | Pre-preg CF machined |
| **Battery** | 4S 1300 mAh LiPo | 6S 5000 mAh LiPo | 22S LiPo / Li-Ion 21700 |
| **OS / FW** | Betaflight | ArduPilot / PX4 | Custom PX4 + RTOS |

---

## 4. Firmware Levels

Firmware complexity scales from a bare-metal C loop reading a PWM receiver up to a full real-time operating system with encrypted communications and hardware redundancy.

---

### Level 1 — Simple (Bare-Metal C / Arduino) 🟢

**Capabilities:** Manual RC passthrough, basic rate stabilisation, no GPS.

```c
// STM32 / Arduino bare-metal PWM read + ESC write
#include <Servo.h>

Servo esc_motor[4];
int pwm_ch[4];

void setup() {
    for (int i = 0; i < 4; i++) {
        esc_motor[i].attach(3 + i);   // pins 3-6
    }
}

void loop() {
    // Read SBUS / PPM from RC receiver
    pwm_ch[0] = pulseIn(2, HIGH);     // throttle
    // Mix throttle + attitude, write to ESCs
    for (int i = 0; i < 4; i++) {
        esc_motor[i].writeMicroseconds(pwm_ch[0]);
    }
}
```

**Stack:** Arduino IDE, STM32duino, or raw CMSIS on STM32F4  
**Loop rate:** 50–400 Hz  
**Sensors:** RC receiver only (no IMU feedback)

---

### Level 2 — Medium (ArduPilot / PX4 Open-Source) 🟡

**Capabilities:** 3-axis stabilisation, GPS position hold, return-to-home, waypoint missions, MAVLink telemetry.

```python
# Ground station MAVLink example (pymavlink)
from pymavlink import mavutil

mav = mavutil.mavlink_connection('udp:127.0.0.1:14550')
mav.wait_heartbeat()

# Arm and take off to 10m
mav.arducopter_arm()
mav.mav.command_long_send(
    mav.target_system, mav.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 10  # altitude = 10 m
)
```

**Stack:** PX4 / ArduPilot + QGroundControl / Mission Planner  
**Loop rate:** 400–1000 Hz (EKF at 50 Hz)  
**Sensors:** IMU, barometer, GPS, compass, optical flow  
**Source:** `src/phase7_integration/hardware_integration.py`

---

### Level 3 — Advanced (Custom PX4 Modules + RTOS) 🟠

**Capabilities:** Custom mission modes, real-time sensor fusion (EKF3), companion computer integration, ROS 2 bridge, precision landing.

```python
# ROS 2 + PX4 uXRCE-DDS bridge (Python node)
import rclpy
from px4_msgs.msg import VehicleOdometry, OffboardControlMode, TrajectorySetpoint

class OffboardController(rclpy.node.Node):
    def __init__(self):
        super().__init__('offboard_ctrl')
        self.sp_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.timer = self.create_timer(0.02, self.send_setpoint)  # 50 Hz

    def send_setpoint(self):
        sp = TrajectorySetpoint()
        sp.position = [0.0, 0.0, -5.0]   # NED: 5 m altitude
        sp.yaw = 0.0
        self.sp_pub.publish(sp)
```

**Stack:** PX4 + NuttX RTOS + ROS 2 Humble + uXRCE-DDS  
**Loop rate:** 1000 Hz (inner loop), 50 Hz (EKF)  
**Hardware:** Cube Orange+, Jetson Orin companion

---

### Level 4 — Proprietary (DJI-Style Stack) 🔴

**Capabilities:** Encrypted RF link, hardware redundancy, obstacle sensing mesh, automated compliance (geofencing, NOTAM), over-the-air firmware updates, fleet management dashboard.

| Feature | Implementation |
|---|---|
| RF encryption | AES-256 on all uplink/downlink |
| Redundant IMUs | Triple IMU voting with FDI |
| Redundant power | Dual battery with OR-ing diode |
| BVLOS compliance | UTM integration, transponder ADS-B |
| OTA updates | Signed firmware bundles, secure bootloader |
| Logging | Encrypted flight data recorder |
| AI inference | On-chip NPU (e.g., RK3588 / Jetson Orin) |

> 💡 **Note:** Building a Level 4 stack is a multi-year engineering effort. Most teams adopt an existing certified platform (DJI, Autel, Skydio) and extend via their SDK.

---

## 5. Production Tiers

### 🟢 Tier 1 — Simple / Hobby ($50–$500)

- **Frame:** Foam-board, PLA 3D print, or cheap CF kit
- **Electronics:** F4 FC, BLHeli_S ESCs, SiK radio, BN-220 GPS
- **Firmware:** Betaflight (racers) or ArduPilot Copter (beginners)
- **Range:** Visual line of sight (VLOS), <1 km
- **Use cases:** FPV freestyle, learning, photography

---

### 🟡 Tier 2 — Medium / Prosumer ($500–$5,000)

- **Frame:** 3D-printed CF-PETG + pultruded CF tubes
- **Electronics:** Cube Orange, Here3 GPS, RFD900x telemetry
- **Firmware:** ArduPilot with custom tuning, or PX4
- **Range:** VLOS/EVLOS up to 5 km with proper antenna
- **Use cases:** Aerial photography, precision agriculture, survey

---

### 🔴 Tier 3 — Production / Industrial ($5,000–$50,000+)

- **Frame:** Pre-preg carbon fiber, machined aluminum inserts
- **Electronics:** Triple-redundant FC, RTK GPS, LTE modem
- **Firmware:** Custom PX4 modules + RTOS + certified software
- **Range:** BVLOS with UTM integration
- **Use cases:** Infrastructure inspection, emergency response, cargo delivery

---

### ⚫ Tier 4 — Specialized / Tactical / Supply

> ⚠️ **Covered here for academic/contextual purposes only.** Building or deploying tactical drones may require government authorization and export control compliance (ITAR/EAR).

| Sub-type | Key Characteristics |
|---|---|
| **Long-range ISR** | Fixed-wing, >100 km range, encrypted HD downlink |
| **Payload delivery** | Precision release mechanism, RTK landing, cold chain monitoring |
| **Loitering munition** | Proportional navigation, terminal guidance (classified stack) |
| **Swarm / coordinated** | Mesh networking, distributed consensus, centralized C2 |
| **Counter-UAS** | RF jamming, net capture, kinetic intercept |

---

## 6. Multi-Language Firmware

Different languages target different points on the **performance vs. development-speed** curve.

### 6.1 Python (MicroPython / CircuitPython) 🐍

Best for rapid prototyping, AI integration on companion computers, and high-level mission logic.

```python
# MicroPython — bare-metal ESC control on RP2040
from machine import Pin, PWM
import time

throttle = PWM(Pin(0), freq=50)

def set_throttle(percent: float) -> None:
    """Set ESC throttle 0.0–1.0 → 1000–2000 µs pulse."""
    us = int(1000 + percent * 1000)
    throttle.duty_ns(us * 1000)

# Arm sequence
set_throttle(0.0)
time.sleep(2)
# Ramp up
for t in range(0, 50, 5):
    set_throttle(t / 100)
    time.sleep(0.1)
```

**Platforms:** Raspberry Pi (Linux Python), RP2040, ESP32, STM32  
**AI libraries:** TensorFlow Lite, ONNX Runtime, OpenCV (companion)

---

### 6.2 TinyGo 🔵

Memory-safe embedded Go — garbage-collected but with a tiny runtime footprint. Great for sensor drivers and state machines.

```go
// TinyGo — I2C IMU read on Arduino Nano 33 BLE
package main

import (
    "machine"
    "tinygo.org/x/drivers/lsm6ds3"
)

func main() {
    machine.I2C0.Configure(machine.I2CConfig{})
    imu := lsm6ds3.New(machine.I2C0)
    imu.Configure()

    for {
        ax, ay, az, _ := imu.ReadAcceleration()
        // ax, ay, az feed into the PID loop in a full implementation
        println(ax, ay, az)
    }
}
```

**Platforms:** Arduino Nano 33, BBC micro:bit, STM32, ESP32  
**Strength:** Memory safety, fast compile, small binary

---

### 6.3 Zig ⚡

Low-level, no hidden allocations, comptime metaprogramming. Ideal for safety-critical flight control where C is too unsafe and Rust is too complex.

```zig
// Zig — PWM output for motor control
const std = @import("std");
const hal = @import("hal"); // HAL abstraction

pub fn setMotorThrottle(channel: u8, throttle_us: u16) void {
    std.debug.assert(throttle_us >= 1000 and throttle_us <= 2000);
    hal.pwm.setDutyMicros(channel, throttle_us);
}
```

**Strength:** C-interop, no runtime, explicit allocation, comptime checks  
**Use case:** Custom flight controller kernel, bootloader, safety monitors

---

### 6.4 Basic C (Arduino / STM32 HAL) 💻

The lingua franca of embedded drone development. Maximum hardware support, zero runtime overhead.

```c
// STM32 HAL — timer-based PWM for ESC
#include "stm32f4xx_hal.h"

TIM_HandleTypeDef htim3;

void Motor_SetThrottle(uint8_t ch, uint16_t us) {
    // us: 1000 (min) to 2000 (max)
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1 + ch, us);
}
```

**Platforms:** STM32F4/F7/H7, AVR, ESP32 (IDF)  
**Use case:** Flight controller firmware kernels (Betaflight, PX4 HAL layer)

---

### 6.5 Language Comparison Table

| Language | Performance | Memory Safety | Dev Speed | AI/ML Support | Embedded Support |
|---|---|---|---|---|---|
| **Python** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ (MicroPython) |
| **TinyGo** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Zig** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **C (bare-metal)** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **C++ (ArduPilot)** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 7. AI-Based Autonomous Firmware

### 7.1 AI Flight Path Planning 🗺️

#### A* Waypoint Navigation

```python
import heapq
from typing import List, Tuple

def astar(grid: list, start: Tuple, goal: Tuple) -> List[Tuple]:
    """A* pathfinding on a 2D occupancy grid (0=free, 1=obstacle)."""
    open_set = [(0, start)]
    came_from = {}
    g = {start: 0}

    def h(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])  # Manhattan heuristic

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nb = (current[0]+dx, current[1]+dy)
            if 0 <= nb[0] < len(grid) and 0 <= nb[1] < len(grid[0]):
                if grid[nb[0]][nb[1]] == 0:
                    new_g = g[current] + 1
                    if new_g < g.get(nb, float('inf')):
                        came_from[nb] = current
                        g[nb] = new_g
                        heapq.heappush(open_set, (new_g + h(nb, goal), nb))
    return []  # no path found
```

#### RRT* for 3D Obstacle-Rich Environments

```python
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RRTNode:
    pos: np.ndarray
    parent: Optional['RRTNode'] = None
    cost: float = 0.0

def rrt_star(start: np.ndarray, goal: np.ndarray,
             obstacles: list, n_iter: int = 500,
             step: float = 1.0, goal_radius: float = 1.5) -> list:
    """RRT* planner for 3D drone navigation."""
    nodes = [RRTNode(pos=start)]

    for _ in range(n_iter):
        rand = np.random.uniform(-50, 50, 3)
        nearest = min(nodes, key=lambda n: np.linalg.norm(n.pos - rand))
        direction = rand - nearest.pos
        norm = np.linalg.norm(direction)
        new_pos = nearest.pos + (direction / norm) * min(step, norm)

        # Simple sphere obstacle check
        if any(np.linalg.norm(new_pos - obs[:3]) < obs[3] for obs in obstacles):
            continue

        new_node = RRTNode(pos=new_pos, parent=nearest,
                           cost=nearest.cost + step)
        nodes.append(new_node)

        if np.linalg.norm(new_pos - goal) < goal_radius:
            path, node = [], new_node
            while node:
                path.append(node.pos.tolist())
                node = node.parent
            return path[::-1]
    return []
```

---

### 7.2 GPS Navigation & Return-to-Home 📡

```python
import math

def haversine(lat1, lon1, lat2, lon2) -> float:
    """Returns distance in meters between two GPS coordinates."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def bearing(lat1, lon1, lat2, lon2) -> float:
    """Returns bearing in degrees (0=North, 90=East)."""
    dlam = math.radians(lon2 - lon1)
    x = math.sin(dlam) * math.cos(math.radians(lat2))
    y = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2))
         - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dlam))
    return (math.degrees(math.atan2(x, y)) + 360) % 360

class ReturnToHome:
    def __init__(self, home_lat, home_lon, home_alt_m, rth_speed_ms=5.0):
        self.home = (home_lat, home_lon, home_alt_m)
        self.speed = rth_speed_ms

    def navigate(self, current_lat, current_lon, current_alt):
        dist = haversine(current_lat, current_lon, self.home[0], self.home[1])
        hdg  = bearing(current_lat, current_lon, self.home[0], self.home[1])
        alt_err = self.home[2] - current_alt
        return {"distance_m": round(dist, 1),
                "heading_deg": round(hdg, 1),
                "altitude_correction_m": round(alt_err, 1)}
```

---

### 7.3 Object Avoidance (Vision + LiDAR) 👁️

```python
import numpy as np

class ObstacleAvoider:
    """Velocity-Obstacle (VO) based collision avoidance."""

    def __init__(self, safety_radius_m: float = 2.0):
        self.r = safety_radius_m

    def compute_avoidance_velocity(self,
            drone_pos: np.ndarray,
            drone_vel: np.ndarray,
            obstacles: list,      # list of (pos, vel, radius) tuples
            desired_vel: np.ndarray) -> np.ndarray:
        """Returns adjusted velocity that avoids all obstacles."""
        avoidance = np.zeros(3)
        for obs_pos, obs_vel, obs_r in obstacles:
            rel_pos = obs_pos - drone_pos
            dist = np.linalg.norm(rel_pos)
            combined_r = self.r + obs_r
            if dist < combined_r * 3:           # within influence zone
                push = (drone_pos - obs_pos)
                weight = max(0, 1 - dist / (combined_r * 3))
                avoidance += push / (dist + 1e-9) * weight * 5.0
        return desired_vel + avoidance

    @staticmethod
    def lidar_to_pointcloud(scan_ranges: list, angle_min: float,
                            angle_increment: float) -> np.ndarray:
        """Convert 2D LiDAR scan to XY point cloud."""
        import math
        points = []
        for i, r in enumerate(scan_ranges):
            if 0.1 < r < 30.0:
                angle = angle_min + i * angle_increment
                points.append([r * math.cos(angle), r * math.sin(angle), 0])
        return np.array(points)
```

---

### 7.4 Kamikaze / Impact Drone Behavior ⚠️

> ⚠️ **This section is included strictly for academic, defensive research, and counter-UAS awareness purposes.** Deploying impact drones (loitering munitions) without proper military/government authorization is illegal in most jurisdictions.

**Proportional Navigation (PN) guidance** — the core algorithm used in terminal-phase intercept:

```python
def proportional_navigation(los_rate_rad_s: float,
                             closing_speed_m_s: float,
                             N: float = 4.0) -> float:
    """
    Returns lateral acceleration command (m/s²).
    N: navigation constant (typically 3–5)
    los_rate_rad_s: line-of-sight angular rate (rad/s)
    closing_speed_m_s: relative closing velocity (m/s)
    """
    return N * closing_speed_m_s * los_rate_rad_s
```

**Behavioral state machine for loitering:**

```
LAUNCH → CLIMB → LOITER (search orbit) → TRACK (target acquired) → DIVE (terminal)
```

Countermeasures (for defensive study): RF jamming on 433/915 MHz/2.4 GHz, GPS spoofing detection, optical signature masking, net-capture systems.

---

### 7.5 Swarm Coordination 🐝

```python
import numpy as np
from dataclasses import dataclass, field
from typing import List

@dataclass
class SwarmAgent:
    id: int
    pos: np.ndarray
    vel: np.ndarray = field(default_factory=lambda: np.zeros(3))

    # Boids-style coefficients
    W_SEP: float = 1.5    # separation weight
    W_ALI: float = 1.0    # alignment weight
    W_COH: float = 1.0    # cohesion weight
    SEP_R: float = 3.0    # separation radius (m)
    NEIGH_R: float = 10.0 # neighbourhood radius (m)

    def update(self, agents: List['SwarmAgent'], goal: np.ndarray, dt: float = 0.05):
        neighbours = [a for a in agents
                      if a.id != self.id
                      and np.linalg.norm(a.pos - self.pos) < self.NEIGH_R]
        sep = ali = coh = np.zeros(3)

        for n in neighbours:
            diff = self.pos - n.pos
            dist = np.linalg.norm(diff) + 1e-9
            if dist < self.SEP_R:
                sep += diff / dist**2          # repulsion

        if neighbours:
            ali = np.mean([n.vel for n in neighbours], axis=0) - self.vel
            coh = np.mean([n.pos for n in neighbours], axis=0) - self.pos

        goal_vec = goal - self.pos
        accel = (self.W_SEP * sep
                 + self.W_ALI * ali
                 + self.W_COH * coh
                 + 2.0 * goal_vec / (np.linalg.norm(goal_vec) + 1e-9))

        self.vel = np.clip(self.vel + accel * dt, -8, 8)  # max 8 m/s
        self.pos += self.vel * dt
```

---

## 8. Getting Started

### 8.1 Quick-Start Checklist ✅

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Run the aircraft basics examples
python examples/intermediate/all_aircraft_types.py

# 3. Run all tests to verify setup
python -m pytest tests/ -v

# 4. Launch main entry point
python main.py
```

### 8.2 Relevant Source Files

| Task | Source File |
|---|---|
| Aircraft type definitions | `src/phase1_aircraft_basics/aircraft_types.py` |
| Fixed-wing design logic | `src/phase1_aircraft_basics/fixed_wing_design.py` |
| Flying-wing design logic | `src/phase1_aircraft_basics/flying_wing_design.py` |
| Multirotor / quadcopter | `src/phase1_aircraft_basics/rotorcraft_design.py` |
| Aerodynamics (lift/drag) | `src/phase1_aircraft_basics/aerodynamics.py` |
| Material properties | `src/phase2_3d_printing/materials.py` |
| Motor mount CAD | `src/phase4_part_design/motor_mount.py` |
| Landing gear CAD | `src/phase4_part_design/landing_gear.py` |
| Battery tray CAD | `src/phase4_part_design/battery_tray.py` |
| Structural checks | `src/phase5_validation/structural_checks.py` |
| ArduPilot/PX4 integration | `src/phase7_integration/hardware_integration.py` |

### 8.3 Recommended Learning Path

```
Phase 0 → Foundations (geometry, Python)
  ↓
Phase 1 → Aircraft types (fixed-wing, flying-wing, multirotor, autogyro)
  ↓
Phase 2 → 3D printing materials and tolerances
  ↓
Phase 3 → CadQuery parametric CAD
  ↓
Phase 4 → Part design (motor mount, arm, battery tray, landing gear)
  ↓
Phase 5 → Structural validation
  ↓
Phase 6 → Design optimisation (weight vs. strength)
  ↓
Phase 7 → Hardware integration + AI autonomy
```

---

## 9. Safety & Legal ⚖️

### 9.1 Flight Safety

> 🚨 **Always verify hardware before first flight.** A mechanical failure at altitude is unrecoverable.

- **Pre-flight checklist:** Motor rotation direction, prop security, CG balance, battery voltage, RC link test, failsafe armed
- **Maiden flights:** Fly over a soft field, low altitude, minimal wind, with a spotter
- **3D-printed parts:** Inspect for layer delamination, micro-cracks at screw holes, and UV degradation after sun exposure
- **LiPo safety:** Never leave charging unattended; use a LiPo-safe bag; discard swollen cells immediately
- **Prop strikes:** Replace props after any ground strike — invisible micro-cracks can cause in-flight failure

### 9.2 Regulations by Region

| Region | Authority | Key Rules |
|---|---|---|
| 🇺🇸 USA | FAA Part 107 | Registration >250 g, VLOS, <400 ft AGL, airspace authorisation (LAANC) |
| 🇪🇺 EU | EASA Open/Specific | CE class marking, registration, UA operator certificate |
| 🇬🇧 UK | CAA | Flyer ID + Operator ID, Congestion Zone restrictions |
| 🇨🇦 Canada | Transport Canada | RPAS registration, basic/advanced operations certificate |
| 🌏 Rest of World | Varies | Always check national CAA; many require local permits |

### 9.3 Autonomous / BVLOS Operations

- Requires **specific operations risk assessment (SORA)** in EU / equivalent waiver in USA
- LTE or satellite backup link required for command & control
- ADS-B In/Out or Remote ID broadcast mandatory in most jurisdictions from 2024+
- For swarm operations: additional coordination with ATC typically required

### 9.4 Export Controls

- Drone technology may be subject to **ITAR** (International Traffic in Arms Regulations) or **EAR** (Export Administration Regulations) in the USA
- Carbon-fiber airframes, encrypted radios, and long-range autonomous systems can be dual-use items
- Always check before shipping hardware or sharing firmware internationally

---

## 🔗 Related Projects in This Repository

- **[AI Development Project](../ai-development-project/)** — AI/ML model integration
- **[Algorithms & Data Structures](../algorithms-and-data-structures/)** — Pathfinding algorithm implementations
- **[Philomath AI](../philomath-ai/)** — Reinforcement learning exploration

---

**Happy Building & Flying! 🚁✨**

For questions or contributions, please open an issue in the repository.
