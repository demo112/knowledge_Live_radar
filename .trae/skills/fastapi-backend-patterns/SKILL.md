---
name: fastapi-backend-patterns
description: "[参考层] Python FastAPI + SQLAlchemy 2.0 异步后端开发模式，供 code-implementation 编写后端代码时参考。"
type: reference
applies_to: server
---

# FastAPI 后端模式

构建可扩展、可维护的 Python FastAPI 异步后端应用指南。适用于 AI Radar 项目。

---

## 激活方式

### 触发场景

- 编写 **FastAPI 路由或服务**
- 实现 **SQLAlchemy 异步数据库操作**
- 处理 **错误、重试、事务**
- 设计 **后端架构模式**

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心 | 后端、服务端、API、FastAPI、路由、服务 |
| 数据库 | SQLAlchemy、数据库、查询、事务、迁移 |
| 模式 | 异步、async、依赖注入、中间件 |

---

## 分层架构

```
backend/app/
├── routers/          # HTTP 请求处理（薄层，仅参数解析和响应包装）
├── services/         # 业务逻辑（核心层）
├── models/           # SQLAlchemy ORM 模型
├── schemas/          # Pydantic 请求/响应模型
├── database.py       # 数据库连接和会话管理
├── config.py         # 配置管理
└── main.py           # 应用入口
```

---

## Router 层模式

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.xxx import XxxCreate, XxxResponse, XxxListResponse
from app.services.xxx_service import XxxService

router = APIRouter(prefix="/api/v1/xxx", tags=["xxx"])

@router.post("/", response_model=XxxResponse, status_code=201)
async def create_item(
    data: XxxCreate,
    db: AsyncSession = Depends(get_db),
) -> XxxResponse:
    """创建资源 - Router 层只做参数接收和响应包装"""
    service = XxxService(db)
    item = await service.create(data)
    return XxxResponse(success=True, data=item)

@router.get("/", response_model=XxxListResponse)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> XxxListResponse:
    service = XxxService(db)
    items, total = await service.list(page=page, page_size=page_size)
    return XxxListResponse(
        success=True,
        data={"items": items, "total": total, "page": page, "page_size": page_size}
    )

@router.get("/{item_id}", response_model=XxxResponse)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> XxxResponse:
    service = XxxService(db)
    item = await service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="资源不存在")
    return XxxResponse(success=True, data=item)
```

---

## Service 层模式

```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.xxx import XxxModel
from app.schemas.xxx import XxxCreate, XxxUpdate
import logging

logger = logging.getLogger(__name__)

class XxxService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: XxxCreate) -> XxxModel:
        instance = XxxModel(**data.model_dump())
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        logger.info(f"Created xxx: {instance.id}")
        return instance

    async def get_by_id(self, item_id: int) -> XxxModel | None:
        result = await self.db.execute(
            select(XxxModel).where(XxxModel.id == item_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[XxxModel], int]:
        # 总数
        count_result = await self.db.execute(select(func.count(XxxModel.id)))
        total = count_result.scalar() or 0

        # 分页查询
        result = await self.db.execute(
            select(XxxModel)
            .order_by(XxxModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def update(self, item_id: int, data: XxxUpdate) -> XxxModel | None:
        instance = await self.get_by_id(item_id)
        if not instance:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, key, value)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def delete(self, item_id: int) -> bool:
        instance = await self.get_by_id(item_id)
        if not instance:
            return False
        await self.db.delete(instance)
        await self.db.commit()
        return True
```

---

## 异步事务模式

```python
async def complex_operation(self, data: ComplexInput) -> Result:
    """需要多步操作的事务"""
    try:
        # 步骤 1
        item = XxxModel(**data.model_dump())
        self.db.add(item)
        await self.db.flush()  # 获取 ID 但不提交

        # 步骤 2（依赖步骤 1 的 ID）
        related = RelatedModel(xxx_id=item.id, ...)
        self.db.add(related)

        # 一次性提交
        await self.db.commit()
        await self.db.refresh(item)
        return item
    except Exception as e:
        await self.db.rollback()
        logger.error(f"事务失败: {e}")
        raise
```

---

## 错误处理模式

```python
# app/exceptions.py
from fastapi import HTTPException

class AppException(HTTPException):
    """应用级异常基类"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})

class NotFoundException(AppException):
    def __init__(self, resource: str, id: int | str):
        super().__init__(
            code=f"ERR_{resource.upper()}_NOT_FOUND",
            message=f"{resource} {id} 不存在",
            status_code=404,
        )

class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__(code="ERR_VALIDATION", message=message, status_code=422)
```

---

## 依赖注入模式

```python
# 数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# 服务依赖
def get_xxx_service(db: AsyncSession = Depends(get_db)) -> XxxService:
    return XxxService(db)

# 在路由中使用
@router.get("/")
async def list_items(service: XxxService = Depends(get_xxx_service)):
    return await service.list()
```

---

## 后台任务模式

```python
from fastapi import BackgroundTasks

@router.post("/trigger-crawl")
async def trigger_crawl(
    source_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """触发异步抓取任务"""
    background_tasks.add_task(execute_crawl, source_id)
    return {"success": True, "message": "抓取任务已提交"}
```

---

## httpx 异步请求模式

```python
import httpx

async def fetch_url(url: str, timeout: float = 30.0) -> str | None:
    """异步 HTTP 请求（用于抓取和 AI 调用）"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.TimeoutException:
        logger.warning(f"请求超时: {url}")
        return None
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP 错误 {e.response.status_code}: {url}")
        return None
    except Exception as e:
        logger.error(f"请求失败: {url}, {e}")
        return None
```

---

## 重试模式（AI 服务调用）

```python
import asyncio

async def call_with_retry(
    func,
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs,
):
    """指数退避重试"""
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"重试 {attempt + 1}/{max_retries}，等待 {delay}s: {e}")
            await asyncio.sleep(delay)
```

---

## 最佳实践

1. **全部使用 async/await** - 不要在异步代码中混入同步阻塞调用
2. **SQLAlchemy 2.0 风格** - 使用 `select()` 而非 `query()`
3. **Router 层保持薄** - 仅做参数解析和响应包装，业务逻辑在 Service 层
4. **类型注解完整** - 函数参数和返回值都要有类型注解
5. **统一错误格式** - 使用自定义异常类，返回 `{code, message}` 格式
6. **日志规范** - 使用 `logging` 模块，关键操作必须记录日志
7. **事务安全** - 多步操作使用 flush + commit，异常时 rollback
8. **外部调用加超时** - httpx 请求必须设置 timeout
9. **AI 调用加重试** - 使用指数退避重试机制
