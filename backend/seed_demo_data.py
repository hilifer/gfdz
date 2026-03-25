"""生成演示数据到数据库"""
import asyncio
import random
from datetime import datetime, date, timedelta

from app.database import engine, Base, async_session
from app.models.station import Station
from app.models.station_data import StationRealtime, StationDaily
from app.models.device import Device
from app.models.alarm import Alarm
from app.models.work_order import WorkOrder, WorkOrderLog
from app.models.manufacturer import Manufacturer

# 电站配置 — 每个厂家配若干电站
STATIONS = [
    # 华为 (manufacturer_id=1)
    {"name": "杭州滨江科技园屋顶电站", "code": "HW-HZ-001", "mfr": 1, "cap": 580.0, "addr": "浙江省杭州市滨江区", "province": "浙江", "city": "杭州", "lng": 120.21, "lat": 30.21, "type": "rooftop", "price": 0.85},
    {"name": "上海张江光伏电站", "code": "HW-SH-002", "mfr": 1, "cap": 1200.0, "addr": "上海市浦东新区张江高科", "province": "上海", "city": "上海", "lng": 121.59, "lat": 31.20, "type": "rooftop", "price": 0.92},
    {"name": "宁波慈溪工业园电站", "code": "HW-NB-003", "mfr": 1, "cap": 860.0, "addr": "浙江省宁波市慈溪市", "province": "浙江", "city": "宁波", "lng": 121.23, "lat": 30.17, "type": "ground", "price": 0.80},
    # 爱士惟 (manufacturer_id=2)
    {"name": "苏州工业园屋顶电站", "code": "AW-SZ-001", "mfr": 2, "cap": 450.0, "addr": "江苏省苏州市工业园区", "province": "江苏", "city": "苏州", "lng": 120.72, "lat": 31.34, "type": "rooftop", "price": 0.88},
    {"name": "无锡新能源基地电站", "code": "AW-WX-002", "mfr": 2, "cap": 320.0, "addr": "江苏省无锡市新吴区", "province": "江苏", "city": "无锡", "lng": 120.36, "lat": 31.49, "type": "distributed", "price": 0.82},
    {"name": "南京江宁分布式电站", "code": "AW-NJ-003", "mfr": 2, "cap": 680.0, "addr": "江苏省南京市江宁区", "province": "江苏", "city": "南京", "lng": 118.84, "lat": 31.95, "type": "distributed", "price": 0.86},
    # 阳光电源 (manufacturer_id=3)
    {"name": "合肥高新区光伏电站", "code": "SG-HF-001", "mfr": 3, "cap": 2000.0, "addr": "安徽省合肥市高新区", "province": "安徽", "city": "合肥", "lng": 117.21, "lat": 31.84, "type": "ground", "price": 0.78},
    {"name": "西安经开区电站", "code": "SG-XA-002", "mfr": 3, "cap": 950.0, "addr": "陕西省西安市经开区", "province": "陕西", "city": "西安", "lng": 108.94, "lat": 34.34, "type": "rooftop", "price": 0.75},
    # 锦浪 (manufacturer_id=4)
    {"name": "温州龙湾户用电站", "code": "SL-WZ-001", "mfr": 4, "cap": 35.0, "addr": "浙江省温州市龙湾区", "province": "浙江", "city": "温州", "lng": 120.81, "lat": 27.93, "type": "rooftop", "price": 0.90},
    {"name": "台州黄岩屋顶电站", "code": "SL-TZ-002", "mfr": 4, "cap": 50.0, "addr": "浙江省台州市黄岩区", "province": "浙江", "city": "台州", "lng": 121.26, "lat": 28.65, "type": "rooftop", "price": 0.88},
    {"name": "金华义乌分布式电站", "code": "SL-JH-003", "mfr": 4, "cap": 120.0, "addr": "浙江省金华市义乌市", "province": "浙江", "city": "金华", "lng": 120.07, "lat": 29.31, "type": "distributed", "price": 0.85},
]

DEVICE_TYPES = [
    ("inverter", "逆变器", "SUN2000-100KTL", 100.0),
    ("meter", "电表", "DTSD1352", None),
    ("combiner_box", "汇流箱", "PVS-16M", None),
]

ALARM_TEMPLATES = [
    ("ALM001", "逆变器过温告警", "warning"),
    ("ALM002", "电网电压偏高", "warning"),
    ("ALM003", "组串电流异常", "critical"),
    ("ALM004", "通信中断", "critical"),
    ("ALM005", "绝缘阻抗低", "warning"),
    ("ALM006", "直流拉弧检测", "critical"),
    ("ALM007", "功率限发", "info"),
    ("ALM008", "防逆流保护", "info"),
]


