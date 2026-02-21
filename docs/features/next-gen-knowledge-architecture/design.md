# Design: Next-Gen Knowledge Architecture

## 1. 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 基于认知模型的三阶段分类 | Service: `CognitiveModelService.classify_content()` (向量粗筛→规则精筛→LLM消歧) |
| Story 2: 认知模型的自动生成与进化 | Service: `CognitiveModelService.generate_model()`, `evolve_model()` |
| Story 3: 节点跨簇存在 | Model: `ClusterNodeMembership` (多对多关系) |
| Story 4: AI 自动发现簇 | Service: `KnowledgeDiscoveryService.discover_clusters()` |
| Story 5: 关系自动发现 | Service: `KnowledgeDiscoveryService.discover_relations()` |
| Story 6: 图谱视图与簇视图 | API: `GET /api/v1/knowledge/graph`, `GET /api/v1/knowledge/clusters` |
| Story 7: 一句话创建知识结构 | API: `POST /api/v1/intent/create` (调用 LLM 生成结构预览) |
| Story 8: 对话式持续调整 | API: `POST /api/v1/intent/refine` |

## 2. 数据模型设计

### 2.1 新增模型 (`backend/app/models/knowledge.py`)

```python
import uuid
from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base

class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    node_type: Mapped[str] = mapped_column(String(50), default="concept") # concept, technology, tool, method, organization
    
    # AI 认知模型
    ai_model: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # 关联 Concept
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("concepts.id"), nullable=True)
    
    # 统计与健康
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    content_count: Mapped[int] = mapped_column(Integer, default=0)
    last_content_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 元数据
    status: Mapped[str] = mapped_column(String(20), default="active") # active, archived
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    # outgoing_relations, incoming_relations, clusters defined below or via back_populates

class KnowledgeCluster(Base):
    __tablename__ = "knowledge_clusters"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cluster_type: Mapped[str] = mapped_column(String(20), default="manual") # manual, ai_generated, intent_created
    center_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("knowledge_nodes.id"), nullable=True)
    
    # 簇级 AI 认知模型
    ai_model: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # 簇特征
    metadata_info: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True) # metadata is reserved
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    node_count: Mapped[int] = mapped_column(Integer, default=0)
    
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ClusterNodeMembership(Base):
    __tablename__ = "cluster_node_memberships"

    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_clusters.id", ondelete="CASCADE"), primary_key=True)
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), default="member") # center, member, peripheral
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class NodeRelation(Base):
    __tablename__ = "node_relations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id", ondelete="CASCADE"))
    target_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_nodes.id", ondelete="CASCADE"))
    
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    evidence: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    discovered_by: Mapped[str] = mapped_column(String(20), default="manual")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### 2.2 修改模型

#### `backend/app/models/content.py`
- `ContentNodeRelation`: 将 `node_id` FK 从 `pyramid_nodes.id` 改为 `knowledge_nodes.id`。

#### `backend/app/models/source.py`
- `SourceNodeRelation`: 将 `node_id` FK 从 `pyramid_nodes.id` 改为 `knowledge_nodes.id`。

## 3. API 定义

### 3.1 意图式创建 (Intent-Driven Creation)

**POST /api/v1/intent/create**
- **描述**: 提交自然语言意图，生成知识结构预览
- **Request**: `{ intent: string, context_cluster_id?: string }`
- **Response**: `{ preview: KnowledgeGraphStructure, suggestion_id: string }`

**POST /api/v1/intent/confirm**
- **描述**: 确认创建知识结构
- **Request**: `{ suggestion_id: string, modifications?: KnowledgeGraphStructure }`
- **Response**: `{ cluster_id: string, node_ids: string[] }`

**POST /api/v1/intent/refine**
- **描述**: 对话式调整建议结构
- **Request**: `{ suggestion_id: string, instruction: string }`
- **Response**: `{ preview: KnowledgeGraphStructure, suggestion_id: string }`

### 3.2 知识图谱管理 (Knowledge Graph Management)

**GET /api/v1/knowledge/clusters**
- **描述**: 获取簇列表
- **Query**: `page, page_size, keyword`

**GET /api/v1/knowledge/clusters/{id}**
- **描述**: 获取簇详情（含中心节点、认知模型摘要）

**GET /api/v1/knowledge/clusters/{id}/graph**
- **描述**: 获取簇内的图谱结构（节点+边）

**POST /api/v1/knowledge/nodes**
- **描述**: 创建节点

**GET /api/v1/knowledge/nodes/{id}**
- **描述**: 获取节点详情（含认知模型）

**POST /api/v1/knowledge/relations**
- **描述**: 创建节点间关系

## 4. 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/app/models/knowledge.py` | 新增 | KnowledgeNode, KnowledgeCluster 等模型定义 |
| `backend/app/models/pyramid.py` | 标记废弃 | 添加废弃注释，后续删除 |
| `backend/app/models/content.py` | 修改 | ContentNodeRelation FK 指向 knowledge_nodes |
| `backend/app/models/source.py` | 修改 | SourceNodeRelation FK 指向 knowledge_nodes |
| `backend/app/schemas/knowledge.py` | 新增 | Pydantic Schemas (Node, Cluster, Relation) |
| `backend/app/schemas/intent.py` | 新增 | IntentRequest, PreviewResponse 等 |
| `backend/app/services/knowledge_service.py` | 新增 | 节点和簇的 CRUD 逻辑 |
| `backend/app/services/cognitive_service.py` | 新增 | 认知模型生成、分类、进化逻辑 |
| `backend/app/services/intent_service.py` | 新增 | 意图理解、结构生成逻辑 |
| `backend/app/routers/knowledge.py` | 新增 | 知识图谱相关 API 路由 |
| `backend/app/routers/intent.py` | 新增 | 意图相关 API 路由 |
| `backend/alembic/versions/xxxx_migration.py` | 新增 | 数据库迁移脚本 |
| `frontend/src/app/(dashboard)/knowledge/page.tsx` | 新增 | 知识图谱主页 |
| `frontend/src/app/(dashboard)/knowledge/intent/page.tsx` | 新增 | 意图式创建页面 |
| `frontend/src/components/knowledge/GraphView.tsx` | 新增 | 图谱可视化组件 |
| `frontend/src/lib/api/knowledge.ts` | 新增 | 前端 API 客户端 |

