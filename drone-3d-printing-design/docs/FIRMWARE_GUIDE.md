# Drone Firmware Guide

## Overview

Firmware is the software that runs directly on a drone's flight controller hardware. It reads sensor data (IMU, GPS, barometer), applies control algorithms to maintain stability, and drives the motor outputs—all in real time, typically at 400–1000 Hz. Choosing the right firmware level determines your drone's capability, safety, and development complexity.

```
Sensors → Firmware (sensor fusion + PID control) → ESCs → Motors → Flight
```

**Why it matters:** Without firmware, your hardware is inert. The firmware level you choose shapes every design decision downstream—from which flight controller you 3D-print a mount for, to how you tune flight characteristics.

---

## Level 1: Simple Bare-Metal Firmware

### What It Is

Bare-metal firmware runs directly on the microcontroller with no operating system. You own every CPU cycle. Execution is deterministic and latency is minimal, but you must manage everything manually: timers, interrupts, peripheral registers.

**Suitable hardware:** Arduino Nano (ATmega328P), Arduino Mega, STM32F103 ("Blue Pill"), STM32F411

### Basic PWM Motor Output (Arduino/C)

ESCs expect a 50 Hz PWM signal with a pulse width of 1000–2000 µs (1 ms = armed/off, 2 ms = full throttle).

```c
#include <Servo.h>

Servo esc1, esc2, esc3, esc4;

void setup() {
    // Attach ESCs to pins 3, 5, 6, 9
    esc1.attach(3, 1000, 2000);
    esc2.attach(5, 1000, 2000);
    esc3.attach(6, 1000, 2000);
    esc4.attach(9, 1000, 2000);

    // Arm sequence: hold low for 2 seconds
    esc1.writeMicroseconds(1000);
    esc2.writeMicroseconds(1000);
    esc3.writeMicroseconds(1000);
    esc4.writeMicroseconds(1000);
    delay(2000);
}

void loop() {
    // Set all motors to 50% throttle (1500 µs)
    int throttle = 1500;
    esc1.writeMicroseconds(throttle);
    esc2.writeMicroseconds(throttle);
    esc3.writeMicroseconds(throttle);
    esc4.writeMicroseconds(throttle);
}
```

### RC Receiver Input — PPM Decoding (STM32/C)

PPM (Pulse Position Modulation) encodes all channels in one wire as gaps between pulses.

```c
#include "stm32f1xx_hal.h"

#define PPM_PIN        GPIO_PIN_0   // PA0 (TIM2_CH1)
#define NUM_CHANNELS   8
#define SYNC_THRESHOLD 3000        // µs — gap that marks frame start

volatile uint16_t ppm_channels[NUM_CHANNELS];
volatile uint8_t  channel_index = 0;
volatile uint32_t last_capture  = 0;

// TIM2 Input Capture IRQ handler
void TIM2_IRQHandler(void) {
    uint32_t now    = TIM2->CCR1;
    uint32_t width  = now - last_capture;
    last_capture    = now;

    if (width > SYNC_THRESHOLD) {
        channel_index = 0;          // sync pulse detected
    } else if (channel_index < NUM_CHANNELS) {
        ppm_channels[channel_index++] = (uint16_t)width;
    }
    TIM2->SR &= ~TIM_SR_CC1IF;      // clear interrupt flag
}

// Usage
// ppm_channels[0] = Roll  (1000–2000 µs)
// ppm_channels[1] = Pitch
// ppm_channels[2] = Throttle
// ppm_channels[3] = Yaw
```

### Minimal PID Loop

```c
typedef struct {
    float kp, ki, kd;
    float integral, prev_error;
} PID;

float pid_update(PID *pid, float setpoint, float measured, float dt) {
    float error      = setpoint - measured;
    pid->integral   += error * dt;
    float derivative = (error - pid->prev_error) / dt;
    pid->prev_error  = error;
    return pid->kp * error + pid->ki * pid->integral + pid->kd * derivative;
}
```

**Why it matters:** At Level 1 you learn what every higher-level framework hides from you—register-level I/O, interrupt timing, and control theory basics.

---

## Level 2: Open-Source Firmware (ArduPilot / PX4)

### Architecture Overview

Both ArduPilot and PX4 are mature, community-driven flight stacks running on dedicated flight controllers (Pixhawk, Cube, Matek, SpeedyBee).

