/// Drone Firmware — Zig
///
/// Targets:
///   • STM32F405 / STM32H743 (common flight controllers)
///   • Raspberry Pi Pico (RP2040)
///   • Any bare-metal ARM Cortex-M via zig build
///
/// Build (native simulation):
///   zig build run
///
/// Build (cross-compile for RP2040):
///   zig build -Dtarget=thumb-freestanding-eabihf
///
/// Key Zig features used:
///   • comptime — zero-cost type safety and code generation
///   • @import  — modular build without a separate build system
///   • error unions — explicit error handling with no exceptions
///   • packed structs — bit-exact register access

const std = @import("std");
const math = std.math;

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const PWM_MIN_US: u32 = 1000; // motor stopped
const PWM_MAX_US: u32 = 2000; // full throttle
const PWM_RANGE_US: u32 = PWM_MAX_US - PWM_MIN_US;
const LOOP_RATE_HZ: u32 = 500;
const LOOP_DT_S: f32 = 1.0 / @as(f32, LOOP_RATE_HZ);

// ---------------------------------------------------------------------------
// PID controller
// ---------------------------------------------------------------------------

/// PID controller with anti-windup and output clamping.
const PID = struct {
    kp:         f32,
    ki:         f32,
    kd:         f32,
    limit:      f32 = 400.0,
    integral:   f32 = 0.0,
    prev_error: f32 = 0.0,

    /// Compute PID output.  dt must be > 0.
    pub fn compute(self: *PID, setpoint: f32, measured: f32, dt: f32) f32 {
        const err = setpoint - measured;

        self.integral = math.clamp(self.integral + err * dt,
                                   -self.limit, self.limit);
        const d_term  = if (dt > 0.0) (err - self.prev_error) / dt else 0.0;
        self.prev_error = err;

        const out = self.kp * err + self.ki * self.integral + self.kd * d_term;
        return math.clamp(out, -self.limit, self.limit);
    }

    pub fn reset(self: *PID) void {
        self.integral   = 0.0;
        self.prev_error = 0.0;
    }
};

// ---------------------------------------------------------------------------
// Complementary filter
// ---------------------------------------------------------------------------

/// Fuses gyroscope and accelerometer to estimate roll & pitch (degrees).
const CompFilter = struct {
    alpha: f32 = 0.98,
    roll:  f32 = 0.0,
    pitch: f32 = 0.0,

    pub fn update(self: *CompFilter,
                  ax: f32, ay: f32, az: f32,
                  gx: f32, gy: f32,
                  dt: f32) struct { roll: f32, pitch: f32 } {

        self.roll  += gx * dt;
        self.pitch += gy * dt;

        if (az != 0.0) {
            const accel_roll  = math.atan2(ay, az) * (180.0 / math.pi);
            const accel_pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))
                                * (180.0 / math.pi);
            self.roll  = self.alpha * self.roll  + (1.0 - self.alpha) * accel_roll;
            self.pitch = self.alpha * self.pitch + (1.0 - self.alpha) * accel_pitch;
        }

        return .{ .roll = self.roll, .pitch = self.pitch };
    }
};

// ---------------------------------------------------------------------------
// Motor mixer (Quad-X frame)
// ---------------------------------------------------------------------------

/// Convert a [0, 1] throttle value to ESC pulse width in µs.
fn throttle_to_us(v: f32) u32 {
    const clamped = math.clamp(v, 0.0, 1.0);
    return PWM_MIN_US + @as(u32, @intFromFloat(clamped * @as(f32, PWM_RANGE_US)));
}

/// Quad-X motor mix.
/// Returns [FL, FR, RR, RL] pulse widths in µs.
fn mix_quad_x(throttle: f32, pitch: f32, roll: f32, yaw: f32) [4]u32 {
    const n: f32 = 500.0;
    return [4]u32{
        throttle_to_us(throttle + pitch / n + roll / n - yaw / n), // FL
        throttle_to_us(throttle + pitch / n - roll / n + yaw / n), // FR
        throttle_to_us(throttle - pitch / n - roll / n - yaw / n), // RR
        throttle_to_us(throttle - pitch / n + roll / n + yaw / n), // RL
    };
}

// ---------------------------------------------------------------------------
// Hardware abstraction — IMU
// ---------------------------------------------------------------------------

