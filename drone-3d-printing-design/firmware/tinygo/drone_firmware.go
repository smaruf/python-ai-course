// Drone Firmware — TinyGo
//
// Targets:
//   • Arduino Nano / Uno  (ATmega328P)   tinygo flash -target arduino
//   • Raspberry Pi Pico   (RP2040)       tinygo flash -target pico
//   • STM32F103 Blue Pill               tinygo flash -target stm32f103xx
//   • BBC micro:bit v2   (nRF52833)      tinygo flash -target microbit-v2
//
// Build:
//   tinygo build -o drone.uf2 -target pico .
//   tinygo flash  -target pico .
//
// Simulate on desktop (no hardware needed):
//   tinygo run .
//
// Dependencies:
//   tinygo.org/x/drivers — hardware drivers (I2C, SPI, UART)
//   Install:  go get tinygo.org/x/drivers

package main

import (
	"machine"
	"math"
	"time"
)

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const (
	pwmFreqHz  = 50    // ESC / servo PWM frequency
	pwmMinUs   = 1000  // motor stopped (µs)
	pwmMaxUs   = 2000  // full throttle (µs)
	loopRateHz = 200   // control loop frequency
	loopDtMs   = 1000 / loopRateHz
)

// ---------------------------------------------------------------------------
// PID controller
// ---------------------------------------------------------------------------

// PID holds the state for a single PID axis.
type PID struct {
	Kp, Ki, Kd float64
	Limit       float64 // anti-windup + output clamp
	integral    float64
	prevError   float64
}

// Compute returns the PID output for the given setpoint / measured pair.
func (p *PID) Compute(setpoint, measured, dt float64) float64 {
	if dt <= 0 {
		return 0
	}
	err := setpoint - measured

	p.integral += err * dt
	if p.integral > p.Limit {
		p.integral = p.Limit
	} else if p.integral < -p.Limit {
		p.integral = -p.Limit
	}

	dTerm := (err - p.prevError) / dt
	p.prevError = err

	out := p.Kp*err + p.Ki*p.integral + p.Kd*dTerm
	if out > p.Limit {
		return p.Limit
	} else if out < -p.Limit {
		return -p.Limit
	}
	return out
}

// Reset clears integrator and derivative state (call on disarm).
func (p *PID) Reset() {
	p.integral  = 0
	p.prevError = 0
}

// ---------------------------------------------------------------------------
// Complementary filter
// ---------------------------------------------------------------------------

// CompFilter fuses gyro and accelerometer to estimate roll / pitch.
type CompFilter struct {
	Alpha float64
	Roll  float64
	Pitch float64
}

// Update performs one filter iteration; returns (roll, pitch) in degrees.
func (f *CompFilter) Update(ax, ay, az, gx, gy, dt float64) (float64, float64) {
	f.Roll  += gx * dt
	f.Pitch += gy * dt

	if az != 0 {
		accelRoll  := math.Atan2(ay, az) * 180 / math.Pi
		accelPitch := math.Atan2(-ax, math.Sqrt(ay*ay+az*az)) * 180 / math.Pi
		f.Roll  = f.Alpha*f.Roll  + (1-f.Alpha)*accelRoll
		f.Pitch = f.Alpha*f.Pitch + (1-f.Alpha)*accelPitch
	}

	return f.Roll, f.Pitch
}

// ---------------------------------------------------------------------------
// Motor output helpers
// ---------------------------------------------------------------------------

// clamp01 constrains v to [0, 1].
func clamp01(v float64) float64 {
	if v < 0 {
		return 0
	}
	if v > 1 {
		return 1
	}
	return v
}

// throttleToUs converts a 0–1 throttle value to ESC µs (1000–2000).
func throttleToUs(v float64) uint32 {
	return uint32(pwmMinUs + clamp01(v)*float64(pwmMaxUs-pwmMinUs))
}

// mixQuadX returns motor PWM values [FL, FR, RR, RL] for a quad-X frame.
func mixQuadX(throttle, pitch, roll, yaw float64) [4]uint32 {
	norm := 500.0
	raw := [4]float64{
		throttle + pitch/norm + roll/norm - yaw/norm,
		throttle + pitch/norm - roll/norm + yaw/norm,
		throttle - pitch/norm - roll/norm - yaw/norm,
		throttle - pitch/norm + roll/norm + yaw/norm,
	}
	var out [4]uint32
	for i, v := range raw {
		out[i] = throttleToUs(v)
	}
	return out
}

// ---------------------------------------------------------------------------
// PWM output (hardware abstraction)
// ---------------------------------------------------------------------------