```
Hardware Abstraction Layer (HAL)
        ↓
Sensor Drivers (IMU, GPS, Baro, Compass)
        ↓
EKF2 / EKF3  (Extended Kalman Filter — sensor fusion)
        ↓
Flight Modes  (Stabilize, AltHold, Loiter, Auto, RTL…)
        ↓
PID Controller → Motor Mixer → ESC Output
```

### Key Features

| Feature | ArduPilot (ArduCopter) | PX4 |
|---------|------------------------|-----|
| Sensor fusion | EKF3 | EKF2 |
| Mission planning | Mission Planner / QGC | QGroundControl |
| GPS modes | Loiter, RTL, Auto | Position, Mission |
| Community | Very large | Large |
| Best for | Beginners, versatility | Research, modularity |

### Setup and Calibration Steps

```
1. Flash firmware via Mission Planner / QGroundControl
2. Mandatory hardware calibration:
   a. Accelerometer (6-position)
   b. Compass (rotate drone on all axes)
   c. Radio calibration (move all sticks to extremes)
   d. ESC calibration (all-high then all-low)
3. Configure frame type (quad X, hexa, octo…)
4. First hover test — check motor directions
5. PID autotuning (ArduCopter AUTOTUNE mode)
```

### Essential Parameter Tuning (ArduPilot)

```
# Rate PIDs (inner loop — controls angular rate)
ATC_RAT_RLL_P   = 0.135    # Roll rate P gain
ATC_RAT_PIT_P   = 0.135    # Pitch rate P gain
ATC_RAT_YAW_P   = 0.180    # Yaw rate P gain

# Angle PIDs (outer loop — controls lean angle)
ATC_ANG_RLL_P   = 4.5
ATC_ANG_PIT_P   = 4.5

# Throttle / altitude control
PSC_VELZ_P      = 5.0      # Vertical velocity P gain
PSC_ACCZ_I      = 2.0      # Vertical acceleration I gain

# Filtering (reduce noise before PID)
INS_GYRO_FILTER = 20       # Gyro low-pass cutoff (Hz)
```

### Supported Flight Modes

- **Stabilize** — self-levels, manual throttle
- **AltHold** — barometer-assisted altitude hold
- **Loiter** — GPS position + altitude hold
- **Auto** — execute waypoint missions
- **RTL** — Return To Launch
- **Guided** — companion computer control via MAVLink

**Why it matters:** ArduPilot/PX4 give you production-grade safety features (failsafe, geofencing, battery monitoring) in days, not months.

---

## Level 3: Advanced Custom Firmware

### Real-Time OS (FreeRTOS)

A RTOS provides task scheduling, prioritisation, and inter-task communication without the full overhead of Linux.

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

QueueHandle_t imu_queue;

// High-priority sensor task (1 kHz)
void vSensorTask(void *params) {
    IMUData data;
    TickType_t xLastWake = xTaskGetTickCount();
    for (;;) {
        imu_read(&data);
        xQueueOverwrite(imu_queue, &data);          // non-blocking write
        vTaskDelayUntil(&xLastWake, pdMS_TO_TICKS(1));
    }
}

// Medium-priority control task (500 Hz)
void vControlTask(void *params) {
    IMUData data;
    TickType_t xLastWake = xTaskGetTickCount();
    for (;;) {
        if (xQueuePeek(imu_queue, &data, 0) == pdTRUE) {
            run_pid_loop(&data);
        }
        vTaskDelayUntil(&xLastWake, pdMS_TO_TICKS(2));
    }
}

int main(void) {
    imu_queue = xQueueCreate(1, sizeof(IMUData));
    xTaskCreate(vSensorTask,  "Sensor",  256, NULL, 5, NULL);
    xTaskCreate(vControlTask, "Control", 512, NULL, 4, NULL);
    vTaskStartScheduler();
}
```

### Custom Sensor Fusion — Complementary + Kalman Filter

```python
# Python prototype — port to C for embedded use
import numpy as np

