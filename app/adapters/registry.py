"""适配器注册表 - 管理所有厂家适配器的注册和获取"""
from typing import Type
from app.adapters.base import BaseAdapter


class AdapterRegistry:
    """适配器注册表"""
    _adapters: dict[str, Type[BaseAdapter]] = {}

    @classmethod
    def register(cls, code: str):
        """
        注册适配器的装饰器。

        用法:
            @AdapterRegistry.register("huawei")
            class HuaweiAdapter(BaseAdapter):
                ...
        """
        def decorator(adapter_cls: Type[BaseAdapter]):
            cls._adapters[code] = adapter_cls
            return adapter_cls
        return decorator

    @classmethod
    def get(cls, code: str) -> Type[BaseAdapter] | None:
        return cls._adapters.get(code)

    @classmethod
    def get_all(cls) -> dict[str, Type[BaseAdapter]]:
        return cls._adapters.copy()

    @classmethod
    def create_adapter(cls, code: str, api_base_url: str,
                       auth_config: dict | None = None,
                       extra_params: dict | None = None) -> BaseAdapter | None:
        """根据厂家编码创建适配器实例"""
        adapter_cls = cls.get(code)
        if adapter_cls is None:
            return None
        return adapter_cls(api_base_url, auth_config, extra_params)
