# Python Drone Firmware

> **Part of [Drone 3D Printing Design](../../README.md)** | [Python AI Course](../../../README.md)  
> See also: [Basic-C Firmware](../c/) | [Zig Firmware](../zig/) | [TinyGo Firmware](../tinygo/)

MicroPython / CircuitPython compatible flight controller.

## Target Hardware

| Board | MCU | Notes |
|-------|-----|-------|
| Raspberry Pi Pico | RP2040 | MicroPython, 2× I2C, 8× PWM |
| Adafruit Feather M4 | SAMD51 | CircuitPython |
| Any Linux SBC | — | Full CPython (SITL / dev) |

## Files

| File | Description |
|------|-------------|
| `drone_firmware.py` | Main firmware — sensor read, PID, motor mix |

## Flashing to Pico (MicroPython)

```bash
# Install mpremote
pip install mpremote

# Copy firmware
mpremote cp drone_firmware.py :main.py

# Run
mpremote run drone_firmware.py
```

## Wiring

```
GP0  → MPU-6050 SDA
GP1  → MPU-6050 SCL
GP2  → ESC 1 (Front-Left)
GP3  → ESC 2 (Front-Right)
GP4  → ESC 3 (Rear-Right)
GP5  → ESC 4 (Rear-Left)
3.3V → MPU-6050 VCC
GND  → MPU-6050 GND, ESC signal GND
```

## Simulation (CPython)

```bash
python drone_firmware.py
```

No hardware required — all peripherals are stubbed automatically.