class KalmanFilter1D:
    """1D Kalman filter for altitude fusion (barometer + accelerometer)."""
    def __init__(self, q=0.001, r=0.1):
        self.x = np.array([0.0, 0.0])   # [altitude, velocity]
        self.P = np.eye(2) * 500
        self.Q = np.eye(2) * q          # process noise
        self.R = np.array([[r]])         # measurement noise
        self.F = np.array([[1, 0.01],
                           [0, 1   ]])   # state transition (dt=0.01 s)
        self.H = np.array([[1, 0]])      # we measure altitude only

    def predict(self, accel_z, dt=0.01):
        B = np.array([[0.5 * dt**2], [dt]])
        self.x = self.F @ self.x + B.flatten() * accel_z
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, baro_altitude):
        y = baro_altitude - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K.flatten() * y[0]
        self.P = (np.eye(2) - K @ self.H) @ self.P
        return self.x[0]   # fused altitude estimate
```

### MAVLink Protocol Integration

MAVLink is the de-facto messaging standard for drone telemetry and commands.

```python
# Send attitude telemetry from companion computer
from pymavlink import mavutil
import time, math

mav = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
mav.wait_heartbeat()

while True:
    roll_deg, pitch_deg, yaw_deg = 0.0, 0.0, 90.0
    mav.mav.attitude_send(
        int(time.time() * 1000),              # time_boot_ms
        math.radians(roll_deg),               # roll (rad)
        math.radians(pitch_deg),              # pitch (rad)
        math.radians(yaw_deg),                # yaw (rad)
        0.0, 0.0, 0.0                         # angular rates
    )
    time.sleep(0.02)   # 50 Hz
```

### Hardware-in-the-Loop (HIL) Testing

HIL replaces real sensors with a physics simulator, letting you validate firmware on actual hardware without flying.

```
Simulator (Gazebo / JSBSim)
      ↓  (HIL_SENSOR MAVLink messages over USB/UART)
Flight Controller Hardware
      ↓  (ACTUATOR_OUTPUT MAVLink messages)
Simulator (closes the loop — updates physics model)
```

**Why it matters:** Level 3 is where research drones, custom autonomous systems, and thesis projects live. You get full algorithmic control while benefiting from a proven messaging ecosystem.

---

## Level 4: Proprietary / Production Firmware

### Architecture Patterns

Production firmware (like that found in DJI, Skydio, or Autel drones) adds layers that open-source builds typically omit:

```
┌─────────────────────────────────────────┐
│           Application Layer             │  Mission logic, AI, vision
├─────────────────────────────────────────┤
│         Flight Management Layer         │  State machine, mode arbitration
├────────────────┬────────────────────────┤
│  Primary FCU   │  Redundant FCU         │  Hot-standby, cross-checks
├────────────────┴────────────────────────┤
│       Hardware Abstraction Layer        │
├─────────────────────────────────────────┤
│    Safety Monitor / Watchdog Process    │  Runs independently of main CPU
└─────────────────────────────────────────┘
```

### Watchdog and Failsafe Pattern (C pseudocode)

```c
#define WATCHDOG_TIMEOUT_MS  500
#define FAILSAFE_THROTTLE    1000   // disarm

static uint32_t last_valid_rc_ms = 0;

void rc_receive_callback(RCFrame *frame) {
    if (frame_is_valid(frame)) {
        last_valid_rc_ms = millis();
        apply_rc_inputs(frame);
    }
}

void safety_monitor_task(void) {   // runs every 10 ms
    uint32_t now = millis();

    // RC link loss failsafe
    if (now - last_valid_rc_ms > WATCHDOG_TIMEOUT_MS) {
        log_event(EVT_RC_FAILSAFE);
        initiate_rtl_or_land();
    }

    // Hardware watchdog — must be kicked every cycle
    HAL_IWDG_Refresh(&hiwdg);
}
```

### Encrypted Communications (DJI-style concept)

```
Ground Station ──AES-256-GCM──► Drone Radio Module
                                        ↓
                               Decrypt + HMAC verify
                                        ↓
                               Command dispatcher
                                        ↓
                           Reject if sequence # stale
