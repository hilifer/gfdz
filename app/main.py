"""光伏电站监控平台 - 主应用"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from app.database import init_db
from app.api import manufacturers, stations, dashboard, data_sync
from app.tasks.scheduler import start_scheduler, stop_scheduler

# 确保适配器被注册
import app.adapters.demo_adapter  # noqa: F401
import app.adapters.huawei_adapter  # noqa: F401
import app.adapters.aiswei_adapter  # noqa: F401
import app.adapters.sungrow_adapter  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("正在启动光伏电站监控平台...")
    await init_db()
    start_scheduler()
    logger.info("平台启动完成")
    yield
    stop_scheduler()
    logger.info("平台已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="多厂家光伏电站监控管理平台",
    version="1.0.0",
    lifespan=lifespan,
)

# 静态文件 & 模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 注册API路由
app.include_router(manufacturers.router)
app.include_router(stations.router)
app.include_router(dashboard.router)
app.include_router(data_sync.router)


# ---- 页面路由 ----
@app.get("/")
async def page_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "active_page": "dashboard"})


@app.get("/stations")
async def page_stations(request: Request):
    return templates.TemplateResponse("stations.html", {"request": request, "active_page": "stations"})


@app.get("/stations/{station_id}")
async def page_station_detail(request: Request, station_id: int):
    return templates.TemplateResponse("station_detail.html", {
        "request": request, "active_page": "stations", "station_id": station_id,
    })


@app.get("/manufacturers")
async def page_manufacturers(request: Request):
    return templates.TemplateResponse("manufacturers.html", {"request": request, "active_page": "manufacturers"})


@app.get("/alarms")
async def page_alarms(request: Request):
    return templates.TemplateResponse("alarms.html", {"request": request, "active_page": "alarms"})
