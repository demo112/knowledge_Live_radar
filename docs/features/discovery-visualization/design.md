# Design: 发现流程可视化 (Discovery Process Visualization)

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 全流程实时可视化 | **Backend**: SSE (Server-Sent Events) 流式推送<br>**Frontend**: `DiscoveryProgress` 组件接收事件并渲染流程图 |
| AC1: 阶段展示 | **Schema**: 定义 `DiscoveryStage` 枚举 (extract, search, filter, proposal)<br>**UI**: 步骤条 (Steps) 组件 |
| AC2: 细粒度进度反馈 | **Event**: `progress` 事件包含当前关键词和搜索结果数<br>**UI**: 实时日志列表 |
| AC3: 过滤逻辑展示 | **Event**: `log` 事件包含过滤原因 (duplicate, exists)<br>**UI**: 统计面板 |
| AC4: 实时流式响应 | **API**: `GET /api/v1/sources/discover/stream`<br>**Lib**: `@microsoft/fetch-event-source` (需安装) |

## 数据模型 (Schema)

```python
# backend/app/schemas/source.py

from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any, Dict, List

class DiscoveryStage(str, Enum):
    EXTRACT = "extract"   # 关键词提取
    SEARCH = "search"     # 网络搜索
    FILTER = "filter"     # 结果过滤
    PROPOSAL = "proposal" # 提案生成
    FINISH = "finish"     # 完成

class DiscoveryStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class DiscoveryEvent(BaseModel):
    event: str  # stage_update, log, progress, result, error
    data: Dict[str, Any]
```

## API 定义

### GET /api/v1/sources/discover/stream

启动发现任务并建立 SSE 连接。

**Query Parameters:**
- `pyramid_id`: UUID (Optional) - 指定金字塔 ID
- `token`: String (Optional) - 用于认证 (如果 EventSource 不支持 Header)

**Response:** `text/event-stream`

**Events:**

1.  **stage_update**
    ```json
    {
      "event": "stage_update",
      "data": {
        "stage": "search",
        "status": "running",
        "label": "正在执行搜索..."
      }
    }
    ```

2.  **log**
    ```json
    {
      "event": "log",
      "data": {
        "message": "Searching for keyword: 'Python'",
        "level": "info",
        "timestamp": "2023-10-01T12:00:00Z"
      }
    }
    ```

3.  **progress**
    ```json
    {
      "event": "progress",
      "data": {
        "current": 2,
        "total": 5,
        "percentage": 40,
        "message": "Processing 2/5 keywords"
      }
    }
    ```

4.  **result**
    ```json
    {
      "event": "result",
      "data": {
        "count": 5,
        "summary": "Found 5 new sources"
      }
    }
    ```

5.  **error**
    ```json
    {
      "event": "error",
      "data": {
        "message": "Search engine unavailable"
      }
    }
    ```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/app/schemas/source.py` | 修改 | 新增 `DiscoveryStage`, `DiscoveryEvent` 等 Schema |
| `backend/app/services/source_discovery.py` | 修改 | 新增 `discover_stream` 方法 (Async Generator)，重构原有逻辑以支持 yield |
| `backend/app/routers/sources.py` | 修改 | 新增 `GET /discover/stream` Endpoint，使用 `StreamingResponse` |
| `frontend/src/components/sources/DiscoveryProgress.tsx` | 新增 | SSE 客户端组件，展示进度和日志 |
| `frontend/src/app/[locale]/(dashboard)/sources/page.tsx` | 修改 | 集成 `DiscoveryProgress` 组件，替换原有 alert 逻辑 |
| `frontend/package.json` | 修改 | 添加 `@microsoft/fetch-event-source` 依赖 |

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| **通信协议** | SSE (Server-Sent Events) | 比 WebSocket 轻量，适合单向进度推送，且符合 HTTP 标准 |
| **前端库** | `@microsoft/fetch-event-source` | 支持自定义 Headers (Auth)，比原生 EventSource 更灵活 |
| **后端实现** | `StreamingResponse` + Generator | FastAPI 标准做法，不阻塞主线程 (需注意 yield 处的异步处理) |
| **状态管理** | 组件内 State | 进度状态仅在当前组件生命周期有效，无需全局 Store |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| **搜索超时** | 搜索过程可能较慢，导致连接超时 | 设置较长的 timeout，后端定期发送 keep-alive 注释 (如 `: keep-alive\n\n`) |
| **并发限制** | 大量用户同时搜索可能触发 DuckDuckGo 限制 | 暂时仅限管理员使用，后端增加简单的速率限制或队列 (MVP暂不实现队列) |
| **连接中断** | 网络波动导致 SSE 断开 | 前端实现自动重连，后端支持断点续传 (MVP 暂不支持断点续传，失败需重试) |

## 需要人决策

- [ ] 是否允许普通用户触发发现任务？(目前假设有权限控制)
- [ ] 搜索失败是否自动重试？(目前设计为手动重试)
