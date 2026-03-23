"""Pydantic schemas for request/response validation"""
from datetime import datetime, date
from pydantic import BaseModel


# ---- 厂家 ----
class ManufacturerCreate(BaseModel):
    name: str
    code: str
    api_base_url: str | None = None
    adapter_class: str = ""
    auth_config: str | None = None
    description: str | None = None
    is_active: bool = True


class ManufacturerUpdate(BaseModel):
    name: str | None = None
    api_base_url: str | None = None
    adapter_class: str | None = None
    auth_config: str | None = None
    description: str | None = None
    is_active: bool | None = None


class ManufacturerResponse(BaseModel):
    id: int
    name: str
    code: str
    api_base_url: str | None
    adapter_class: str
    auth_config: str | None
    description: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- 电站 ----
class StationCreate(BaseModel):
    name: str
    station_code: str
    manufacturer_id: int
    capacity: float | None = None
    location: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    extra_params: str | None = None
    is_active: bool = True


class StationUpdate(BaseModel):
    name: str | None = None
    station_code: str | None = None
    capacity: float | None = None
    location: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    extra_params: str | None = None
    is_active: bool | None = None


class StationResponse(BaseModel):
    id: int
    name: str
    station_code: str
    manufacturer_id: int
    capacity: float | None
    location: str | None
    status: str
    is_active: bool
    last_sync_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- 发电数据 ----
class GenerationDataResponse(BaseModel):
    id: int
    station_id: int
    record_date: date
    daily_generation: float | None
    monthly_generation: float | None
    yearly_generation: float | None
    total_generation: float | None
    current_power: float | None
    daily_income: float | None
    daily_peak_power: float | None
    equivalent_hours: float | None
    pr_value: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- 告警 ----
class AlarmResponse(BaseModel):
    id: int
    station_id: int
    alarm_code: str | None
    alarm_name: str
    alarm_level: str
    alarm_time: datetime
    recover_time: datetime | None
    status: str
    description: str | None
    device_name: str | None

    model_config = {"from_attributes": True}
