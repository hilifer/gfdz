"""厂家适配器工厂"""
import json
import logging

from app.adapters.base import (
    BaseAdapter,
    StationInfo,
    StationRealtimeData,
    StationDailyData,
    DeviceInfo,
    DeviceRealtimeData,
    AlarmInfo,
)
from app.adapters.huawei import HuaweiAdapter
from app.adapters.aiswei import AisweiAdapter
from app.adapters.sungrow import SungrowAdapter
from app.adapters.solis import SolisAdapter

logger = logging.getLogger(__name__)

__all__ = [
    "BaseAdapter",
    "StationInfo",
    "StationRealtimeData",
    "StationDailyData",
    "DeviceInfo",
    "DeviceRealtimeData",
    "AlarmInfo",
    "HuaweiAdapter",
    "AisweiAdapter",
    "SungrowAdapter",
    "SolisAdapter",
    "get_adapter",
    "register_adapter",
]

# 适配器注册表
_ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {
    "huawei": HuaweiAdapter,
    "aiswei": AisweiAdapter,
    "sungrow": SungrowAdapter,
    "solis": SolisAdapter,
}


def register_adapter(code: str, cls: type[BaseAdapter]):
    """注册一个厂家适配器"""
    _ADAPTER_REGISTRY[code] = cls


def get_adapter(manufacturer_code: str, api_base_url: str, auth_config: dict | str) -> BaseAdapter:
    """
    根据厂家编码创建对应的适配器实例。

    Args:
        manufacturer_code: 厂家编码 (huawei/aiswei/sungrow)
        api_base_url: API 基础地址
        auth_config: 认证配置 (dict 或 JSON 字符串)

    Returns:
        BaseAdapter 实例

    Raises:
        ValueError: 未知的厂家编码
    """
    if isinstance(auth_config, str):
        auth_config = json.loads(auth_config)

    cls = _ADAPTER_REGISTRY.get(manufacturer_code)
    if cls is not None:
        return cls(api_base_url=api_base_url, auth_config=auth_config)

    raise ValueError(
        f"未知的厂家编码: {manufacturer_code!r}。"
        f"支持的编码: {', '.join(sorted(_ADAPTER_REGISTRY.keys()))}"
    )
