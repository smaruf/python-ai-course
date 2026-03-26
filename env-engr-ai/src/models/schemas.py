"""
Pydantic v2 schemas for the Environmental Engineering AI Platform.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SensorType(str, Enum):
    TEMPERATURE = "TEMPERATURE"
    HUMIDITY = "HUMIDITY"
    PH = "PH"
    DISSOLVED_OXYGEN = "DISSOLVED_OXYGEN"
    TURBIDITY = "TURBIDITY"
    CO2 = "CO2"
    METHANE = "METHANE"
    FLOW_RATE = "FLOW_RATE"
    PRESSURE = "PRESSURE"
    MOISTURE = "MOISTURE"
    SOLAR_IRRADIANCE = "SOLAR_IRRADIANCE"
    WIND_SPEED = "WIND_SPEED"
    POWER_OUTPUT = "POWER_OUTPUT"


class WasteType(str, Enum):
    ORGANIC = "ORGANIC"
    RECYCLABLE = "RECYCLABLE"
    HAZARDOUS = "HAZARDOUS"
    INERT = "INERT"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class FermentationStage(str, Enum):
    INOCULATION = "INOCULATION"
    EXPONENTIAL = "EXPONENTIAL"
    STATIONARY = "STATIONARY"
    DECLINE = "DECLINE"


class OilGrade(str, Enum):
    EXTRA_VIRGIN = "EXTRA_VIRGIN"
    VIRGIN = "VIRGIN"
    REFINED = "REFINED"
    POMACE = "POMACE"
    OFF_GRADE = "OFF_GRADE"


class EnergySource(str, Enum):
    SOLAR = "SOLAR"
    WIND = "WIND"
    BIOGAS = "BIOGAS"
    HYDRO = "HYDRO"


class ProcessStage(str, Enum):
    STARTUP = "STARTUP"
    RUNNING = "RUNNING"
    SHUTDOWN = "SHUTDOWN"
    MAINTENANCE = "MAINTENANCE"
    FAULT = "FAULT"


# ---------------------------------------------------------------------------
# Sensor schemas
# ---------------------------------------------------------------------------

class SensorReading(BaseModel):
    model_config = ConfigDict(frozen=False)

    reading_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sensor_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    value: float
    unit: str
    quality: float = Field(default=1.0)

    @field_validator("quality", mode="before")
    @classmethod
    def clamp_quality(cls, v: float) -> float:
        return max(0.0, min(1.0, float(v)))


class SensorConfig(BaseModel):
    model_config = ConfigDict(frozen=False)

    sensor_id: str
    sensor_type: SensorType
    location: str
    calibration_offset: float = 0.0
    sampling_interval_s: float = Field(default=1.0, gt=0.0)


# ---------------------------------------------------------------------------
# Waste management schemas
# ---------------------------------------------------------------------------

class WasteClassification(BaseModel):
    model_config = ConfigDict(frozen=False)

    reading_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    waste_type: WasteType
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_action: str
    features: dict[str, float]


# ---------------------------------------------------------------------------
# Biofuel schemas
# ---------------------------------------------------------------------------

class BiofuelMetrics(BaseModel):
    model_config = ConfigDict(frozen=False)

    batch_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    temperature: float  # °C
    ph: float
    sugar_content: float  # g/L
    ethanol_yield: float  # % v/v
    stage: FermentationStage
    co2_rate: float  # mL/min

    @field_validator("ph")
    @classmethod
    def validate_ph(cls, v: float) -> float:
        if not (0.0 <= v <= 14.0):
            raise ValueError(f"pH must be between 0 and 14, got {v}")
        return v


# ---------------------------------------------------------------------------
# Edible oil schemas
# ---------------------------------------------------------------------------

class EdibleOilMetrics(BaseModel):
    model_config = ConfigDict(frozen=False)

    batch_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    temperature: float  # °C
    pressure: float  # bar
    moisture_content: float  # %
    quality_grade: OilGrade
    acidity: float  # % free fatty acids
    peroxide_value: float  # meq O2/kg


# ---------------------------------------------------------------------------
# Renewable energy schemas
# ---------------------------------------------------------------------------

class RenewableEnergyMetrics(BaseModel):
    model_config = ConfigDict(frozen=False)

    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: EnergySource
    timestamp: datetime = Field(default_factory=datetime.now)
    power_output_w: float = Field(ge=0.0)
    efficiency: float = Field(ge=0.0, le=1.0)
    capacity_factor: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, float] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Alert and system status schemas
# ---------------------------------------------------------------------------

class Alert(BaseModel):
    model_config = ConfigDict(frozen=False)

    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: AlertSeverity
    source_module: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    resolved: bool = False
    acknowledged: bool = False


class SystemStatus(BaseModel):
    model_config = ConfigDict(frozen=False)

    timestamp: datetime = Field(default_factory=datetime.now)
    active_sensors: list[str] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)
    module_statuses: dict[str, str] = Field(default_factory=dict)
