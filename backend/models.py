"""
Pydantic models defining the shape of API responses.
"""

from pydantic import BaseModel
from datetime import datetime


class SensorListResponse(BaseModel):
    sensors: list[str]


class HourlyReading(BaseModel):
    sensor_id: str
    hour: datetime
    co2_ppm_mean: float
    co2_ppm_min: float
    co2_ppm_max: float
    temp_c_mean: float
    temp_c_min: float
    temp_c_max: float
    humidity_pct_mean: float
    humidity_pct_min: float
    humidity_pct_max: float
    pressure_hpa_mean: float
    pressure_hpa_min: float
    pressure_hpa_max: float


class ReadingsResponse(BaseModel):
    sensor_id: str
    readings: list[HourlyReading]