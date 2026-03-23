"""数据同步服务 - 供定时任务调用"""
import json
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from config import settings
from app.models.manufacturer import Manufacturer
from app.models.power_station import PowerStation
from app.models.generation_data import GenerationData
from app.models.alarm import Alarm
from app.adapters import AdapterRegistry

logger = logging.getLogger(__name__)

# 同步引擎（APScheduler需要同步session，这里用httpx的同步方式处理）
sync_engine = create_engine(settings.SYNC_DATABASE_URL, echo=False)


async def sync_single_station(station_id: int, db_session) -> dict:
    """同步单个电站"""
    station = await db_session.get(PowerStation, station_id)
    if not station:
        return {"success": False, "error": "电站不存在"}

    manufacturer = await db_session.get(Manufacturer, station.manufacturer_id)
    if not manufacturer:
        return {"success": False, "error": "厂家不存在"}

    auth_config = json.loads(manufacturer.auth_config) if manufacturer.auth_config else {}
    extra_params = json.loads(station.extra_params) if station.extra_params else {}

    adapter = AdapterRegistry.create_adapter(
        code=manufacturer.code,
        api_base_url=manufacturer.api_base_url or "",
        auth_config=auth_config,
        extra_params=extra_params,
    )
    if not adapter:
        return {"success": False, "error": f"无适配器: {manufacturer.code}"}

    try:
        result = await adapter.sync_station_data(station.station_code)
        if "error" in result:
            return {"success": False, "error": result["error"]}

        gen_data = result.get("realtime") or result.get("daily")
        if gen_data:
            record = GenerationData(
                station_id=station_id,
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
            db_session.add(record)

        for alarm_data in result.get("alarms", []):
            alarm = Alarm(
                station_id=station_id,
                alarm_code=alarm_data.alarm_code,
                alarm_name=alarm_data.alarm_name,
                alarm_level=alarm_data.alarm_level,
                alarm_time=alarm_data.alarm_time,
                recover_time=alarm_data.recover_time,
                status=alarm_data.status,
                description=alarm_data.description,
                device_name=alarm_data.device_name,
            )
            db_session.add(alarm)

        station.last_sync_at = datetime.now()
        await db_session.commit()
        return {"success": True}
    except Exception as e:
        logger.exception(f"同步电站[{station.name}]失败")
        return {"success": False, "error": str(e)}
    finally:
        await adapter.close()
