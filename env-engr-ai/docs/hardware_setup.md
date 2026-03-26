# Hardware Setup Guide

## Bill of Materials

| Component | Qty | Use |
|---|---|---|
| Raspberry Pi 4 (2GB) | 1 | Main data collection node |
| Arduino Uno R3 | 1 | Analog sensor acquisition |
| DHT22 sensor | 2 | Temperature + Humidity |
| DS18B20 (waterproof) | 2 | Liquid temperature |
| Atlas Scientific EZO-pH | 1 | pH measurement |
| MQ135 gas sensor | 1 | CO₂/air quality |
| ADS1115 ADC | 1 | 16-bit ADC for analog sensors |
| NTC 10kΩ thermistor | 2 | Arduino temperature |
| Capacitive moisture sensor | 2 | Soil/substrate moisture |
| 10kΩ resistors | 5 | Pull-ups and dividers |
| 4.7kΩ resistor | 2 | 1-Wire pull-up |

## RPi GPIO Pin Map

```
Pin  1 (3.3V) ──── DHT22 VCC, EZO-pH VCC
Pin  3 (SDA)  ──── ADS1115 SDA, EZO-pH SDA
Pin  4 (5V)   ──── Arduino VCC (if powered via RPi)
Pin  5 (SCL)  ──── ADS1115 SCL, EZO-pH SCL
Pin  6 (GND)  ──── Common ground
Pin  7 (GPIO4) ─── DHT22 DATA (10kΩ pull-up to 3.3V)
                   DS18B20 DATA (4.7kΩ pull-up to 3.3V)
Pin  9 (GND)  ──── DS18B20 GND
Pin 14 (GND)  ──── DHT22 GND
Pin 17 (3.3V) ──── DS18B20 VCC
```