```

Key principles:
- **AES-256-GCM** for symmetric encryption with authentication
- **Sequence numbers** to prevent replay attacks
- **Certificate pinning** for OTA update servers
- **Secure boot** to verify firmware signatures at startup

### OTA (Over-the-Air) Update Flow

```
1. Server signs firmware bundle with private key (Ed25519)
2. Drone polls update server at scheduled interval
3. Drone verifies bundle signature with embedded public key
4. Download to inactive flash partition (A/B partition scheme)
5. Verify SHA-256 checksum of downloaded bundle
6. Reboot into new partition
7. If boot fails 3 times → roll back to previous partition
```

### Health Monitoring and Diagnostics

```python
# Example: structured health telemetry log (Python representation)
health_report = {
    "timestamp_utc": "2025-01-15T10:30:00Z",
    "flight_id": "flight_0042",
    "battery": {
        "voltage_v": 14.8,
        "current_a": 18.5,
        "capacity_remaining_pct": 72,
        "cell_delta_mv": 12          # flag if > 50 mV
    },
    "imu": {
        "gyro_ok": True,
        "accel_ok": True,
        "vibration_rms_g": 0.08      # flag if > 0.30 g
    },
    "motors": {
        "rpm": [8200, 8190, 8210, 8195],
        "temp_c": [42, 41, 43, 42]   # flag if > 80°C
    },
    "estimator": {
        "ekf_healthy": True,
        "gps_hdop": 1.2,             # flag if > 2.0
        "pos_variance": 0.04
    }
}
```

**Why it matters:** Production firmware is what turns a drone into a certified, deployable product. Redundancy, encryption, and OTA updates are non-negotiable for commercial operations.

---

## Choosing the Right Level

| Criterion | Level 1 Bare-Metal | Level 2 ArduPilot/PX4 | Level 3 Custom RTOS | Level 4 Proprietary |
|-----------|-------------------|----------------------|---------------------|---------------------|
| **Development time** | Days–weeks | Hours–days | Weeks–months | Months–years |
| **GPS / auto modes** | ❌ Manual only | ✅ Built-in | ✅ Build your own | ✅ Full suite |
| **Sensor fusion** | ❌ Raw sensors | ✅ EKF2/3 | ✅ Custom Kalman | ✅ Multi-sensor |
| **Safety features** | ⚠️ DIY only | ✅ Failsafe, geofence | ✅ Custom | ✅ Certified-grade |
| **Community support** | ⚠️ Arduino forums | ✅ Very large | ⚠️ Varies | ❌ Internal only |
| **Regulatory use** | ❌ Hobby/research | ⚠️ With config | ⚠️ With effort | ✅ Certifiable |
| **Best for** | Learning, micro drones | Most builds | Research, PhDs | Commercial products |

---

## Firmware Flashing & Toolchain

### Level 1 — Arduino / STM32

```bash
# Arduino (avrdude via CLI)
arduino-cli compile --fqbn arduino:avr:nano my_firmware/
arduino-cli upload  --fqbn arduino:avr:nano --port /dev/ttyUSB0 my_firmware/

# STM32 via ST-Link (arm-none-eabi toolchain)
arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -O2 -o firmware.elf main.c
arm-none-eabi-objcopy -O binary firmware.elf firmware.bin
st-flash write firmware.bin 0x08000000
```

### Level 2 — ArduPilot / PX4

```bash
# ArduPilot: build for Pixhawk 4
./waf configure --board Pixhawk4
./waf copter
# Flash via Mission Planner or:
mavproxy.py --master /dev/ttyACM0 --aircraft mycopter

# PX4: build and flash
make px4_fmu-v5_default          # build
make px4_fmu-v5_default upload   # flash over USB
```

### Level 3 — FreeRTOS / Zephyr

```bash
# Zephyr (West build system)
west init zephyrproject
west update
west build -b stm32f4_disco samples/hello_world
west flash

# FreeRTOS via STM32CubeIDE
# 1. Generate project from STM32CubeMX with FreeRTOS middleware enabled
# 2. Import into STM32CubeIDE
# 3. Build: Project → Build All
# 4. Flash: Run → Debug As → STM32 Cortex-M C/C++ Application
```

### Level 4 — Production CI/CD

```yaml
# GitHub Actions example: build + sign firmware artifact
name: Firmware CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install ARM toolchain
        run: sudo apt-get install -y gcc-arm-none-eabi
      - name: Build firmware
        run: make BOARD=production RELEASE=1
      - name: Sign firmware bundle
        run: |
          openssl dgst -sha256 -sign private_key.pem \
                 -out firmware.bin.sig firmware.bin
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: firmware-signed
          path: |
            firmware.bin
            firmware.bin.sig
