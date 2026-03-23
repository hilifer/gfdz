"""智能定时任务调度器

根据不同平台的限流策略，智能安排同步任务：
- 华为: 电站实时数据每5分钟才能调1次，日数据每天25次，按需合理分配
- 爱士惟: 全局100次/分钟，相对宽裕
- 阳光电源: 保守30次/分钟

调度策略:
1. 按厂家分组，同一厂家的电站共享一个adapter实例（共享Token和限流器）
2. 同一厂家内串行同步（避免并发撞限流）
3. 不同厂家间并行同步（互不影响）
4. 遇到限流自动跳过，下次再同步
"""
import asyncio
import json
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from config import settings
from app.database import async_session
from app.models.manufacturer import Manufacturer
from app.models.power_station import PowerStation
from app.models.generation_data import GenerationData
from app.models.alarm import Alarm
from app.adapters import AdapterRegistry, RateLimitExceeded

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def _sync_manufacturer_stations(manufacturer_id: int, db):
    """同步单个厂家下的所有电站（串行，共享adapter实例）"""
    manufacturer = await db.get(Manufacturer, manufacturer_id)
    if not manufacturer or not manufacturer.is_active:
        return 0, 0

    auth_config = json.loads(manufacturer.auth_config) if manufacturer.auth_config else {}

    # 查询该厂家下所有活跃电站
    result = await db.execute(
        select(PowerStation).where(
            PowerStation.manufacturer_id == manufacturer_id,
            PowerStation.is_active == True,
        )
    )
    stations = result.scalars().all()
    if not stations:
        return 0, 0

    # 创建共享的adapter实例
    # 合并所有电站的extra_params（用于华为动态限流计算）
    merged_extra = {}
    for s in stations:
        if s.extra_params:
            try:
                merged_extra.update(json.loads(s.extra_params))
            except (json.JSONDecodeError, TypeError):
                pass

    adapter = AdapterRegistry.create_adapter(
        code=manufacturer.code,
        api_base_url=manufacturer.api_base_url or "",
        auth_config=auth_config,
        extra_params=merged_extra,
    )
    if not adapter:
        logger.warning(f"厂家[{manufacturer.name}]无适配器: {manufacturer.code}")
        return 0, len(stations)

    success = 0
    failed = 0

    try:
        # 先认证一次
        await adapter.authenticate()

        for station in stations:
            try:
                result_data = await adapter.sync_station_data(station.station_code)

                if "error" in result_data:
                    failed += 1
                    logger.warning(f"同步[{station.name}]失败: {result_data['error']}")
                    continue

                # 保存数据
                gen_data = result_data.get("realtime") or result_data.get("daily")
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

                for alarm_data in result_data.get("alarms", []):
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
                success += 1

            except RateLimitExceeded as e:
                logger.warning(f"同步[{station.name}]遇到限流，跳过剩余电站: {e}")
                failed += len(stations) - success - failed
                break  # 限流了就不再继续同一厂家的电站
            except Exception as e:
                failed += 1
                logger.exception(f"同步[{station.name}]异常: {e}")

        await db.commit()
    except RateLimitExceeded as e:
        logger.warning(f"厂家[{manufacturer.name}]认证限流: {e}")
        failed = len(stations)
    except Exception as e:
        logger.exception(f"厂家[{manufacturer.name}]同步异常: {e}")
        failed = len(stations) - success
    finally:
        await adapter.close()

    return success, failed


async def scheduled_sync_all():
    """
    智能同步所有电站。
    不同厂家并行同步，同一厂家内串行（避免限流冲突）。
    """
    logger.info("开始智能同步所有电站数据...")
    start_time = datetime.now()

    async with async_session() as db:
        # 获取所有活跃厂家
        result = await db.execute(
            select(Manufacturer).where(Manufacturer.is_active == True)
        )
        manufacturers = result.scalars().all()

        if not manufacturers:
            logger.info("无活跃厂家，跳过同步")
            return

        # 并行执行各厂家的同步任务
        tasks = [
            _sync_manufacturer_stations(m.id, db)
            for m in manufacturers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_success = 0
        total_failed = 0
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                logger.error(f"厂家[{manufacturers[i].name}]同步异常: {r}")
                total_failed += 1
            else:
                s, f = r
                total_success += s
                total_failed += f

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"智能同步完成: 成功{total_success}, 失败{total_failed}, "
        f"耗时{elapsed:.1f}s"
    )


def start_scheduler():
    """启动定时调度器"""
    scheduler.add_job(
        scheduled_sync_all,
        "interval",
        minutes=settings.SYNC_INTERVAL_MINUTES,
        id="sync_all_stations",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"智能调度器已启动，同步间隔: {settings.SYNC_INTERVAL_MINUTES}分钟")


def stop_scheduler():
    """停止调度器"""
    if scheduler.running:
        scheduler.shutdown()
