"""华为 FusionSolar 适配器"""
import logging
import time
from datetime import date, datetime, timezone

import httpx

from .base import (
    AlarmInfo,
    BaseAdapter,
    DeviceInfo,
    DeviceRealtimeData,
    StationDailyData,
    StationInfo,
    StationRealtimeData,
)

logger = logging.getLogger(__name__)

# Huawei devTypeId → our device_type string
_DEV_TYPE_MAP: dict[int, str] = {
    1: "inverter",
    2: "inverter",          # string inverter
    10: "storage",          # ESS
    17: "combiner_box",
    38: "weather_station",
    47: "meter",
    62: "dongle",
}


class HuaweiAdapter(BaseAdapter):
    """Huawei FusionSolar iMaster NORTHBOUND API adapter.

    Default API base: https://intl.fusionsolar.huawei.com
    auth_config keys: userName, systemCode
    """

    MANUFACTURER = "huawei"
    TOKEN_LIFETIME_S = 30 * 60  # 30 minutes

    def __init__(self, api_base_url: str, auth_config: dict):
        super().__init__(api_base_url, auth_config)
        self._xsrf_token: str | None = None
        self._token_acquired_at: float = 0.0
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.api_base_url,
                verify=False,  # intl server requires this
                timeout=httpx.Timeout(30.0, connect=10.0),
                headers={"Content-Type": "application/json"},
            )
        return self._client

    def _token_expired(self) -> bool:
        if self._xsrf_token is None:
            return True
        return (time.monotonic() - self._token_acquired_at) >= self.TOKEN_LIFETIME_S - 60

    async def _ensure_auth(self) -> None:
        """Re-authenticate when token is missing or about to expire."""
        if self._token_expired():
            await self.authenticate()

    async def _post(self, path: str, payload: dict | None = None) -> dict:
        """POST with automatic auth refresh and basic error handling."""
        await self._ensure_auth()
        client = self._get_client()
        headers = {}
        if self._xsrf_token:
            headers["XSRF-TOKEN"] = self._xsrf_token
        resp = await client.post(path, json=payload or {}, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        if not body.get("success", True) and body.get("failCode", 0) != 0:
            code = body.get("failCode")
            msg = body.get("message", "")
            # 305 = token expired
            if code == 305:
                logger.warning("Huawei token expired, re-authenticating")
                await self.authenticate()
                headers["XSRF-TOKEN"] = self._xsrf_token or ""
                resp = await client.post(path, json=payload or {}, headers=headers)
                resp.raise_for_status()
                body = resp.json()
            else:
                raise RuntimeError(f"Huawei API error {code}: {msg}")
        return body

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        client = self._get_client()
        payload = {
            "userName": self.auth_config["userName"],
            "systemCode": self.auth_config["systemCode"],
        }
        resp = await client.post("/thirdData/login", json=payload)
        resp.raise_for_status()
        body = resp.json()
        if not body.get("success", False) and body.get("failCode", 0) != 0:
            logger.error("Huawei login failed: %s", body.get("message"))
            return False

        # Token comes back as a Set-Cookie or response header
        token = resp.headers.get("xsrf-token") or resp.cookies.get("XSRF-TOKEN")
        if not token:
            logger.error("Huawei login succeeded but no XSRF-TOKEN in response")
            return False

        self._xsrf_token = token
        self._token_acquired_at = time.monotonic()
        logger.info("Huawei authenticated successfully")
        return True

    async def get_station_list(self) -> list[StationInfo]:
        stations: list[StationInfo] = []
        page = 1
        while True:
            body = await self._post("/thirdData/stations", {"pageNo": page})
            data = body.get("data") or {}
            items = data.get("list") or []
            for item in items:
                stations.append(
                    StationInfo(
                        station_code=str(item["plantCode"]),
                        name=item.get("plantName", ""),
                        capacity_kwp=_safe_float(item.get("capacity")),
                        longitude=_safe_float(item.get("longitude")),
                        latitude=_safe_float(item.get("latitude")),
                        address=item.get("plantAddress"),
                        extra=item,
                    )
                )
            total = data.get("total", 0) or data.get("pageCount", 0)
            if len(stations) >= total or not items:
                break
            page += 1
        return stations

    async def get_station_realtime(self, station_code: str) -> StationRealtimeData | None:
        body = await self._post(
            "/thirdData/getStationRealKpi",
            {"stationCodes": station_code},
        )
        data_list = body.get("data") or []
        if not data_list:
            return None
        kpi = data_list[0].get("dataItemMap", {})
        return StationRealtimeData(
            current_power_kw=_safe_float(kpi.get("real_health_state")),  # not available directly
            today_generation=_safe_float(kpi.get("day_power")),
            month_generation=_safe_float(kpi.get("month_power")),
            total_generation=_safe_float(kpi.get("total_power")),
        )

    async def get_station_daily(self, station_code: str, query_date: date) -> StationDailyData | None:
        ts_ms = int(
            datetime(query_date.year, query_date.month, query_date.day, tzinfo=timezone.utc).timestamp() * 1000
        )
        body = await self._post(
            "/thirdData/getKpiStationDay",
            {"stationCodes": station_code, "collectTime": ts_ms},
        )
        data_list = body.get("data") or []
        if not data_list:
            return None
        kpi = data_list[0].get("dataItemMap", {})
        return StationDailyData(
            date=query_date,
            generation_kwh=_safe_float(kpi.get("productPower")),
        )

    async def get_device_list(self, station_code: str) -> list[DeviceInfo]:
        body = await self._post(
            "/thirdData/getDevList",
            {"stationCodes": station_code},
        )
        devices: list[DeviceInfo] = []
        for item in body.get("data") or []:
            dev_type_id = item.get("devTypeId")
            devices.append(
                DeviceInfo(
                    device_code=str(item["id"]),
                    device_name=item.get("devName", ""),
                    device_type=_DEV_TYPE_MAP.get(dev_type_id, f"unknown_{dev_type_id}"),
                    brand="huawei",
                    serial_number=item.get("esnCode"),
                    status="normal",
                )
            )
        return devices

    async def get_device_realtime(self, station_code: str, device_code: str) -> DeviceRealtimeData | None:
        # We need devTypeId; default to inverter (1) if not provided.
        body = await self._post(
            "/thirdData/getDevRealKpi",
            {"devIds": device_code, "devTypeId": 1},
        )
        data_list = body.get("data") or []
        if not data_list:
            return None
        kpi = data_list[0].get("dataItemMap", {})
        return DeviceRealtimeData(
            device_code=device_code,
            timestamp=datetime.now(tz=timezone.utc),
            power_kw=_safe_float(kpi.get("active_power")),
            voltage_v=_safe_float(kpi.get("a_u")) or _safe_float(kpi.get("mppt_1_cap")),
            current_a=_safe_float(kpi.get("a_i")),
            temperature=_safe_float(kpi.get("temperature")),
            frequency=_safe_float(kpi.get("elec_freq")),
            daily_generation=_safe_float(kpi.get("day_cap")),
            raw_data=kpi,
        )

    async def get_alarms(self, station_code: str) -> list[AlarmInfo]:
        now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        one_day_ago_ms = now_ms - 86_400_000
        body = await self._post(
            "/thirdData/getAlarmList",
            {
                "stationCodes": station_code,
                "beginTime": one_day_ago_ms,
                "endTime": now_ms,
                "language": "zh_CN",
            },
        )
        alarms: list[AlarmInfo] = []
        data = body.get("data") or {}
        for item in data.get("list") or []:
            raise_time = item.get("raiseTime") or item.get("alarmTime")
            alarms.append(
                AlarmInfo(
                    alarm_code=str(item.get("alarmId", "")),
                    alarm_name=item.get("alarmName", ""),
                    alarm_level=_huawei_alarm_level(item.get("lev")),
                    alarm_time=_ts_to_datetime(raise_time),
                    recover_time=_ts_to_datetime(item.get("clearTime")) if item.get("clearTime") else None,
                    device_name=item.get("devName"),
                    description=item.get("alarmCause"),
                )
            )
        return alarms

    # ------------------------------------------------------------------
    # Additional read-only KPI endpoints (Huawei SmartPVMS V6)
    # ------------------------------------------------------------------

    async def get_station_hourly(self, station_codes: list, collect_time: int) -> dict:
        """获取电站小时数据 (hourly generation data).

        Args:
            station_codes: List of station codes.
            collect_time: Timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getKpiStationHour",
            {"stationCodes": ",".join(str(c) for c in station_codes), "collectTime": collect_time},
        )

    async def get_station_monthly(self, station_codes: list, collect_time: int) -> dict:
        """获取电站月数据 (monthly generation data).

        Args:
            station_codes: List of station codes.
            collect_time: Timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getKpiStationMonth",
            {"stationCodes": ",".join(str(c) for c in station_codes), "collectTime": collect_time},
        )

    async def get_station_yearly(self, station_codes: list, collect_time: int) -> dict:
        """获取电站年数据 (yearly generation data).

        Args:
            station_codes: List of station codes.
            collect_time: Timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getKpiStationYear",
            {"stationCodes": ",".join(str(c) for c in station_codes), "collectTime": collect_time},
        )

    async def get_device_history(
        self, device_id: int, device_type_id: int, start_time: int, end_time: int
    ) -> dict:
        """获取设备历史数据 (device history KPI).

        Args:
            device_id: Device ID.
            device_type_id: Device type ID (e.g. 1 for inverter).
            start_time: Start timestamp in milliseconds.
            end_time: End timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getDevHistoryKpi",
            {
                "devIds": str(device_id),
                "devTypeId": device_type_id,
                "startTime": start_time,
                "endTime": end_time,
            },
        )

    async def get_device_daily(self, device_id: int, device_type_id: int, collect_time: int) -> dict:
        """获取设备日数据 (device daily KPI).

        Args:
            device_id: Device ID.
            device_type_id: Device type ID.
            collect_time: Timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getDevKpiDay",
            {"devIds": str(device_id), "devTypeId": device_type_id, "collectTime": collect_time},
        )

    async def get_device_monthly(self, device_id: int, device_type_id: int, collect_time: int) -> dict:
        """获取设备月数据 (device monthly KPI).

        Args:
            device_id: Device ID.
            device_type_id: Device type ID.
            collect_time: Timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getDevKpiMonth",
            {"devIds": str(device_id), "devTypeId": device_type_id, "collectTime": collect_time},
        )

    async def get_device_yearly(self, device_id: int, device_type_id: int, collect_time: int) -> dict:
        """获取设备年数据 (device yearly KPI).

        Args:
            device_id: Device ID.
            device_type_id: Device type ID.
            collect_time: Timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getDevKpiYear",
            {"devIds": str(device_id), "devTypeId": device_type_id, "collectTime": collect_time},
        )

    async def get_device_5min(
        self, device_id: int, device_type_id: int, collect_time: int, start_time: int, end_time: int
    ) -> dict:
        """获取设备5分钟历史数据 (device 5-minute granularity data).

        Args:
            device_id: Device ID.
            device_type_id: Device type ID.
            collect_time: Timestamp in milliseconds.
            start_time: Start timestamp in milliseconds.
            end_time: End timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getDevFiveMinutes",
            {
                "devIds": str(device_id),
                "devTypeId": device_type_id,
                "collectTime": collect_time,
                "startTime": start_time,
                "endTime": end_time,
            },
        )

    async def get_station_list_history(self, collect_time: int) -> dict:
        """获取电站列表（含历史时间参数）(station list with time filter).

        Args:
            collect_time: Timestamp in milliseconds.
        """
        return await self._post(
            "/thirdData/getStationList",
            {"pageNo": 1, "collectTime": collect_time},
        )

    async def close(self) -> None:
        if self._xsrf_token:
            try:
                client = self._get_client()
                await client.post(
                    "/thirdData/logout",
                    json={"xsrfToken": self._xsrf_token},
                    headers={"XSRF-TOKEN": self._xsrf_token},
                )
            except Exception:
                logger.debug("Huawei logout request failed (non-critical)")
            self._xsrf_token = None
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------

def _safe_float(val: object) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _ts_to_datetime(ts: int | None) -> datetime:
    if ts is None:
        return datetime.now(tz=timezone.utc)
    # Huawei uses millisecond timestamps
    if ts > 1e12:
        ts = int(ts / 1000)
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _huawei_alarm_level(lev: int | None) -> str:
    mapping = {1: "critical", 2: "warning", 3: "info"}
    return mapping.get(lev or 0, "info")
