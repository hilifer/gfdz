"""数据同步服务 - 核心同步逻辑"""
import json
import logging
import traceback
from datetime import date, datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters import get_adapter
from app.adapters.base import BaseAdapter
from app.database import async_session
from app.models.alarm import Alarm
from app.models.device import Device
from app.models.manufacturer import Manufacturer
from app.models.station import Station
from app.models.station_data import StationDaily, StationRealtime
from app.models.sync_log import SyncLog

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: create a SyncLog entry
# ---------------------------------------------------------------------------

async def _create_sync_log(
    db: AsyncSession,
    *,
    sync_type: str,
    manufacturer_code: str,
    station_id: int | None = None,
    status: str = "success",
    records_count: int = 0,
    error_message: str | None = None,
) -> SyncLog:
    log = SyncLog(
        sync_type=sync_type,
        manufacturer_code=manufacturer_code,
        station_id=station_id,
        status=status,
        records_count=records_count,
        error_message=error_message,
        started_at=datetime.now(),
        finished_at=datetime.now(),
    )
    db.add(log)
    return log


# ---------------------------------------------------------------------------
# Helper: load active manufacturers and build adapters
# ---------------------------------------------------------------------------

async def _get_active_manufacturers(db: AsyncSession) -> list[Manufacturer]:
    result = await db.execute(
        select(Manufacturer).where(Manufacturer.is_active == True)
    )
    return list(result.scalars().all())


def _make_adapter(mfr: Manufacturer) -> BaseAdapter:
    auth_config = mfr.auth_config
    if isinstance(auth_config, str):
        auth_config = json.loads(auth_config)
    return get_adapter(mfr.code, mfr.api_base_url or "", auth_config or {})


# ---------------------------------------------------------------------------
# 1. sync_all_stations  -  同步电站列表
# ---------------------------------------------------------------------------

async def sync_all_stations() -> dict:
    """遍历所有活跃厂家，拉取电站列表并 upsert 到 DB."""
    summary = {"total": 0, "created": 0, "updated": 0, "errors": []}

    async with async_session() as db:
        manufacturers = await _get_active_manufacturers(db)

        for mfr in manufacturers:
            adapter = _make_adapter(mfr)
            try:
                await adapter.authenticate()
                station_list = await adapter.get_station_list()

                for info in station_list:
                    summary["total"] += 1

                    # 查找是否已存在
                    existing = await db.scalar(
                        select(Station).where(
                            and_(
                                Station.station_code == info.station_code,
                                Station.manufacturer_id == mfr.id,
                            )
                        )
                    )

                    if existing:
                        # 更新
                        existing.name = info.name
                        if info.capacity_kwp is not None:
                            existing.capacity_kwp = info.capacity_kwp
                        if info.longitude is not None:
                            existing.longitude = info.longitude
                        if info.latitude is not None:
                            existing.latitude = info.latitude
                        if info.address:
                            existing.address = info.address
                        existing.status = info.status
                        existing.updated_at = datetime.now()
                        summary["updated"] += 1
                    else:
                        # 创建
                        station = Station(
                            station_code=info.station_code,
                            name=info.name,
                            manufacturer_id=mfr.id,
                            capacity_kwp=info.capacity_kwp,
                            longitude=info.longitude,
                            latitude=info.latitude,
                            address=info.address,
                            status=info.status,
                            extra_config=json.dumps(info.extra) if info.extra else None,
                        )
                        db.add(station)
                        summary["created"] += 1

                # 更新厂家同步时间
                mfr.last_sync_at = datetime.now()

                await _create_sync_log(
                    db,
                    sync_type="station_list",
                    manufacturer_code=mfr.code,
                    status="success",
                    records_count=len(station_list),
                )

                await db.commit()
                logger.info(
                    "同步电站列表完成: 厂家=%s, 数量=%d",
                    mfr.code,
                    len(station_list),
                )
            except Exception as exc:
                await db.rollback()
                err_msg = f"[{mfr.code}] {exc.__class__.__name__}: {exc}"
                summary["errors"].append(err_msg)
                logger.error("同步电站列表失败: %s\n%s", err_msg, traceback.format_exc())

                async with async_session() as log_db:
                    await _create_sync_log(
                        log_db,
                        sync_type="station_list",
                        manufacturer_code=mfr.code,
                        status="failed",
                        error_message=str(exc)[:2000],
                    )
                    await log_db.commit()
            finally:
                await adapter.close()

    return summary


# ---------------------------------------------------------------------------
# 2. sync_realtime_data  -  同步实时数据
# ---------------------------------------------------------------------------

