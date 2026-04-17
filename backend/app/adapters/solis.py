"""锦浪 Solis Cloud API V2 适配器"""
import base64
import hashlib
import hmac
import json
import logging
from datetime import date, datetime, timedelta, timezone
from email.utils import formatdate
from time import mktime

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

# Solis inverter state → base status
_STATE_MAP: dict[int, str] = {
    1: "normal",   # online
    2: "offline",  # offline
    3: "alarm",    # alarm
}


class SolisAdapter(BaseAdapter):
    """Solis Cloud API V2.0.2 adapter.

    Default API base: https://api.ginlong.com:13333
    auth_config keys: api_id, api_secret
    """

    MANUFACTURER = "solis"

    def __init__(self, api_base_url: str, auth_config: dict):
        super().__init__(api_base_url, auth_config)
        self._api_id: str = auth_config["api_id"]
        self._api_secret: str = auth_config["api_secret"]
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.api_base_url,
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._client

    @staticmethod
    def _content_md5(body: bytes) -> str:
        """Return Base64(MD5(body))."""
        digest = hashlib.md5(body).digest()  # noqa: S324
        return base64.b64encode(digest).decode()

    def _sign(self, content_md5: str, content_type: str, date_str: str, path: str) -> str:
        """Compute HmacSHA1 signature for Solis API."""
        param = f"POST\n{content_md5}\n{content_type}\n{date_str}\n{path}"
        h = hmac.new(
            self._api_secret.encode(),
            param.encode(),
            hashlib.sha1,  # noqa: S303
        )
        return base64.b64encode(h.digest()).decode()

    def _build_headers(self, body: bytes, path: str) -> dict[str, str]:
        """Build authenticated headers for a POST request."""
        content_type = "application/json;charset=UTF-8"
        content_md5 = self._content_md5(body)
        # RFC 2822 date in GMT
        now = datetime.now(tz=timezone.utc)
        date_str = formatdate(timeval=mktime(now.timetuple()), usegmt=True)
        sign = self._sign(content_md5, content_type, date_str, path)
        return {
            "Content-MD5": content_md5,
            "Content-Type": content_type,
            "Date": date_str,
            "Authorization": f"API {self._api_id}:{sign}",
        }

    async def _post(self, path: str, payload: dict | None = None) -> dict:
        """Authenticated POST request with basic error handling."""
        client = self._get_client()
        body = json.dumps(payload or {}).encode()
        headers = self._build_headers(body, path)
        resp = await client.post(path, content=body, headers=headers)
        resp.raise_for_status()
        result = resp.json()
        if not result.get("success", True):
            code = result.get("code")
            msg = result.get("msg", "")
            raise RuntimeError(f"Solis API error {code}: {msg}")
        return result

    async def _post_all_pages(self, path: str, payload: dict | None = None) -> list[dict]:
        """Paginate through a Solis paged endpoint and return all records."""
        payload = dict(payload or {})
        page = 1
        page_size = 100
        records: list[dict] = []
        while True:
            payload["pageNo"] = page
            payload["pageSize"] = page_size
            body = await self._post(path, payload)
            data = body.get("data") or {}
            page_data = data.get("page") or {}
            items = page_data.get("records") or []
            records.extend(items)
            total = page_data.get("total", 0)
            if len(records) >= total or not items:
                break
            page += 1
        return records

    # ------------------------------------------------------------------
    # Public interface — required
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """Verify credentials by fetching the station list (page 1)."""
        try:
            await self._post("/v1/api/userStationList", {"pageNo": 1, "pageSize": 1})
            logger.info("Solis authenticated successfully")
            return True
        except Exception:
            logger.exception("Solis authentication check failed")
            return False

    async def get_station_list(self) -> list[StationInfo]:
        records = await self._post_all_pages("/v1/api/userStationList")
        stations: list[StationInfo] = []
        for item in records:
            stations.append(
                StationInfo(
                    station_code=str(item["id"]),
                    name=item.get("stationName", ""),
                    capacity_kwp=_safe_float(item.get("capacity")),
                    status=_STATE_MAP.get(item.get("state", 0), "normal"),
                    longitude=_safe_float(item.get("longitude")),
                    latitude=_safe_float(item.get("latitude")),
                    address=item.get("address"),
                    extra=item,
                )
            )
        return stations

    async def get_station_realtime(self, station_code: str) -> StationRealtimeData | None:
        body = await self._post("/v1/api/stationDetail", {"id": station_code})
        data = body.get("data")
        if not data:
            return None
        return StationRealtimeData(
            current_power_kw=_safe_float(data.get("power")),
            today_generation=_safe_float(data.get("dayEnergy")),
            month_generation=_safe_float(data.get("monthEnergy")),
            year_generation=_safe_float(data.get("yearEnergy")),
            total_generation=_safe_float(data.get("allEnergy")),
        )

    async def get_station_daily(self, station_code: str, query_date: date) -> StationDailyData | None:
        body = await self._post(
            "/v1/api/stationDay",
            {
                "id": station_code,
                "money": "",
                "time": query_date.strftime("%Y-%m-%d"),
                "timeZone": "8",
            },
        )
        data_list = body.get("data") or []
        if not data_list:
            return None
        # Sum/find peak across intra-day data points
        total_kwh: float = 0.0
        peak_kw: float = 0.0
        for point in data_list:
            gen = _safe_float(point.get("generation")) or _safe_float(point.get("energy")) or 0.0
            total_kwh += gen
            power = _safe_float(point.get("power")) or 0.0
            if power > peak_kw:
                peak_kw = power
        return StationDailyData(
            date=query_date,
            generation_kwh=total_kwh if total_kwh else None,
            peak_power_kw=peak_kw if peak_kw else None,
        )

    # ------------------------------------------------------------------
    # Public interface — optional overrides
    # ------------------------------------------------------------------

    async def get_device_list(self, station_code: str) -> list[DeviceInfo]:
        records = await self._post_all_pages(
            "/v1/api/inverterList",
            {"stationId": station_code},
        )
        devices: list[DeviceInfo] = []
        for item in records:
            devices.append(
                DeviceInfo(
                    device_code=str(item["id"]),
                    device_name=item.get("sn", ""),
                    device_type="inverter",
                    brand="solis",
                    model=item.get("productModel"),
                    serial_number=item.get("sn"),
                    rated_power=_safe_float(item.get("power")),
                    status=_STATE_MAP.get(item.get("state", 0), "normal"),
                )
            )
        # Also fetch collectors
        try:
            collector_records = await self._post_all_pages("/v1/api/collectorList")
            for item in collector_records:
                devices.append(
                    DeviceInfo(
                        device_code=str(item.get("id", "")),
                        device_name=item.get("sn", ""),
                        device_type="dongle",
                        brand="solis",
                        serial_number=item.get("sn"),
                        status=_STATE_MAP.get(item.get("state", 0), "normal"),
                    )
                )
        except Exception:
            logger.debug("Failed to fetch Solis collector list (non-critical)")
        return devices

    async def get_device_realtime(self, station_code: str, device_code: str) -> DeviceRealtimeData | None:
        body = await self._post("/v1/api/inverterDetail", {"id": device_code})
        data = body.get("data")
        if not data:
            return None

        ts = data.get("dataTimestamp")
        timestamp = _ts_to_datetime(ts)

        return DeviceRealtimeData(
            device_code=device_code,
            timestamp=timestamp,
            power_kw=_safe_float(data.get("pac")),
            voltage_v=_safe_float(data.get("uAc1")),
            current_a=_safe_float(data.get("iAc1")),
            temperature=_safe_float(data.get("inverterTemperature")),
            frequency=_safe_float(data.get("fac")),
            daily_generation=_safe_float(data.get("eToday")),
            raw_data=data,
        )

    async def get_alarms(self, station_code: str) -> list[AlarmInfo]:
        # Solis 告警查询最大支持 31 天，默认拉取最近 7 天
        now = datetime.now(tz=timezone.utc)
        begin = now - timedelta(days=7)
        records = await self._post_all_pages(
            "/v1/api/alarmList",
            {
                "stationId": station_code,
                "alarmBeginTime": begin.strftime("%Y-%m-%d 00:00:00"),
                "alarmEndTime": now.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        alarms: list[AlarmInfo] = []
        for item in records:
            alarms.append(
                AlarmInfo(
                    alarm_code=str(item.get("alarmId", "")),
                    alarm_name=item.get("alarmMsg", ""),
                    alarm_level=_solis_alarm_level(item.get("alarmType")),
                    alarm_time=_parse_datetime(item.get("alarmTime")),
                    recover_time=_parse_datetime(item.get("clearTime")) if item.get("clearTime") else None,
                    device_name=item.get("inverterSn"),
                    description=item.get("alarmMsg"),
                )
            )
        return alarms

    # ------------------------------------------------------------------
    # Extra Solis-specific methods (not part of BaseAdapter)
    # ------------------------------------------------------------------

    async def get_inverter_day(self, inverter_id: str, query_date: date, *, sn: str | None = None, time_zone: str = "8") -> list[dict]:
        """Fetch intra-day data for a single inverter."""
        payload: dict = {"id": inverter_id, "money": "", "time": query_date.strftime("%Y-%m-%d"), "timeZone": time_zone}
        if sn:
            payload["sn"] = sn
        body = await self._post("/v1/api/inverterDay", payload)
        return body.get("data") or []

    async def get_inverter_month(self, inverter_id: str, month: str, *, sn: str | None = None) -> list[dict]:
        """Fetch monthly data for a single inverter. month format: '2023-06'."""
        payload: dict = {"id": inverter_id, "money": "", "month": month}
        if sn:
            payload["sn"] = sn
        body = await self._post("/v1/api/inverterMonth", payload)
        return body.get("data") or []

    async def get_inverter_year(self, inverter_id: str, year: str, *, sn: str | None = None) -> list[dict]:
        """Fetch yearly data for a single inverter. year format: '2023'."""
        payload: dict = {"id": inverter_id, "money": "", "year": year}
        if sn:
            payload["sn"] = sn
        body = await self._post("/v1/api/inverterYear", payload)
        return body.get("data") or []

    async def get_inverter_all(self, inverter_id: str, *, sn: str | None = None) -> list[dict]:
        """Fetch all-years data for a single inverter."""
        payload: dict = {"id": inverter_id, "money": ""}
        if sn:
            payload["sn"] = sn
        body = await self._post("/v1/api/inverterAll", payload)
        return body.get("data") or []

    async def get_station_month(self, station_id: str, month: str) -> list[dict]:
        """Fetch monthly data for a station. month format: '2023-06'."""
        body = await self._post("/v1/api/stationMonth", {"id": station_id, "money": "", "month": month})
        return body.get("data") or []

    async def get_station_year(self, station_id: str, year: str) -> list[dict]:
        """Fetch yearly data for a station. year format: '2023'."""
        body = await self._post("/v1/api/stationYear", {"id": station_id, "money": "", "year": year})
        return body.get("data") or []

    async def close(self) -> None:
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


def _ts_to_datetime(ts: int | float | None) -> datetime:
    if ts is None:
        return datetime.now(tz=timezone.utc)
    # Solis uses millisecond timestamps
    if ts > 1e12:
        ts = int(ts) // 1000
    return datetime.fromtimestamp(int(ts), tz=timezone.utc)


def _parse_datetime(val: str | int | None) -> datetime:
    """Parse a datetime from string or timestamp."""
    if val is None:
        return datetime.now(tz=timezone.utc)
    if isinstance(val, (int, float)):
        return _ts_to_datetime(val)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(val, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.now(tz=timezone.utc)


def _solis_alarm_level(alarm_type: int | str | None) -> str:
    """Map Solis alarm type to base alarm level."""
    try:
        t = int(alarm_type) if alarm_type is not None else 0
    except (ValueError, TypeError):
        return "info"
    # Solis alarm types: 1=fault(critical), 2=warning, 3=notice(info)
    mapping = {1: "critical", 2: "warning", 3: "info"}
    return mapping.get(t, "info")
