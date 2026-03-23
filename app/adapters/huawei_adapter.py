"""华为 FusionSolar 北向接口适配器

认证: XSRF-TOKEN，有效期30分钟，提前刷新
限流规则: 每个接口独立限流，基于电站/设备数量动态计算
详见 SmartPVMS_V600R024C10_北向接口参考-V6.pdf

主要接口限制（以7个电站、54逆变器、2电表、48 Dongle为例）：
- 登录: 每10分钟5次
- 电站列表: 每天34次
- 电站实时: 每5分钟1次（并发1分钟1次）
- 电站日/月/年: 每天25次（并发1分钟1次）
- 设备实时: 每5分钟3次
- 告警: 每30分钟3次
"""
import logging
import time
from datetime import date, datetime

import httpx

from app.adapters.base import BaseAdapter, StationInfo, GenerationRecord, AlarmRecord
from app.adapters.registry import AdapterRegistry
from app.adapters.rate_limiter import RateLimitManager, RateLimitExceeded

logger = logging.getLogger(__name__)


@AdapterRegistry.register("huawei")
class HuaweiAdapter(BaseAdapter):
    """华为FusionSolar北向接口适配器"""

    TOKEN_REFRESH_SECONDS = 25 * 60  # 提前5分钟刷新（Token有效期30分钟）

    def __init__(self, api_base_url: str, auth_config: dict | None = None, extra_params: dict | None = None):
        super().__init__(api_base_url, auth_config, extra_params)
        self._xsrf_token: str | None = None
        self._token_time: float = 0

        # 从extra_params获取电站/设备数量来初始化限流
        station_count = (extra_params or {}).get("station_count", 7)
        device_counts = (extra_params or {}).get("device_counts", {1: 54, 47: 2, 62: 48})
        self._limiter = RateLimitManager.init_huawei(station_count, device_counts)

    def _get_default_headers(self) -> dict:
        return {"Content-Type": "application/json"}

    def _is_token_valid(self) -> bool:
        if not self._xsrf_token:
            return False
        return (time.monotonic() - self._token_time) < self.TOKEN_REFRESH_SECONDS

    async def _request(self, endpoint: str, data: dict | None = None) -> dict:
        """
        带智能限流的请求方法。
        - 自动检查Token有效性并刷新
        - 按接口级限流等待
        - 遇到407自动等待后重试
        """
        if not self._is_token_valid() and endpoint != "login":
            await self.authenticate()

        # 接口级限流
        try:
            wait = await self._limiter.acquire(endpoint)
            if wait > 0:
                logger.info(f"华为接口[{endpoint}]限流等待 {wait:.1f}s")
        except RateLimitExceeded as e:
            logger.warning(f"华为接口[{endpoint}]限流已满: {e}")
            raise

        client = await self.get_client()
        headers = {}
        cookies = {}
        if self._xsrf_token:
            headers["XSRF-TOKEN"] = self._xsrf_token
            cookies["XSRF-TOKEN"] = self._xsrf_token

        resp = await client.post(
            f"/thirdData/{endpoint}",
            json=data or {},
            headers=headers,
            cookies=cookies,
        )
        resp.raise_for_status()
        result = resp.json()

        fail_code = result.get("failCode", 0)

        # Token过期(305)，重新认证后重试
        if fail_code == 305:
            logger.info("华为Token已过期，重新认证")
            await self.authenticate()
            await self._limiter.acquire(endpoint)
            headers["XSRF-TOKEN"] = self._xsrf_token
            cookies["XSRF-TOKEN"] = self._xsrf_token
            resp = await client.post(
                f"/thirdData/{endpoint}",
                json=data or {},
                headers=headers,
                cookies=cookies,
            )
            resp.raise_for_status()
            result = resp.json()
            fail_code = result.get("failCode", 0)

        # 限流错误(407)，记录并抛出
        if fail_code == 407:
            msg = f"华为接口[{endpoint}]服务端限流(407): {result.get('message', '')}"
            logger.warning(msg)
            raise RateLimitExceeded(msg)

        # 系统级限流(403/429)
        if fail_code in (403, 429):
            msg = f"华为系统级限流({fail_code}): 请间隔1分钟后重试"
            logger.warning(msg)
            raise RateLimitExceeded(msg)

        if fail_code != 0 and not result.get("success", True):
            raise Exception(f"华为API错误: {fail_code} - {result.get('message', '')}")

        return result

    async def authenticate(self) -> bool:
        """登录获取XSRF-TOKEN"""
        try:
            await self._limiter.acquire("login")
        except RateLimitExceeded:
            logger.error("华为登录接口限流(10分钟内已登录5次)，等待限流窗口重置")
            raise

        client = await self.get_client()
        resp = await client.post("/thirdData/login", json={
            "userName": self.auth_config.get("username", ""),
            "systemCode": self.auth_config.get("password", ""),
        })
        resp.raise_for_status()

        token = resp.cookies.get("XSRF-TOKEN") or resp.headers.get("XSRF-TOKEN", "")
        if not token:
            # 也尝试从response body获取
            body = resp.json()
            if body.get("failCode", 0) != 0:
                raise Exception(f"华为登录失败: {body.get('failCode')} - {body.get('message', '')}")
            raise Exception("华为登录失败: 未获取到XSRF-TOKEN")

        self._xsrf_token = token
        self._token_time = time.monotonic()
        logger.info("华为FusionSolar认证成功")
        return True

    async def get_station_list(self) -> list[StationInfo]:
        result = await self._request("getStationList", {})
        stations = []
        for item in result.get("data", []):
            stations.append(StationInfo(
                station_code=item.get("stationCode", ""),
                name=item.get("stationName", ""),
                capacity=item.get("capacity"),
                status=self._map_status(item.get("stationStatus")),
                extra=item,
            ))
        return stations

    async def get_station_realtime(self, station_code: str) -> GenerationRecord | None:
        result = await self._request("getStationRealKpi", {
            "stationCodes": station_code,
        })
        data_list = result.get("data", [])
        if not data_list:
            return None

        item = data_list[0]
        kpi = item.get("dataItemMap", {})
        return GenerationRecord(
            record_date=date.today(),
            current_power=kpi.get("real_health_state"),
            daily_generation=kpi.get("day_power"),
            monthly_generation=kpi.get("month_power"),
            total_generation=kpi.get("total_power"),
            raw_data=item,
        )

    async def get_station_daily(self, station_code: str, query_date: date) -> GenerationRecord | None:
        collect_time = int(datetime.combine(query_date, datetime.min.time()).timestamp() * 1000)
        result = await self._request("getKpiStationDay", {
            "stationCodes": station_code,
            "collectTime": collect_time,
        })
        data_list = result.get("data", [])
        if not data_list:
            return None

        item = data_list[0]
        kpi = item.get("dataItemMap", {})
        installed_cap = kpi.get("installed_capacity")
        inverter_power = kpi.get("inverter_power", 0)
        return GenerationRecord(
            record_date=query_date,
            daily_generation=inverter_power,
            daily_income=kpi.get("revenue"),
            equivalent_hours=(
                inverter_power / installed_cap if installed_cap else None
            ),
            raw_data=item,
        )

    async def get_station_alarms(self, station_code: str) -> list[AlarmRecord]:
        try:
            now = datetime.now()
            result = await self._request("getAlarmList", {
                "stationCodes": station_code,
                "beginTime": int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000),
                "endTime": int(now.timestamp() * 1000),
                "language": "zh_CN",
            })
        except (RateLimitExceeded, Exception) as e:
            logger.warning(f"华为告警接口调用失败: {e}")
            return []

        alarms = []
        for item in result.get("data", {}).get("list", []):
            alarms.append(AlarmRecord(
                alarm_name=item.get("alarmName", "未知告警"),
                alarm_time=datetime.fromtimestamp(item.get("raiseTime", 0) / 1000),
                alarm_code=str(item.get("alarmId", "")),
                alarm_level=self._map_alarm_level(item.get("severity")),
                status="active" if item.get("status") == 1 else "recovered",
                recover_time=(
                    datetime.fromtimestamp(item["clearTime"] / 1000)
                    if item.get("clearTime") else None
                ),
                description=item.get("alarmCause", ""),
                device_name=item.get("devName", ""),
            ))
        return alarms

    async def logout(self):
        try:
            if self._xsrf_token:
                await self._limiter.acquire("logout")
                client = await self.get_client()
                await client.post(
                    "/thirdData/logout",
                    headers={"XSRF-TOKEN": self._xsrf_token},
                    cookies={"XSRF-TOKEN": self._xsrf_token},
                )
        except Exception:
            pass
        finally:
            self._xsrf_token = None

    async def close(self):
        await self.logout()
        await super().close()

    def get_rate_limit_stats(self) -> dict:
        """获取限流统计信息"""
        return self._limiter.get_stats()

    @staticmethod
    def _map_status(status_code) -> str:
        return {1: "normal", 2: "fault", 3: "offline"}.get(status_code, "normal")

    @staticmethod
    def _map_alarm_level(severity) -> str:
        return {1: "critical", 2: "critical", 3: "warning", 4: "info"}.get(severity, "info")
