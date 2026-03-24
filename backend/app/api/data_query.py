"""历史数据查询接口 — 通过适配器直接查询厂家API"""
import json
import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters import get_adapter
from app.adapters.solis import SolisAdapter
from app.database import get_db
from app.dependencies import get_current_user
from app.models.device import Device
from app.models.manufacturer import Manufacturer
from app.models.station import Station

logger = logging.getLogger(__name__)

router = APIRouter()


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
        # Use Solis-specific method if available, otherwise fall back
        if isinstance(adapter, SolisAdapter):
            data = await adapter.get_station_month(station.station_code, month)
        else:
            # Generic fallback: return empty (adapter doesn't support monthly)
            data = []
        return {"station_id": station_id, "month": month, "data": data}
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
        else:
            data = []
        return {"station_id": station_id, "year": year, "data": data}
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
    """查询设备历史数据（通过厂家API）"""
    device, station, mfr = await _get_device_with_manufacturer(device_id, db)
    adapter = _make_adapter(mfr)
    try:
        await adapter.authenticate()
        if isinstance(adapter, SolisAdapter):
            start_date = _parse_date(start)
            end_date = _parse_date(end)
            # Cap range to 31 days to avoid excessive API calls
            if (end_date - start_date).days > 31:
                end_date = start_date + timedelta(days=31)
            all_data: list[dict] = []
            d = start_date
            while d <= end_date:
                try:
                    day_data = await adapter.get_inverter_day(
                        device.device_code, d
                    )
                    for point in day_data:
                        point["date"] = d.isoformat()
                    all_data.extend(day_data)
                except Exception:
                    logger.debug("Failed to fetch inverter day data for %s on %s", device.device_code, d)
                d += timedelta(days=1)
            return {
                "device_id": device_id,
                "start": start,
                "end": end_date.isoformat(),
                "data": all_data,
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
            data = await adapter.get_inverter_day(device.device_code, query_date)
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
        return {"device_id": device_id, "date": date, "data": data}
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
            data = await adapter.get_inverter_month(device.device_code, month)
        else:
            data = []
        return {"device_id": device_id, "month": month, "data": data}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("查询设备月度数据失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail=f"查询厂家API失败: {exc}")
    finally:
        await adapter.close()


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
