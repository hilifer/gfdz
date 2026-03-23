"""阳光电源 iSolarCloud 适配器

认证: AppKey + UserSecret + Token (登录获取)
API文档: https://developer-api.isolarcloud.com/#/home
限流: 待官方确认，保守设置30次/分钟
"""
import hashlib
import logging
import time
from datetime import date, datetime

import httpx

from app.adapters.base import BaseAdapter, StationInfo, GenerationRecord, AlarmRecord
from app.adapters.registry import AdapterRegistry
from app.adapters.rate_limiter import RateLimitManager

logger = logging.getLogger(__name__)


@AdapterRegistry.register("sungrow")
class SungrowAdapter(BaseAdapter):
    """阳光电源iSolarCloud适配器"""

    TOKEN_REFRESH_SECONDS = 55 * 60  # Token有效期约1小时，提前5分钟刷新

    def __init__(self, api_base_url: str, auth_config: dict | None = None, extra_params: dict | None = None):
        super().__init__(api_base_url, auth_config, extra_params)
        self._app_key = self.auth_config.get("app_key", "")
        self._user_account = self.auth_config.get("username", "")
        self._user_password = self.auth_config.get("password", "")
        self._access_token: str | None = None
        self._token_time: float = 0
        self._limiter = RateLimitManager.init_sungrow()

    def _get_default_headers(self) -> dict:
        return {"Content-Type": "application/json"}

    def _is_token_valid(self) -> bool:
        if not self._access_token:
            return False
        return (time.monotonic() - self._token_time) < self.TOKEN_REFRESH_SECONDS

    async def _request(self, api_name: str, params: dict | None = None) -> dict:
        """
        统一请求方法。
        iSolarCloud API格式: POST /openapi/{api_name}
        body: {"appkey": ..., "token": ..., ...params}
        """
        if not self._is_token_valid() and api_name != "login":
            await self.authenticate()

        await self._limiter.acquire()

        body = {
            "appkey": self._app_key,
            **({"token": self._access_token} if self._access_token else {}),
            **(params or {}),
        }

        client = await self.get_client()
        resp = await client.post(f"/openapi/{api_name}", json=body)
        resp.raise_for_status()
        result = resp.json()

        result_code = result.get("result_code")
        if result_code and str(result_code) != "1":
            # Token过期重试
            if str(result_code) in ("301", "401", "10001"):
                logger.info("阳光电源Token已过期，重新认证")
                await self.authenticate()
                body["token"] = self._access_token
                await self._limiter.acquire()
                resp = await client.post(f"/openapi/{api_name}", json=body)
                resp.raise_for_status()
                result = resp.json()
                if str(result.get("result_code")) != "1":
                    raise Exception(
                        f"阳光API错误: {result.get('result_code')} - {result.get('result_msg', '')}"
                    )
            else:
                raise Exception(
                    f"阳光API错误: {result_code} - {result.get('result_msg', '')}"
                )

        return result

    async def authenticate(self) -> bool:
        """登录获取Token"""
        await self._limiter.acquire()

        # 密码需要SHA256加密
        password_hash = hashlib.sha256(
            self._user_password.encode("utf-8")
        ).hexdigest()

        client = await self.get_client()
        resp = await client.post("/openapi/login", json={
            "appkey": self._app_key,
            "user_account": self._user_account,
            "user_password": password_hash,
        })
        resp.raise_for_status()
        result = resp.json()

        if str(result.get("result_code")) != "1":
            raise Exception(f"阳光电源登录失败: {result.get('result_msg', '')}")

        data = result.get("result_data", {})
        self._access_token = data.get("token", "")
        if not self._access_token:
            raise Exception("阳光电源登录失败: 未获取到Token")

        self._token_time = time.monotonic()
        logger.info("阳光电源iSolarCloud认证成功")
        return True

    async def get_station_list(self) -> list[StationInfo]:
        result = await self._request("getPowerStationList", {
            "curPage": 1,
            "size": 100,
        })
        stations = []
        data = result.get("result_data", {})
        for item in data.get("pageList", []):
            stations.append(StationInfo(
                station_code=str(item.get("ps_id", "")),
                name=item.get("ps_name", ""),
                capacity=item.get("installed_power_map", {}).get("value"),
                status=self._map_status(item.get("connect_state")),
                extra=item,
            ))
        return stations

    async def get_station_realtime(self, station_code: str) -> GenerationRecord | None:
        result = await self._request("getPowerStationDetail", {
            "ps_id": station_code,
        })
        data = result.get("result_data", {})
        if not data:
            return None

        def _safe_float(val) -> float | None:
            if val is None:
                return None
            try:
                if isinstance(val, dict):
                    val = val.get("value")
                return float(val) if val is not None else None
            except (ValueError, TypeError):
                return None

        return GenerationRecord(
            record_date=date.today(),
            current_power=_safe_float(data.get("curr_power")),
            daily_generation=_safe_float(data.get("today_energy")),
            monthly_generation=_safe_float(data.get("month_energy")),
            yearly_generation=_safe_float(data.get("year_energy")),
            total_generation=_safe_float(data.get("total_energy")),
            raw_data=data,
        )

    async def get_station_daily(self, station_code: str, query_date: date) -> GenerationRecord | None:
        result = await self._request("queryPsProfit", {
            "ps_id": station_code,
            "date_type": "1",  # 1=日
            "start_date": query_date.strftime("%Y%m%d"),
            "end_date": query_date.strftime("%Y%m%d"),
        })
        data = result.get("result_data", {})
        data_list = data.get("list", [])
        if not data_list:
            return None

        item = data_list[0]
        return GenerationRecord(
            record_date=query_date,
            daily_generation=self._safe_float(item.get("energy")),
            daily_income=self._safe_float(item.get("income")),
            raw_data=item,
        )

    async def get_station_alarms(self, station_code: str) -> list[AlarmRecord]:
        try:
            result = await self._request("getFaultList", {
                "ps_id": station_code,
                "curPage": 1,
                "size": 50,
            })
        except Exception as e:
            logger.warning(f"阳光电源告警接口调用失败: {e}")
            return []

        alarms = []
        data = result.get("result_data", {})
        for item in data.get("pageList", []):
            alarm_time_str = item.get("fault_time", "")
            try:
                alarm_time = datetime.strptime(alarm_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                alarm_time = datetime.now()

            recover_time = None
            if item.get("recover_time"):
                try:
                    recover_time = datetime.strptime(item["recover_time"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass

            alarms.append(AlarmRecord(
                alarm_name=item.get("fault_name", "未知告警"),
                alarm_time=alarm_time,
                alarm_code=str(item.get("fault_code", "")),
                alarm_level=self._map_alarm_level(item.get("fault_level")),
                status="recovered" if item.get("process_status") == 2 else "active",
                recover_time=recover_time,
                description=item.get("fault_description", ""),
                device_name=item.get("device_name", ""),
            ))
        return alarms

    def get_rate_limit_stats(self) -> dict:
        return self._limiter.get_stats()

    @staticmethod
    def _safe_float(val) -> float | None:
        if val is None:
            return None
        try:
            if isinstance(val, dict):
                val = val.get("value")
            return float(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _map_status(state) -> str:
        mapping = {1: "normal", 0: "offline", 2: "fault"}
        return mapping.get(state, "normal")

    @staticmethod
    def _map_alarm_level(level) -> str:
        mapping = {1: "info", 2: "warning", 3: "critical"}
        return mapping.get(level, "info")
