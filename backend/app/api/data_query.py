"""历史数据查询接口 — 通过适配器直接查询厂家API"""
import json
import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters import get_adapter
from app.adapters.aiswei import AisweiAdapter
from app.adapters.solis import SolisAdapter
from app.adapters.sungrow import SungrowAdapter
from app.database import get_db
from app.dependencies import get_current_user
from app.models.device import Device
from app.models.manufacturer import Manufacturer
from app.models.station import Station

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Platform-specific constraints (from API documentation)
# ---------------------------------------------------------------------------
# AiSWEI:
#   - getPlantEventPro / getInverterHisErrorPagePro: max 7 days
#   - getInverterDataPagePro: max 7 days
# Sungrow:
#   - getDevicePointMinuteDataList: max 3-hour window, no today data
#   - getDevicePointsDayMonthYearDataList: max 100 days (day), 24 months (month), 5 years (year)
#   - query_type: 1=day, 2=month, 3=year; data_type: 2=peak, 4=sum
# Solis:
#   - inverterDay/stationDay: requires money="" and timeZone="8"

_MAX_RANGE_DAYS = {
    "aiswei": 7,
    "solis": 31,
    "sungrow": 100,
    "huawei": 31,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_station_with_manufacturer(
    station_id: int, db: AsyncSession
) -> tuple[Station, Manufacturer]:
    """Load a station and its manufacturer; raise 404 if missing."""
    station = await db.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="电站不存在")
    manufacturer = await db.get(Manufacturer, station.manufacturer_id)
    if not manufacturer:
        raise HTTPException(status_code=404, detail="厂家不存在")
    return station, manufacturer


async def _get_device_with_manufacturer(
    device_id: int, db: AsyncSession
) -> tuple[Device, Station, Manufacturer]:
    """Load a device, its station and manufacturer; raise 404 if missing."""
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    station = await db.get(Station, device.station_id)
    if not station:
        raise HTTPException(status_code=404, detail="电站不存在")
    manufacturer = await db.get(Manufacturer, station.manufacturer_id)
    if not manufacturer:
        raise HTTPException(status_code=404, detail="厂家不存在")
    return device, station, manufacturer


def _make_adapter(mfr: Manufacturer):
    auth_config = mfr.auth_config
    if isinstance(auth_config, str):
        auth_config = json.loads(auth_config)
    return get_adapter(mfr.code, mfr.api_base_url or "", auth_config or {})


def _enforce_date_range(start_date: date, end_date: date, mfr_code: str) -> date:
    """Clamp end_date to manufacturer's maximum query range."""
    max_days = _MAX_RANGE_DAYS.get(mfr_code, 31)
    if (end_date - start_date).days > max_days:
        return start_date + timedelta(days=max_days)
    return end_date


# ---------------------------------------------------------------------------
# Station endpoints
# ---------------------------------------------------------------------------

