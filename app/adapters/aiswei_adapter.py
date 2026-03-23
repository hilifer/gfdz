"""爱士惟 AiSWEI Cloud 适配器

认证: HMAC-SHA256签名 (AppKey + AppSecret)
限流: 全局100次/分钟 (OLDAPI)
签名规则:
  StringToSign = HTTPMethod + "\n" + Accept + "\n" + Content-MD5 + "\n"
                 + Content-Type + "\n" + Date + "\n" + Headers + "\n" + Url
  Signature = Base64(HmacSHA256(Secret, StringToSign))
  放入Header: X-Ca-Signature
"""
import hashlib
import hmac
import base64
import logging
import time
import uuid
from datetime import date, datetime
from urllib.parse import urlencode

import httpx

from app.adapters.base import BaseAdapter, StationInfo, GenerationRecord, AlarmRecord
from app.adapters.registry import AdapterRegistry
from app.adapters.rate_limiter import RateLimitManager

logger = logging.getLogger(__name__)


@AdapterRegistry.register("aiswei")
class AisweiAdapter(BaseAdapter):
    """爱士惟AiSWEI Cloud适配器"""

    def __init__(self, api_base_url: str, auth_config: dict | None = None, extra_params: dict | None = None):
        super().__init__(api_base_url, auth_config, extra_params)
        self._app_key = self.auth_config.get("app_key", "")
        self._app_secret = self.auth_config.get("app_secret", "")
        self._token = self.auth_config.get("token", "")
        self._limiter = RateLimitManager.init_aiswei()

    def _get_default_headers(self) -> dict:
        return {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json",
        }

    def _sign_request(self, method: str, path: str, params: dict | None = None,
                      content_type: str = "", content_md5: str = "") -> dict:
        """
        生成签名请求头。

        签名字符串格式:
        HTTPMethod\nAccept\nContent-MD5\nContent-Type\nDate\nHeaders\nUrl
        """
        accept = "application/json"
        date_str = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())

        # 自定义Header（参与签名的X-Ca头）
        ca_headers = {
            "X-Ca-Key": self._app_key,
            "X-Ca-Timestamp": timestamp,
            "X-Ca-Nonce": nonce,
            "X-Ca-Stage": "RELEASE",
        }

        # 组织Headers签名字符串（按Key字典排序）
        sorted_header_keys = sorted(ca_headers.keys())
        headers_str = ""
        for key in sorted_header_keys:
            headers_str += f"{key}:{ca_headers[key]}\n"

        # 组织签名Header列表
        signature_headers = ",".join(sorted_header_keys)

        # 组织URL（Path + 排序后的Query参数）
        url_str = path
        if params:
            sorted_params = sorted(params.items())
            query_string = "&".join(
                f"{k}={v}" if v != "" else k
                for k, v in sorted_params
            )
            url_str = f"{path}?{query_string}"

        # 构造StringToSign
        string_to_sign = (
            f"{method}\n"
            f"{accept}\n"
            f"{content_md5}\n"
            f"{content_type}\n"
            f"{date_str}\n"
            f"{headers_str}"
            f"{url_str}"
        )

        # HmacSHA256 计算签名
        signature = base64.b64encode(
            hmac.new(
                self._app_secret.encode("utf-8"),
                string_to_sign.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        # 合并所有请求头
        result_headers = {
            "Accept": accept,
            "Date": date_str,
            "X-Ca-Key": self._app_key,
            "X-Ca-Timestamp": timestamp,
            "X-Ca-Nonce": nonce,
            "X-Ca-Stage": "RELEASE",
            "X-Ca-Signature-Headers": signature_headers,
            "X-Ca-Signature": signature,
        }
        if content_type:
            result_headers["Content-Type"] = content_type

        return result_headers

    async def _request(self, endpoint: str, params: dict | None = None) -> dict:
        """带限流的GET请求"""
        await self._limiter.acquire()

        path = f"/pro/{endpoint}"
        all_params = dict(params or {})
        if self._token:
            all_params["token"] = self._token

        headers = self._sign_request("GET", path, all_params)
        client = await self.get_client()

        resp = await client.get(path, params=all_params, headers=headers)
        resp.raise_for_status()
        result = resp.json()

        if result.get("status") != 200:
            raise Exception(f"爱士惟API错误: {result.get('status')} - {result.get('info', '')}")

        return result

    async def authenticate(self) -> bool:
        """爱士惟使用签名认证，不需要登录，验证凭据有效性"""
        try:
            result = await self._request("getPlanListPro", {
                "order": "0",
                "pageNum": "1",
                "pageSize": "1",
            })
            logger.info("爱士惟AiSWEI认证验证成功")
            return True
        except Exception as e:
            logger.error(f"爱士惟认证验证失败: {e}")
            return False

    async def get_station_list(self) -> list[StationInfo]:
        """获取电站列表（分页获取全部）"""
        stations = []
        page = 1
        page_size = 50

        while True:
            result = await self._request("getPlanListPro", {
                "order": "0",
                "pageNum": str(page),
                "pageSize": str(page_size),
            })

            data = result.get("data", {})
            for item in data.get("result", []):
                stations.append(StationInfo(
                    station_code=item.get("apikey", ""),
                    name=item.get("name", ""),
                    capacity=item.get("totalpower"),
                    status=self._map_status(item.get("status")),
                    extra={
                        "etoday": item.get("etoday"),
                        "etotal": item.get("etotal"),
                        "position": item.get("position", ""),
                        "latitude": item.get("wd"),
                        "longitude": item.get("jd"),
                    },
                ))

            total_pages = data.get("totalPages", 1)
            if page >= total_pages:
                break
            page += 1

        return stations

    async def get_station_realtime(self, station_code: str) -> GenerationRecord | None:
        """获取电站实时概览数据"""
        result = await self._request("getPlantOverviewPro", {
            "apikey": station_code,
        })
        data = result.get("data", {})
        if not data:
            return None

        def _get_value(key: str) -> float | None:
            obj = data.get(key, {})
            if isinstance(obj, dict):
                val = obj.get("value")
                return float(val) if val is not None else None
            return None

        power_w = _get_value("Power")
        return GenerationRecord(
            record_date=date.today(),
            current_power=power_w / 1000 if power_w else None,  # W -> kW
            daily_generation=_get_value("E-Today"),
            monthly_generation=_get_value("E-Month"),
            yearly_generation=_get_value("E-Year"),
            total_generation=_get_value("E-Total"),
            raw_data=data,
        )

    async def get_station_daily(self, station_code: str, query_date: date) -> GenerationRecord | None:
        """获取电站日发电数据"""
        result = await self._request("getPlantOutputPro", {
            "apikey": station_code,
            "period": "bydays",
            "date": query_date.strftime("%Y-%m-%d"),
        })
        data = result.get("data", {})
        results = data.get("result", [])

        # 找到对应日期的数据
        daily_gen = None
        for item in results:
            if item.get("time", "").startswith(query_date.strftime("%Y-%m-%d")):
                try:
                    daily_gen = float(item.get("value", 0))
                except (ValueError, TypeError):
                    pass
                break

        if daily_gen is None and results:
            # 如果只有一条记录，直接使用
            try:
                daily_gen = float(results[-1].get("value", 0))
            except (ValueError, TypeError):
                pass

        if daily_gen is None:
            return None

        return GenerationRecord(
            record_date=query_date,
            daily_generation=daily_gen,
            raw_data=data,
        )

    async def get_station_alarms(self, station_code: str) -> list[AlarmRecord]:
        """获取电站告警/事件"""
        try:
            result = await self._request("getPlantEventPro", {
                "apikey": station_code,
                "pageNum": "1",
                "pageSize": "50",
            })
        except Exception as e:
            logger.warning(f"爱士惟告警接口调用失败: {e}")
            return []

        alarms = []
        data = result.get("data", {})
        for item in data.get("result", []):
            alarm_time_str = item.get("time", "")
            try:
                alarm_time = datetime.strptime(alarm_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                alarm_time = datetime.now()

            alarms.append(AlarmRecord(
                alarm_name=item.get("event", "未知事件"),
                alarm_time=alarm_time,
                alarm_code=item.get("code", ""),
                alarm_level=self._map_event_level(item.get("level")),
                status="active" if item.get("status") == 0 else "recovered",
                description=item.get("description", ""),
                device_name=item.get("sn", ""),
            ))
        return alarms

    async def get_inverter_realtime(self, station_code: str) -> list[dict]:
        """获取电站下逆变器最新数据"""
        result = await self._request("getLastTsDataPro", {
            "apikey": station_code,
        })
        return result.get("data", [])

    def get_rate_limit_stats(self) -> dict:
        return self._limiter.get_stats()

    @staticmethod
    def _map_status(status) -> str:
        mapping = {0: "offline", 1: "normal", 2: "fault", 3: "fault", 4: "normal"}
        return mapping.get(status, "normal")

    @staticmethod
    def _map_event_level(level) -> str:
        mapping = {0: "info", 1: "warning", 2: "critical", 3: "critical"}
        return mapping.get(level, "info")
