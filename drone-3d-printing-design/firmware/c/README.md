# Basic-C Drone Firmware

> **Part of [Drone 3D Printing Design](../../README.md)** | [Python AI Course](../../../README.md)  
> See also: [Zig Firmware](../zig/) | [TinyGo Firmware](../tinygo/) | [Python Firmware](../python/)

Bare-metal C flight controller — maximum portability and performance.

## Supported Platforms

| Platform | MCU | Compiler | Flash Command |
|----------|-----|----------|---------------|
| Linux / macOS | x86/ARM | `gcc` | — (simulation) |
| Arduino Nano/Uno | ATmega328P | `avr-gcc` | `avrdude` |
| STM32F103 Blue Pill | Cortex-M3 | `arm-none-eabi-gcc` | OpenOCD / STLink |
| STM32F405 (Pixhawk-style) | Cortex-M4F | `arm-none-eabi-gcc` | OpenOCD |

## Files

| File | Description |
|------|-------------|
| `drone_firmware.c` | Complete firmware: PID, filter, mixer, HAL stubs |
| `Makefile` | Build rules for all targets |

## Simulate on Linux / macOS

```bash
gcc -std=c11 -Wall -Wextra -O2 -lm -o drone_sim drone_firmware.c
./drone_sim
```

Expected output:
```
Basic-C Drone Firmware — simulation mode
Running 500 Hz control loop for 200 iterations...

Final motor outputs after 200 iterations:
  Front-Left  : 1XXXX µs
  Front-Right : 1XXXX µs
  Rear-Right  : 1XXXX µs
  Rear-Left   : 1XXXX µs
```

## Build for Arduino Nano

```bash
make arduino
avrdude -c arduino -p m328p -P /dev/ttyUSB0 -b 115200 \
        -U flash:w:drone.hex
```

## Build for STM32F4

```bash
make stm32f4
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
        -c "program drone.elf verify reset exit"
```

## Key Features

- ✅ Self-contained single `.c` file — zero external dependencies
- ✅ PID controller with anti-windup
- ✅ Complementary filter (gyro + accelerometer fusion)
- ✅ Quad-X motor mixer
- ✅ Hardware abstraction layer (HAL) — swap stubs for real drivers
- ✅ Failsafe: motor cut on disarm / RC loss
