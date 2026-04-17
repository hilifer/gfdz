"""光伏电站监控平台 — FastAPI 入口"""
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.api import auth, dashboard, stations, devices, alarms, manufacturers, work_orders, system, data_query
from app.pages import router as pages_router

logger = logging.getLogger(__name__)


async def _initial_sync_if_empty():
    """启动时如果数据库为空则后台同步一次"""
    from sqlalchemy import select, func
    from app.database import async_session
    from app.models.station import Station
    from app.services.sync_service import run_full_sync

    try:
        # 等数据库连接稳定
        await asyncio.sleep(3)
        async with async_session() as db:
            count = await db.scalar(select(func.count(Station.id)))
        if count and count > 0:
            logger.info("数据库已有 %d 个电站，跳过初始同步", count)
            return
        logger.info("数据库为空，开始后台同步各厂家数据...")
        results = await run_full_sync()
        logger.info("后台同步完成: %s", {k: (v.get("success", v.get("created", 0)) if isinstance(v, dict) else v) for k, v in results.items()})
    except Exception as e:
        logger.error("后台同步失败: %s", e, exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 等待数据库就绪，最多重试 30 次（约 30 秒）
    for attempt in range(1, 31):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库连接成功，表已创建")
            break
        except Exception as e:
            logger.warning("数据库连接失败 (第%d次): %s", attempt, e)
            if attempt == 30:
                logger.error("数据库连接失败，放弃重试")
                raise
            await asyncio.sleep(1)
    # 初始化默认管理员和厂家
    from app.services.init_data import init_default_data
    await init_default_data()
    # 后台触发首次同步（不阻塞应用启动）
    asyncio.create_task(_initial_sync_if_empty())
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["总览"])
app.include_router(stations.router, prefix="/api/stations", tags=["电站"])
app.include_router(devices.router, prefix="/api/devices", tags=["设备"])
app.include_router(alarms.router, prefix="/api/alarms", tags=["告警"])
app.include_router(manufacturers.router, prefix="/api/manufacturers", tags=["厂家"])
app.include_router(work_orders.router, prefix="/api/work-orders", tags=["工单"])
app.include_router(system.router, prefix="/api/system", tags=["系统"])
app.include_router(data_query.router, prefix="/api/query", tags=["数据查询"])


# 静态文件
_static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

# 页面路由（放在 API 路由之后，避免冲突）
app.include_router(pages_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
