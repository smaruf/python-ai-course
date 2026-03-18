/**
 * drone_firmware.c — Basic-C Drone Firmware
 *
 * Targets:
 *   • Arduino Nano / Uno  (ATmega328P)  — upload with avr-gcc / Arduino IDE
 *   • STM32F103 Blue Pill              — compile with arm-none-eabi-gcc
 *   • STM32F405 (Pixhawk-style FC)     — compile with arm-none-eabi-gcc
 *   • Any POSIX system (Linux/macOS)   — simulate with gcc
 *
 * Compile & simulate on Linux/macOS:
 *   gcc -std=c11 -Wall -Wextra -O2 -lm -o drone_sim drone_firmware.c
 *   ./drone_sim
 *
 * Compile for Arduino Nano (avr-gcc):
 *   avr-gcc -mmcu=atmega328p -DF_CPU=16000000UL -Os -o drone.elf drone_firmware.c
 *   avr-objcopy -O ihex drone.elf drone.hex
 *   avrdude -c arduino -p m328p -P /dev/ttyUSB0 -U flash:w:drone.hex
 *
 * Compile for STM32F1 (arm-none-eabi-gcc):
 *   arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -O2 -lm \
 *       -o drone.elf drone_firmware.c
 */

#define _USE_MATH_DEFINES   /* required for M_PI on some C11 toolchains */
#ifndef M_PI
#  define M_PI 3.14159265358979323846
#endif
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* -------------------------------------------------------------------------
 * Constants
 * ---------------------------------------------------------------------- */

#define PWM_MIN_US      1000u   /**< Motor stopped (µs) */
#define PWM_MAX_US      2000u   /**< Full throttle (µs) */
#define PWM_MID_US      1500u   /**< Servo neutral (µs) */
#define LOOP_RATE_HZ    500u    /**< Control loop rate */
#define LOOP_DT_S       (1.0f / LOOP_RATE_HZ)

/** Maximum PWM output range (used in normalisation). */
#define PWM_RANGE_US    (PWM_MAX_US - PWM_MIN_US)

/* -------------------------------------------------------------------------
 * Types
 * ---------------------------------------------------------------------- */

/** Single-axis PID controller state. */
typedef struct {
    float kp;
    float ki;
    float kd;
    float limit;        /**< Anti-windup + output clamp. */
    float integral;
    float prev_error;
} PID;

/** Estimated vehicle attitude (degrees). */
typedef struct {
    float roll;
    float pitch;
    float yaw;
} Attitude;

/** Raw IMU reading. */
typedef struct {
    float ax, ay, az;   /**< Accelerometer (m/s²). */
    float gx, gy, gz;   /**< Gyroscope (°/s). */
} IMUReading;

/** RC stick inputs (normalised). */
typedef struct {
    float throttle; /**< 0.0 – 1.0  */
    float roll;     /**< -1.0 – +1.0 */
    float pitch;    /**< -1.0 – +1.0 */
    float yaw;      /**< -1.0 – +1.0 */
    bool  armed;
} RCInput;

/* -------------------------------------------------------------------------
 * Utility macros
 * ---------------------------------------------------------------------- */

#define CLAMP(x, lo, hi)  ((x) < (lo) ? (lo) : (x) > (hi) ? (hi) : (x))
#define DEG2RAD(d)         ((d) * (float)M_PI / 180.0f)
#define RAD2DEG(r)         ((r) * 180.0f / (float)M_PI)

/* -------------------------------------------------------------------------
 * PID functions
 * ---------------------------------------------------------------------- */

/**
 * Initialise a PID controller.
 *
 * @param pid     Pointer to PID state to initialise.
 * @param kp      Proportional gain.
 * @param ki      Integral gain.
 * @param kd      Derivative gain.
 * @param limit   Anti-windup and output limit.
 */
static void pid_init(PID *pid, float kp, float ki, float kd, float limit)
{
    pid->kp         = kp;
    pid->ki         = ki;
    pid->kd         = kd;
    pid->limit      = limit;
    pid->integral   = 0.0f;
    pid->prev_error = 0.0f;
}

/**
 * Compute PID output.
 *
 * @param pid       Pointer to PID state.
 * @param setpoint  Desired value.
 * @param measured  Current measured value.
 * @param dt        Loop time in seconds (must be > 0).
 * @return          PID output, clamped to [-limit, +limit].
 */
