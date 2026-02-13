# 技术设计：AI 辅助金字塔进化 (Pyramid Evolution)

## 1. 概述

本设计旨在实现知识金字塔的自动化进化能力，包括内容的自动归类、概念的聚类发现以及节点结构的动态调整。核心目标是减少人工维护成本，确保知识结构的实时性和准确性。

## 2. 核心功能映射

| 需求 | 实现方案 | 涉及模块 |
|------|----------|----------|
| AC1: 基于概念匹配的归类 | 使用语义相似度/精确匹配将 Content 关联到 Node | EvolutionEngine, NodeService |
| AC2: 概念聚类发现 | 定期分析未归类内容，发现新概念簇 | EvolutionEngine |
| AC3: 结构调整建议 | 基于聚类结果生成节点拆分/合并提案 | EvolutionEngine, ApprovalService |
| 数据同步与一致性 | 事务性关联操作，实时更新统计信息 | NodeService, Database |

## 3. 数据模型设计

### 3.1 扩展 PyramidNode

在 `backend/app/models/pyramid.py` 中，`PyramidNode` 需要增加统计字段，用于快速展示和热度分析。

```python
class PyramidNode(Base):
    # ... 现有字段 ...
    
    # 新增字段
    content_count: Mapped[int] = mapped_column(Integer, default=0) # 关联内容数量
    last_content_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True) # 最新内容时间
```

### 3.2 确认 ContentNodeRelation

`backend/app/models/content.py` 中已定义的 `ContentNodeRelation` 能够满足需求，但需确保外键约束和索引优化。

```python
class ContentNodeRelation(Base):
    __tablename__ = "content_node_relations"
    
    # 复合主键确保唯一性
    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), primary_key=True)
    node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramid_nodes.id", ondelete="CASCADE"), primary_key=True)
    
    confidence: Mapped[float] = mapped_column(Float, default=1.0) # AI 置信度
    source: Mapped[str] = mapped_column(String(20), default="manual") # manual, ai_auto, ai_confirm
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
```

## 4. 核心服务设计

### 4.1 NodeService 扩展 (数据同步核心)

负责处理节点与内容的关联，并维护数据一致性。

```python
class NodeService:
    async def link_content(self, node_id: UUID, content_id: UUID, source: str = "manual", confidence: float = 1.0):
        """
        关联内容到节点，并同步更新统计信息。
        使用数据库事务确保原子性。
        """
        async with self.db.begin():
            # 1. 检查是否存在
            # 2. 创建关联记录
            # 3. 更新节点 content_count + 1
            # 4. 更新节点 last_content_at
            pass

    async def unlink_content(self, node_id: UUID, content_id: UUID):
        """
        解除关联，并同步更新统计信息。
        """
        async with self.db.begin():
            # 1. 删除关联记录
            # 2. 更新节点 content_count - 1
            pass
```

### 4.2 VectorService (向量服务)

负责文本向量化和相似度检索。使用 ChromaDB 作为向量存储。

```python
class VectorService:
    def __init__(self):
        # 初始化 ChromaDB 客户端 (PersistentClient)
        pass

    async def upsert_content_vector(self, content_id: UUID, text: str, metadata: dict):
        """
        将内容向量化并存入 ChromaDB。
        """
        pass
        
    async def upsert_node_vector(self, node_id: UUID, text: str, metadata: dict):
        """
        将节点(名称+描述)向量化并存入 ChromaDB。
        """
        pass

    async def search_similar_nodes(self, query_text: str, limit: int = 5, threshold: float = 0.8) -> List[dict]:
        """
        根据文本搜索相似节点。
        """
        pass
```

### 4.3 EvolutionEngine (进化引擎)

负责执行 AI 任务。

```python
class EvolutionEngine:
    async def auto_classify_content(self, content_item: ContentItem):
        """
        自动归类单个内容。
        1. 获取内容 concepts / summary
        2. 调用 VectorService.search_similar_nodes
        3. 若相似度 > 0.8 (配置阈值)，调用 NodeService.link_content
        """
        pass
        
    async def discover_clusters(self, pyramid_id: UUID):
        """
        发现新概念聚类。
        1. 获取该金字塔下未归类的内容
        2. 使用聚类算法 (如 DBSCAN on Embeddings) 或 LLM 分析
        3. 生成结构调整提案 (Approval)
        """
        pass
```

## 5. API 设计

### 5.1 进化操作

- `POST /api/v1/evolution/classify`: 触发全量或增量自动归类任务。
- `POST /api/v1/evolution/clusters/{pyramid_id}`: 触发聚类发现任务。

### 5.2 节点内容管理

- `GET /api/v1/nodes/{id}/contents`: 获取节点关联的内容列表。
- `POST /api/v1/nodes/{id}/contents`: 手动关联内容。
- `DELETE /api/v1/nodes/{id}/contents/{content_id}`: 解除关联。

## 6. 数据流与同步机制

1.  **AI 归类**:
    - `CrawlService` -> `ContentItem` (Stored) -> `VectorService.upsert` -> `EvolutionEngine.auto_classify_content` -> `NodeService.link_content` -> DB Update (Relation + Node Stats).

2.  **人工干预**:
    - User UI -> `API` -> `NodeService.link/unlink` -> DB Update.
    - 节点变更 (Create/Update) -> `VectorService.upsert_node_vector` (同步更新向量库).

3.  **一致性保障**:
    - **事务**: 所有的关联/解绑操作必须在事务中完成。
    - **级联删除**: 数据库外键配置 `ON DELETE CASCADE`。
    - **向量同步**: 节点或内容更新时，需异步更新向量库。

## 7. 文件变更清单

- `backend/requirements.txt`: 新增 `chromadb`, `sentence-transformers` (可选，或使用 API 向量化)。
- `backend/app/models/pyramid.py`: 新增统计字段。
- `backend/app/models/content.py`: 优化 Relation 模型。
- `backend/app/services/vector_service.py`: 新建，封装 ChromaDB。
- `backend/app/services/node_service.py`: 新增内容关联逻辑。
- `backend/app/services/evolution_engine.py`: 新建，实现归类和聚类逻辑。
- `backend/app/routers/evolution.py`: 新建 API 路由。
- `backend/app/routers/nodes.py`: 新增内容管理接口。

## 8. 配置项

- `VECTOR_DB_PATH`: 向量数据库持久化路径。
- `AUTO_CLASSIFY_THRESHOLD`: 自动归类阈值，默认 **0.8**。
