"""数据同步API"""
import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.manufacturer import Manufacturer
from app.models.power_station import PowerStation
from app.models.generation_data import GenerationData
from app.models.alarm import Alarm
from app.adapters import AdapterRegistry, RateLimitManager

router = APIRouter(prefix="/api/sync", tags=["数据同步"])


@router.post("/station/{sid}")
async def sync_station(sid: int, db: AsyncSession = Depends(get_db)):
    """手动同步单个电站数据"""
    station = await db.get(PowerStation, sid)
    if not station:
        raise HTTPException(404, "电站不存在")

    manufacturer = await db.get(Manufacturer, station.manufacturer_id)
    if not manufacturer:
        raise HTTPException(404, "厂家不存在")

    auth_config = json.loads(manufacturer.auth_config) if manufacturer.auth_config else {}
    extra_params = json.loads(station.extra_params) if station.extra_params else {}

    adapter = AdapterRegistry.create_adapter(
        code=manufacturer.code,
        api_base_url=manufacturer.api_base_url or "",
        auth_config=auth_config,
        extra_params=extra_params,
    )
    if not adapter:
        raise HTTPException(400, f"未找到厂家[{manufacturer.code}]的适配器")

    try:
        result = await adapter.sync_station_data(station.station_code)

        if "error" in result:
            return {"success": False, "error": result["error"]}

        # 保存实时/日数据
        gen_data = result.get("realtime") or result.get("daily")
        if gen_data:
            record = GenerationData(
                station_id=sid,
                record_date=gen_data.record_date,
                daily_generation=gen_data.daily_generation,
                monthly_generation=gen_data.monthly_generation,
                yearly_generation=gen_data.yearly_generation,
                total_generation=gen_data.total_generation,
                current_power=gen_data.current_power,
                daily_income=gen_data.daily_income,
                daily_peak_power=gen_data.daily_peak_power,
                equivalent_hours=gen_data.equivalent_hours,
                pr_value=gen_data.pr_value,
                raw_data=json.dumps(gen_data.raw_data, ensure_ascii=False) if gen_data.raw_data else None,
            )
            db.add(record)

        # 保存告警
        for alarm_data in result.get("alarms", []):
            alarm = Alarm(
                station_id=sid,
                alarm_code=alarm_data.alarm_code,
                alarm_name=alarm_data.alarm_name,
                alarm_level=alarm_data.alarm_level,
                alarm_time=alarm_data.alarm_time,
                recover_time=alarm_data.recover_time,
                status=alarm_data.status,
                description=alarm_data.description,
                device_name=alarm_data.device_name,
            )
            db.add(alarm)

        # 更新同步时间
        station.last_sync_at = datetime.now()
        await db.commit()

        return {"success": True, "message": "同步完成"}
    finally:
        await adapter.close()


@router.post("/all")
async def sync_all_stations(db: AsyncSession = Depends(get_db)):
    """同步所有活跃电站数据"""
    result = await db.execute(
        select(PowerStation).where(PowerStation.is_active == True)
    )
    stations = result.scalars().all()

    success_count = 0
    fail_count = 0
    errors = []

    for station in stations:
        try:
            manufacturer = await db.get(Manufacturer, station.manufacturer_id)
            if not manufacturer:
                continue

            auth_config = json.loads(manufacturer.auth_config) if manufacturer.auth_config else {}
            extra_params = json.loads(station.extra_params) if station.extra_params else {}

            adapter = AdapterRegistry.create_adapter(
                code=manufacturer.code,
                api_base_url=manufacturer.api_base_url or "",
                auth_config=auth_config,
                extra_params=extra_params,
            )
            if not adapter:
                fail_count += 1
                errors.append(f"{station.name}: 无适配器")
                continue

            try:
                sync_result = await adapter.sync_station_data(station.station_code)

                if "error" in sync_result:
                    fail_count += 1
                    errors.append(f"{station.name}: {sync_result['error']}")
                    continue

                gen_data = sync_result.get("realtime") or sync_result.get("daily")
                if gen_data:
                    record = GenerationData(
                        station_id=station.id,
                        record_date=gen_data.record_date,
                        daily_generation=gen_data.daily_generation,
                        monthly_generation=gen_data.monthly_generation,
                        yearly_generation=gen_data.yearly_generation,
                        total_generation=gen_data.total_generation,
                        current_power=gen_data.current_power,
                        daily_income=gen_data.daily_income,
                        daily_peak_power=gen_data.daily_peak_power,
                        equivalent_hours=gen_data.equivalent_hours,
                        pr_value=gen_data.pr_value,
                        raw_data=json.dumps(gen_data.raw_data, ensure_ascii=False) if gen_data.raw_data else None,
                    )
                    db.add(record)

                for alarm_data in sync_result.get("alarms", []):
                    alarm = Alarm(
                        station_id=station.id,
                        alarm_code=alarm_data.alarm_code,
                        alarm_name=alarm_data.alarm_name,
                        alarm_level=alarm_data.alarm_level,
                        alarm_time=alarm_data.alarm_time,
                        recover_time=alarm_data.recover_time,
                        status=alarm_data.status,
                        description=alarm_data.description,
                        device_name=alarm_data.device_name,
                    )
                    db.add(alarm)

                station.last_sync_at = datetime.now()
                success_count += 1
            finally:
                await adapter.close()

        except Exception as e:
            fail_count += 1
            errors.append(f"{station.name}: {str(e)}")

    await db.commit()
    return {
        "total": len(stations),
        "success": success_count,
        "failed": fail_count,
        "errors": errors,
    }


@router.get("/rate-limits")
async def get_rate_limit_stats():
    """查看所有平台的限流统计信息"""
    return RateLimitManager.get_all_stats()


@router.get("/adapters")
async def list_registered_adapters():
    """查看已注册的适配器列表"""
    adapters = AdapterRegistry.get_all()
    return {
        code: adapter_cls.__name__
        for code, adapter_cls in adapters.items()
    }