static float pid_compute(PID *pid, float setpoint, float measured, float dt)
{
    float err, p_term, i_term, d_term, output;

    if (dt <= 0.0f) return 0.0f;

    err = setpoint - measured;

    /* Proportional */
    p_term = pid->kp * err;

    /* Integral with anti-windup */
    pid->integral += err * dt;
    pid->integral  = CLAMP(pid->integral, -pid->limit, pid->limit);
    i_term         = pid->ki * pid->integral;

    /* Derivative on measurement (avoids kick on setpoint change) */
    d_term          = pid->kd * (err - pid->prev_error) / dt;
    pid->prev_error = err;

    output = p_term + i_term + d_term;
    return CLAMP(output, -pid->limit, pid->limit);
}

/** Reset integrator and derivative state (call on disarm). */
static void pid_reset(PID *pid)
{
    pid->integral   = 0.0f;
    pid->prev_error = 0.0f;
}

/* -------------------------------------------------------------------------
 * Complementary filter
 * ---------------------------------------------------------------------- */

/** Complementary filter state. */
typedef struct {
    float alpha;  /**< Gyro trust weight (0.96–0.99 typical). */
    float roll;
    float pitch;
} CompFilter;

/**
 * Update the complementary filter with one IMU reading.
 *
 * @param f    Pointer to filter state.
 * @param imu  Pointer to IMU reading.
 * @param dt   Loop time in seconds.
 */
static void compfilter_update(CompFilter *f,
                              const IMUReading *imu,
                              float dt)
{
    float accel_roll, accel_pitch;

    /* Gyro integration */
    f->roll  += imu->gx * dt;
    f->pitch += imu->gy * dt;

    /* Accelerometer angles */
    if (imu->az != 0.0f) {
        accel_roll  = RAD2DEG(atan2f(imu->ay, imu->az));
        accel_pitch = RAD2DEG(atan2f(-imu->ax,
                                     sqrtf(imu->ay * imu->ay
                                           + imu->az * imu->az)));

        f->roll  = f->alpha * f->roll  + (1.0f - f->alpha) * accel_roll;
        f->pitch = f->alpha * f->pitch + (1.0f - f->alpha) * accel_pitch;
    }
}

/* -------------------------------------------------------------------------
 * Motor mixer — Quad-X frame
 * ---------------------------------------------------------------------- */

/**
 * Convert normalised throttle [0,1] to ESC pulse width (µs).
 */
static uint32_t throttle_to_us(float v)
{
    float clamped = CLAMP(v, 0.0f, 1.0f);
    return PWM_MIN_US + (uint32_t)(clamped * (float)PWM_RANGE_US);
}

/**
 * Quad-X motor mixer.
 *
 * Motor layout (top view):
 *   FL(0)  FR(1)
 *     \   /
 *      \ /
 *       X
 *      / \
 *     /   \
 *   RL(3) RR(2)
 *
 * @param throttle  0.0–1.0
 * @param pitch     -1.0 to +1.0 (PID output, normalised by 500)
 * @param roll      -1.0 to +1.0
 * @param yaw       -1.0 to +1.0
 * @param out_us    Output array of 4 PWM values in µs [FL, FR, RR, RL].
 */
static void mix_quad_x(float throttle, float pitch,
                        float roll,     float yaw,
                        uint32_t out_us[4])
{
    const float N = 500.0f;
    out_us[0] = throttle_to_us(throttle + pitch/N + roll/N - yaw/N); /* FL */
    out_us[1] = throttle_to_us(throttle + pitch/N - roll/N + yaw/N); /* FR */
    out_us[2] = throttle_to_us(throttle - pitch/N - roll/N - yaw/N); /* RR */
    out_us[3] = throttle_to_us(throttle - pitch/N + roll/N + yaw/N); /* RL */
}

/* -------------------------------------------------------------------------
 * Hardware abstraction — simulation stubs
 * Replace these with real peripheral drivers on target hardware.
 * ---------------------------------------------------------------------- */

/**
 * Read IMU — simulated near-level values.
 *
 * On real STM32 hardware replace with:
 *   spi_read_mpu6000(buf, sizeof(buf));
 *   imu->ax = (int16_t)((buf[0] << 8) | buf[1]) / ACCEL_SCALE * 9.81f;
 *   ...
 */