async def sync_realtime_data() -> dict:
    """遍历所有电站，拉取实时数据并 upsert 到 StationRealtime."""
    summary = {"total": 0, "success": 0, "errors": []}

    async with async_session() as db:
        manufacturers = await _get_active_manufacturers(db)

        for mfr in manufacturers:
            adapter = _make_adapter(mfr)
            try:
                await adapter.authenticate()

                # 获取该厂家所有活跃电站
                result = await db.execute(
                    select(Station).where(
                        and_(
                            Station.manufacturer_id == mfr.id,
                            Station.is_active == True,
                        )
                    )
                )
                stations = list(result.scalars().all())

                station_success = 0
                for station in stations:
                    summary["total"] += 1
                    try:
                        data = await adapter.get_station_realtime(station.station_code)
                        if data is None:
                            continue

                        # Upsert realtime record
                        rt = await db.scalar(
                            select(StationRealtime).where(
                                StationRealtime.station_id == station.id
                            )
                        )
                        if rt:
                            rt.current_power_kw = data.current_power_kw
                            rt.today_generation = data.today_generation
                            rt.month_generation = data.month_generation
                            rt.year_generation = data.year_generation
                            rt.total_generation = data.total_generation
                            rt.updated_at = datetime.now()
                        else:
                            rt = StationRealtime(
                                station_id=station.id,
                                current_power_kw=data.current_power_kw,
                                today_generation=data.today_generation,
                                month_generation=data.month_generation,
                                year_generation=data.year_generation,
                                total_generation=data.total_generation,
                            )
                            db.add(rt)

                        # 计算今日收益
                        if data.today_generation and station.electricity_price:
                            rt.today_revenue = round(
                                data.today_generation * station.electricity_price, 2
                            )

                        station.last_sync_at = datetime.now()
                        station_success += 1
                    except Exception as exc:
                        err_msg = f"[{mfr.code}/{station.station_code}] {exc}"
                        summary["errors"].append(err_msg)
                        logger.error("同步实时数据失败: %s", err_msg)

                await _create_sync_log(
                    db,
                    sync_type="realtime",
                    manufacturer_code=mfr.code,
                    status="success" if not summary["errors"] else "partial",
                    records_count=station_success,
                )
                summary["success"] += station_success

                await db.commit()
                logger.info(
                    "同步实时数据完成: 厂家=%s, 成功=%d/%d",
                    mfr.code,
                    station_success,
                    len(stations),
                )
            except Exception as exc:
                await db.rollback()
                err_msg = f"[{mfr.code}] {exc.__class__.__name__}: {exc}"
                summary["errors"].append(err_msg)
                logger.error("同步实时数据失败(厂家级): %s\n%s", err_msg, traceback.format_exc())

                async with async_session() as log_db:
                    await _create_sync_log(
                        log_db,
                        sync_type="realtime",
                        manufacturer_code=mfr.code,
                        status="failed",
                        error_message=str(exc)[:2000],
                    )
                    await log_db.commit()
            finally:
                await adapter.close()

    return summary


# ---------------------------------------------------------------------------
# 3. sync_daily_data  -  同步日发电数据
# ---------------------------------------------------------------------------

