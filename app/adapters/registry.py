"""适配器注册表 - 管理所有厂家适配器的注册和获取

每个厂家适配器的元数据定义在 ADAPTER_CONFIGS 中，包括：
- 候选URL列表（系统自动探测，不需要用户填写）
- 认证字段（根据协议不同，只展示必要的参数）
- 探测方式（用于连接测试的只读接口信息）

安全原则：所有探测和数据采集只使用【只读/查询】接口，
         绝不调用任何操作/控制电站的接口。
"""
import logging
from dataclasses import dataclass, field
from typing import Type

import httpx

from app.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


@dataclass
class AuthField:
    """认证字段定义"""
    key: str          # JSON key
    label: str        # 显示名称
    type: str = "text"  # text / password
    required: bool = True
    placeholder: str = ""
    help_text: str = ""  # 补充说明
    default: str = ""    # 默认值

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "type": self.type,
            "required": self.required,
            "placeholder": self.placeholder,
            "help_text": self.help_text,
            "default": self.default,
        }


@dataclass
class AdapterMeta:
    """适配器元数据 - 描述厂家的配置需求"""
    name: str       # 显示名称
    code: str       # 厂家编码
    urls: list[dict] = field(default_factory=list)   # [{"url": "...", "label": "..."}]
    auth_fields: list[AuthField] = field(default_factory=list)
    description: str = ""
    # 探测相关（只读接口）
    probe_method: str = "POST"     # HTTP方法
    probe_path: str = "/"          # 探测路径
    probe_timeout: float = 10.0    # 超时秒数

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "code": self.code,
            "urls": self.urls,
            "auth_fields": [f.to_dict() for f in self.auth_fields],
            "description": self.description,
        }


# =====================================================================
#  各厂家适配器的配置元数据
#
#  URL列表：每个厂家的所有区域节点，系统自动逐个探测
#  认证字段：只展示该协议必需的参数，用户不需要关心URL
#  探测方式：只用最轻量的只读接口测试连通性
# =====================================================================

