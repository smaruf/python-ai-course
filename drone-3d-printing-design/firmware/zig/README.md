# Zig Drone Firmware

> **Part of [Drone 3D Printing Design](../../README.md)** | [Python AI Course](../../../README.md)  
> See also: [Basic-C Firmware](../c/) | [TinyGo Firmware](../tinygo/) | [Python Firmware](../python/)

Zero-overhead, memory-safe systems firmware written in Zig.

## Why Zig?

| Property | Zig | C | TinyGo |
|----------|-----|---|--------|
| Memory safety | ✅ (comptime) | ⚠️ manual | ✅ |
| No hidden allocations | ✅ | ✅ | ⚠️ GC |
| Cross-compile | ✅ first-class | Needs toolchain | ✅ |
| C interop | ✅ native | — | ✅ |
| Error handling | `try`/`!T` | errno / panic | `error` |

## Files

| File | Description |
|------|-------------|
| `drone_firmware.zig` | Main firmware: PID, filter, motor mix |
| `build.zig` | Zig build script |

## Simulate (native x86/ARM)

```bash
# Install Zig ≥ 0.12: https://ziglang.org/download/
zig build run
```

## Cross-compile for RP2040

```bash
zig build -Dtarget=thumb-freestanding-eabihf -Doptimize=ReleaseSmall
```

## Cross-compile for STM32F4

```bash
zig build -Dtarget=thumb-freestanding-eabihf \
          -Dcpu=cortex_m4 \
          -Doptimize=ReleaseFast
```

## Key Features

- ✅ `comptime` PID gains — validated at compile time
- ✅ Explicit error handling with `try` / `!T`  
- ✅ Packed structs for hardware register access
- ✅ No runtime panics in release builds
- ✅ Zero dependencies — pure standard library
