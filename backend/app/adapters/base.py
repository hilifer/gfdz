"""厂家适配器基类 — 所有厂家必须实现这些接口"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class StationInfo:
    station_code: str
    name: str
    capacity_kwp: float | None = None
    status: str = "normal"
    longitude: float | None = None
    latitude: float | None = None
    address: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class StationRealtimeData:
    current_power_kw: float | None = None
    today_generation: float | None = None
    month_generation: float | None = None
    year_generation: float | None = None
    total_generation: float | None = None


@dataclass
class StationDailyData:
    date: date
    generation_kwh: float | None = None
    peak_power_kw: float | None = None
    equivalent_hours: float | None = None


@dataclass
class DeviceInfo:
    device_code: str
    device_name: str
    device_type: str  # inverter/meter/combiner_box/weather_station/storage
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    rated_power: float | None = None
    status: str = "normal"


@dataclass
class DeviceRealtimeData:
    device_code: str
    timestamp: datetime
    power_kw: float | None = None
    voltage_v: float | None = None
    current_a: float | None = None
    temperature: float | None = None
    frequency: float | None = None
    daily_generation: float | None = None
    raw_data: dict = field(default_factory=dict)


@dataclass
class AlarmInfo:
    alarm_code: str
    alarm_name: str
    alarm_level: str  # info/warning/critical
    alarm_time: datetime
    recover_time: datetime | None = None
    device_name: str | None = None
    description: str | None = None


class BaseAdapter(ABC):
    """所有厂家适配器的基类"""

    def __init__(self, api_base_url: str, auth_config: dict):
        self.api_base_url = api_base_url.rstrip("/")
        self.auth_config = auth_config

    @abstractmethod
    async def authenticate(self) -> bool:
        """认证/登录"""

    @abstractmethod
    async def get_station_list(self) -> list[StationInfo]:
        """获取电站列表"""

    @abstractmethod
    async def get_station_realtime(self, station_code: str) -> StationRealtimeData | None:
        """获取电站实时数据"""

    @abstractmethod
    async def get_station_daily(self, station_code: str, query_date: date) -> StationDailyData | None:
        """获取电站日数据"""

    async def get_device_list(self, station_code: str) -> list[DeviceInfo]:
        """获取设备列表（可选实现）"""
        return []

    async def get_device_realtime(self, station_code: str, device_code: str) -> DeviceRealtimeData | None:
        """获取设备实时数据（可选实现）"""
        return None

    async def get_alarms(self, station_code: str) -> list[AlarmInfo]:
        """获取告警列表（可选实现）"""
        return []

    async def close(self):
        """关闭连接"""
        pass