@router.get("/stations/{station_id}/hourly")
async def station_hourly(
    station_id: int,
    date: str = Query(..., description="日期, 格式: 2024-01-01"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """查询电站某日的小时级数据（通过厂家API）"""
    station, mfr = await _get_station_with_manufacturer(station_id, db)
    adapter = _make_adapter(mfr)
    try:
        await adapter.authenticate()
        query_date = _parse_date(date)
        data = await adapter.get_station_daily(station.station_code, query_date)
        if data is None:
            return {"station_id": station_id, "date": date, "data": None}
        return {
            "station_id": station_id,
            "date": date,
            "manufacturer": mfr.code,
            "data": {
                "generation_kwh": data.generation_kwh,
                "peak_power_kw": data.peak_power_kw,
                "equivalent_hours": data.equivalent_hours,
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("查询电站小时数据失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail=f"查询厂家API失败: {exc}")
    finally:
        await adapter.close()


@router.get("/stations/{station_id}/monthly")
async def station_monthly(
    station_id: int,
    month: str = Query(..., description="月份, 格式: 2024-01"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """查询电站月度数据（通过厂家API）"""
    station, mfr = await _get_station_with_manufacturer(station_id, db)
    adapter = _make_adapter(mfr)
    try:
        await adapter.authenticate()
        if isinstance(adapter, SolisAdapter):
            data = await adapter.get_station_month(station.station_code, month)
        elif isinstance(adapter, AisweiAdapter):
            data_raw = await adapter.get_station_output(station.station_code, "bymonth", month)
            data = data_raw.get("data", {}).get("result", [])
        elif isinstance(adapter, SungrowAdapter):
            # Sungrow: use getPowerStationList data (already includes month_energy)
            rt = await adapter.get_station_realtime(station.station_code)
            data = [{"month_generation": rt.month_generation}] if rt else []
        else:
            data = []
        return {"station_id": station_id, "month": month, "manufacturer": mfr.code, "data": data}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("查询电站月度数据失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail=f"查询厂家API失败: {exc}")
    finally:
        await adapter.close()


@router.get("/stations/{station_id}/yearly")
async def station_yearly(
    station_id: int,
    year: str = Query(..., description="年份, 格式: 2024"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """查询电站年度数据（通过厂家API）"""
    station, mfr = await _get_station_with_manufacturer(station_id, db)
    adapter = _make_adapter(mfr)
    try:
        await adapter.authenticate()
        if isinstance(adapter, SolisAdapter):
            data = await adapter.get_station_year(station.station_code, year)
        elif isinstance(adapter, AisweiAdapter):
            data_raw = await adapter.get_station_output(station.station_code, "byyear", year)
            data = data_raw.get("data", {}).get("result", [])
        elif isinstance(adapter, SungrowAdapter):
            rt = await adapter.get_station_realtime(station.station_code)
            data = [{"year_generation": rt.year_generation}] if rt else []
        else:
            data = []
        return {"station_id": station_id, "year": year, "manufacturer": mfr.code, "data": data}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("查询电站年度数据失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail=f"查询厂家API失败: {exc}")
    finally:
        await adapter.close()


# ---------------------------------------------------------------------------
# Device endpoints
# ---------------------------------------------------------------------------

@router.get("/devices/{device_id}/history")
async def device_history_via_adapter(
    device_id: int,
    start: str = Query(..., description="开始日期, 格式: 2024-01-01"),
    end: str = Query(..., description="结束日期, 格式: 2024-01-02"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """查询设备历史数据（通过厂家API）

    注意各平台限制:
    - 爱士惟: 最大7天
    - 锦浪: 最大31天
    - 阳光: 最大100天（历史接口不含当天数据）
    """
    device, station, mfr = await _get_device_with_manufacturer(device_id, db)
    adapter = _make_adapter(mfr)
    try:
        await adapter.authenticate()
        start_date = _parse_date(start)
        end_date = _parse_date(end)
        end_date = _enforce_date_range(start_date, end_date, mfr.code)

        if isinstance(adapter, SolisAdapter):
            all_data: list[dict] = []
            d = start_date
            while d <= end_date:
                try:
                    day_data = await adapter.get_inverter_day(
                        device.device_code, d,
                        sn=device.serial_number,
                        time_zone="8",
                    )
                    for point in day_data:
                        point["date"] = d.isoformat()
                    all_data.extend(day_data)
                except Exception:
                    logger.debug("Solis inverter day data fetch failed for %s on %s", device.device_code, d)
                d += timedelta(days=1)
            return {
                "device_id": device_id,
                "start": start,
                "end": end_date.isoformat(),
                "manufacturer": mfr.code,
                "data": all_data,
            }
        elif isinstance(adapter, AisweiAdapter):
            sdt = f"{start_date.isoformat()} 00:00:00"
            edt = f"{end_date.isoformat()} 23:59:59"
            data_raw = await adapter.get_inverter_data_page(
                station.station_code, device.device_code, sdt, edt, page=1, size=100,
            )
            data = data_raw.get("data", {}).get("result", [])
            return {
                "device_id": device_id,
                "start": start,
                "end": end_date.isoformat(),
                "manufacturer": mfr.code,
                "max_days": 7,
                "data": data,
            }
        else:
            # Generic: use base adapter device realtime
            data = await adapter.get_device_realtime(
                station.station_code, device.device_code
            )
            if data is None:
                return {"device_id": device_id, "start": start, "end": end, "data": []}
            return {
                "device_id": device_id,
                "start": start,
                "end": end,
                "manufacturer": mfr.code,
                "data": [
                    {
                        "timestamp": data.timestamp.isoformat(),
                        "power_kw": data.power_kw,
                        "voltage_v": data.voltage_v,
                        "current_a": data.current_a,
                        "temperature": data.temperature,
                        "daily_generation": data.daily_generation,
                    }
                ],
            }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("查询设备历史数据失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail=f"查询厂家API失败: {exc}")
    finally:
        await adapter.close()


@router.get("/devices/{device_id}/daily")
async def device_daily(
    device_id: int,
    date: str = Query(..., description="日期, 格式: 2024-01-01"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """查询设备某日的详细数据（通过厂家API）"""
    device, station, mfr = await _get_device_with_manufacturer(device_id, db)
    adapter = _make_adapter(mfr)
    try:
        await adapter.authenticate()
        query_date = _parse_date(date)
        if isinstance(adapter, SolisAdapter):
            data = await adapter.get_inverter_day(
                device.device_code, query_date,
                sn=device.serial_number,
                time_zone="8",
            )
        elif isinstance(adapter, AisweiAdapter):
            data_raw = await adapter.get_inverter_etoday(device.device_code, date)
            data = data_raw.get("data", {})
        else:
            # Generic fallback
            rt = await adapter.get_device_realtime(
                station.station_code, device.device_code
            )
            data = []
            if rt:
                data = [
                    {
                        "timestamp": rt.timestamp.isoformat(),
                        "power_kw": rt.power_kw,
                        "daily_generation": rt.daily_generation,
                    }
                ]
        return {"device_id": device_id, "date": date, "manufacturer": mfr.code, "data": data}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("查询设备日数据失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail=f"查询厂家API失败: {exc}")
    finally:
        await adapter.close()


@router.get("/devices/{device_id}/monthly")
async def device_monthly(
    device_id: int,
    month: str = Query(..., description="月份, 格式: 2024-01"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """查询设备月度数据（通过厂家API）"""
    device, station, mfr = await _get_device_with_manufacturer(device_id, db)
    adapter = _make_adapter(mfr)
    try:
        await adapter.authenticate()
        if isinstance(adapter, SolisAdapter):
            data = await adapter.get_inverter_month(
                device.device_code, month, sn=device.serial_number,
            )
        elif isinstance(adapter, AisweiAdapter):
            data_raw = await adapter.get_inverter_output(device.device_code, "bymonth", month)
            data = data_raw.get("data", {}).get("result", [])
        else:
            data = []
        return {"device_id": device_id, "month": month, "manufacturer": mfr.code, "data": data}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("查询设备月度数据失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail=f"查询厂家API失败: {exc}")
    finally:
        await adapter.close()


# ---------------------------------------------------------------------------
# Platform constraints info endpoint
# ---------------------------------------------------------------------------

@router.get("/platform-constraints")
async def platform_constraints(_=Depends(get_current_user)):
    """返回各平台API查询限制，供前端做校验提示"""
    return {
        "aiswei": {
            "max_history_days": 7,
            "notes": "爱士惟历史数据查询最大跨度7天；事件/故障查询最大跨度7天",
        },
        "solis": {
            "max_history_days": 31,
            "notes": "锦浪日数据查询需要指定时区(默认UTC+8)",
        },
        "sungrow": {
            "max_history_days": 100,
            "notes": "阳光历史分钟数据最大跨度3小时，且不含当天数据；日/月/年数据不含当天",
        },
        "huawei": {
            "max_history_days": 31,
            "notes": "华为北向接口有频率限制，每10分钟5次（注销接口）",
        },
    }


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _parse_date(s: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        parts = s.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (IndexError, ValueError):
        raise HTTPException(status_code=400, detail=f"日期格式错误: {s}, 应为 YYYY-MM-DD")