```

---

## Testing & Simulation

### Software-in-the-Loop (SITL)

SITL runs the full flight firmware in a process on your computer — no hardware required.

```bash
# ArduPilot SITL (Linux/macOS/WSL)
cd ardupilot
sim_vehicle.py -v ArduCopter --console --map

# Connect Mission Planner to localhost:14550
# Or use MAVProxy:
mavproxy.py --master tcp:127.0.0.1:5760 \
            --out udp:127.0.0.1:14550

# Example: arm and takeoff via CLI
arm throttle
mode guided
takeoff 10         # climb to 10 metres
```

### Gazebo Full Physics Simulation

```bash
# PX4 + Gazebo (Ignition) integration
cd PX4-Autopilot
make px4_sitl gz_x500      # X500 quadcopter model in Gazebo

# In a second terminal — send a mission via QGroundControl or:
python3 - <<'EOF'
from pymavlink import mavutil, mavwp
mav = mavutil.mavlink_connection('udp:localhost:14540')
mav.wait_heartbeat()
mav.mav.command_long_send(
    mav.target_system, mav.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 10   # takeoff to 10 m
)
EOF
```

### Unit Testing Control Algorithms

```python
# Test PID controller without hardware
import pytest
from pid import PIDController

def test_pid_zero_error():
    pid = PIDController(kp=1.0, ki=0.1, kd=0.05)
    output = pid.update(setpoint=0.0, measured=0.0, dt=0.01)
    assert output == pytest.approx(0.0)

def test_pid_proportional_response():
    pid = PIDController(kp=2.0, ki=0.0, kd=0.0)
    output = pid.update(setpoint=10.0, measured=0.0, dt=0.01)
    assert output == pytest.approx(20.0)   # kp × error = 2.0 × 10

def test_pid_integral_windup_clamp():
    pid = PIDController(kp=1.0, ki=1.0, kd=0.0, integral_limit=5.0)
    for _ in range(1000):
        pid.update(setpoint=100.0, measured=0.0, dt=0.01)
    assert abs(pid.integral) <= 5.0
```

---

## Validation Checklist

Before flying any firmware level:

- ✅ Motor rotation directions correct (props off first)
- ✅ Throttle channel maps to collective thrust (not roll/pitch)
- ✅ RC failsafe tested (disconnect transmitter — drone should land/RTL)
- ✅ Battery failsafe set (voltage threshold triggers RTL)
- ✅ ESC calibration complete
- ✅ Compass not saturated near power cables
- ✅ Vibration damping adequate (IMU vibration < 0.3 g RMS)
- ✅ First flights at low altitude, wide-open space

---

## Common Pitfalls

1. **Motor direction reversed:** Check with props off — swap any two wires on that motor.

2. **Compass/motor interference:** Route power cables away from compass; use an external GPS/compass mast.

3. **Integral windup:** Always clamp the integral term or use anti-windup logic.
   ```c
   pid->integral = fmaxf(-INTEGRAL_MAX, fminf(INTEGRAL_MAX, pid->integral));
   ```

4. **Loop timing drift:** Use `vTaskDelayUntil` (FreeRTOS) or a hardware timer ISR — never `delay()`.

5. **Sensor aliasing:** Always low-pass filter gyro/accel data before feeding the PID; filter cutoff should be below half the loop rate (Nyquist).

---

## Summary

| Level | Stack | Controller | Use Case |
|-------|-------|------------|----------|
| 1 | Bare-metal C | Arduino / STM32 | Learning, micro-drones |
| 2 | ArduPilot / PX4 | Pixhawk / Matek | Sport, mapping, FPV |
| 3 | FreeRTOS / Zephyr | STM32H7 / i.MX RT | Research, custom autonomy |
| 4 | Proprietary | Custom SoC / dual-MCU | Commercial products |

Start at Level 2 for most real drone projects. Drop to Level 1 to understand fundamentals, climb to Level 3 when you need algorithmic control, and reach Level 4 only when building a certified or commercial product.

**Time Investment:** Level 1 = 1–2 weeks | Level 2 = 2–5 days | Level 3 = 2–4 months | Level 4 = 1+ year  
**Difficulty:** 🟢 L1 Beginner → 🟡 L2 Intermediate → 🟠 L3 Advanced → 🔴 L4 Expert
