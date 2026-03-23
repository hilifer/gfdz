"""适配器注册表 - 管理所有厂家适配器的注册和获取"""
from dataclasses import dataclass, field
from typing import Type
from app.adapters.base import BaseAdapter


@dataclass
class AdapterMeta:
    """适配器元数据 - 描述厂家的配置需求"""
    name: str  # 显示名称
    code: str  # 厂家编码
    urls: list[dict] = field(default_factory=list)  # [{"url": "https://...", "label": "描述"}]
    auth_fields: list[dict] = field(default_factory=list)  # [{"key": "username", "label": "用户名", "type": "text", "required": True}]
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "code": self.code,
            "urls": self.urls,
            "auth_fields": self.auth_fields,
            "description": self.description,
        }


# 各厂家适配器的配置元数据
ADAPTER_CONFIGS: dict[str, AdapterMeta] = {
    "huawei": AdapterMeta(
        name="华为 FusionSolar",
        code="huawei",
        urls=[
            {"url": "https://intl.fusionsolar.huawei.com", "label": "国际站 (intl)"},
            {"url": "https://eu5.fusionsolar.huawei.com", "label": "欧洲站 (eu5)"},
            {"url": "https://au5.fusionsolar.huawei.com", "label": "澳洲站 (au5)"},
            {"url": "https://la5.fusionsolar.huawei.com", "label": "拉美站 (la5)"},
            {"url": "https://me5.fusionsolar.huawei.com", "label": "中东站 (me5)"},
            {"url": "https://af5.fusionsolar.huawei.com", "label": "非洲站 (af5)"},
            {"url": "https://sg5.fusionsolar.huawei.com", "label": "亚太站 (sg5)"},
            {"url": "https://cn5.fusionsolar.huawei.com", "label": "中国站 (cn5)"},
        ],
        auth_fields=[
            {"key": "username", "label": "系统账号 (userName)", "type": "text", "required": True, "placeholder": "北向API系统账号"},
            {"key": "password", "label": "系统密码 (systemCode)", "type": "password", "required": True, "placeholder": "北向API系统密码"},
        ],
        description="华为FusionSolar北向接口，使用XSRF-TOKEN认证",
    ),
    "sungrow": AdapterMeta(
        name="阳光电源 iSolarCloud",
        code="sungrow",
        urls=[
            {"url": "https://gateway.isolarcloud.com", "label": "国际站 (gateway)"},
            {"url": "https://gateway.isolarcloud.com.hk", "label": "亚太站 (Hong Kong)"},
            {"url": "https://augateway.isolarcloud.com", "label": "澳洲站 (AU)"},
            {"url": "https://eugateway.isolarcloud.com", "label": "欧洲站 (EU)"},
        ],
        auth_fields=[
            {"key": "app_key", "label": "AppKey", "type": "text", "required": True, "placeholder": "开发者AppKey"},
            {"key": "username", "label": "用户账号", "type": "text", "required": True, "placeholder": "iSolarCloud账号"},
            {"key": "password", "label": "用户密码", "type": "password", "required": True, "placeholder": "iSolarCloud密码"},
        ],
        description="阳光电源iSolarCloud开放API，使用AppKey+Token认证",
    ),
    "aiswei": AdapterMeta(
        name="爱士惟 AiSWEI Cloud",
        code="aiswei",
        urls=[
            {"url": "https://dev.aiswei.com", "label": "开发者API (dev)"},
            {"url": "https://fop.solplanet.net", "label": "Solplanet (国际)"},
        ],
        auth_fields=[
            {"key": "app_key", "label": "AppKey (X-Ca-Key)", "type": "text", "required": True, "placeholder": "应用AppKey"},
            {"key": "app_secret", "label": "AppSecret", "type": "password", "required": True, "placeholder": "应用AppSecret"},
            {"key": "token", "label": "Token (可选)", "type": "text", "required": False, "placeholder": "如有预置Token填写"},
        ],
        description="爱士惟AiSWEI Cloud API，使用HMAC-SHA256签名认证",
    ),
    "demo": AdapterMeta(
        name="演示/测试",
        code="demo",
        urls=[
            {"url": "http://localhost", "label": "本地测试"},
        ],
        auth_fields=[],
        description="演示适配器，生成模拟数据，无需认证",
    ),
}


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
    def get_meta(cls, code: str) -> AdapterMeta | None:
        return ADAPTER_CONFIGS.get(code)

    @classmethod
    def get_all_meta(cls) -> dict[str, dict]:
        """返回所有已注册适配器的元数据"""
        result = {}
        for code in cls._adapters:
            meta = ADAPTER_CONFIGS.get(code)
            if meta:
                result[code] = meta.to_dict()
            else:
                result[code] = {"name": code, "code": code, "urls": [], "auth_fields": [], "description": ""}
        return result

    @classmethod
    def create_adapter(cls, code: str, api_base_url: str,
                       auth_config: dict | None = None,
                       extra_params: dict | None = None) -> BaseAdapter | None:
        """根据厂家编码创建适配器实例"""
        adapter_cls = cls.get(code)
        if adapter_cls is None:
            return None
        return adapter_cls(api_base_url, auth_config, extra_params)
