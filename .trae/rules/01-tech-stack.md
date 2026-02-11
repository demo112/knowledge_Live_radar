# 技术栈规范

## 前端

| 类型 | 技术 | 说明 |
|------|------|------|
| 框架 | Next.js | App Router，React 18+ |
| 语言 | TypeScript | 严格模式 |
| 样式 | Tailwind CSS | 原子化 CSS |
| 可视化 | ReactFlow | 金字塔/节点可视化 |
| 状态管理 | Zustand 或 React Context | 轻量级 |
| HTTP 客户端 | fetch / axios | API 调用 |

## 后端

| 类型 | 技术 | 说明 |
|------|------|------|
| 框架 | Python FastAPI | 异步高性能 |
| 语言 | Python 3.11+ | 类型注解 |
| ORM | SQLAlchemy 2.0 | 异步模式 |
| 数据库 | PostgreSQL（生产）/ SQLite（开发） | 双数据库支持 |
| 数据库迁移 | Alembic | 版本管理 |
| 任务调度 | APScheduler / Celery | 定时任务 |
| AI 服务 | 硅基流动 API | 大语言模型调用 |

## 通用

| 类型 | 技术 | 说明 |
|------|------|------|
| 容器化 | Docker + Docker Compose | 后续部署 |
| API 文档 | OpenAPI / Swagger | FastAPI 自动生成 |
| 包管理（前端） | pnpm | 推荐 |
| 包管理（后端） | pip / poetry | Python 依赖管理 |