ADAPTER_CONFIGS: dict[str, AdapterMeta] = {
    # ---- 华为 FusionSolar 北向接口 ----
    # 认证方式: userName + systemCode → XSRF-TOKEN
    # 探测接口: POST /thirdData/login (只读，登录接口)
    # 各区域站点对应不同地理区域的FusionSolar部署
    "huawei": AdapterMeta(
        name="华为 FusionSolar",
        code="huawei",
        urls=[
            {"url": "https://intl.fusionsolar.huawei.com", "label": "国际站 (intl)", "region": "global"},
            {"url": "https://eu5.fusionsolar.huawei.com",  "label": "欧洲站 (eu5)", "region": "eu"},
            {"url": "https://au5.fusionsolar.huawei.com",  "label": "澳洲站 (au5)", "region": "au"},
            {"url": "https://la5.fusionsolar.huawei.com",  "label": "拉美站 (la5)", "region": "la"},
            {"url": "https://me5.fusionsolar.huawei.com",  "label": "中东站 (me5)", "region": "me"},
            {"url": "https://af5.fusionsolar.huawei.com",  "label": "非洲站 (af5)", "region": "af"},
            {"url": "https://sg5.fusionsolar.huawei.com",  "label": "亚太站 (sg5)", "region": "sg"},
            {"url": "https://cn5.fusionsolar.huawei.com",  "label": "中国站 (cn5)", "region": "cn"},
        ],
        auth_fields=[
            AuthField(
                key="username",
                label="系统账号",
                type="text",
                required=True,
                placeholder="北向API系统账号",
                help_text="FusionSolar北向接口的userName，在智能光伏云管理系统中创建",
                default="YRKJAPI",
            ),
            AuthField(
                key="password",
                label="系统密码",
                type="password",
                required=True,
                placeholder="北向API systemCode",
                help_text="FusionSolar北向接口的systemCode密码",
                default="huawei666",
            ),
        ],
        description="华为FusionSolar北向接口 — 使用XSRF-TOKEN认证，自动探测所属区域节点",
        probe_method="POST",
        probe_path="/thirdData/login",
        probe_timeout=10.0,
    ),

    # ---- 阳光电源 iSolarCloud ----
    # 认证方式: AppKey + 账号 + 密码(SHA256) → Token
    # 探测接口: POST /openapi/login (只读，登录接口)
    # 不同区域网关地址不同
    "sungrow": AdapterMeta(
        name="阳光电源 iSolarCloud",
        code="sungrow",
        urls=[
            {"url": "https://gateway.isolarcloud.com",     "label": "国际站", "region": "global"},
            {"url": "https://gateway.isolarcloud.com.hk",  "label": "亚太站 (HK)", "region": "hk"},
            {"url": "https://augateway.isolarcloud.com",   "label": "澳洲站 (AU)", "region": "au"},
            {"url": "https://eugateway.isolarcloud.com",   "label": "欧洲站 (EU)", "region": "eu"},
        ],
        auth_fields=[
            AuthField(
                key="app_key",
                label="AppKey",
                type="text",
                required=True,
                placeholder="开发者应用AppKey",
                help_text="在iSolarCloud开发者平台创建应用后获取",
                default="C37DA83CA621494DAF1859221169CDC9",
            ),
            AuthField(
                key="username",
                label="用户账号",
                type="text",
                required=True,
                placeholder="iSolarCloud登录账号",
                help_text="iSolarCloud平台的登录账号（邮箱或手机号）",
                default="yrkj_nibian",
            ),
            AuthField(
                key="password",
                label="用户密码",
                type="password",
                required=True,
                placeholder="iSolarCloud登录密码",
                help_text="明文密码，系统内部自动SHA256加密后传输",
                default="yr@123456",
            ),
        ],
        description="阳光电源iSolarCloud开放API — 使用AppKey+Token认证，密码自动SHA256加密",
        probe_method="POST",
        probe_path="/openapi/login",
        probe_timeout=10.0,
    ),

    # ---- 爱士惟 AiSWEI Cloud ----
    # 认证方式: AppKey + AppSecret → HMAC-SHA256签名（无需登录）
    # 探测接口: GET /pro/getPlanListPro (只读，电站列表)
    # 签名认证，每个请求都带签名，无需login
    "aiswei": AdapterMeta(
        name="爱士惟 AiSWEI Cloud",
        code="aiswei",
        urls=[
            {"url": "https://dev.aiswei.com",    "label": "开发者站 (dev)", "region": "cn"},
            {"url": "https://fop.solplanet.net",  "label": "Solplanet国际站", "region": "global"},
        ],
        auth_fields=[
            AuthField(
                key="app_key",
                label="AppKey",
                type="text",
                required=True,
                placeholder="X-Ca-Key 应用密钥",
                help_text="在AiSWEI Cloud开放平台创建应用后获取的AppKey",
                default="204929444",
            ),
            AuthField(
                key="app_secret",
                label="AppSecret",
                type="password",
                required=True,
                placeholder="HMAC签名密钥",
                help_text="与AppKey配对的AppSecret，用于HMAC-SHA256签名",
                default="S9eyOBeTqUn56eAn5XovdjbDVMef6lRE",
            ),
            AuthField(
                key="token",
                label="Token",
                type="text",
                required=False,
                placeholder="预置Token（可选）",
                help_text="部分接口需要Token参数，如无可留空",
                default="R3dBOTVXeUdGRDBTTmJvMjZyNDF0QT09",
            ),
        ],
        description="爱士惟AiSWEI Cloud API — 使用HMAC-SHA256签名认证，无需登录",
        probe_method="GET",
        probe_path="/pro/getPlanListPro",
        probe_timeout=10.0,
    ),

    # ---- 演示/测试 ----
    "demo": AdapterMeta(
        name="演示/测试",
        code="demo",
        urls=[
            {"url": "http://localhost", "label": "本地测试", "region": "local"},
        ],
        auth_fields=[],
        description="演示适配器，生成模拟数据，无需认证配置",
        probe_method="GET",
        probe_path="/",
        probe_timeout=3.0,
    ),
}