/// IMU reading (acceleration m/s², gyro °/s).
const IMUReading = struct {
    ax: f32, ay: f32, az: f32,
    gx: f32, gy: f32, gz: f32,
};

/// Read IMU — returns simulated near-level values.
/// On real hardware: call MPU-6000 / ICM-42688 SPI driver here.
fn read_imu() IMUReading {
    return .{
        .ax = 0.0,  .ay = 0.1, .az = -9.81,
        .gx = 0.5,  .gy = 0.2, .gz = 0.0,
    };
}

// ---------------------------------------------------------------------------
// Hardware abstraction — RC input
// ---------------------------------------------------------------------------

const RCInput = struct {
    throttle: f32 = 0.0,  // 0–1
    roll:     f32 = 0.0,  // -1 to +1
    pitch:    f32 = 0.0,
    yaw:      f32 = 0.0,
    armed:    bool = false,
};

/// Read RC channels — simulation stub; replace with PPM/SBUS UART ISR.
fn read_rc() RCInput {
    return .{ .throttle = 0.45, .roll = 0.1, .armed = true };
}

// ---------------------------------------------------------------------------
// Hardware abstraction — PWM output
// ---------------------------------------------------------------------------

/// Write µs pulse to an ESC / servo channel.
/// On real hardware: write to timer compare register.
fn set_pwm(channel: u8, us: u32) void {
    // Real STM32 example (pseudo-register write):
    //   TIM3.CCR[channel] = us_to_ccr(us, timer_period);
    //
    // Simulation: no-op (or print for debugging)
    _ = channel;
    _ = us;
}

// ---------------------------------------------------------------------------
// Failsafe
// ---------------------------------------------------------------------------

/// Trigger failsafe: cut throttle and disarm.
fn trigger_failsafe(motors: *[4]u32) void {
    for (motors) |*m| m.* = PWM_MIN_US;
}

// ---------------------------------------------------------------------------
// Main loop
// ---------------------------------------------------------------------------

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();

    var filter = CompFilter{};
    var pid_roll  = PID{ .kp = 4.5, .ki = 0.04, .kd = 0.40 };
    var pid_pitch = PID{ .kp = 4.5, .ki = 0.04, .kd = 0.40 };
    var pid_yaw   = PID{ .kp = 6.0, .ki = 0.10, .kd = 0.20 };

    var armed = false;
    var motors = [4]u32{ PWM_MIN_US, PWM_MIN_US, PWM_MIN_US, PWM_MIN_US };

    try stdout.print("Zig Drone Firmware — simulation mode\n", .{});
    try stdout.print("Running {d} Hz control loop...\n\n", .{LOOP_RATE_HZ});

    // Run 200 iterations for demonstration
    var i: u32 = 0;
    while (i < 200) : (i += 1) {
        const imu = read_imu();
        const rc  = read_rc();

        // Arm / disarm
        if (rc.armed and !armed) {
            armed = true;
            pid_roll.reset();
            pid_pitch.reset();
            pid_yaw.reset();
        } else if (!rc.armed) {
            armed = false;
        }

        // Attitude
        const att = filter.update(imu.ax, imu.ay, imu.az,
                                   imu.gx, imu.gy,
                                   LOOP_DT_S);

        // PID
        const roll_cmd  = pid_roll.compute(0.0, att.roll,  LOOP_DT_S);
        const pitch_cmd = pid_pitch.compute(0.0, att.pitch, LOOP_DT_S);
        const yaw_cmd   = pid_yaw.compute(0.0, imu.gz,     LOOP_DT_S);

        // Mix
        if (armed) {
            motors = mix_quad_x(rc.throttle, pitch_cmd, roll_cmd, yaw_cmd);
        } else {
            trigger_failsafe(&motors);
        }

        // Write outputs
        for (motors, 0..) |us, ch| {
            set_pwm(@intCast(ch), us);
        }
    }

    // Print final motor values
    try stdout.print("Final motor outputs after {d} iterations:\n", .{i});
    const labels = [_][]const u8{
        "Front-Left", "Front-Right", "Rear-Right", "Rear-Left",
    };
    for (motors, 0..) |us, idx| {
        try stdout.print("  {s:12}: {d} µs\n", .{ labels[idx], us });
    }
}
