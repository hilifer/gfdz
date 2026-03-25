"""AiSWEI (艾斯威) 适配器 — HMAC-SHA256 签名认证"""
import base64
import hashlib
import hmac
import logging
import time
import uuid
from datetime import date, datetime, timezone
from urllib.parse import urlencode, urlparse

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


class AisweiAdapter(BaseAdapter):
    """AiSWEI cloud adapter (HMAC-SHA256 signed requests).

    Default API base: https://api.general.aisweicloud.com
    auth_config keys: token, key (AppKey), secret (AppSecret)
    """

    MANUFACTURER = "aiswei"

    SIGNED_HEADERS = ["X-Ca-Key", "X-Ca-Nonce", "X-Ca-Stage", "X-Ca-Timestamp", "X-Ca-Version"]

    def __init__(self, api_base_url: str, auth_config: dict):
        super().__init__(api_base_url, auth_config)
        self._token: str = auth_config["token"]
        self._app_key: str = auth_config["key"]
        self._app_secret: str = auth_config["secret"]
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

    def _sign(
        self,
        method: str,
        path_with_query: str,
        accept: str = "application/json",
        content_type: str = "",
        content_md5: str = "",
        date_str: str = "",
    ) -> dict[str, str]:
        """Build HMAC-SHA256 signed headers for a request."""
        timestamp = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex

        # Headers that participate in signing (sorted)
        header_values = {
            "X-Ca-Key": self._app_key,
            "X-Ca-Nonce": nonce,
            "X-Ca-Stage": "RELEASE",
            "X-Ca-Timestamp": timestamp,
            "X-Ca-Version": "1",
        }

        # Build canonical headers string
        sorted_keys = sorted(header_values.keys())
        headers_str = "\n".join(f"{k}:{header_values[k]}" for k in sorted_keys)

        # String to sign
        string_to_sign = "\n".join(
            [
                method.upper(),
                accept,
                content_md5,
                content_type,
                date_str,
                headers_str + "\n" + path_with_query,
            ]
        )

        signature = base64.b64encode(
            hmac.new(
                self._app_secret.encode("utf-8"),
                string_to_sign.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        return {
            "Accept": accept,
            "X-Ca-Key": self._app_key,
            "X-Ca-Timestamp": timestamp,
            "X-Ca-Nonce": nonce,
            "X-Ca-Stage": "RELEASE",
            "X-Ca-Version": "1",
            "X-Ca-Signature-Headers": ",".join(sorted_keys),
            "X-Ca-Signature": signature,
        }

    async def _get(self, path: str, params: dict | None = None) -> dict:
        """Signed GET request."""
        params = params or {}
        # Always inject token
        params.setdefault("token", self._token)

        query_string = urlencode(params, doseq=True)
        full_path = f"{path}?{query_string}" if query_string else path

        headers = self._sign("GET", full_path, accept="application/json")
        client = self._get_client()
        resp = await client.get(full_path, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        if body.get("code") not in (None, 0, "0", 200, "200"):
            raise RuntimeError(f"AiSWEI API error: {body}")
        return body

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def authenticate(self) -> bool:
        """AiSWEI uses HMAC signing — no login call needed. Validate by fetching stations."""
        try:
            await self._get("/pro/getPlanListPro", {"pageNum": 1, "pageSize": 1, "order": 0})
            logger.info("AiSWEI authentication (signature check) succeeded")
            return True
        except Exception:
            logger.exception("AiSWEI authentication check failed")
            return False

    async def get_station_list(self) -> list[StationInfo]:
        stations: list[StationInfo] = []
        page = 1
        page_size = 100
        while True:
            body = await self._get(
                "/pro/getPlanListPro",
                {"order": 0, "pageNum": page, "pageSize": page_size},
            )
            data = body.get("data") or {}
            items = data.get("result") or []
            for item in items:
                stations.append(
                    StationInfo(
                        station_code=str(item.get("apikey", "")),
                        name=item.get("name", ""),
                        capacity_kwp=_safe_float(item.get("totalpower")),
                        longitude=_safe_float(item.get("jd")),
                        latitude=_safe_float(item.get("wd")),
                        address=item.get("position"),
                        status=_aiswei_station_status(item.get("status")),
                        extra={
                            "etoday": item.get("etoday"),
                            "etotal": item.get("etotal"),
                        },
                    )
                )
            if len(items) < page_size:
                break
            page += 1
        return stations

    async def get_station_realtime(self, station_code: str) -> StationRealtimeData | None:
        body = await self._get(
            "/pro/getPlantOverviewPro",
            {"apikey": station_code},
        )
        data = body.get("data")
        if not data:
            return None

        def _extract(key: str) -> float | None:
            entry = data.get(key)
            if isinstance(entry, dict):
                return _safe_float(entry.get("value"))
            return _safe_float(entry)

        return StationRealtimeData(
            current_power_kw=_safe_float_div(_extract("Power"), 1000.0),  # API returns W, convert to kW
            today_generation=_extract("E-Today"),
            month_generation=_extract("E-Month"),
            year_generation=_extract("E-Year"),
            total_generation=_extract("E-Total"),
        )

    async def get_station_daily(self, station_code: str, query_date: date) -> StationDailyData | None:
        # AiSWEI does not have a dedicated daily-energy endpoint in the standard
        # pro API.  We can approximate using the overview on the query date.
        # If the query_date is today we can use E-Today from overview.
        rt = await self.get_station_realtime(station_code)
        if rt is None:
            return None
        if query_date == date.today():
            return StationDailyData(date=query_date, generation_kwh=rt.today_generation)
        # Historical daily data not directly available through this API
        return StationDailyData(date=query_date, generation_kwh=None)

    async def get_device_list(self, station_code: str) -> list[DeviceInfo]:
        body = await self._get(
            "/pro/getDeviceListPro",
            {"apikey": station_code},
        )
        devices: list[DeviceInfo] = []
        data = body.get("data") or []
        for group in data:
            for inv in group.get("inverters") or []:
                devices.append(
                    DeviceInfo(
                        device_code=str(inv.get("isn", "")),
                        device_name=inv.get("isn", ""),
                        device_type="inverter",
                        brand="aiswei",
                        serial_number=inv.get("isn"),
                        status=_aiswei_inv_state(inv.get("istate")),
                    )
                )
        return devices

    async def get_device_realtime(self, station_code: str, device_code: str) -> DeviceRealtimeData | None:
        body = await self._get(
            "/pro/getLastTsDataPro",
            {"isnos": device_code},
        )
        data_list = body.get("data") or []
        if not data_list:
            return None
        item = data_list[0]
        # AiSWEI quirks: va1–3 in 0.1 V, ia1–3 in 0.1 A, fac in 0.01 Hz,
        # pac in W, etd in 0.1 kWh, eto in 0.1 kWh, cf in 0.1 °C
        pac_w = _safe_float(item.get("pac"))
        va1 = _safe_float(item.get("va1"))
        ia1 = _safe_float(item.get("ia1"))
        fac = _safe_float(item.get("fac"))
        cf = _safe_float(item.get("cf"))
        etd = _safe_float(item.get("etd"))

        return DeviceRealtimeData(
            device_code=device_code,
            timestamp=datetime.now(tz=timezone.utc),
            power_kw=pac_w / 1000.0 if pac_w is not None else None,
            voltage_v=va1 / 10.0 if va1 is not None else None,
            current_a=ia1 / 10.0 if ia1 is not None else None,
            temperature=cf / 10.0 if cf is not None else None,
            frequency=fac / 100.0 if fac is not None else None,
            daily_generation=etd / 10.0 if etd is not None else None,
            raw_data=item,
        )

    async def get_alarms(self, station_code: str) -> list[AlarmInfo]:
        today = date.today()
        body = await self._get(
            "/pro/getPlantEventPro",
            {
                "apikey": station_code,
                "sdt": today.strftime("%Y-%m-%d"),
                "edt": today.strftime("%Y-%m-%d"),
            },
        )
        alarms: list[AlarmInfo] = []
        data = body.get("data") or {}
        for item in data.get("result") or []:
            alarms.append(
                AlarmInfo(
                    alarm_code=str(item.get("eventCode", "")),
                    alarm_name=item.get("eventCode", ""),
                    alarm_level=_aiswei_event_level(item.get("eventType")),
                    alarm_time=_parse_aiswei_time(item.get("eventTime")),
                    device_name=item.get("ssno"),
                    description=item.get("eventCode"),
                )
            )

        # Also fetch current inverter errors
        try:
            err_body = await self._get(
                "/pro/getInverterCurrentErrorPro",
                {"apikey": station_code},
            )
            for item in err_body.get("data") or []:
                alarms.append(
                    AlarmInfo(
                        alarm_code=str(item.get("faultCode") or item.get("errorCode", "")),
                        alarm_name=item.get("errorCode", ""),
                        alarm_level="critical",
                        alarm_time=_parse_aiswei_time(item.get("errorDate")),
                        device_name=item.get("isno"),
                        description=item.get("context"),
                    )
                )
        except Exception:
            logger.debug("Failed to fetch inverter current errors", exc_info=True)

        return alarms

    # ------------------------------------------------------------------
    # Extended read-only API endpoints
    # ------------------------------------------------------------------

    async def get_station_output(
        self, apikey: str, period: str, date: str | None = None,
    ) -> dict:
        """getPlantOutputPro — station output time-series.

        Args:
            apikey: station API key (station_code).
            period: one of 'bydays', 'bymonth', 'byyear', 'bytotal'.
            date: date string whose format depends on *period*
                  (e.g. 'yyyy-MM-dd' for bydays, 'yyyy-MM' for bymonth,
                  'yyyy' for byyear).  Optional for 'bytotal'.

        Returns:
            Raw API response body (data.result[], data.dataunit).
        """
        params: dict = {"apikey": apikey, "period": period}
        if date is not None:
            params["date"] = date
        return await self._get("/pro/getPlantOutputPro", params)

    async def get_inverter_data_page(
        self,
        apikey: str,
        isn: str,
        sdt: str,
        edt: str,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """getInverterDataPagePro — paginated inverter time-series data.

        Args:
            apikey: station API key.
            isn: inverter serial number.
            sdt: start time 'yyyy-MM-dd HH:mm:ss'.
            edt: end time 'yyyy-MM-dd HH:mm:ss'.
            page: page number (1-based).
            size: page size.
        """
        return await self._get("/pro/getInverterDataPagePro", {
            "apikey": apikey,
            "isn": isn,
            "sdt": sdt,
            "edt": edt,
            "pageNum": page,
            "pageSize": size,
        })

    async def get_inverter_etoday(self, isn: str, date: str) -> dict:
        """getInverterETodayPro — inverter daily energy.

        Args:
            isn: inverter serial number.
            date: date string 'yyyy-MM-dd'.
        """
        return await self._get("/pro/getInverterETodayPro", {
            "isn": isn,
            "date": date,
        })

    async def get_inverter_history_errors(
        self,
        apikey: str,
        isn: str,
        sdt: str,
        edt: str,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """getInverterHisErrorPagePro — paginated historical inverter errors.

        Args:
            apikey: station API key.
            isn: inverter serial number.
            sdt: start time 'yyyy-MM-dd HH:mm:ss'.
            edt: end time 'yyyy-MM-dd HH:mm:ss'.
            page: page number (1-based).
            size: page size.
        """
        return await self._get("/pro/getInverterHisErrorPagePro", {
            "apikey": apikey,
            "isn": isn,
            "sdt": sdt,
            "edt": edt,
            "pageNum": page,
            "pageSize": size,
        })

    async def get_inverter_overview(self, isn: str) -> dict:
        """getInverterOverviewPro — inverter overview (energy, CO2, etc.).

        Args:
            isn: inverter serial number.
        """
        return await self._get("/pro/getInverterOverviewPro", {"isn": isn})

    async def get_inverter_output(
        self, isn: str, period: str, date: str | None = None,
    ) -> dict:
        """getInverterOutputPro — inverter output time-series.

        Args:
            isn: inverter serial number.
            period: one of 'bydays', 'bymonth', 'byyear', 'bytotal'.
            date: date string whose format depends on *period*.
        """
        params: dict = {"isn": isn, "period": period}
        if date is not None:
            params["date"] = date
        return await self._get("/pro/getInverterOutputPro", params)

    async def get_inverter_detail(self, isn: str) -> dict:
        """getInverterDetail — inverter basic info.

        Args:
            isn: inverter serial number.
        """
        return await self._get("/pro/getInverterDetail", {"isn": isn})

    async def get_user_detail(self) -> dict:
        """getUserDetail — current user / station basic info."""
        return await self._get("/pro/getUserDetail")

    async def get_collector_location(self, psno: str) -> dict:
        """getLocationPro — collector location (address, longitude, latitude).

        Args:
            psno: collector serial number.

        Returns:
            Raw response with address, jd (longitude), wd (latitude).
        """
        return await self._get("/pro/getLocationPro", {"psno": psno})

    async def get_inverter_recover_status(self, isn: str, event_id: str) -> dict:
        """getInverterRecoverStatusPro — check if an inverter error has recovered.

        Args:
            isn: inverter serial number.
            event_id: the event/error ID to check.
        """
        return await self._get("/pro/getInverterRecoverStatusPro", {
            "isn": isn,
            "eventId": event_id,
        })

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


def _safe_float_div(val: float | None, divisor: float) -> float | None:
    if val is None:
        return None
    return val / divisor


def _aiswei_station_status(status: object) -> str:
    mapping = {0: "offline", 1: "normal", 2: "warning", 3: "alarm", 4: "partial_offline"}
    return mapping.get(int(status) if status is not None else -1, "unknown")


def _aiswei_inv_state(state: object) -> str:
    # istate: 0=offline, 1=online, 2=cached (per API doc)
    mapping = {0: "offline", 1: "normal", 2: "offline"}
    return mapping.get(int(state) if state is not None else -1, "unknown")


def _aiswei_event_level(event_type: object) -> str:
    mapping = {1: "info", 2: "warning", 3: "critical"}
    return mapping.get(int(event_type) if event_type is not None else 0, "info")


def _parse_aiswei_time(val: object) -> datetime:
    if val is None:
        return datetime.now(tz=timezone.utc)
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val / 1000 if val > 1e12 else val, tz=timezone.utc)
    if isinstance(val, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(val, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return datetime.now(tz=timezone.utc)
