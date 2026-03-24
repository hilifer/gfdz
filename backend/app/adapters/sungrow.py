"""Sungrow iSolarCloud 适配器"""
import hashlib
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

# Token validity: Sungrow tokens generally last 2 hours; refresh at 100 min.
_TOKEN_TTL_SECONDS = 100 * 60


class SungrowAdapter(BaseAdapter):
    """Sungrow iSolarCloud OpenAPI adapter.

    Default API base: https://gateway.isolarcloud.com/openapi
    auth_config keys: appkey, secret, username, password
    """

    MANUFACTURER = "sungrow"

    def __init__(self, api_base_url: str, auth_config: dict):
        super().__init__(api_base_url, auth_config)
        self._appkey: str = auth_config.get("appkey", "")
        self._secret: str = auth_config.get("secret", "")
        self._username: str = auth_config.get("username", "")
        self._password: str = auth_config.get("password", "")
        self._token: str | None = None
        self._token_acquired_at: float = 0.0
        self._user_id: str | None = None
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.api_base_url,
                timeout=httpx.Timeout(30.0, connect=10.0),
                headers={"Content-Type": "application/json"},
            )
        return self._client

    def _token_expired(self) -> bool:
        if self._token is None:
            return True
        return (time.monotonic() - self._token_acquired_at) > _TOKEN_TTL_SECONDS

    async def _ensure_auth(self) -> None:
        if self._token_expired():
            await self.authenticate()

    def _build_payload(self, extra: dict | None = None) -> dict:
        """Build a standard Sungrow API payload with appkey and token."""
        payload: dict = {"appkey": self._appkey}
        if self._token:
            payload["token"] = self._token
        if extra:
            payload.update(extra)
        return payload

    async def _post(self, path: str, extra: dict | None = None) -> dict:
        """Authenticated POST helper."""
        await self._ensure_auth()
        client = self._get_client()
        payload = self._build_payload(extra)
        resp = await client.post(path, json=payload)
        resp.raise_for_status()
        body = resp.json()
        result_code = body.get("result_code") or body.get("result_msg", {}).get("result_code")
        if result_code not in (None, "1", 1, "0", 0):
            logger.warning(
                "Sungrow API %s error: code=%s msg=%s",
                path,
                result_code,
                body.get("result_msg"),
            )
        return body

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        client = self._get_client()
        # Sungrow expects the password as an MD5 hash in some API versions
        password_hash = hashlib.md5(self._password.encode("utf-8")).hexdigest()
        payload = {
            "appkey": self._appkey,
            "user_account": self._username,
            "user_password": password_hash,
        }
        try:
            resp = await client.post("/openapi/login", json=payload)
            resp.raise_for_status()
            body = resp.json()
            result_data = body.get("result_data") or {}
            token = result_data.get("token")
            if not token:
                logger.error("Sungrow authenticate: no token in response: %s", body.get("result_msg"))
                return False
            self._token = token
            self._user_id = result_data.get("user_id")
            self._token_acquired_at = time.monotonic()
            logger.info("Sungrow authenticated successfully (user_id=%s)", self._user_id)
            return True
        except Exception:
            logger.exception("Sungrow authentication failed")
            return False

    async def get_station_list(self) -> list[StationInfo]:
        stations: list[StationInfo] = []
        page_no = 1
        page_size = 100
        while True:
            body = await self._post("/openapi/getPlantList", {
                "curPage": str(page_no),
                "size": str(page_size),
            })
            result_data = body.get("result_data") or {}
            items = result_data.get("pageList") or result_data.get("list") or []
            if not items:
                break
            for s in items:
                ps_id = str(s.get("ps_id") or s.get("plant_id", ""))
                stations.append(
                    StationInfo(
                        station_code=ps_id,
                        name=s.get("ps_name") or s.get("plant_name", ""),
                        capacity_kwp=_safe_float(s.get("installed_power_map") or s.get("design_capacity")),
                        status=_map_status(s.get("ps_status") or s.get("status")),
                        longitude=_safe_float(s.get("longitude")),
                        latitude=_safe_float(s.get("latitude")),
                        address=s.get("address") or s.get("ps_location"),
                        extra={k: v for k, v in s.items() if k not in (
                            "ps_id", "plant_id", "ps_name", "plant_name",
                            "installed_power_map", "design_capacity",
                            "longitude", "latitude", "address", "ps_location",
                            "ps_status", "status",
                        )},
                    )
                )
            if len(items) < page_size:
                break
            page_no += 1
        return stations

    async def get_station_realtime(self, station_code: str) -> StationRealtimeData | None:
        body = await self._post("/openapi/getPlantRealData", {"ps_id": station_code})
        result_data = body.get("result_data") or {}
        # Sungrow may return data nested under different keys
        data = result_data if isinstance(result_data, dict) else {}

        return StationRealtimeData(
            current_power_kw=_safe_float(
                data.get("curr_power") or data.get("current_power")
            ),
            today_generation=_safe_float(
                data.get("today_energy") or data.get("day_energy")
            ),
            month_generation=_safe_float(
                data.get("month_energy") or data.get("monthly_energy")
            ),
            year_generation=_safe_float(
                data.get("year_energy") or data.get("yearly_energy")
            ),
            total_generation=_safe_float(
                data.get("total_energy") or data.get("total_power")
            ),
        )

    async def get_station_daily(self, station_code: str, query_date: date) -> StationDailyData | None:
        date_str = query_date.strftime("%Y%m%d")
        body = await self._post("/openapi/getPlantDayReport", {
            "ps_id": station_code,
            "date": date_str,
        })
        result_data = body.get("result_data") or {}
        # Try multiple possible response structures
        items = result_data.get("data") or result_data.get("list") or []
        if isinstance(items, list) and items:
            rec = items[0] if items else {}
        elif isinstance(result_data, dict):
            rec = result_data
        else:
            return None

        return StationDailyData(
            date=query_date,
            generation_kwh=_safe_float(
                rec.get("generation") or rec.get("energy") or rec.get("day_energy")
            ),
            peak_power_kw=_safe_float(rec.get("peak_power")),
            equivalent_hours=_safe_float(rec.get("equivalent_hours") or rec.get("full_hours")),
        )

    async def get_device_list(self, station_code: str) -> list[DeviceInfo]:
        body = await self._post("/openapi/getDeviceList", {"ps_id": station_code})
        result_data = body.get("result_data") or {}
        items = result_data.get("pageList") or result_data.get("list") or []
        devices: list[DeviceInfo] = []
        for d in items:
            dev_type_raw = d.get("device_type") or d.get("dev_type", "")
            devices.append(
                DeviceInfo(
                    device_code=str(d.get("device_id") or d.get("id", "")),
                    device_name=d.get("device_name") or d.get("dev_name", ""),
                    device_type=_normalise_device_type(dev_type_raw),
                    brand="sungrow",
                    model=d.get("device_model") or d.get("dev_model"),
                    serial_number=d.get("sn") or d.get("serial_number"),
                    rated_power=_safe_float(d.get("rated_power")),
                    status=_map_status(d.get("device_status") or d.get("status")),
                )
            )
        return devices

    async def get_device_realtime(self, station_code: str, device_code: str) -> DeviceRealtimeData | None:
        body = await self._post("/openapi/getDeviceRealData", {
            "ps_id": station_code,
            "device_id": device_code,
        })
        result_data = body.get("result_data") or {}
        if not result_data:
            return None

        data = result_data if isinstance(result_data, dict) else {}
        return DeviceRealtimeData(
            device_code=device_code,
            timestamp=datetime.now(tz=timezone.utc),
            power_kw=_safe_float(data.get("active_power") or data.get("pac")),
            voltage_v=_safe_float(data.get("grid_voltage") or data.get("ua")),
            current_a=_safe_float(data.get("grid_current") or data.get("ia")),
            temperature=_safe_float(data.get("temperature") or data.get("tmp")),
            frequency=_safe_float(data.get("frequency") or data.get("fac")),
            daily_generation=_safe_float(data.get("today_energy") or data.get("etd")),
            raw_data=data,
        )

    async def get_alarms(self, station_code: str) -> list[AlarmInfo]:
        body = await self._post("/openapi/getAlarmList", {
            "ps_id": station_code,
            "page_no": "1",
            "page_size": "100",
        })
        result_data = body.get("result_data") or {}
        items = result_data.get("pageList") or result_data.get("list") or []
        alarms: list[AlarmInfo] = []
        for a in items:
            level_raw = a.get("alarm_level") or a.get("level", "")
            level = _map_alarm_level(level_raw)
            alarm_time = _parse_datetime(a.get("alarm_time") or a.get("start_time"))
            recover_time = _parse_datetime(a.get("recover_time") or a.get("end_time"))
            alarms.append(
                AlarmInfo(
                    alarm_code=str(a.get("alarm_code") or a.get("fault_code", "")),
                    alarm_name=a.get("alarm_name") or a.get("fault_name", ""),
                    alarm_level=level,
                    alarm_time=alarm_time or datetime.now(tz=timezone.utc),
                    recover_time=recover_time,
                    device_name=a.get("device_name") or a.get("dev_name"),
                    description=a.get("alarm_desc") or a.get("description"),
                )
            )
        return alarms

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
        self._token = None


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------

