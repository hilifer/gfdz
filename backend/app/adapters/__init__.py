"""厂家适配器工厂"""
import json
import logging

from app.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

# 适配器注册表
_ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {}


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

    # 尝试动态导入
    try:
        if manufacturer_code == "huawei":
            from app.adapters.huawei import HuaweiAdapter
            register_adapter("huawei", HuaweiAdapter)
            return HuaweiAdapter(api_base_url=api_base_url, auth_config=auth_config)
        elif manufacturer_code == "aiswei":
            from app.adapters.aiswei import AisweiAdapter
            register_adapter("aiswei", AisweiAdapter)
            return AisweiAdapter(api_base_url=api_base_url, auth_config=auth_config)
        elif manufacturer_code == "sungrow":
            from app.adapters.sungrow import SungrowAdapter
            register_adapter("sungrow", SungrowAdapter)
            return SungrowAdapter(api_base_url=api_base_url, auth_config=auth_config)
    except ImportError:
        logger.warning("适配器模块 %s 尚未实现，使用桩适配器", manufacturer_code)

    # 返回桩适配器（适配器模块尚未实现时使用）
    return _StubAdapter(api_base_url=api_base_url, auth_config=auth_config, code=manufacturer_code)


class _StubAdapter(BaseAdapter):
    """桩适配器 - 在具体厂家适配器未实现时使用，所有方法返回空结果"""

    def __init__(self, api_base_url: str, auth_config: dict, code: str = "unknown"):
        super().__init__(api_base_url, auth_config)
        self._code = code

    async def authenticate(self) -> bool:
        logger.info("桩适配器[%s] authenticate - 跳过", self._code)
        return True

    async def get_station_list(self):
        logger.info("桩适配器[%s] get_station_list - 返回空列表", self._code)
        return []

    async def get_station_realtime(self, station_code: str):
        logger.info("桩适配器[%s] get_station_realtime(%s) - 返回 None", self._code, station_code)
        return None

    async def get_station_daily(self, station_code: str, query_date):
        logger.info("桩适配器[%s] get_station_daily(%s) - 返回 None", self._code, station_code)
        return None

    async def get_device_list(self, station_code: str):
        return []

    async def get_alarms(self, station_code: str):
        return []
