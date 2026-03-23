"""适配器基类 - 所有厂家适配器必须继承此类"""
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

import httpx


@dataclass
class StationInfo:
    """电站信息"""
    station_code: str
    name: str
    capacity: float | None = None
    status: str = "normal"
    extra: dict = field(default_factory=dict)


@dataclass
class GenerationRecord:
    """发电数据记录"""
    record_date: date
    daily_generation: float | None = None
    monthly_generation: float | None = None
    yearly_generation: float | None = None
    total_generation: float | None = None
    current_power: float | None = None
    daily_income: float | None = None
    daily_peak_power: float | None = None
    equivalent_hours: float | None = None
    pr_value: float | None = None
    raw_data: dict = field(default_factory=dict)


@dataclass
class AlarmRecord:
    """告警记录"""
    alarm_name: str
    alarm_time: datetime
    alarm_code: str | None = None
    alarm_level: str = "info"
    status: str = "active"
    recover_time: datetime | None = None
    description: str | None = None
    device_name: str | None = None


class BaseAdapter(ABC):
    """
    厂家API适配器基类。

    每个厂家需要实现一个适配器子类，将厂家特定的API响应转换为统一的数据格式。

    使用方法:
    1. 继承 BaseAdapter
    2. 实现所有抽象方法
    3. 在 app/adapters/registry.py 中注册
    """

    def __init__(self, api_base_url: str, auth_config: dict | None = None, extra_params: dict | None = None):
        self.api_base_url = api_base_url.rstrip("/")
        self.auth_config = auth_config or {}
        self.extra_params = extra_params or {}
        self._client: httpx.AsyncClient | None = None
        self._token: str | None = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.api_base_url,
                timeout=30.0,
                headers=self._get_default_headers(),
            )
        return self._client

    def _get_default_headers(self) -> dict:
        """获取默认请求头，子类可覆盖"""
        return {"Content-Type": "application/json"}

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def authenticate(self) -> bool:
        """认证/登录，获取token等凭证。成功返回True。"""
        ...

    @abstractmethod
    async def get_station_list(self) -> list[StationInfo]:
        """获取电站列表"""
        ...

    @abstractmethod
    async def get_station_realtime(self, station_code: str) -> GenerationRecord | None:
        """获取电站实时数据"""
        ...

    @abstractmethod
    async def get_station_daily(self, station_code: str, query_date: date) -> GenerationRecord | None:
        """获取电站日发电数据"""
        ...

    @abstractmethod
    async def get_station_alarms(self, station_code: str) -> list[AlarmRecord]:
        """获取电站告警信息"""
        ...

    async def sync_station_data(self, station_code: str, query_date: date | None = None) -> dict[str, Any]:
        """
        同步电站数据（模板方法）。
        返回包含 realtime, daily, alarms 的字典。
        """
        target_date = query_date or date.today()
        result = {"realtime": None, "daily": None, "alarms": []}

        try:
            await self.authenticate()
            result["realtime"] = await self.get_station_realtime(station_code)
            result["daily"] = await self.get_station_daily(station_code, target_date)
            result["alarms"] = await self.get_station_alarms(station_code)
        except Exception as e:
            result["error"] = str(e)

        return result