## 5. 影响分析与迁移策略

### 5.1 影响范围
- **核心数据结构变更**: `Pyramid` 体系完全废弃，影响所有基于 Pyramid 的功能（如信息流分类、金字塔视图）。
- **内容关联**: 现有内容的关联关系需要迁移到新节点。
- **信息源关联**: 现有信息源的关联关系需要迁移。

### 5.2 迁移策略 (Migration Strategy)
1.  **Schema 迁移**: 创建新表 `knowledge_*`。
2.  **数据迁移 (Script)**:
    - 遍历所有 `Pyramid` -> 创建对应的 `KnowledgeCluster`。
    - 遍历所有 `PyramidNode` -> 创建对应的 `KnowledgeNode`。
    - 建立 `ClusterNodeMembership` 关系。
    - 转换 `PyramidNode.parent_id` 关系为 `NodeRelation` (type='is_part_of')。
    - 迁移 `content_node_relations` 数据：将 old `node_id` 映射到 new `node_id`。
    - 迁移 `source_node_relations` 数据。
3.  **代码切换**:
    - 更新 `ContentItem` 和 `InformationSource` 的 ORM 关联。
    - 切换 API 路由到新的 `knowledge` 路由。
4.  **清理**:
    - 验证无误后，删除旧表和旧代码。

### 5.3 风险点
- **数据一致性**: 迁移过程中可能会有数据丢失，需先备份。
- **性能**: 图谱查询比树状查询复杂，需优化索引和查询语句。
- **认知模型生成**: 这是一个耗时过程，迁移初期节点可能只有空模型，需后台异步生成。

## 6. 技术决策

- **图数据库 vs 关系型数据库**:
    - 决策: 继续使用 PostgreSQL。
    - 理由: 现有架构基于 PG，PG 的递归查询和 JSONB 能力足以支撑目前的图谱规模（万级节点），引入 Neo4j 等专用图数据库成本过高。
- **可视化库**:
    - 决策: 前端使用 `react-force-graph` 或 `ReactFlow` (继续使用或切换)。
    - 理由: 需求提到"图谱视图"，`react-force-graph` 更适合展示网络拓扑，`ReactFlow` 更适合流程或层级图。建议引入 `react-force-graph` 用于图谱展示，保留 `ReactFlow` 用于特定的结构化展示。
