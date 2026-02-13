# Design: 知识金字塔核心管理增强

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 金字塔全生命周期 | API: `POST /pyramids`, `DELETE /pyramids/{id}`, `GET /pyramids` (增强返回健康度) |
| Story 2: 拆分节点 | API: `POST /pyramids/{id}/nodes/split`, Service: `PyramidService.split_node` |
| Story 2: 合并节点 | API: `POST /pyramids/{id}/nodes/merge`, Service: `PyramidService.merge_nodes` |
| Story 2: 跨金字塔关联 | API: `POST /nodes/{id}/links`, Model: `NodeRelation` |
| Story 3: 健康度计算 | Service: `HealthEvaluator`, API: `GET /pyramids/{id}/health` |
| Story 3: 可视化 | Service: `VisualizationService`, API: `GET /pyramids/{id}/visualization` |

## 数据模型

### 1. 节点关联表 (新增)

```python
# backend/app/models/node_relation.py

from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid

class NodeRelation(Base):
    __tablename__ = "node_relations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramid_nodes.id"), nullable=False)
    target_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramid_nodes.id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(50), default="related") # related, prerequisite, etc.
    
    __table_args__ = (
        UniqueConstraint('source_node_id', 'target_node_id', 'relation_type', name='uq_node_relation'),
    )
```

### 2. 金字塔模型 (修改)

无需修改 Schema，但需确认 `PyramidNode` 是否包含 `updated_at`。如果 `Base` 中没有，需添加。假设 `Base` 中无，则需在 `PyramidNode` 添加 `updated_at` 以支持“更新活跃度”计算。

## API 定义

### 1. 拆分节点

**POST /api/v1/pyramids/{id}/nodes/split**

将一个节点拆分为多个子节点。

**Request:**
```python
class NodeSplitRequest(BaseModel):
    source_node_id: UUID
    children_names: List[str] # 新子节点名称列表
    distribute_strategy: str = "manual" # manual, auto (future)
```

### 2. 合并节点

**POST /api/v1/pyramids/{id}/nodes/merge**

将多个节点合并为一个新节点。

**Request:**
```python
class NodeMergeRequest(BaseModel):
    source_node_ids: List[UUID]
    target_name: str
    target_description: Optional[str] = None
```

### 3. 关联节点

**POST /api/v1/nodes/{id}/links**

建立节点间关联。

**Request:**
```python
class NodeLinkRequest(BaseModel):
    target_node_id: UUID
    relation_type: str = "related"
```

### 4. 获取可视化数据

**GET /api/v1/pyramids/{id}/visualization**

返回 ReactFlow 格式的数据。

**Response:**
```python
class VisualizationData(BaseModel):
    nodes: List[VisNode]
    edges: List[VisEdge]

class VisNode(BaseModel):
    id: str
    data: Dict[str, Any] # label, health_score, content_count, etc.
    position: Dict[str, float]
    type: str = "default"

class VisEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str = "default"
```

### 5. 获取健康度详情

**GET /api/v1/pyramids/{id}/health**

触发并返回健康度评估。

**Response:**
```python
class HealthScore(BaseModel):
    total_score: int
    metrics: Dict[str, int] # depth_balance, coverage, activity
    suggestions: List[str]
```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| backend/app/models/node_relation.py | 新增 | NodeRelation 模型 |
| backend/app/schemas/node_ops.py | 新增 | 拆分/合并/关联的 Request Schemas |
| backend/app/schemas/visualization.py | 新增 | 可视化响应 Schemas |
| backend/app/schemas/health.py | 新增 | 健康度响应 Schemas |
| backend/app/services/pyramid_service.py | 修改 | 添加 split_node, merge_nodes 方法 |
| backend/app/services/node_service.py | 新增 | 处理节点关联逻辑 (如果独立的话) |
| backend/app/services/visualization_service.py | 新增 | 生成可视化数据 |
| backend/app/services/health_evaluator.py | 新增 | 健康度计算逻辑 |
| backend/app/routers/pyramids.py | 修改 | 添加 visualization, health, split, merge 路由 |
| backend/app/routers/nodes.py | 修改 | 添加 link 路由 |

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 删除节点 | 拆分/合并逻辑复杂，可能产生孤儿节点 | 中 |
| 节点查询 | 需关联查询 NodeRelation | 低 |

## 决策点

- [ ] **内容迁移策略**：拆分节点时，原有内容如何处理？
    - 方案 A：全部保留在原节点（原节点变为父节点）。
    - 方案 B：必须指定分配给哪个子节点。
    - **推荐方案 A**（实现简单，数据安全）。
- [ ] **可视化布局**：后端计算位置还是前端计算？
    - 方案 A：后端计算（使用 graphviz 或类似库）。
    - 方案 B：前端计算（ReactFlow 自带或 dagre）。
    - **推荐方案 B**（后端只返回层级结构，前端负责布局渲染）。

## 风险点

- **健康度计算性能**：如果金字塔很大，实时计算可能慢。
    - **应对**：添加 1-5 分钟的缓存。
- **并发修改**：拆分/合并时如果有其他写入。
    - **应对**：使用数据库事务。