async def seed():
    async with async_session() as db:
        # 检查是否已有数据
        from sqlalchemy import select, func
        count = await db.scalar(select(func.count(Station.id)))
        if count and count > 0:
            print(f"数据库已有 {count} 个电站，跳过")
            return

        now = datetime.now()
        today = date.today()
        station_ids = []

        # 创建电站
        for i, cfg in enumerate(STATIONS, 1):
            statuses = ["normal"] * 8 + ["fault", "offline"]
            st = Station(
                name=cfg["name"],
                station_code=cfg["code"],
                manufacturer_id=cfg["mfr"],
                capacity_kwp=cfg["cap"],
                address=cfg["addr"],
                province=cfg["province"],
                city=cfg["city"],
                longitude=cfg["lng"],
                latitude=cfg["lat"],
                station_type=cfg["type"],
                grid_type=random.choice(["full_feed", "self_use"]),
                commissioned_date=today - timedelta(days=random.randint(180, 1200)),
                electricity_price=cfg["price"],
                contact_name=random.choice(["张工", "李工", "王工", "赵工", "陈工"]),
                contact_phone=f"138{random.randint(10000000, 99999999)}",
                status=random.choice(statuses),
                is_active=True,
                last_sync_at=now - timedelta(minutes=random.randint(1, 30)),
            )
            db.add(st)
            await db.flush()
            station_ids.append((st.id, cfg["cap"], cfg["price"]))

            # 实时数据
            cap = cfg["cap"]
            hour = now.hour
            # 模拟功率曲线（白天有功率）
            if 6 <= hour <= 18:
                power_ratio = max(0, 1 - abs(hour - 12) / 7) * random.uniform(0.5, 0.9)
            else:
                power_ratio = 0
            current_power = round(cap * power_ratio, 2)
            today_gen = round(cap * random.uniform(2.5, 4.5), 1)  # 日等效小时
            month_gen = round(today_gen * today.day * random.uniform(0.85, 1.0), 1)
            year_gen = round(today_gen * (today.timetuple().tm_yday) * random.uniform(0.8, 0.95), 1)
            total_gen = round(year_gen * random.uniform(1.5, 3.0), 1)

            rt = StationRealtime(
                station_id=st.id,
                current_power_kw=current_power,
                today_generation=today_gen,
                month_generation=month_gen,
                year_generation=year_gen,
                total_generation=total_gen,
                today_revenue=round(today_gen * cfg["price"], 2),
            )
            db.add(rt)

            # 设备
            n_inverters = max(1, int(cap / 100))
            for j in range(n_inverters):
                dev = Device(
                    station_id=st.id,
                    device_code=f"{cfg['code']}-INV-{j+1:02d}",
                    device_name=f"{cfg['name']}-逆变器{j+1}",
                    device_type="inverter",
                    brand=["华为", "阳光电源", "锦浪", "爱士惟"][cfg["mfr"]-1],
                    model="SUN2000-100KTL" if cap > 100 else "SUN2000-36KTL",
                    serial_number=f"SN{random.randint(100000, 999999)}",
                    rated_power=min(100, cap / n_inverters),
                    status="normal",
                    last_data_at=now - timedelta(minutes=random.randint(1, 15)),
                )
                db.add(dev)

            # 电表
            dev_meter = Device(
                station_id=st.id,
                device_code=f"{cfg['code']}-MTR-01",
                device_name=f"{cfg['name']}-电表",
                device_type="meter",
                brand="安科瑞",
                model="DTSD1352",
                serial_number=f"MTR{random.randint(100000, 999999)}",
                status="normal",
                last_data_at=now - timedelta(minutes=random.randint(1, 15)),
            )
            db.add(dev_meter)

            # 30日发电数据
            for d in range(30):
                dt = today - timedelta(days=d)
                # 天气因素
                weather = random.choice([1.0, 1.0, 1.0, 0.8, 0.6, 0.3, 0.9])
                gen = round(cap * random.uniform(2.5, 4.5) * weather, 1)
                daily = StationDaily(
                    station_id=st.id,
                    date=dt,
                    generation_kwh=gen,
                    peak_power_kw=round(cap * random.uniform(0.7, 0.95), 1),
                    revenue=round(gen * cfg["price"], 2),
                    equivalent_hours=round(gen / cap, 2),
                    pr_value=round(random.uniform(0.75, 0.92), 3),
                    co2_reduction=round(gen * 0.997, 1),
                )
                db.add(daily)

        # 告警数据
        for sid, cap, price in station_ids:
            n_alarms = random.randint(0, 4)
            for _ in range(n_alarms):
                tpl = random.choice(ALARM_TEMPLATES)
                alarm_time = now - timedelta(hours=random.randint(1, 72))
                recovered = random.random() > 0.4
                alarm = Alarm(
                    station_id=sid,
                    alarm_code=tpl[0],
                    alarm_name=tpl[1],
                    alarm_level=tpl[2],
                    alarm_time=alarm_time,
                    recover_time=alarm_time + timedelta(hours=random.randint(1, 12)) if recovered else None,
                    status="recovered" if recovered else "active",
                    device_name=f"逆变器{random.randint(1, 3)}",
                )
                db.add(alarm)

        # 工单
        for sid, cap, price in random.sample(station_ids, min(4, len(station_ids))):
            wo = WorkOrder(
                order_no=f"WO{today.strftime('%Y%m%d')}{random.randint(1, 99):04d}",
                title=random.choice(["逆变器巡检", "组件清洗", "电缆检查", "防雷检测", "通信恢复"]),
                station_id=sid,
                order_type=random.choice(["corrective", "preventive"]),
                priority=random.choice(["low", "medium", "high"]),
                status=random.choice(["pending", "in_progress", "completed"]),
                description="系统自动生成的演示工单",
                creator_id=1,
            )
            db.add(wo)

        await db.commit()
        print(f"演示数据生成完毕: {len(STATIONS)} 个电站")


asyncio.run(seed())