async def probe_url(url: str, method: str = "GET", path: str = "/",
                    timeout: float = 10.0, **kwargs) -> dict:
    """
    探测单个URL的连通性。

    只做最基础的网络层探测：能否建立TCP连接并收到HTTP响应。
    不验证业务逻辑（如认证是否正确），因为认证失败也说明URL可达。

    返回: {"reachable": bool, "status_code": int|None, "detail": str}
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            if method.upper() == "POST":
                resp = await client.post(f"{url.rstrip('/')}{path}", json=kwargs.get("body", {}))
            else:
                resp = await client.get(f"{url.rstrip('/')}{path}", params=kwargs.get("params"))
            return {
                "reachable": True,
                "status_code": resp.status_code,
                "detail": f"HTTP {resp.status_code}",
            }
    except httpx.ConnectTimeout:
        return {"reachable": False, "status_code": None, "detail": "连接超时"}
    except httpx.ConnectError as e:
        return {"reachable": False, "status_code": None, "detail": f"连接失败: {e}"}
    except Exception as e:
        return {"reachable": False, "status_code": None, "detail": str(e)}


async def auto_detect_url(code: str, auth_config: dict | None = None) -> dict:
    """
    自动探测厂家的可用URL。

    逐个尝试该厂家的所有候选URL，用对应的只读探测接口测试。
    对于需要认证的接口，认证失败(401/403等)也算URL可达，
    只有网络不通才认为不可用。

    安全说明：
    - 华为: 用login接口探测，即使密码错也只是返回错误码，不会产生副作用
    - 阳光: 用login接口探测，同上
    - 爱士惟: 用签名GET查询接口，只读无副作用
    - 所有探测都不会调用任何操作/控制类接口

    返回: {"success": bool, "url": str|None, "results": [...]}
    """
    meta = ADAPTER_CONFIGS.get(code)
    if not meta:
        return {"success": False, "url": None, "results": [],
                "error": f"未知的厂家编码: {code}"}

    auth_config = auth_config or {}
    results = []

    for url_item in meta.urls:
        url = url_item["url"]
        label = url_item["label"]

        # 根据厂家构造探测请求体
        probe_kwargs = _build_probe_request(code, url, auth_config, meta)

        result = await probe_url(
            url=url,
            method=meta.probe_method,
            path=meta.probe_path,
            timeout=meta.probe_timeout,
            **probe_kwargs,
        )
        result["url"] = url
        result["label"] = label

        # 进一步检查：如果能拿到业务响应，验证认证是否成功
        if result["reachable"] and auth_config:
            auth_result = await _try_authenticate(code, url, auth_config, meta)
            result["auth_ok"] = auth_result["success"]
            result["auth_detail"] = auth_result["detail"]
        else:
            result["auth_ok"] = None
            result["auth_detail"] = ""

        results.append(result)
        logger.info(f"探测 {code} URL [{label}] {url}: "
                     f"reachable={result['reachable']}, auth_ok={result.get('auth_ok')}")

    # 优先选认证成功的，其次选可达的
    auth_ok_urls = [r for r in results if r.get("auth_ok") is True]
    if auth_ok_urls:
        return {"success": True, "url": auth_ok_urls[0]["url"],
                "label": auth_ok_urls[0]["label"], "results": results}

    reachable_urls = [r for r in results if r["reachable"]]
    if reachable_urls:
        return {"success": True, "url": reachable_urls[0]["url"],
                "label": reachable_urls[0]["label"], "results": results,
                "warning": "URL可达但认证未通过，请检查认证参数"}

    return {"success": False, "url": None, "results": results,
            "error": "所有候选URL均不可达，请检查网络"}


def _build_probe_request(code: str, url: str, auth_config: dict,
                         meta: AdapterMeta) -> dict:
    """构造探测请求的参数（只用只读接口）"""
    if code == "huawei":
        return {"body": {
            "userName": auth_config.get("username", ""),
            "systemCode": auth_config.get("password", ""),
        }}
    elif code == "sungrow":
        import hashlib
        password = auth_config.get("password", "")
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest() if password else ""
        return {"body": {
            "appkey": auth_config.get("app_key", ""),
            "user_account": auth_config.get("username", ""),
            "user_password": password_hash,
        }}
    elif code == "aiswei":
        # 爱士惟签名较复杂，简单探测只检查连通性
        return {"params": {"order": "0", "pageNum": "1", "pageSize": "1"}}
    else:
        return {}


async def _try_authenticate(code: str, url: str, auth_config: dict,
                            meta: AdapterMeta) -> dict:
    """
    尝试用只读接口验证认证是否正确。

    安全保证：
    - 华为: POST /thirdData/login → 只返回token，无副作用
    - 阳光: POST /openapi/login → 只返回token，无副作用
    - 爱士惟: GET /pro/getPlanListPro → 只读查询
    - 绝不调用任何写入/控制/操作类接口
    """
    try:
        async with httpx.AsyncClient(timeout=meta.probe_timeout, verify=False) as client:
            if code == "huawei":
                resp = await client.post(f"{url}/thirdData/login", json={
                    "userName": auth_config.get("username", ""),
                    "systemCode": auth_config.get("password", ""),
                })
                body = resp.json()
                fail_code = body.get("failCode", -1)
                if fail_code == 0:
                    # 登录成功，立即登出释放会话（logout也是只读/清理接口）
                    token = resp.cookies.get("XSRF-TOKEN") or resp.headers.get("XSRF-TOKEN", "")
                    if token:
                        try:
                            await client.post(f"{url}/thirdData/logout",
                                              headers={"XSRF-TOKEN": token},
                                              cookies={"XSRF-TOKEN": token})
                        except Exception:
                            pass
                    return {"success": True, "detail": "认证成功"}
                else:
                    return {"success": False,
                            "detail": f"认证失败(code={fail_code}): {body.get('message', '')}"}

            elif code == "sungrow":
                import hashlib
                password = auth_config.get("password", "")
                password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest() if password else ""
                resp = await client.post(f"{url}/openapi/login", json={
                    "appkey": auth_config.get("app_key", ""),
                    "user_account": auth_config.get("username", ""),
                    "user_password": password_hash,
                })
                body = resp.json()
                if str(body.get("result_code")) == "1":
                    return {"success": True, "detail": "认证成功"}
                else:
                    return {"success": False,
                            "detail": f"认证失败: {body.get('result_msg', '')}"}

            elif code == "aiswei":
                # 签名认证较复杂，这里简化：如果能得到业务响应就算成功
                import hashlib, hmac, base64, time as _time, uuid
                app_key = auth_config.get("app_key", "")
                app_secret = auth_config.get("app_secret", "")
                if not app_key or not app_secret:
                    return {"success": False, "detail": "缺少AppKey或AppSecret"}

                from datetime import datetime
                path = "/pro/getPlanListPro"
                params = {"order": "0", "pageNum": "1", "pageSize": "1"}
                token = auth_config.get("token", "")
                if token:
                    params["token"] = token

                accept = "application/json"
                date_str = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
                timestamp = str(int(_time.time() * 1000))
                nonce = str(uuid.uuid4())
                ca_headers = {
                    "X-Ca-Key": app_key,
                    "X-Ca-Timestamp": timestamp,
                    "X-Ca-Nonce": nonce,
                    "X-Ca-Stage": "RELEASE",
                }
                sorted_keys = sorted(ca_headers.keys())
                headers_str = "".join(f"{k}:{ca_headers[k]}\n" for k in sorted_keys)
                signature_headers = ",".join(sorted_keys)
                sorted_params = sorted(params.items())
                query_string = "&".join(
                    f"{k}={v}" if v != "" else k for k, v in sorted_params
                )
                url_str = f"{path}?{query_string}"
                string_to_sign = f"GET\n{accept}\n\n\n{date_str}\n{headers_str}{url_str}"
                signature = base64.b64encode(
                    hmac.new(
                        app_secret.encode("utf-8"),
                        string_to_sign.encode("utf-8"),
                        hashlib.sha256,
                    ).digest()
                ).decode("utf-8")

                req_headers = {
                    "Accept": accept,
                    "Date": date_str,
                    **ca_headers,
                    "X-Ca-Signature-Headers": signature_headers,
                    "X-Ca-Signature": signature,
                }
                resp = await client.get(f"{url}{path}", params=params, headers=req_headers)
                body = resp.json()
                if body.get("status") == 200:
                    return {"success": True, "detail": "签名认证成功"}
                else:
                    return {"success": False,
                            "detail": f"认证失败: {body.get('info', '')}"}

            elif code == "demo":
                return {"success": True, "detail": "演示模式，无需认证"}

    except Exception as e:
        return {"success": False, "detail": f"认证测试异常: {e}"}

    return {"success": False, "detail": "未知厂家类型"}


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
                result[code] = {"name": code, "code": code, "urls": [],
                                "auth_fields": [], "description": ""}
        return result

    @classmethod
    def get_default_url(cls, code: str) -> str | None:
        """获取厂家的第一个默认URL"""
        meta = ADAPTER_CONFIGS.get(code)
        if meta and meta.urls:
            return meta.urls[0]["url"]
        return None

    @classmethod
    def create_adapter(cls, code: str, api_base_url: str,
                       auth_config: dict | None = None,
                       extra_params: dict | None = None) -> BaseAdapter | None:
        """根据厂家编码创建适配器实例"""
        adapter_cls = cls.get(code)
        if adapter_cls is None:
            return None
        return adapter_cls(api_base_url, auth_config, extra_params)
