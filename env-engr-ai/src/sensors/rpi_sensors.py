"""
Raspberry Pi sensor implementations with graceful fallback to mock behavior.
"""
import time
from datetime import datetime
from typing import Optional

from src.models.schemas import SensorConfig, SensorReading, SensorType
from src.sensors.base import AbstractSensor, MockSensor

# Attempt hardware imports; fall back gracefully
try:
    import RPi.GPIO as GPIO  # type: ignore
    _GPIO_AVAILABLE = True
except ImportError:
    _GPIO_AVAILABLE = False

try:
    import smbus2  # type: ignore
    _SMBUS_AVAILABLE = True
except ImportError:
    _SMBUS_AVAILABLE = False


class DHT22Sensor(AbstractSensor):
    """
    DHT22 temperature + humidity sensor via GPIO.
    Falls back to MockSensor if RPi.GPIO is unavailable.
    """

    def __init__(self, config: SensorConfig, gpio_pin: int = 4) -> None:
        super().__init__(config)
        self._gpio_pin = gpio_pin
        self._mock: Optional[MockSensor] = None
        if not _GPIO_AVAILABLE:
            self._mock = MockSensor(config)

    def initialize(self) -> bool:
        if self._mock:
            return self._mock.initialize()
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._gpio_pin, GPIO.IN)
            self._initialized = True
            return True
        except Exception:
            self._mock = MockSensor(self.config)
            return self._mock.initialize()

    def read(self) -> SensorReading:
        if self._mock:
            return self._mock.read()
        try:
            # Real DHT22 protocol: send start pulse, read 40 bits
            # This is a simplified placeholder for the actual bit-bang protocol
            raw_value = self._read_dht22_raw()
            reading = SensorReading(
                sensor_id=self.config.sensor_id,
                timestamp=datetime.now(),
                value=raw_value + self.config.calibration_offset,
                unit="°C" if self.config.sensor_type == SensorType.TEMPERATURE else "%RH",
                quality=0.95,
            )
            self._last_reading = reading
            return reading
        except Exception:
            if not self._mock:
                self._mock = MockSensor(self.config)
                self._mock.initialize()
            return self._mock.read()

    def _read_dht22_raw(self) -> float:
        """Read raw value from DHT22 via bit-bang GPIO protocol."""
        # Send start signal
        GPIO.setup(self._gpio_pin, GPIO.OUT)
        GPIO.output(self._gpio_pin, GPIO.LOW)
        time.sleep(0.02)
        GPIO.output(self._gpio_pin, GPIO.HIGH)
        GPIO.setup(self._gpio_pin, GPIO.IN)

        # Collect pulse timings
        pulses: list[float] = []
        last_state = GPIO.input(self._gpio_pin)
        last_time = time.time()
        for _ in range(500):
            state = GPIO.input(self._gpio_pin)
            if state != last_state:
                pulses.append(time.time() - last_time)
                last_time = time.time()
                last_state = state
            if len(pulses) >= 84:
                break

        if len(pulses) < 84:
            raise IOError("DHT22 did not respond correctly")

        # Decode 40 bits from pulse widths
        bits: list[int] = []
        for i in range(2, min(82, len(pulses)), 2):
            if pulses[i] > 0.00005:
                bits.append(1)
            else:
                bits.append(0)

        if len(bits) < 40:
            raise IOError("Insufficient bits from DHT22")

        # Assemble bytes
        raw_bytes = [0] * 5
        for i in range(40):
            raw_bytes[i // 8] = (raw_bytes[i // 8] << 1) | bits[i]

        checksum = sum(raw_bytes[:4]) & 0xFF
        if checksum != raw_bytes[4]:
            raise IOError("DHT22 checksum error")

        if self.config.sensor_type == SensorType.HUMIDITY:
            return ((raw_bytes[0] << 8) | raw_bytes[1]) / 10.0
        else:
            temp = ((raw_bytes[2] & 0x7F) << 8) | raw_bytes[3]
            if raw_bytes[2] & 0x80:
                temp = -temp
            return temp / 10.0

    def calibrate(self, reference_value: float) -> None:
        if self._last_reading:
            self.config.calibration_offset += reference_value - self._last_reading.value

    def shutdown(self) -> None:
        self._initialized = False
        if _GPIO_AVAILABLE and not self._mock:
            try:
                GPIO.cleanup(self._gpio_pin)
            except Exception:
                pass


class MQ135Sensor(AbstractSensor):
    """
    MQ135 air quality sensor (analog) read via external ADC.
    Falls back to MockSensor if hardware unavailable.
    """

    # Calibration constants
    RLOAD = 10.0   # Load resistance kΩ
    RZERO = 76.63  # Sensor resistance in clean air
    PARA = 116.6020682
    PARB = 2.769034857

    def __init__(self, config: SensorConfig, adc_channel: int = 0) -> None:
        super().__init__(config)
        self._adc_channel = adc_channel
        self._mock: Optional[MockSensor] = None
        if not (_GPIO_AVAILABLE and _SMBUS_AVAILABLE):
            self._mock = MockSensor(config)

    def initialize(self) -> bool:
        if self._mock:
            return self._mock.initialize()
        try:
            # Initialize I2C ADC (e.g., ADS1115 at 0x48)
            self._bus = smbus2.SMBus(1)
            self._initialized = True
            return True
        except Exception:
            self._mock = MockSensor(self.config)
            return self._mock.initialize()

    def _read_adc(self) -> int:
        """Read raw 12-bit ADC value from MCP3008 or similar."""
        config_reg = 0xC183 | (self._adc_channel << 12)
        msg_w = smbus2.i2c_msg.write(0x48, [config_reg >> 8, config_reg & 0xFF])
        msg_r = smbus2.i2c_msg.read(0x48, 2)
        self._bus.i2c_rdwr(msg_w)
        time.sleep(0.01)
        self._bus.i2c_rdwr(msg_r)
        raw = list(msg_r)
        return ((raw[0] & 0x0F) << 8) | raw[1]

    def _calculate_ppm(self, adc_value: int) -> float:
        """Convert ADC reading to CO2 equivalent ppm."""
        voltage = adc_value * 3.3 / 4096.0
        rs = (3.3 - voltage) / voltage * self.RLOAD
        ratio = rs / self.RZERO
        ppm = self.PARA * (ratio ** (-self.PARB))
        return max(300.0, min(10000.0, ppm))

    def read(self) -> SensorReading:
        if self._mock:
            return self._mock.read()
        try:
            adc_val = self._read_adc()
            ppm = self._calculate_ppm(adc_val) + self.config.calibration_offset
            reading = SensorReading(
                sensor_id=self.config.sensor_id,
                timestamp=datetime.now(),
                value=round(ppm, 1),
                unit="ppm",
                quality=0.9,
            )
            self._last_reading = reading
            return reading
        except Exception:
            if not self._mock:
                self._mock = MockSensor(self.config)
                self._mock.initialize()
            return self._mock.read()

    def calibrate(self, reference_value: float) -> None:
        if self._last_reading:
            self.config.calibration_offset += reference_value - self._last_reading.value

    def shutdown(self) -> None:
        self._initialized = False
        if _SMBUS_AVAILABLE and not self._mock:
            try:
                self._bus.close()
            except Exception:
                pass


class DS18B20Sensor(AbstractSensor):
    """
    DS18B20 waterproof temperature sensor via 1-Wire interface.
    Reads from /sys/bus/w1/devices/<id>/w1_slave.
    """

    W1_BASE = "/sys/bus/w1/devices"

    def __init__(self, config: SensorConfig, device_id: str = None) -> None:
        super().__init__(config)
        self._device_id = device_id
        self._device_path: Optional[str] = None
        self._mock: Optional[MockSensor] = None

    def initialize(self) -> bool:
        import os
        import glob
        try:
            if self._device_id:
                self._device_path = f"{self.W1_BASE}/{self._device_id}/w1_slave"
            else:
                devices = glob.glob(f"{self.W1_BASE}/28-*/w1_slave")
                if not devices:
                    raise FileNotFoundError("No DS18B20 found on 1-Wire bus")
                self._device_path = devices[0]
            # Verify readable
            with open(self._device_path, "r"):
                pass
            self._initialized = True
            return True
        except Exception:
            self._mock = MockSensor(self.config)
            return self._mock.initialize()

    def _read_temp_raw(self) -> list[str]:
        with open(self._device_path, "r") as f:
            return f.readlines()

    def read(self) -> SensorReading:
        if self._mock:
            return self._mock.read()
        try:
            lines = self._read_temp_raw()
            # Wait for valid CRC
            retries = 0
            while lines[0].strip()[-3:] != "YES" and retries < 5:
                time.sleep(0.2)
                lines = self._read_temp_raw()
                retries += 1
            if lines[0].strip()[-3:] != "YES":
                raise IOError("DS18B20 CRC failed")
            equals_pos = lines[1].find("t=")
            if equals_pos == -1:
                raise IOError("Temperature not found in DS18B20 output")
            temp_c = float(lines[1][equals_pos + 2:]) / 1000.0
            temp_c += self.config.calibration_offset
            reading = SensorReading(
                sensor_id=self.config.sensor_id,
                timestamp=datetime.now(),
                value=round(temp_c, 3),
                unit="°C",
                quality=0.98,
            )
            self._last_reading = reading
            return reading
        except Exception:
            if not self._mock:
                self._mock = MockSensor(self.config)
                self._mock.initialize()
            return self._mock.read()

    def calibrate(self, reference_value: float) -> None:
        if self._last_reading:
            self.config.calibration_offset += reference_value - self._last_reading.value

    def shutdown(self) -> None:
        self._initialized = False


class PHSensor(AbstractSensor):
    """
    pH sensor read via I2C ADC (e.g., Atlas Scientific or analog with ADS1115).
    Falls back to MockSensor if smbus2 unavailable.
    """

    # Atlas Scientific EZO-pH I2C address
    ATLAS_I2C_ADDR = 0x63
    # Calibration: mV at pH 4, pH 7, pH 10
    PH_CALIBRATION = {4.0: 184.0, 7.0: 0.0, 10.0: -184.0}

    def __init__(self, config: SensorConfig, i2c_bus: int = 1,
                 i2c_address: int = 0x63) -> None:
        super().__init__(config)
        self._i2c_bus = i2c_bus
        self._i2c_address = i2c_address
        self._bus: Optional[object] = None
        self._mock: Optional[MockSensor] = None
        if not _SMBUS_AVAILABLE:
            self._mock = MockSensor(config)

    def initialize(self) -> bool:
        if self._mock:
            return self._mock.initialize()
        try:
            self._bus = smbus2.SMBus(self._i2c_bus)
            self._initialized = True
            return True
        except Exception:
            self._mock = MockSensor(self.config)
            return self._mock.initialize()

    def _query_atlas(self, command: str) -> str:
        """Send command to Atlas EZO module and read response."""
        encoded = [ord(c) for c in command]
        self._bus.write_i2c_block_data(self._i2c_address, 0, encoded)
        time.sleep(0.9)  # Processing time per Atlas spec
        data = self._bus.read_i2c_block_data(self._i2c_address, 0, 31)
        # Strip leading status byte and null bytes
        response = "".join([chr(b) for b in data[1:] if b not in (0, 1, 2, 254, 255)])
        return response.strip()

    def read(self) -> SensorReading:
        if self._mock:
            r = self._mock.read()
            # Override unit for pH mock
            r.unit = "pH"
            return r
        try:
            response = self._query_atlas("R")
            ph_value = float(response) + self.config.calibration_offset
            ph_value = max(0.0, min(14.0, ph_value))
            reading = SensorReading(
                sensor_id=self.config.sensor_id,
                timestamp=datetime.now(),
                value=round(ph_value, 2),
                unit="pH",
                quality=0.95,
            )
            self._last_reading = reading
            return reading
        except Exception:
            if not self._mock:
                self._mock = MockSensor(self.config)
                self._mock.initialize()
            r = self._mock.read()
            r.unit = "pH"
            return r

    def calibrate(self, reference_value: float) -> None:
        if self._last_reading:
            self.config.calibration_offset += reference_value - self._last_reading.value
        if not self._mock and self._bus:
            try:
                if abs(reference_value - 7.0) < 0.5:
                    self._query_atlas(f"Cal,mid,{reference_value:.2f}")
                elif reference_value < 5.0:
                    self._query_atlas(f"Cal,low,{reference_value:.2f}")
                else:
                    self._query_atlas(f"Cal,high,{reference_value:.2f}")
            except Exception:
                pass

    def shutdown(self) -> None:
        self._initialized = False
        if _SMBUS_AVAILABLE and self._bus and not self._mock:
            try:
                self._bus.close()
            except Exception:
                pass
