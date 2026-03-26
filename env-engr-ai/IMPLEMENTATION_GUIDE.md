# Implementation Guide

Step-by-step guide for deploying the Environmental Engineering AI Platform.

---

## 1. Raspberry Pi Setup

### 1.1 OS and Dependencies
```bash
# Flash Raspberry Pi OS Lite (64-bit)
# Enable I2C and 1-Wire:
sudo raspi-config  # Interface Options → I2C, 1-Wire

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
nano .env  # Set PC_URL, NODE_ID, SENSORS
```

### 1.2 DHT22 Wiring
```
RPi Pin 1  (3.3V) ──────────── DHT22 Pin 1 (VCC)
RPi Pin 7  (GPIO4) ──┬──────── DHT22 Pin 2 (DATA)
                     │
                    10kΩ (pull-up)
                     │
RPi Pin 6  (GND)  ──┴──────── DHT22 Pin 4 (GND)
```

### 1.3 DS18B20 (1-Wire) Wiring
```
RPi Pin 1  (3.3V) ──────────── DS18B20 VCC (Red)
RPi Pin 4  (GPIO4) ──┬──────── DS18B20 DATA (Yellow)
                     │
                    4.7kΩ (pull-up to 3.3V)
RPi Pin 6  (GND)  ──────────── DS18B20 GND (Black)
```

### 1.4 Atlas Scientific EZO-pH (I²C) Wiring
```
RPi Pin 1  (3.3V) ──────────── EZO-pH VCC
RPi Pin 3  (SDA)  ──────────── EZO-pH SDA
RPi Pin 5  (SCL)  ──────────── EZO-pH SCL
RPi Pin 6  (GND)  ──────────── EZO-pH GND
```

---

## 2. Arduino Setup

### 2.1 Arduino Uno Wiring
```
Arduino A0 ──── NTC Thermistor ──── 10kΩ ──── 5V
                       │
                      GND

Arduino A1 ──── pH Sensor AOUT
Arduino A2 ──── Capacitive Moisture AOUT
Arduino D2 ──── Status LED ──── 220Ω ──── GND
Arduino 5V ──── Sensor VCC
Arduino GND ─── Sensor GND
```

### 2.2 Upload Firmware
```bash
# Using Arduino IDE: open firmware/arduino/sensor_node.ino
# Board: Arduino Uno
# Port: /dev/ttyACM0 (Linux) or COM3 (Windows)
# Upload → monitor Serial at 9600 baud
```

---

## 3. PC/Server Setup

### 3.1 Install and Test
```bash
cd env-engr-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify setup
python -m pytest tests/ -v
python main.py demo
```

### 3.2 Start Sensor Node on RPi
```bash
# On Raspberry Pi:
python firmware/rpi/sensor_node.py
```

---

## 4. Calibration Procedures

### 4.1 pH Sensor Calibration
1. Prepare pH 4.0 and pH 7.0 buffer solutions
2. Rinse electrode with distilled water
3. Place in pH 7.0 buffer, wait 60 seconds
4. Record voltage; update `pH7_voltage` in `sensor_node.ino`
5. Place in pH 4.0 buffer, wait 60 seconds
6. Record voltage; update `pH4_voltage` in `sensor_node.ino`

### 4.2 NTC Thermistor Calibration
```c
// In sensor_node.ino, verify:
const float BCOEFFICIENT = 3950.0;   // Check datasheet
const float NTC_NOMINAL   = 10000.0; // 10kΩ at 25°C
```

### 4.3 Moisture Sensor Calibration
1. Read ADC with sensor in dry air → update `MOISTURE_DRY`
2. Read ADC with sensor submerged in water → update `MOISTURE_WET`

---

## 5. Module-Specific Configuration

### 5.1 Biofuel – Target Parameters
```python
# In fermentation.py, OPTIMAL_RANGES:
FermentationStage.EXPONENTIAL: {
    "temperature": (30.0, 35.0),  # Adjust for your yeast strain
    "ph": (4.0, 5.0),
}
```

### 5.2 Edible Oil – Standards
```python
# To add a new standard in quality_control.py:
STANDARDS["MY_STANDARD"] = {
    OilGrade.EXTRA_VIRGIN: {"acidity_max": 0.8, "peroxide_max": 20.0, "moisture_max": 0.2},
}
```

### 5.3 Renewable Energy – Panel Parameters
```python
solar = SolarPanelMonitor(
    panel_id="PV_01",
    rated_power_w=400.0,    # Your panel's rated power
    panel_area_m2=2.0,      # Panel physical area
)
```

---

## 6. Deployment Checklist

- [ ] RPi OS flashed and updated
- [ ] I2C and 1-Wire enabled in raspi-config
- [ ] All sensors wired and physically tested
- [ ] Arduino sketch uploaded, serial output verified
- [ ] Python dependencies installed
- [ ] `.env` file configured with correct PC_URL
- [ ] pH sensor calibrated with buffer solutions
- [ ] Temperature sensor cross-checked with reference thermometer
- [ ] `python -m pytest tests/ -v` – all tests pass
- [ ] `python main.py demo` – demo runs successfully
- [ ] `python firmware/rpi/sensor_node.py` – data flowing to PC
- [ ] Alert thresholds configured in `main.py`
- [ ] Log directory writable

---

## 7. Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `RuntimeError: No DS18B20 found` | 1-Wire not enabled or bad wiring | Check raspi-config, verify 4.7kΩ pull-up |
| pH readings drift | Need calibration | Follow Section 4.1 |
| DHT22 returns NaN | GPIO timing issue | Ensure no other GPIO-intensive tasks |
| `smbus2` not found | Not installed | `pip install smbus2` |
| Arduino serial garbage | Wrong baud rate | Set 9600 baud in Serial Monitor |
| Neural network not converging | Learning rate too high | Reduce `learning_rate` in classifier |
