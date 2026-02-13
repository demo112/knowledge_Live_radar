# 技术栈规范

## 前端

| 类型 | 技术 | 版本/说明 |
|------|------|-----------|
| 框架 | Next.js | v16, App Router, React 19 |
| 语言 | TypeScript | 严格模式 |
| 样式 | Tailwind CSS | v4+ |
| 可视化 | ReactFlow | 金字塔/节点可视化 |
| 状态管理 | Zustand 或 React Context | 轻量级 |
| HTTP 客户端 | fetch | 内置 API 调用 |
| 包管理 | pnpm | 推荐 |

## 后端

| 类型 | 技术 | 版本/说明 |
|------|------|-----------|
| 框架 | FastAPI | v0.115+, 异步优先 |
| 语言 | Python | 3.12+, 类型注解必须 |
| ORM | SQLAlchemy | 2.0, 异步模式 (AsyncSession) |
| 数据库 | PostgreSQL / SQLite | asyncpg(生产) / aiosqlite(开发) |
| 数据库迁移 | Alembic | 版本管理 |
| 任务调度 | APScheduler | 定时抓取、健康检查 |
| AI 服务 | 硅基流动 API | httpx 异步调用 |
| HTTP 客户端 | httpx | 异步请求（抓取、AI 调用） |
| 包管理 | pip / poetry | Python 依赖管理 |

## 后端编码规范

### 异步模式（核心要求）

```python
# ✅ 正确：使用 async/await + AsyncSession
async def get_items(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item).where(Item.active == True))
    return list(result.scalars().all())

# ❌ 错误：使用同步 Session
def get_items(db: Session) -> list[Item]:
    return db.query(Item).filter(Item.active == True).all()
```

### SQLAlchemy 2.0 风格

```python
# ✅ 正确：select() 语句风格
from sqlalchemy import select
stmt = select(Model).where(Model.id == id)
result = await db.execute(stmt)

# ❌ 错误：旧式 query() 风格
db.query(Model).filter(Model.id == id).first()
```

### 服务层模式

```python
# 标准服务类结构
class XxxService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: XxxCreate) -> XxxModel:
        instance = XxxModel(**data.model_dump())
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
```

### 路由层模式

```python
# 标准路由结构
router = APIRouter(prefix="/api/v1/xxx", tags=["xxx"])

@router.get("/", response_model=PaginatedResponse)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = XxxService(db)
    return await service.list(page=page, page_size=page_size)
```

## 通用

| 类型 | 技术 | 说明 |
|------|------|------|
| 容器化 | Docker + Docker Compose | 后续部署 |
| API 文档 | OpenAPI / Swagger | FastAPI 自动生成 |
| 代码格式化 | Ruff (Python) / Prettier (TS) | 统一风格 |
| 类型检查 | mypy (Python) / tsc (TS) | 类型安全 |