async def sync_daily_data(target_date: date | None = None) -> dict:
    """遍历所有电站，拉取日发电量并 upsert 到 StationDaily."""
    if target_date is None:
        target_date = date.today()

    summary = {"date": target_date.isoformat(), "total": 0, "success": 0, "errors": []}

    async with async_session() as db:
        manufacturers = await _get_active_manufacturers(db)

        for mfr in manufacturers:
            adapter = _make_adapter(mfr)
            try:
                await adapter.authenticate()

                result = await db.execute(
                    select(Station).where(
                        and_(
                            Station.manufacturer_id == mfr.id,
                            Station.is_active == True,
                        )
                    )
                )
                stations = list(result.scalars().all())

                station_success = 0
                for station in stations:
                    summary["total"] += 1
                    try:
                        data = await adapter.get_station_daily(
                            station.station_code, target_date
                        )
                        if data is None:
                            continue

                        # Upsert daily record
                        existing = await db.scalar(
                            select(StationDaily).where(
                                and_(
                                    StationDaily.station_id == station.id,
                                    StationDaily.date == target_date,
                                )
                            )
                        )

                        if existing:
                            existing.generation_kwh = data.generation_kwh
                            existing.peak_power_kw = data.peak_power_kw
                            existing.equivalent_hours = data.equivalent_hours
                        else:
                            daily = StationDaily(
                                station_id=station.id,
                                date=target_date,
                                generation_kwh=data.generation_kwh,
                                peak_power_kw=data.peak_power_kw,
                                equivalent_hours=data.equivalent_hours,
                            )
                            db.add(daily)

                        # 计算日收益
                        record = existing or daily  # type: ignore[possibly-undefined]
                        if data.generation_kwh and station.electricity_price:
                            record.revenue = round(
                                data.generation_kwh * station.electricity_price, 2
                            )

                        # 计算 CO2 减排 (约 0.997 kg/kWh)
                        if data.generation_kwh:
                            record.co2_reduction = round(
                                data.generation_kwh * 0.997, 2
                            )

                        station_success += 1
                    except Exception as exc:
                        err_msg = f"[{mfr.code}/{station.station_code}] {exc}"
                        summary["errors"].append(err_msg)
                        logger.error("同步日数据失败: %s", err_msg)

                await _create_sync_log(
                    db,
                    sync_type="daily",
                    manufacturer_code=mfr.code,
                    status="success" if not summary["errors"] else "partial",
                    records_count=station_success,
                )
                summary["success"] += station_success

                await db.commit()
                logger.info(
                    "同步日数据完成: 厂家=%s, 日期=%s, 成功=%d/%d",
                    mfr.code,
                    target_date,
                    station_success,
                    len(stations),
                )
            except Exception as exc:
                await db.rollback()
                err_msg = f"[{mfr.code}] {exc.__class__.__name__}: {exc}"
                summary["errors"].append(err_msg)
                logger.error("同步日数据失败(厂家级): %s\n%s", err_msg, traceback.format_exc())

                async with async_session() as log_db:
                    await _create_sync_log(
                        log_db,
                        sync_type="daily",
                        manufacturer_code=mfr.code,
                        status="failed",
                        error_message=str(exc)[:2000],
                    )
                    await log_db.commit()
            finally:
                await adapter.close()

    return summary


# ---------------------------------------------------------------------------
# 4. sync_devices  -  同步设备列表
# ---------------------------------------------------------------------------

async def sync_devices() -> dict:
    """遍历所有电站，拉取设备列表并 upsert 到 devices."""
    summary = {"total": 0, "created": 0, "updated": 0, "errors": []}

    async with async_session() as db:
        manufacturers = await _get_active_manufacturers(db)

        for mfr in manufacturers:
            adapter = _make_adapter(mfr)
            try:
                await adapter.authenticate()

                result = await db.execute(
                    select(Station).where(
                        and_(
                            Station.manufacturer_id == mfr.id,
                            Station.is_active == True,
                        )
                    )
                )
                stations = list(result.scalars().all())

                for station in stations:
                    try:
                        devices = await adapter.get_device_list(station.station_code)
                        for dev_info in devices:
                            summary["total"] += 1

                            existing = await db.scalar(
                                select(Device).where(
                                    and_(
                                        Device.station_id == station.id,
                                        Device.device_code == dev_info.device_code,
                                    )
                                )
                            )

                            if existing:
                                existing.device_name = dev_info.device_name
                                existing.device_type = dev_info.device_type
                                existing.brand = dev_info.brand
                                existing.model = dev_info.model
                                existing.serial_number = dev_info.serial_number
                                existing.rated_power = dev_info.rated_power
                                existing.status = dev_info.status
                                existing.updated_at = datetime.now()
                                summary["updated"] += 1
                            else:
                                device = Device(
                                    station_id=station.id,
                                    device_code=dev_info.device_code,
                                    device_name=dev_info.device_name,
                                    device_type=dev_info.device_type,
                                    brand=dev_info.brand,
                                    model=dev_info.model,
                                    serial_number=dev_info.serial_number,
                                    rated_power=dev_info.rated_power,
                                    status=dev_info.status,
                                )
                                db.add(device)
                                summary["created"] += 1

                    except Exception as exc:
                        err_msg = f"[{mfr.code}/{station.station_code}] {exc}"
                        summary["errors"].append(err_msg)
                        logger.error("同步设备列表失败: %s", err_msg)

                await _create_sync_log(
                    db,
                    sync_type="device",
                    manufacturer_code=mfr.code,
                    status="success" if not summary["errors"] else "partial",
                    records_count=summary["created"] + summary["updated"],
                )

                await db.commit()
                logger.info("同步设备列表完成: 厂家=%s", mfr.code)
            except Exception as exc:
                await db.rollback()
                err_msg = f"[{mfr.code}] {exc.__class__.__name__}: {exc}"
                summary["errors"].append(err_msg)
                logger.error("同步设备列表失败(厂家级): %s\n%s", err_msg, traceback.format_exc())

                async with async_session() as log_db:
                    await _create_sync_log(
                        log_db,
                        sync_type="device",
                        manufacturer_code=mfr.code,
                        status="failed",
                        error_message=str(exc)[:2000],
                    )
                    await log_db.commit()
            finally:
                await adapter.close()

    return summary


