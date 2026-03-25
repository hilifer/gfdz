"""页面路由 — 使用 Jinja2 模板渲染"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def page_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/stations", response_class=HTMLResponse)
async def page_stations(request: Request):
    return templates.TemplateResponse("stations.html", {"request": request})


@router.get("/stations/{station_id}", response_class=HTMLResponse)
async def page_station_detail(request: Request, station_id: int):
    return templates.TemplateResponse("station_detail.html", {"request": request})


@router.get("/devices", response_class=HTMLResponse)
async def page_devices(request: Request):
    return templates.TemplateResponse("devices.html", {"request": request})


@router.get("/devices/{device_id}", response_class=HTMLResponse)
async def page_device_detail(request: Request, device_id: int):
    return templates.TemplateResponse("device_detail.html", {"request": request})


@router.get("/alarms", response_class=HTMLResponse)
async def page_alarms(request: Request):
    return templates.TemplateResponse("alarms.html", {"request": request})


@router.get("/analysis/generation", response_class=HTMLResponse)
async def page_generation(request: Request):
    return templates.TemplateResponse("generation.html", {"request": request})


@router.get("/analysis/revenue", response_class=HTMLResponse)
async def page_revenue(request: Request):
    return templates.TemplateResponse("revenue.html", {"request": request})


@router.get("/work-orders", response_class=HTMLResponse)
async def page_work_orders(request: Request):
    return templates.TemplateResponse("work_orders.html", {"request": request})


@router.get("/settings/manufacturers", response_class=HTMLResponse)
async def page_manufacturers(request: Request):
    return templates.TemplateResponse("manufacturers.html", {"request": request})


@router.get("/settings/price", response_class=HTMLResponse)
async def page_price(request: Request):
    return templates.TemplateResponse("price.html", {"request": request})


@router.get("/settings/users", response_class=HTMLResponse)
async def page_users(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})
