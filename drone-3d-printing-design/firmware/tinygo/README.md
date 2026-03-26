# TinyGo Drone Firmware

> **Part of [Drone 3D Printing Design](../../README.md)** | [Python AI Course](../../../README.md)  
> See also: [Basic-C Firmware](../c/) | [Zig Firmware](../zig/) | [Python Firmware](../python/)

Memory-safe, compiled Go firmware for embedded flight controllers.

## Why TinyGo?

| Property | TinyGo | C | MicroPython |
|----------|--------|---|-------------|
| Memory safety | ✅ | ⚠️ manual | ✅ |
| Binary size | ~20–80 KB | ~5–40 KB | N/A (interpreted) |
| Execution speed | Fast (compiled) | Fastest | Slow |
| Concurrency | goroutines | RTOS tasks | asyncio |
| Debugging | Good | Good | REPL |

## Supported Targets

```bash
# Raspberry Pi Pico (RP2040)
tinygo flash -target pico .

# Arduino Nano / Uno
tinygo flash -target arduino .

# STM32F103 Blue Pill
tinygo flash -target stm32f103xx .

# BBC micro:bit v2
tinygo flash -target microbit-v2 .
```

## Desktop Simulation

```bash
# Install TinyGo: https://tinygo.org/getting-started/install/
tinygo run .
```

## Files

| File | Description |
|------|-------------|
| `drone_firmware.go` | Main firmware: PID, complementary filter, motor mix |
| `go.mod` | Go module file |

## Wiring (Pico)

```
GP2 → ESC 1 (Front-Left)   PWM
GP3 → ESC 2 (Front-Right)  PWM
GP4 → ESC 3 (Rear-Right)   PWM
GP5 → ESC 4 (Rear-Left)    PWM
GP0 → MPU-6050 SDA  (I2C0)
GP1 → MPU-6050 SCL  (I2C0)
```

## Key Features

- ✅ No garbage-collection pauses in hot loop (uses fixed-size structs)
- ✅ PID controller with anti-windup
- ✅ Complementary filter (gyro + accel fusion)
- ✅ Quad-X motor mixer
- ✅ Hardware abstraction — swap `setPWM` / `readIMU` for real drivers
