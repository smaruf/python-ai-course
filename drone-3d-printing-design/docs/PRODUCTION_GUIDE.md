# Drone Production Guide

> **Part of [Python AI Course](../../README.md)** — A comprehensive reference for building drones across all production tiers, from sub-$100 hobby quads to industrial BVLOS platforms.  
> See also: [IMPLEMENTATION_GUIDE.md](../IMPLEMENTATION_GUIDE.md) | [FIRMWARE_GUIDE.md](FIRMWARE_GUIDE.md) | [AI_FLIGHT_GUIDE.md](AI_FLIGHT_GUIDE.md)

This guide covers the complete production lifecycle — hardware selection, assembly, firmware, quality assurance, and regulatory compliance — across five tiers from a beginner's first build to industrial-scale deployment.

---

## 📋 Table of Contents

1. [Production Tier Classification](#1-production-tier-classification)
2. [Tier 1: Simple / Hobby Drones](#2-tier-1-simplehobby-drones-50500)
3. [Tier 2: Medium / Prosumer Drones](#3-tier-2-mediumprosumer-drones-5005000)
4. [Tier 3: Production / Industrial Drones](#4-tier-3-productionindustrial-drones-500050000)
5. [Tier 4: Military / Tactical Drones](#5-tier-4-militarytactical-drones-context--study)
6. [Tier 5: Supply / Delivery Drones](#6-tier-5-supplydelivery-drones)
7. [Quality Assurance](#7-quality-assurance)
8. [Regulatory Compliance](#8-regulatory-compliance)

---

## 1. Production Tier Classification

Each tier is a distinct engineering discipline, not just a price bracket. Moving up a tier typically means adding redundancy, certification burden, and operational complexity — not just more expensive parts.

| Tier | Name | Budget | Primary Use | Regulatory Class |
|---|---|---|---|---|
| 1 | Simple / Hobby | $50–$500 | Learning, FPV, basic photography | FAA Part 107 or recreational |
| 2 | Medium / Prosumer | $500–$5,000 | Professional photo, inspection, agri | FAA Part 107 (commercial) |
| 3 | Production / Industrial | $5,000–$50,000 | BVLOS, delivery, critical inspection | FAA Part 135 / type certification |
| 4 | Military / Tactical | Government contract | ISR, EW, tactical logistics | ITAR/EAR — export controlled |
| 5 | Supply / Delivery | $10,000–$100,000+ | Urban air mobility, fleet logistics | FAA Part 135 + UTM integration |

**Design rule of thumb:** Each tier up doubles reliability requirements and roughly 10× the certification overhead.

```
Tier 1 → Tier 2: add GPS, dual IMU, proper ground station
Tier 2 → Tier 3: add redundant everything, RTOS, encrypted comms, weather sealing
Tier 3 → Tier 5: add type cert, DAL-C software, fleet ops infrastructure
```

---

## 2. Tier 1: Simple/Hobby Drones ($50–$500)

### Target Use Cases
- Learning to fly and tune multirotors
- FPV freestyle and racing
- Basic aerial photography (non-commercial)
- Testing firmware modifications and algorithms

### Frame

3D-printed frames in **PLA or PETG** are viable at this tier — crashes are frequent and reprinting arms is faster than ordering replacements. Foam board fuselages (EPP/EPS) are standard for fixed-wing.

| Material | Best For | Print Settings |
|---|---|---|
| PLA | Arm prototypes, light frames | 4 perimeters, 40% gyroid infill |
| PETG | Arms that flex on impact | 4 perimeters, 30% gyroid infill |
| TPU 95A | Motor mounts, vibration isolation | 3 perimeters, 20% gyroid infill |
| EPP foam | Fixed-wing fuselage/wings | Cut and bond, no printing needed |

**Standard frames:** 5" quad (210 mm), 3" micro quad (130 mm), FT Flyer foam fixed-wing.

### Electronics

| Component | Recommended Part | Notes |
|---|---|---|
| Flight Controller | SpeedyBee F405 / Matek F722 | F7 preferred for blackbox + OSD |
| ESC | 4-in-1 35A BLHeli_32 | Bidirectional DSHOT for RPM filtering |
| Motors | 2306 2400KV (5") / 1404 3800KV (3") | Match KV to prop+battery combo |
| Props | HQProp 5×4.3×3 (5") | Tri-blade for freestyle, bi-blade for efficiency |
| Battery | 4S 1300–1500 mAh LiPo (5") | 45C+ discharge rating |
| Receiver | ExpressLRS 2.4 GHz | Sub-5 ms latency, free/open-source |
| VTX | 25–200 mW 5.8 GHz | Use legal power limits for your region |
| Camera (FPV) | RunCam Phoenix 2 / Caddx Ratel 2 | WDR sensor for mixed lighting |
| GPS (optional) | BN-220 or BN-880 | Required for position hold and RTH |

### Firmware: Betaflight / iNAV

**Betaflight** is the standard for freestyle/racing; **iNAV** adds GPS navigation capabilities.

```
# Betaflight CLI — minimal tuning baseline (5" quad, 4S)
set gyro_lpf2_static_hz = 0          # disable static LPF2, use RPM filter
set dyn_notch_count = 1
set dyn_notch_q = 500
set motor_pwm_protocol = DSHOT300
set pid_process_denom = 2            # 4 kHz PID loop on F7

# PID starting point (tune per-build)
set p_roll  = 42
set i_roll  = 85
set d_roll  = 38
set p_pitch = 46
set i_pitch = 88
set d_pitch = 42
set p_yaw   = 40
set i_yaw   = 80
```

```
# iNAV GPS navigation modes
# Enable in Configurator → Modes tab:
# ARM / ANGLE / NAV ALTHOLD / NAV POSHOLD / NAV RTH / FAILSAFE
```

### Assembly Guide Summary

1. **Print frame** — arms first; test-fit motors before printing centre plate
2. **Solder power** — battery lead → XT30/60 → 4-in-1 ESC → motor wires (check direction)
3. **Stack electronics** — ESC bottom, FC top; use M3 nylon standoffs + anti-vibration grommets
4. **Bind receiver** — match UART/protocol in Betaflight Ports tab
5. **Motor direction test** — spin each motor in Betaflight Motor tab; reverse by swapping two wires
6. **Prop guards / props** — install last; confirm correct rotation pattern (X config: CW front-left & rear-right)
7. **First hover** — over soft grass; trim throttle mid-point, check stability

### Bill of Materials — Tier 1 (5" Freestyle Quad)

| # | Component | Part / Source | Qty | Unit Price | Total |
|---|---|---|---|---|---|
| 1 | Frame arms (PETG) | Self-printed (filament ~$0.80/arm) | 4 | $0.80 | $3.20 |
| 2 | Centre plate (PETG) | Self-printed | 1 | $1.50 | $1.50 |
| 3 | Flight controller | SpeedyBee F405 v3 | 1 | $35 | $35 |
| 4 | 4-in-1 ESC | SpeedyBee BLS 35A | 1 | $30 | $30 |
| 5 | Motors | Emax ECO II 2306 | 4 | $14 | $56 |
| 6 | Props | HQProp 5×4.3×3 | 4 pairs | $2 | $8 |
| 7 | Battery | CNHL 4S 1300 mAh 100C | 2 | $22 | $44 |
| 8 | Receiver | ELRS Happymodel EP2 | 1 | $12 | $12 |
| 9 | FPV camera | RunCam Phoenix 2 | 1 | $28 | $28 |
| 10 | VTX | AKK X2-ultimate 25–400 mW | 1 | $18 | $18 |
| 11 | Hardware kit | M3 standoffs, screws, zip ties | 1 | $8 | $8 |
| 12 | XT30 connectors | XT30 pair + 14 AWG wire | 1 | $4 | $4 |
| **Total** | | | | | **~$248** |

---

## 3. Tier 2: Medium/Prosumer Drones ($500–$5,000)

### Target Use Cases
- Professional aerial photography and videography
- Agricultural spraying and mapping
- Infrastructure inspection (powerlines, bridges)
- Search and rescue support

### Frame

Commercial-grade frames use **carbon fibre (CF) tubes and CNC-machined aluminium plates**. 3D printing is still used for non-structural mounts (gimbal plate, camera hood, antenna brackets).

| Material | Application | Source |
|---|---|---|
| 3K CF tube, 16 mm OD | Folding arms | RCTimer / Hobby King |
| 3 mm CF plate | Top/bottom plates, motor mounts | Rockwest Composites |
| 6061-T6 aluminium | Yaw bearing, payload rail | CNC from DXF file |
| PETG / CF-PETG | Gimbal tray, antenna mast | Self-printed |

**Standard platforms:** DJI F450 clone (450 mm), Tarot 650, Foxtech Hover 1 (hexacopter).

### Electronics

| Component | Recommended Part | Notes |
|---|---|---|
| Flight Controller | Cube Orange+ or Pixhawk 6C | Dual IMU standard; Cube has isolated IMU |
| Companion Computer | Raspberry Pi 4 or NVIDIA Jetson Nano | Runs mission software, video processing |
| ESC | Zubax Myxa or T-Motor Flame 60A | CAN-bus preferred over PWM at this tier |
| Motors | T-Motor MN3508 / Antigravity 4004 | Efficiency-rated, >10:1 thrust/weight |
| Battery | 6S 10,000–16,000 mAh LiPo smart | Use BMS-equipped packs for safety |
| GPS | Here3+ (CAN) or uBlox F9P | RTK-capable F9P for survey-grade position |
| Dual GPS | Two Here3+ for heading + redundancy | ArduCopter supports GPS yaw |
| Gimbal | DJI RS3 Pro or Gremsy T3 | 3-axis stabilisation; UART/CAN control |
| Telemetry | Herelink or RFD900x | 30+ km range; Herelink integrates GCS |
| Lidar (optional) | TF-Luna / Benewake CE30 | Terrain following and landing assist |

### Firmware: ArduPilot / PX4

**ArduCopter (ArduPilot)** is the community standard for professional multirotors. It supports full autonomous missions, geofencing, terrain following, and SITL simulation.

```python
# ArduPilot parameter baseline — hexacopter, 6S, T-Motor
# Load via Mission Planner → Full Parameter List

MOT_THST_EXPO    = 0.65   # motor thrust expo (calibrate empirically)
MOT_SPIN_ARM     = 0.10   # minimum spin on arm
MOT_SPIN_MIN     = 0.15   # minimum spin in flight
INS_GYRO_FILTER  = 20     # gyro LPF (Hz) — increase for larger craft
ATC_RAT_RLL_P    = 0.135  # roll rate P (start low, tune up)
ATC_RAT_RLL_I    = 0.135
ATC_RAT_RLL_D    = 0.0036
BATT_MONITOR     = 4      # voltage + current monitor enabled
BATT_LOW_VOLT    = 21.0   # 6S low voltage warning (3.5 V/cell)
BATT_CRT_VOLT    = 19.8   # critical — RTL trigger (3.3 V/cell)
FS_THR_ENABLE    = 1      # throttle failsafe → RTL
GCS_PID_MASK     = 0      # disable PID tuning in flight (production)
```

### Redundancy Basics

At this tier, add these safety layers:

- **Dual GPS** — ArduCopter blends both; detects multipath/jamming
- **Dual battery monitor** — independent voltage sensor on second battery
- **Geofence** — hard altitude and radius limits in firmware
- **RC failsafe** — RTL after 1.5 s signal loss
- **Pre-arm checks** — never override; fix root cause instead

### Bill of Materials — Tier 2 (Hexacopter, Mapping Platform)

| # | Component | Part / Source | Qty | Unit Price | Total |
|---|---|---|---|---|---|
| 1 | Frame kit | Tarot T960 hexacopter frame | 1 | $220 | $220 |
| 2 | Flight controller | Cube Orange+ | 1 | $280 | $280 |
| 3 | Carrier board | Cube Standard Carrier | 1 | $85 | $85 |
| 4 | GPS/compass | Here3+ GNSS (CAN) | 2 | $130 | $260 |
| 5 | ESCs | T-Motor Flame 60A HV | 6 | $55 | $330 |
| 6 | Motors | T-Motor MN3508 580KV | 6 | $58 | $348 |
| 7 | Props | 15×5.5" CF folding | 6 pairs | $18 | $108 |
| 8 | Battery | Tattu Plus 6S 16000 mAh smart | 2 | $185 | $370 |
| 9 | Telemetry | RFD900x modem pair | 1 | $180 | $180 |
| 10 | GCS tablet | Herelink controller | 1 | $530 | $530 |
| 11 | Gimbal | Gremsy T3 | 1 | $680 | $680 |
| 12 | Camera | Sony A7C (payload) | 1 | $1,800 | $1,800 |
| 13 | Companion PC | RPi 4B 4 GB | 1 | $75 | $75 |
| 14 | Power module | Mauch PL Series 200A | 1 | $68 | $68 |
| 15 | Misc hardware | CF standoffs, wire, heat shrink | 1 | $65 | $65 |
| **Total** | | | | | **~$5,399** |

> *Target lower-end of tier by substituting Sony camera with a GoPro Hero 12 (~$400 saving) and Herelink with RFD900x + laptop GCS.*

---

## 4. Tier 3: Production/Industrial Drones ($5,000–$50,000)

### Target Use Cases
- BVLOS (Beyond Visual Line Of Sight) corridor inspection
- Last-mile package delivery
- Offshore oil/gas platform inspection (IP67 required)
- Emergency medical supply delivery

### Frame

Industrial frames are custom-engineered for fatigue life, weather sealing, and maintainability.

| Component | Specification | Rationale |
|---|---|---|
| Monocoque shell | 12K CF prepreg, autoclave-cured | Maximum stiffness/weight; no fastener holes in skin |
| Arm tubes | Pultruded CF, 25 mm OD, 2 mm wall | Certified modulus, consistent properties |
| Motor mounts | Machined 7075-T6 aluminium | Bearing-race quality surface for vibration isolation |
| Sealing | IP67 gaskets, conformal coating on PCBs | Withstand 30 min at 1 m submersion |
| Thermal | Heat pipes + forced air on ESC/motor | Continuous duty at 45°C ambient |

### Electronics

| Component | Specification | Notes |
|---|---|---|
| Flight Controller | Pixhawk 6X or custom STM32H7 | Triple-redundant IMU (ICM-42688 × 3) |
| Secondary FC | CAN-connected backup node | Monitors primary; takes over on watchdog timeout |
| GNSS | uBlox F9P × 2 (GPS+GLONASS+BeiDou) | RTK corrections via LTE; dual-antenna heading |
| LTE/5G modem | Sierra Wireless RV55 or Quectel RM500Q | Primary C2 link; redundant to RF |
| RF Datalink | Digi XBee 900 HP or Microhard pDDL | RF fallback C2; AES-256 encrypted |
| Computer | NVIDIA Jetson Orin NX 16 GB | AI inference, HD video encode, mission logic |
| ESC | Myxa/Kotleta20 (CAN bus) | Per-motor telemetry; field-updatable firmware |
| Battery management | Smart BMS, cell-level monitoring | SOH tracking, fault logging, charge balancing |
| Payload interface | MIL-DTL-38999 connector, CAN + power | Hot-swap payload capability |

### Firmware Architecture

```
┌─────────────────────────────────────────────────────┐
│  Mission Computer (Jetson Orin)                     │
│  ┌─────────────┐  ┌────────────┐  ┌─────────────┐  │
│  │ Mission Mgr │  │ Video/AI   │  │  Fleet API  │  │
│  │ (ROS2)      │  │ (TensorRT) │  │  (MQTT/TLS) │  │
│  └──────┬──────┘  └────────────┘  └─────────────┘  │
│         │ MAVLink2 over UART/UDP                     │
├─────────┼───────────────────────────────────────────┤
│  Primary FC (Pixhawk 6X, ArduPilot 4.x custom)      │
│  ┌──────┴──────┐  ┌────────────┐  ┌─────────────┐  │
│  │ Sensor Fuse │  │ PID/EKF3   │  │  Failsafe   │  │
│  │ Triple IMU  │  │ 400 Hz     │  │  State Mach │  │
│  └─────────────┘  └────────────┘  └──────┬──────┘  │
│         │ CAN FD bus                      │         │
│  ┌──────┴──────────────────────────┐      │         │
│  │ ESC nodes × 6/8 (Myxa)         │      │         │
│  └─────────────────────────────────┘      │         │
│                                            │         │
│  Backup FC (CAN watchdog node) ◄───────────┘         │
└─────────────────────────────────────────────────────┘
```

**Encrypted telemetry snippet (Python, MavProxy plugin):**

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, struct

class EncryptedTelemetryChannel:
    def __init__(self, key_bytes: bytes):
        self.aesgcm = AESGCM(key_bytes)   # 256-bit key

    def encrypt_packet(self, mavlink_bytes: bytes) -> bytes:
        nonce = os.urandom(12)            # 96-bit random nonce
        ct    = self.aesgcm.encrypt(nonce, mavlink_bytes, None)
        return nonce + ct                 # prepend nonce for decryption

    def decrypt_packet(self, raw: bytes) -> bytes:
        nonce, ct = raw[:12], raw[12:]
        return self.aesgcm.decrypt(nonce, ct, None)
```

### Certification Requirements

| Certification | Requirement | Lead Time |
|---|---|---|
| FAA Part 107 waiver | BVLOS, night ops, over-people | 6–18 months |
| FAA Part 135 air carrier | Delivery operations | 12–36 months |
| CE Marking (EU) | Radio, EMC, RoHS compliance | 3–6 months + lab testing |
| FCC Part 15/47 | RF transmitter certification | 2–4 months |
| IP67 testing | IEC 60529 ingress protection | 2–4 weeks (3rd party lab) |
| DO-160G | Environmental qualification | Per test section; 3–6 months |

### Bill of Materials — Tier 3 (BVLOS Inspection Hexacopter)

| # | Component | Specification | Qty | Unit Price | Total |
|---|---|---|---|---|---|
| 1 | CF monocoque frame | Custom autoclave layup | 1 | $2,400 | $2,400 |
| 2 | Primary FC | Pixhawk 6X | 1 | $520 | $520 |
| 3 | Backup FC node | mRo UAVCAN node | 1 | $145 | $145 |
| 4 | Dual RTK GNSS | uBlox F9P × 2 custom PCB | 2 | $320 | $640 |
| 5 | CAN ESC | Myxa 3.x (Field-orientated control) | 6 | $180 | $1,080 |
| 6 | Motors | T-Motor U8 II 100KV | 6 | $165 | $990 |
| 7 | Props | T-Motor 28×9.2" CF | 6 pairs | $85 | $510 |
| 8 | Battery | 12S 30,000 mAh smart LiPo | 2 | $680 | $1,360 |
| 9 | Mission computer | NVIDIA Jetson Orin NX 16 GB | 1 | $490 | $490 |
| 10 | LTE modem | Quectel RM500Q + antenna | 1 | $310 | $310 |
| 11 | RF datalink | Microhard pDDL900 pair | 1 | $1,200 | $1,200 |
| 12 | Payload camera | FLIR Vue TZ20-R (thermal+EO) | 1 | $5,800 | $5,800 |
| 13 | Gimbal | Gremsy H16 (heavy payload) | 1 | $1,850 | $1,850 |
| 14 | BMS unit | Custom 12S BMS + CAN | 2 | $220 | $440 |
| 15 | IP67 sealing kit | Gaskets, conformal coat, glands | 1 | $380 | $380 |
| 16 | Structural hardware | MIL-spec fasteners, wire harness | 1 | $620 | $620 |
| **Total** | | | | | **~$16,735** |

---

## 5. Tier 4: Military/Tactical Drones (Context & Study)

> ⚠️ **Important Notice:** This section is provided for **educational context and academic study only**. Development, export, and sale of military UAS systems is governed by **ITAR (International Traffic in Arms Regulations)** and **EAR (Export Administration Regulations)**. Manufacturing or exporting listed items without proper licensing is a federal crime. No production instructions are given here.

### Loitering Munitions (Switchblade-type) — Context Only

Loitering munitions (e.g., AeroVironment Switchblade 300/600, Teledyne FLIR Altius) are tube-launched, GPS/INS/EO-guided munitions that orbit a target before terminal guidance. Key subsystems from a systems-engineering perspective:

- **EO/IR seeker** — dual-mode electro-optical + infrared with image-based target tracking (deep learning CNN)
- **INS/GNSS** — GPS anti-jam, inertial fallback for GPS-denied environments
- **Warhead integration** — requires ATF licensing; not covered here
- **Datalink** — frequency-hopping spread spectrum, AES-256, jam-resistant

### Long-Range ISR Drones — Context Only

Platforms such as the RQ-4 Global Hawk and MQ-9 Reaper class operate at FL600+ for 24–40 hour endurance, carrying multi-spectral sensor suites. Key design considerations (academic):

| Parameter | Typical Specification |
|---|---|
| Wingspan | 35–40 m (Global Hawk class) |
| Endurance | 24–40 hours |
| Service ceiling | 60,000 ft |
| Sensor suite | SAR, GMTI, EO/IR, SIGINT |
| Datalink | Ku-band SATCOM, LOS CDL |

### Swarm Coordination Systems — Academic Context

Swarm UAS research explores decentralised coordination where each agent uses local rules to achieve global behaviour (analogous to flocking algorithms). Academic implementations use:

```python
# Boids-style flocking — academic illustration only
def compute_swarm_velocity(agent, neighbours, weights=(1.2, 1.0, 0.8)):
    separation = sum((agent.pos - n.pos) / (dist(agent, n)**2 + 1e-6)
                     for n in neighbours if dist(agent, n) < 2.0)
    alignment  = mean_velocity(neighbours) - agent.velocity
    cohesion   = mean_position(neighbours) - agent.pos
    return (weights[0] * separation +
            weights[1] * alignment  +
            weights[2] * cohesion)
```

### Electronic Warfare Hardening — Concepts

EW-hardened UAS incorporate (academic descriptions):

- **FHSS / DSSS datalinks** — frequency-hopping and direct-sequence spread spectrum defeat narrowband jamming
- **Anti-spoof GNSS** — dual-frequency (L1+L2/L5), cryptographic authentication (GPS M-code requires mil clearance)
- **LPI/LPD comms** — low probability of intercept/detection through burst transmission and adaptive power
- **EM shielding** — Faraday shielding on avionics against directed-energy HPM effects

### Safety & Legal Notes

- All military UAS are **USML Category XI** items under ITAR. Exporting hardware, software, or technical data to foreign nationals without a DSP-5 licence is a felony.
- University research programs use **TAA (Technical Assistance Agreements)** for collaborative work.
- Hobbyists and commercial operators must remain in the civilian regulatory framework (FAA Part 107/135); military-grade capabilities (e.g., FPV with weapons integration) are not legal for civilian use anywhere in the US.

---

## 6. Tier 5: Supply/Delivery Drones

### Target Use Cases
- Last-mile parcel delivery (Wing, Amazon Prime Air model)
- Medical supply delivery (blood, vaccines) to remote clinics
- Offshore rig consumables delivery
- Urban Air Mobility (UAM) passenger/cargo VTOL

### Urban Air Mobility (UAM) Concepts

UAM aircraft operate in the 0–3,000 ft AGL urban airspace (U-space/UTM). Design constraints:

| Constraint | Requirement |
|---|---|
| Noise | < 65 dB(A) at 50 m (community acceptance) |
| Safety | DAL-B or better for passenger craft (DO-178C) |
| Charging | < 15 min fast-charge for 30–50 km range |
| Payload | 2–5 kg parcel or 80–100 kg passenger |
| Redundancy | N+2 motor/prop redundancy minimum |

### VTOL Fixed-Wing Hybrids

VTOL hybrids combine multirotor vertical take-off with fixed-wing cruise efficiency. Two dominant configurations:

```
Tilt-rotor (V-22 analogue):
  [Lift rotor] ──── [Wing] ──── [Lift rotor]
  Rotors tilt 0°→90° for transition; complex mechanically.

Separate lift+cruise (preferred for UAS):
  [Lift motor ×4] on fuselage + [Cruise motor] on nose
  Lift motors idle in cruise; simpler, heavier.
```

**Transition algorithm (ArduPilot VTOL):**

```python
# Simplified VTOL transition state machine
class VTOLTransition:
    HOVER   = "hover"
    ACCEL   = "accel"     # gain airspeed before reducing lift
    BLEND   = "blend"     # blend lift and wing contribution
    FW      = "fixed_wing"

    def update(self, airspeed_ms, pitch_deg, state):
        if state == self.HOVER and airspeed_ms > 8.0:
            return self.ACCEL
        if state == self.ACCEL and airspeed_ms > 14.0:
            return self.BLEND
        if state == self.BLEND and airspeed_ms > 19.0 and pitch_deg < 5.0:
            return self.FW
        return state
```

### Payload Release Mechanisms

Three standard release mechanisms for delivery drones:

| Mechanism | Best For | Complexity |
|---|---|---|
| Winch + cable | Precision doorstep delivery (Wing model) | Medium |
| Servo latch hook | Simple drop at hover | Low |
| Pneumatic ejector | Fast-cycle high-volume ops | High |

**Servo latch release (Arduino code):**

```c
#include <Servo.h>
Servo latch;

void setup() {
    latch.attach(9);
    latch.write(0);    // locked position
}

void release_payload() {
    latch.write(90);   // open latch
    delay(800);        // hold open
    latch.write(0);    // re-lock for next payload
}
```

### Fleet Management Systems

Production delivery networks require a Fleet Management System (FMS):

```
┌──────────────┐      REST/gRPC      ┌──────────────────┐
│  Order Mgmt  │ ──────────────────► │  FMS Backend     │
│  (e-commerce)│                     │  (fleet dispatch,│
└──────────────┘                     │   route planning,│
                                     │   UTM integration)│
                                     └────────┬─────────┘
                                              │ MAVLink / MQTT
                                   ┌──────────┴──────────┐
                                   │  Drone × N           │
                                   │  (each with 4G/5G   │
                                   │   C2 datalink)       │
                                   └─────────────────────┘
```

**Minimum FMS capabilities:**
- Real-time GCS position tracking for all active vehicles
- Automated mission generation from delivery address (geocoding → waypoints)
- UTM/U-space integration for airspace deconfliction
- Battery state-of-health tracking and charge scheduling
- Incident reporting and automated NOTAM filing

### Bill of Materials — Tier 5 (Delivery VTOL, 3 kg Payload)

| # | Component | Specification | Qty | Unit Price | Total |
|---|---|---|---|---|---|
| 1 | VTOL airframe | Custom CF + glass hybrid, 2.4 m span | 1 | $3,200 | $3,200 |
| 2 | Lift motors | T-Motor U5 KV400 | 4 | $95 | $380 |
| 3 | Cruise motor | T-Motor AT4130 KV530 | 1 | $75 | $75 |
| 4 | ESCs (lift) | Flame 40A HV | 4 | $48 | $192 |
| 5 | ESC (cruise) | Flame 60A HV | 1 | $55 | $55 |
| 6 | Flight controller | Cube Orange+ with VTOL firmware | 1 | $365 | $365 |
| 7 | GNSS | Here3+ × 2 | 2 | $130 | $260 |
| 8 | Mission computer | RPi CM4 8 GB + custom carrier | 1 | $180 | $180 |
| 9 | LTE modem | Quectel EC25 + SIM | 1 | $85 | $85 |
| 10 | Payload bay | CNC Al 6061 with servo latch | 1 | $340 | $340 |
| 11 | Battery | 6S 22,000 mAh lightweight LiPo | 1 | $420 | $420 |
| 12 | Parachute | Indemnis Nexus (10 m/s deployment) | 1 | $1,800 | $1,800 |
| 13 | Remote ID module | BlueMark DB120 (FAA compliant) | 1 | $110 | $110 |
| 14 | Hardware + wiring | Certified aircraft wire, MIL connectors | 1 | $480 | $480 |
| **Total** | | | | | **~$7,942** |

---

## 7. Quality Assurance

### Pre-Flight Checklist

Run this checklist before **every** flight, regardless of tier.

```
PRE-FLIGHT CHECKLIST
─────────────────────────────────────────────────────────
STRUCTURE
  [ ] Frame: inspect for cracks, loose screws, broken welds
  [ ] Props: no chips, cracks, or delamination; correctly torqued
  [ ] Motors: spin freely, no bearing roughness
  [ ] Payload: secured, weight within limits, CG verified

ELECTRONICS
  [ ] Battery voltage: >3.7 V/cell (LiPo); connections secure
  [ ] RC link: correct model loaded, failsafe confirmed
  [ ] GPS: ≥6 satellites, HDOP <2.0 before arming
  [ ] Compass: calibration current (<30 days or last incident)
  [ ] Datalink: telemetry confirmed at GCS
  [ ] Camera/payload: recording, focus, stabilisation test

FIRMWARE / GCS
  [ ] Firmware version: matches approved build hash
  [ ] Mission plan: loaded and verified against chart
  [ ] Geofence: active, correct boundaries
  [ ] Failsafe actions: RTL altitude, battery threshold confirmed
  [ ] Remote ID: broadcasting (Tier 3+)

ENVIRONMENT
  [ ] NOTAM: checked for operating area
  [ ] Weather: wind <75% of airframe rating, no thunderstorms within 10 NM
  [ ] Observers: safety pilot briefed; clear LOS to aircraft
─────────────────────────────────────────────────────────
```

### Test Flight Procedures

**Tier 1–2 initial maiden flight:**

1. Verify motor direction and prop rotation before installing props
2. Tie down or hold aircraft; spin motors to 30% — verify no oscillation
3. Hover test: 1 m AGL for 30 s, confirm attitude response to stick inputs
4. Altitude hold test (if GPS): command 5 m hold, observe drift (<0.5 m)
5. RTH test: trigger via switch at 20 m distance; verify auto-landing within 2 m of launch point

**Tier 3+ acceptance test procedure:**

```
ATP (Acceptance Test Procedure) — Revision 1.0

1. Bench Test
   a. IMU calibration — record baseline vibration FFT
   b. ESC self-test via CAN — report all motor serial numbers
   c. GNSS cold acquisition time — must be <90 s
   d. Encrypted C2 link — verify AES-256 round-trip latency <200 ms

2. Tethered Hover (3 m tether)
   a. 10-minute hover, log all telemetry
   b. Confirm triple-IMU agreement within 0.5°
   c. Simulate FC failover — backup node must assume control within 500 ms

3. Free-Flight Qualification
   a. Waypoint mission: 10 waypoints, 200 m circuit, 3 laps
   b. Position accuracy: stop at each waypoint, verify within 1.5 m of target
   c. RTL from max operational radius — verify landing within 3 m of home
   d. Payload drop test (Tier 5): verify release, payload intact
```

### Documentation Requirements

Maintain the following records per vehicle serial number:

| Document | Minimum Content | Tier |
|---|---|---|
| Build log | Component serial numbers, solder dates, test results | All |
| Firmware log | Version, config hash, date of each update | All |
| Flight log | Date, location, duration, pilot, incidents | All |
| Maintenance log | Parts replaced, inspections passed, next due date | 2+ |
| Calibration record | IMU, compass, ESC, sensor dates | 2+ |
| ATP report | Signed acceptance test results | 3+ |
| Airworthiness statement | Structural inspection, load test results | 3+ |

---

## 8. Regulatory Compliance

### Requirements by Tier

| Requirement | Tier 1 | Tier 2 | Tier 3 | Tier 5 |
|---|---|---|---|---|
| FAA registration | Yes (>250 g) | Yes | Yes | Yes |
| Remote ID | Recommended | Required | Required | Required |
| FAA Part 107 cert | If commercial | Required | Required | Required |
| Part 107 waiver | No | Sometimes | BVLOS waiver | BVLOS waiver |
| Part 135 air carrier | No | No | Yes (delivery) | Yes |
| EASA C-class label | EU only | EU only | EU type cert | EU type cert |
| Insurance | Recommended | Required (commercial) | Required | Required |

### FAA Registration & Remote ID

**Register** any drone ≥ 250 g at [faa.gov/uas/getting_started/register_drone](https://www.faa.gov/uas/getting_started/register_drone). Mark the registration number on the exterior.

**Remote ID (effective September 2023):** All drones operated under Part 107 must broadcast Remote ID. Options:

- **Standard Remote ID** — built-in broadcast from the flight controller or add-on module
- **Remote ID module** — add-on Bluetooth/WiFi broadcast; plug into FC USB or auxiliary port

```python
# Remote ID MAVLink message (OpenDroneID)
# ArduPilot broadcasts this automatically when DID_* params are set

# Required parameters (Mission Planner / MAVLink):
DID_ENABLE      = 1          # enable Remote ID subsystem
DID_MAVLINK_EN  = 1          # broadcast via MAVLink → external module
# Also requires GPS lock before arming when DID_ENABLE = 1
```

### EASA / International Requirements

| Region | Framework | Key Requirement |
|---|---|---|
| European Union | EASA UAS Regulation 2019/947 | C0–C6 class labels; Open/Specific/Certified categories |
| United Kingdom | UK CAA CAP 722 | OSC (Operational Safety Case) for complex ops |
| Australia | CASA Part 101 | Excluded / certified operator; ReOC for commercial |
| Canada | Transport Canada CARs Part IX | Advanced RPAS certificate for controlled airspace |
| Japan | MLIT UAS Act (2022 revision) | Category III requires type certification |

### Insurance Requirements

| Tier | Minimum Coverage | Notes |
|---|---|---|
| 1 (recreational) | Recommended $500K liability | AMA membership includes $2.5 M coverage |
| 2 (commercial) | $1 M liability minimum | Required by most clients; check local laws |
| 3 (industrial) | $2–5 M liability | Hull insurance recommended on >$10K aircraft |
| 5 (delivery) | $5–25 M liability + hull | Cargo liability insurance also required |

---

*This guide is a living document. For the latest regulatory information, always consult your national aviation authority directly. Regulations for UAS are updated frequently and vary by country.*