def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _map_status(val) -> str:
    if val is None:
        return "normal"
    val_str = str(val).lower()
    if val_str in ("1", "normal", "online", "running"):
        return "normal"
    if val_str in ("0", "offline", "disconnected"):
        return "offline"
    if val_str in ("2", "alarm", "fault", "error"):
        return "alarm"
    return "normal"


def _map_alarm_level(val) -> str:
    val_str = str(val).lower()
    if val_str in ("1", "info", "prompt", "low"):
        return "info"
    if val_str in ("2", "warning", "medium"):
        return "warning"
    if val_str in ("3", "4", "critical", "error", "fault", "high"):
        return "critical"
    return "info"


def _normalise_device_type(raw: str | int) -> str:
    raw_str = str(raw).lower()
    type_map = {
        "inverter": "inverter",
        "1": "inverter",
        "meter": "meter",
        "combiner": "combiner_box",
        "combiner_box": "combiner_box",
        "weather": "weather_station",
        "weather_station": "weather_station",
        "storage": "storage",
        "battery": "storage",
    }
    for key, value in type_map.items():
        if key in raw_str:
            return value
    return raw_str or "unknown"


def _parse_datetime(val) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        try:
            return datetime.fromtimestamp(val / 1000 if val > 1e12 else val, tz=timezone.utc)
        except (OSError, ValueError):
            return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y%m%d%H%M%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(val), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None
