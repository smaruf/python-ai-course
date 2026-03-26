/**
 * Arduino Environmental Sensor Node
 * 
 * Reads: temperature (NTC thermistor), pH (analog), soil moisture (capacitive)
 * Sends JSON over Serial at 9600 baud
 * Format: {"sensor_id":"temp_01","value":23.5,"unit":"C","quality":0.95,"ts":12345}
 * 
 * Wiring:
 *   A0: NTC thermistor (10kΩ) with 10kΩ pull-down to GND
 *   A1: pH sensor analog output (0–14 pH → 0–5V)
 *   A2: Capacitive moisture sensor (3.3V–5V output)
 *   D2: Status LED (blinks on successful send)
 */

#include <Arduino.h>

// -----------------------------------------------------------------------
// Pin definitions
// -----------------------------------------------------------------------
const int PIN_TEMP     = A0;
const int PIN_PH       = A1;
const int PIN_MOISTURE = A2;
const int PIN_LED      = 2;

// -----------------------------------------------------------------------
// Calibration constants
// -----------------------------------------------------------------------
// NTC thermistor (Steinhart-Hart coefficients for 10k NTC B=3950)
const float NTC_NOMINAL    = 10000.0;  // Resistance at 25°C (Ω)
const float TEMP_NOMINAL    = 25.0;    // Reference temperature (°C)
const float BCOEFFICIENT    = 3950.0;  // Beta coefficient
const float SERIES_RESISTOR = 10000.0; // Series resistor value (Ω)

// pH sensor calibration: 2-point (pH4 and pH7 buffer solutions)
// IMPORTANT: Update these values after performing calibration with buffer solutions.
// Use pH 4.01 and pH 7.01 certified buffers and record the measured voltages below.
// Optionally store in EEPROM for persistence across power cycles.
float pH4_voltage  = 3.00;  // Measured voltage at pH 4.0 (update at calibration)
float pH7_voltage  = 2.50;  // Measured voltage at pH 7.0
float ph_slope     = (7.0 - 4.0) / (pH7_voltage - pH4_voltage);

// Moisture sensor: dry and wet ADC readings (0–1023)
const int MOISTURE_DRY = 850;   // ADC reading in air
const int MOISTURE_WET = 350;   // ADC reading submerged

// -----------------------------------------------------------------------
// Constants
// -----------------------------------------------------------------------
const unsigned long SEND_INTERVAL_MS = 2000;  // 2 seconds between sends
const int ADC_SAMPLES = 8;  // Oversampling for noise reduction
const float ADC_REF   = 5.0;   // V
const int ADC_MAX     = 1023;

// -----------------------------------------------------------------------
// Sensor validity ranges
// -----------------------------------------------------------------------
const float TEMP_MIN     = -10.0;
const float TEMP_MAX     = 60.0;
const float PH_MIN       = 0.0;
const float PH_MAX       = 14.0;
const float MOISTURE_MIN = 0.0;
const float MOISTURE_MAX = 100.0;

unsigned long lastSendTime = 0;
unsigned long sampleCount  = 0;

// -----------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------
int readADCOversampled(int pin, int samples) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delayMicroseconds(100);
  }
  return (int)(sum / samples);
}

float adcToVoltage(int adcValue) {
  return (float)adcValue * ADC_REF / ADC_MAX;
}

float readTemperature() {
  int raw = readADCOversampled(PIN_TEMP, ADC_SAMPLES);
  float voltage = adcToVoltage(raw);
  if (voltage < 0.1 || voltage > (ADC_REF - 0.1)) {
    return NAN;  // Sensor disconnected
  }
  // Voltage divider → thermistor resistance
  float resistance = SERIES_RESISTOR * voltage / (ADC_REF - voltage);
  // Steinhart-Hart equation
  float steinhart = resistance / NTC_NOMINAL;
  steinhart = log(steinhart);
  steinhart /= BCOEFFICIENT;
  steinhart += 1.0 / (TEMP_NOMINAL + 273.15);
  steinhart = 1.0 / steinhart;
  return steinhart - 273.15;
}

float readPH() {
  int raw = readADCOversampled(PIN_PH, ADC_SAMPLES);
  float voltage = adcToVoltage(raw);
  if (voltage < 0.05 || voltage > (ADC_REF - 0.05)) {
    return NAN;  // Sensor disconnected
  }
  float ph = 7.0 + (pH7_voltage - voltage) * ph_slope;
  return ph;
}

float readMoisture() {
  int raw = readADCOversampled(PIN_MOISTURE, ADC_SAMPLES);
  // Map to 0-100% (inverted: higher ADC = drier)
  float pct = (float)(MOISTURE_DRY - raw) / (MOISTURE_DRY - MOISTURE_WET) * 100.0;
  return constrain(pct, 0.0, 100.0);
}

float calculateQuality(float value, float minVal, float maxVal) {
  if (isnan(value))    return 0.0;
  if (value < minVal || value > maxVal) return 0.3;
  // Quality degrades near edges of valid range
  float mid   = (minVal + maxVal) / 2.0;
  float range = (maxVal - minVal) / 2.0;
  float dist  = abs(value - mid) / range;
  return 1.0 - 0.2 * dist;
}

void sendJSON(const char* sensorId, float value, const char* unit, float quality) {
  if (isnan(value)) return;  // Skip NaN readings
  
  Serial.print(F("{\"sensor_id\":\""));
  Serial.print(sensorId);
  Serial.print(F("\",\"value\":"));
  Serial.print(value, 3);
  Serial.print(F(",\"unit\":\""));
  Serial.print(unit);
  Serial.print(F("\",\"quality\":"));
  Serial.print(quality, 3);
  Serial.print(F(",\"ts\":"));
  Serial.print(millis());
  Serial.println(F("}"));
}

// -----------------------------------------------------------------------
// Arduino lifecycle
// -----------------------------------------------------------------------
void setup() {
  Serial.begin(9600);
  while (!Serial) { ; }  // Wait for serial on Leonardo/Due

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);
  
  // Discard first ADC readings (settling time)
  for (int i = 0; i < 5; i++) {
    analogRead(PIN_TEMP);
    analogRead(PIN_PH);
    analogRead(PIN_MOISTURE);
    delay(10);
  }

  Serial.println(F("{\"type\":\"startup\",\"node\":\"arduino_01\"}"));
}

void loop() {
  unsigned long now = millis();
  if (now - lastSendTime >= SEND_INTERVAL_MS) {
    lastSendTime = now;
    sampleCount++;

    // Read sensors
    float temp     = readTemperature();
    float ph       = readPH();
    float moisture = readMoisture();

    // Calculate quality scores
    float q_temp     = calculateQuality(temp, TEMP_MIN, TEMP_MAX);
    float q_ph       = calculateQuality(ph, PH_MIN, PH_MAX);
    float q_moisture = calculateQuality(moisture, MOISTURE_MIN, MOISTURE_MAX);

    // Send readings
    sendJSON("temp_01", temp, "C", q_temp);
    sendJSON("ph_01", ph, "pH", q_ph);
    sendJSON("moisture_01", moisture, "%", q_moisture);

    // Blink LED
    digitalWrite(PIN_LED, HIGH);
    delay(50);
    digitalWrite(PIN_LED, LOW);
  }
}