// setPWM writes a PWM pulse width to a machine.Pin.
// On hardware this uses the machine.PWM API.
// On desktop (tinygo run) it prints to stdout for inspection.
func setPWM(pin machine.Pin, us uint32) {
	// Real implementation — uncomment on actual hardware:
	//
	//   pwm := machine.PWM0   // choose correct PWM peripheral for the pin
	//   pwm.Configure(machine.PWMConfig{Period: 20_000_000})  // 50 Hz
	//   ch, _ := pwm.Channel(pin)
	//   pwm.Set(ch, pwm.Top()*us/20_000)
	//
	// Simulation stub:
	_ = pin
	_ = us
}

// ---------------------------------------------------------------------------
// Simulated IMU (replace with tinygo.org/x/drivers/mpu6050 on hardware)
// ---------------------------------------------------------------------------

// readIMU returns (ax, ay, az m/s², gx, gy, gz °/s).
// Simulation returns near-level values; replace with real driver call.
func readIMU() (ax, ay, az, gx, gy, gz float64) {
	// On hardware (Pico + MPU-6050 via I2C):
	//   sensor := mpu6050.New(machine.I2C0)
	//   sensor.Configure()
	//   data, _ := sensor.ReadAcceleration()
	//   ...
	return 0.0, 0.1, -9.81, 0.5, 0.2, 0.0
}

// ---------------------------------------------------------------------------
// RC input (simulated — replace with PPM/SBUS parser on hardware)
// ---------------------------------------------------------------------------

// RCInput holds normalised stick values.
type RCInput struct {
	Throttle float64 // 0–1
	Roll     float64 // -1 to +1
	Pitch    float64 // -1 to +1
	Yaw      float64 // -1 to +1
	Armed    bool
}

// readRC returns the latest RC input.
// Simulation returns a gentle hover command; replace with UART/PPM ISR.
func readRC() RCInput {
	return RCInput{
		Throttle: 0.45,
		Roll:     0.1,
		Pitch:    0.0,
		Yaw:      0.0,
		Armed:    true,
	}
}

// ---------------------------------------------------------------------------
// Motor pins (adjust for your wiring)
// ---------------------------------------------------------------------------

var motorPins = [4]machine.Pin{
	machine.GP2, // Front-Left
	machine.GP3, // Front-Right
	machine.GP4, // Rear-Right
	machine.GP5, // Rear-Left
}

// ---------------------------------------------------------------------------
// Main firmware loop
// ---------------------------------------------------------------------------

func main() {
	// Configure motor pins as output
	for _, pin := range motorPins {
		pin.Configure(machine.PinConfig{Mode: machine.PinOutput})
	}

	// Disarm pulse to all ESCs
	for _, pin := range motorPins {
		setPWM(pin, pwmMinUs)
	}
	time.Sleep(2 * time.Second) // ESC arming delay

	// Sensors & controllers
	filter := CompFilter{Alpha: 0.98}
	pids := [3]PID{
		{Kp: 4.5, Ki: 0.04, Kd: 0.40, Limit: 400}, // roll
		{Kp: 4.5, Ki: 0.04, Kd: 0.40, Limit: 400}, // pitch
		{Kp: 6.0, Ki: 0.10, Kd: 0.20, Limit: 400}, // yaw
	}

	dt := float64(loopDtMs) / 1000.0
	armed := false

	for {
		loopStart := time.Now()

		// Read sensors
		ax, ay, az, gx, gy, gz := readIMU()
		rc := readRC()

		// Arm / disarm logic
		if rc.Armed && !armed {
			armed = true
			for i := range pids {
				pids[i].Reset()
			}
		} else if !rc.Armed {
			armed = false
		}

		// Attitude estimate
		roll, pitch := filter.Update(ax, ay, az, gx, gy, dt)

		// PID control
		rollCmd  := pids[0].Compute(0.0, roll,  dt)
		pitchCmd := pids[1].Compute(0.0, pitch, dt)
		yawCmd   := pids[2].Compute(0.0, gz,    dt)

		// Motor mix
		var motorUS [4]uint32
		if armed {
			motorUS = mixQuadX(rc.Throttle, pitchCmd, rollCmd, yawCmd)
		} else {
			motorUS = [4]uint32{pwmMinUs, pwmMinUs, pwmMinUs, pwmMinUs}
		}

		// Write outputs
		for i, pin := range motorPins {
			setPWM(pin, motorUS[i])
		}

		// Rate limiting
		elapsed := time.Since(loopStart)
		target  := time.Duration(loopDtMs) * time.Millisecond
		if elapsed < target {
			time.Sleep(target - elapsed)
		}
	}
}
