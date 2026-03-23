"""厂家管理API"""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.manufacturer import Manufacturer
from app.schemas.schemas import ManufacturerCreate, ManufacturerUpdate, ManufacturerResponse
from app.adapters.registry import AdapterRegistry, auto_detect_url, ADAPTER_CONFIGS

router = APIRouter(prefix="/api/manufacturers", tags=["厂家管理"])


# ---- 适配器配置接口（放在 /{mid} 之前避免路由冲突）----

@router.get("/adapter-configs")
async def get_adapter_configs():
    """获取所有适配器的配置元数据（认证字段、描述等）"""
    return AdapterRegistry.get_all_meta()


class TestConnectionRequest(BaseModel):
    """连接测试请求"""
    code: str
    auth_config: dict | None = None


@router.post("/test-connection")
async def test_connection(req: TestConnectionRequest):
    """
    测试厂家连接 — 自动探测所有候选URL，验证认证。

    安全说明：只使用只读接口（login/查询），绝不调用操作类接口。

    流程：
    1. 逐个尝试该厂家的所有候选URL
    2. 检查网络连通性
    3. 如果提供了认证参数，验证认证是否正确
    4. 返回每个URL的测试结果，推荐可用的URL
    """
    if req.code not in ADAPTER_CONFIGS:
        raise HTTPException(400, f"未知的厂家编码: {req.code}")

    result = await auto_detect_url(req.code, req.auth_config)
    return result


# ---- 厂家CRUD ----

@router.get("", response_model=list[ManufacturerResponse])
async def list_manufacturers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Manufacturer).order_by(Manufacturer.id))
    return result.scalars().all()


@router.get("/{mid}", response_model=ManufacturerResponse)
async def get_manufacturer(mid: int, db: AsyncSession = Depends(get_db)):
    m = await db.get(Manufacturer, mid)
    if not m:
        raise HTTPException(404, "厂家不存在")
    return m


@router.post("", response_model=ManufacturerResponse)
async def create_manufacturer(data: ManufacturerCreate, db: AsyncSession = Depends(get_db)):
    # 如果没有提供API URL，使用该厂家的默认URL
    dump = data.model_dump()
    if not dump.get("api_base_url"):
        default_url = AdapterRegistry.get_default_url(dump.get("code", ""))
        dump["api_base_url"] = default_url

    # adapter_class 默认跟 code 一致
    if not dump.get("adapter_class"):
        dump["adapter_class"] = dump.get("code", "")

    m = Manufacturer(**dump)
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m


@router.put("/{mid}", response_model=ManufacturerResponse)
async def update_manufacturer(mid: int, data: ManufacturerUpdate, db: AsyncSession = Depends(get_db)):
    m = await db.get(Manufacturer, mid)
    if not m:
        raise HTTPException(404, "厂家不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    await db.commit()
    await db.refresh(m)
    return m


@router.delete("/{mid}")
async def delete_manufacturer(mid: int, db: AsyncSession = Depends(get_db)):
    m = await db.get(Manufacturer, mid)
    if not m:
        raise HTTPException(404, "厂家不存在")
    await db.delete(m)
    await db.commit()
    return {"message": "已删除"}