static void hal_read_imu(IMUReading *imu)
{
    imu->ax = 0.0f;
    imu->ay = 0.1f;
    imu->az = -9.81f;
    imu->gx = 0.5f;
    imu->gy = 0.2f;
    imu->gz = 0.0f;
}

/**
 * Read RC input — simulated.
 *
 * On real hardware replace with PPM/SBUS parser in UART ISR.
 */
static void hal_read_rc(RCInput *rc)
{
    rc->throttle = 0.45f;
    rc->roll     = 0.1f;
    rc->pitch    = 0.0f;
    rc->yaw      = 0.0f;
    rc->armed    = true;
}

/**
 * Set ESC/servo PWM pulse width.
 *
 * On real STM32 hardware replace with:
 *   TIM3->CCR1 = us_to_ccr(us, TIM3->ARR);
 */
static void hal_set_pwm(uint8_t channel, uint32_t us)
{
    (void)channel;
    (void)us;
    /* No-op in simulation */
}

/* -------------------------------------------------------------------------
 * Failsafe
 * ---------------------------------------------------------------------- */

/** Cut all motor outputs (called on RC loss or critical battery). */
static void trigger_failsafe(uint32_t motors[4])
{
    motors[0] = motors[1] = motors[2] = motors[3] = PWM_MIN_US;
}

/* -------------------------------------------------------------------------
 * Main loop
 * ---------------------------------------------------------------------- */

/**
 * Firmware entry point.
 *
 * On microcontrollers this function never returns (while(1)).
 * On the simulation build it exits after @p loop_count iterations.
 */
int main(void)
{
    const int LOOP_COUNT = 200;

    /* State */
    CompFilter filter  = { .alpha = 0.98f, .roll = 0.0f, .pitch = 0.0f };
    PID pid_roll, pid_pitch, pid_yaw;
    pid_init(&pid_roll,  4.5f, 0.04f, 0.40f, 400.0f);
    pid_init(&pid_pitch, 4.5f, 0.04f, 0.40f, 400.0f);
    pid_init(&pid_yaw,   6.0f, 0.10f, 0.20f, 400.0f);

    uint32_t motors[4] = { PWM_MIN_US, PWM_MIN_US, PWM_MIN_US, PWM_MIN_US };
    bool armed = false;

    printf("Basic-C Drone Firmware — simulation mode\n");
    printf("Running %u Hz control loop for %d iterations...\n\n",
           LOOP_RATE_HZ, LOOP_COUNT);

    for (int i = 0; i < LOOP_COUNT; i++) {
        IMUReading imu;
        RCInput    rc;

        hal_read_imu(&imu);
        hal_read_rc(&rc);

        /* Arm / disarm */
        if (rc.armed && !armed) {
            armed = true;
            pid_reset(&pid_roll);
            pid_reset(&pid_pitch);
            pid_reset(&pid_yaw);
        } else if (!rc.armed) {
            armed = false;
        }

        /* Sensor fusion */
        compfilter_update(&filter, &imu, LOOP_DT_S);

        /* PID */
        float roll_cmd  = pid_compute(&pid_roll,  0.0f, filter.roll,  LOOP_DT_S);
        float pitch_cmd = pid_compute(&pid_pitch, 0.0f, filter.pitch, LOOP_DT_S);
        float yaw_cmd   = pid_compute(&pid_yaw,   0.0f, imu.gz,       LOOP_DT_S);

        /* Motor mix */
        if (armed) {
            mix_quad_x(rc.throttle, pitch_cmd, roll_cmd, yaw_cmd, motors);
        } else {
            trigger_failsafe(motors);
        }

        /* Write to ESCs */
        for (uint8_t ch = 0; ch < 4; ch++) {
            hal_set_pwm(ch, motors[ch]);
        }
    }

    /* Print final motor state */
    const char *labels[4] = {
        "Front-Left", "Front-Right", "Rear-Right", "Rear-Left"
    };
    printf("Final motor outputs after %d iterations:\n", LOOP_COUNT);
    for (int i = 0; i < 4; i++) {
        printf("  %-12s: %u µs\n", labels[i], motors[i]);
    }

    return 0;
}