# ---------------------------------------------------------------------------
# 5. sync_alarms  -  同步告警
# ---------------------------------------------------------------------------

async def sync_alarms() -> dict:
    """遍历所有电站，拉取告警并创建新 Alarm 记录（跳过已存在的）."""
    summary = {"total": 0, "created": 0, "skipped": 0, "errors": []}

    async with async_session() as db:
        manufacturers = await _get_active_manufacturers(db)

        for mfr in manufacturers:
            adapter = _make_adapter(mfr)
            try:
                await adapter.authenticate()

                result = await db.execute(
                    select(Station).where(
                        and_(
                            Station.manufacturer_id == mfr.id,
                            Station.is_active == True,
                        )
                    )
                )
                stations = list(result.scalars().all())

                for station in stations:
                    try:
                        alarm_list = await adapter.get_alarms(station.station_code)

                        for alarm_info in alarm_list:
                            summary["total"] += 1

                            # 去重：同一电站 + 告警编码 + 告警时间
                            existing = await db.scalar(
                                select(Alarm).where(
                                    and_(
                                        Alarm.station_id == station.id,
                                        Alarm.alarm_code == alarm_info.alarm_code,
                                        Alarm.alarm_time == alarm_info.alarm_time,
                                    )
                                )
                            )

                            if existing:
                                # 更新恢复时间（如果有）
                                if alarm_info.recover_time and not existing.recover_time:
                                    existing.recover_time = alarm_info.recover_time
                                    existing.status = "recovered"
                                summary["skipped"] += 1
                                continue

                            alarm = Alarm(
                                station_id=station.id,
                                alarm_code=alarm_info.alarm_code,
                                alarm_name=alarm_info.alarm_name,
                                alarm_level=alarm_info.alarm_level,
                                alarm_time=alarm_info.alarm_time,
                                recover_time=alarm_info.recover_time,
                                status="recovered" if alarm_info.recover_time else "active",
                                description=alarm_info.description,
                                device_name=alarm_info.device_name,
                            )
                            db.add(alarm)
                            summary["created"] += 1

                    except Exception as exc:
                        err_msg = f"[{mfr.code}/{station.station_code}] {exc}"
                        summary["errors"].append(err_msg)
                        logger.error("同步告警失败: %s", err_msg)

                await _create_sync_log(
                    db,
                    sync_type="alarm",
                    manufacturer_code=mfr.code,
                    status="success" if not summary["errors"] else "partial",
                    records_count=summary["created"],
                )

                await db.commit()
                logger.info("同步告警完成: 厂家=%s, 新增=%d", mfr.code, summary["created"])
            except Exception as exc:
                await db.rollback()
                err_msg = f"[{mfr.code}] {exc.__class__.__name__}: {exc}"
                summary["errors"].append(err_msg)
                logger.error("同步告警失败(厂家级): %s\n%s", err_msg, traceback.format_exc())

                async with async_session() as log_db:
                    await _create_sync_log(
                        log_db,
                        sync_type="alarm",
                        manufacturer_code=mfr.code,
                        status="failed",
                        error_message=str(exc)[:2000],
                    )
                    await log_db.commit()
            finally:
                await adapter.close()

    return summary


# ---------------------------------------------------------------------------
# 6. run_full_sync  -  完整同步（用于手动触发）
# ---------------------------------------------------------------------------

async def run_full_sync() -> dict:
    """执行一次完整同步：电站列表 -> 设备 -> 实时 -> 日数据 -> 告警."""
    results = {}
    logger.info("========== 开始完整同步 ==========")

    logger.info("--- 同步电站列表 ---")
    results["stations"] = await sync_all_stations()

    logger.info("--- 同步设备列表 ---")
    results["devices"] = await sync_devices()

    logger.info("--- 同步实时数据 ---")
    results["realtime"] = await sync_realtime_data()

    logger.info("--- 同步日发电数据 ---")
    results["daily"] = await sync_daily_data()

    logger.info("--- 同步告警 ---")
    results["alarms"] = await sync_alarms()

    logger.info("========== 完整同步结束 ==========")
    return results
