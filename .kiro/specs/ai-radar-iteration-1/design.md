# 设计文档 - 迭代 1：骨架搭建

## 概述

本设计文档描述 AI Radar 系统迭代 1 的技术实现方案。迭代 1 的目标是搭建系统骨架，包括：
- 前后端基础架构
- 核心数据模型（金字塔、节点、信息源、内容）
- 基本 UI 框架（金字塔可视化、信息流、管理界面骨架）
- 数据库设计与基础 API

本迭代聚焦于需求 1-3（金字塔管理）、需求 4（信息源基础管理）、需求 22-24（基础 UI）、需求 27（数据持久化）、需求 31（API 接口）、需求 38（金字塔模板）的基础实现。

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (Next.js)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  金字塔视图   │  │   信息流视图  │  │   管理视图   │          │
│  │  (ReactFlow) │  │  (列表组件)   │  │  (表单组件)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                           │                                      │
│                    ┌──────┴──────┐                              │
│                    │  API Client │                              │
│                    └──────┬──────┘                              │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────┼─────────────────────────────────────┐
│                         后端 (FastAPI)                           │
│                    ┌──────┴──────┐                              │
│                    │  API Router │                              │
│                    └──────┬──────┘                              │
│         ┌────────────────┼────────────────┐                     │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐             │
│  │ Pyramid Svc │  │  Source Svc │  │ Content Svc │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         └────────────────┼────────────────┘                     │
│                    ┌──────┴──────┐                              │
│                    │  Repository │                              │
│                    └──────┬──────┘                              │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │   Database    │
                    │ (SQLite/PG)   │
                    └───────────────┘
```

### 目录结构

```
ai-radar/
├── frontend/                    # Next.js 前端
│   ├── src/
│   │   ├── app/                # App Router 页面
│   │   │   ├── page.tsx        # 首页（信息流）
│   │   │   ├── pyramid/        # 金字塔页面
│   │   │   ├── sources/        # 信息源管理
│   │   │   └── layout.tsx      # 布局
│   │   ├── components/         # 组件
│   │   │   ├── pyramid/        # 金字塔相关组件
│   │   │   ├── feed/           # 信息流组件
│   │   │   ├── sources/        # 信息源组件
│   │   │   └── ui/             # 通用 UI 组件
│   │   ├── lib/                # 工具库
│   │   │   ├── api.ts          # API 客户端
│   │   │   └── types.ts        # 类型定义
│   │   └── styles/             # 样式
│   ├── package.json
│   └── tailwind.config.js
│
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 应用入口
│   │   ├── api/                # API 路由
│   │   │   ├── pyramids.py     # 金字塔 API
│   │   │   ├── nodes.py        # 节点 API
│   │   │   ├── sources.py      # 信息源 API
│   │   │   └── contents.py     # 内容 API
│   │   ├── models/             # 数据模型
│   │   │   ├── pyramid.py
│   │   │   ├── node.py
│   │   │   ├── source.py
│   │   │   └── content.py
│   │   ├── schemas/            # Pydantic 模式
│   │   │   ├── pyramid.py
│   │   │   ├── node.py
│   │   │   ├── source.py
│   │   │   └── content.py
│   │   ├── services/           # 业务逻辑
│   │   │   ├── pyramid_service.py
│   │   │   ├── node_service.py
│   │   │   └── source_service.py
│   │   ├── repositories/       # 数据访问
│   │   │   └── base.py
│   │   ├── db/                 # 数据库
│   │   │   ├── database.py     # 数据库连接
│   │   │   └── migrations/     # 迁移脚本
│   │   └── config.py           # 配置
│   ├── requirements.txt
│   └── alembic.ini
│
└── README.md
```

## 组件与接口

### 后端组件

#### 1. 数据模型 (SQLAlchemy Models)

```python
# models/pyramid.py
class Pyramid(Base):
    __tablename__ = "pyramids"
    
    id: str                    # UUID
    name: str                  # 金字塔名称
    description: str           # 描述
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
    is_deleted: bool           # 软删除标记

# models/node.py
class PyramidNode(Base):
    __tablename__ = "pyramid_nodes"
    
    id: str                    # UUID
    pyramid_id: str            # 所属金字塔 ID
    parent_id: str | None      # 父节点 ID（根节点为 None）
    name: str                  # 节点名称
    description: str           # 描述
    level: int                 # 层级深度
    sort_order: int            # 同级排序
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

# models/source.py
class InformationSource(Base):
    __tablename__ = "information_sources"
    
    id: str                    # UUID
    name: str                  # 信息源名称
    source_type: str           # 类型: rss/api/web/user
    config: dict               # JSON 配置（URL、选择器等）
    status: str                # 状态: discovered/verified/active/monitoring/adjusting/retired
    health_score: int          # 健康度 0-100
    created_at: datetime
    updated_at: datetime
    last_crawled_at: datetime | None
    is_deleted: bool

# models/source_node_mapping.py
class SourceNodeMapping(Base):
    __tablename__ = "source_node_mappings"
    
    id: str
    source_id: str             # 信息源 ID
    node_id: str               # 节点 ID
    weight: float              # 关联权重 0-1
    created_at: datetime

# models/content.py
class ContentItem(Base):
    __tablename__ = "content_items"
    
    id: str                    # UUID
    source_id: str | None      # 来源信息源 ID
    title: str                 # 标题
    url: str                   # 原文 URL
    summary: str | None        # AI 摘要
    raw_content: str | None    # 原始内容
    tags: list[str]            # 标签
    quality_score: int | None  # 质量分数 0-100
    validation_status: str     # 校验状态: pending/passed/failed
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

# models/content_node_mapping.py
class ContentNodeMapping(Base):
    __tablename__ = "content_node_mappings"
    
    id: str
    content_id: str            # 内容 ID
    node_id: str               # 节点 ID
    confidence: float          # 分类置信度 0-1
    is_primary: bool           # 是否主分类
    created_at: datetime
```

#### 2. API 模式 (Pydantic Schemas)

```python
# schemas/pyramid.py
class PyramidCreate(BaseModel):
    name: str
    description: str = ""
    template: str | None = None  # 模板名称

class PyramidUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class PyramidResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    node_count: int
    content_count: int
    health_score: int | None

class PyramidDetailResponse(PyramidResponse):
    nodes: list["NodeResponse"]

# schemas/node.py
class NodeCreate(BaseModel):
    pyramid_id: str
    parent_id: str | None = None
    name: str
    description: str = ""
    sort_order: int = 0

class NodeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sort_order: int | None = None

class NodeMove(BaseModel):
    new_parent_id: str | None

class NodeResponse(BaseModel):
    id: str
    pyramid_id: str
    parent_id: str | None
    name: str
    description: str
    level: int
    sort_order: int
    children: list["NodeResponse"] = []
    content_count: int
    source_count: int

# schemas/source.py
class SourceCreate(BaseModel):
    name: str
    source_type: Literal["rss", "api", "web", "user"]
    config: dict
    node_ids: list[str] = []

class SourceUpdate(BaseModel):
    name: str | None = None
    config: dict | None = None
    status: str | None = None

class SourceResponse(BaseModel):
    id: str
    name: str
    source_type: str
    config: dict
    status: str
    health_score: int
    last_crawled_at: datetime | None
    created_at: datetime
    node_ids: list[str]

# schemas/content.py
class ContentResponse(BaseModel):
    id: str
    title: str
    url: str
    summary: str | None
    tags: list[str]
    quality_score: int | None
    validation_status: str
    source_name: str | None
    published_at: datetime | None
    created_at: datetime
    node_ids: list[str]
```

#### 3. 服务层接口

```python
# services/pyramid_service.py
class PyramidService:
    async def create_pyramid(self, data: PyramidCreate) -> Pyramid:
        """创建金字塔，如果指定模板则基于模板创建"""
        pass
    
    async def get_pyramid(self, pyramid_id: str) -> Pyramid | None:
        """获取金字塔详情"""
        pass
    
    async def list_pyramids(self) -> list[Pyramid]:
        """获取所有金字塔列表"""
        pass
    
    async def update_pyramid(self, pyramid_id: str, data: PyramidUpdate) -> Pyramid:
        """更新金字塔基本信息"""
        pass
    
    async def delete_pyramid(self, pyramid_id: str) -> None:
        """软删除金字塔及其所有节点"""
        pass
    
    async def get_pyramid_visualization(self, pyramid_id: str) -> dict:
        """获取金字塔可视化数据"""
        pass
    
    async def calculate_health_score(self, pyramid_id: str) -> int:
        """计算金字塔健康度"""
        pass

# services/node_service.py
class NodeService:
    async def create_node(self, data: NodeCreate) -> PyramidNode:
        """创建节点"""
        pass
    
    async def get_node(self, node_id: str) -> PyramidNode | None:
        """获取节点详情"""
        pass
    
    async def get_node_tree(self, pyramid_id: str) -> list[PyramidNode]:
        """获取金字塔的完整节点树"""
        pass
    
    async def update_node(self, node_id: str, data: NodeUpdate) -> PyramidNode:
        """更新节点信息"""
        pass
    
    async def move_node(self, node_id: str, data: NodeMove) -> PyramidNode:
        """移动节点到新的父节点"""
        pass
    
    async def delete_node(self, node_id: str) -> None:
        """删除节点及其子节点"""
        pass
    
    async def get_node_contents(self, node_id: str, page: int, size: int) -> list[ContentItem]:
        """获取节点下的内容列表"""
        pass

# services/source_service.py
class SourceService:
    async def create_source(self, data: SourceCreate) -> InformationSource:
        """创建信息源"""
        pass
    
    async def get_source(self, source_id: str) -> InformationSource | None:
        """获取信息源详情"""
        pass
    
    async def list_sources(self, status: str | None = None) -> list[InformationSource]:
        """获取信息源列表"""
        pass
    
    async def update_source(self, source_id: str, data: SourceUpdate) -> InformationSource:
        """更新信息源"""
        pass
    
    async def delete_source(self, source_id: str) -> None:
        """删除信息源"""
        pass
    
    async def link_source_to_nodes(self, source_id: str, node_ids: list[str]) -> None:
        """关联信息源到节点"""
        pass
    
    async def test_source(self, source_id: str) -> dict:
        """测试信息源抓取"""
        pass
```

#### 4. API 路由

```python
# api/pyramids.py
router = APIRouter(prefix="/api/pyramids", tags=["pyramids"])

@router.post("/", response_model=PyramidResponse)
async def create_pyramid(data: PyramidCreate): ...

@router.get("/", response_model=list[PyramidResponse])
async def list_pyramids(): ...

@router.get("/{pyramid_id}", response_model=PyramidDetailResponse)
async def get_pyramid(pyramid_id: str): ...

@router.put("/{pyramid_id}", response_model=PyramidResponse)
async def update_pyramid(pyramid_id: str, data: PyramidUpdate): ...

@router.delete("/{pyramid_id}")
async def delete_pyramid(pyramid_id: str): ...

@router.get("/{pyramid_id}/visualization")
async def get_visualization(pyramid_id: str): ...

@router.get("/{pyramid_id}/health")
async def get_health(pyramid_id: str): ...

# api/nodes.py
router = APIRouter(prefix="/api/nodes", tags=["nodes"])

@router.post("/", response_model=NodeResponse)
async def create_node(data: NodeCreate): ...

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str): ...

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(node_id: str, data: NodeUpdate): ...

@router.put("/{node_id}/move", response_model=NodeResponse)
async def move_node(node_id: str, data: NodeMove): ...

@router.delete("/{node_id}")
async def delete_node(node_id: str): ...

@router.get("/{node_id}/contents", response_model=list[ContentResponse])
async def get_node_contents(node_id: str, page: int = 1, size: int = 20): ...

# api/sources.py
router = APIRouter(prefix="/api/sources", tags=["sources"])

@router.post("/", response_model=SourceResponse)
async def create_source(data: SourceCreate): ...

@router.get("/", response_model=list[SourceResponse])
async def list_sources(status: str | None = None): ...

@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(source_id: str): ...

@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(source_id: str, data: SourceUpdate): ...

@router.delete("/{source_id}")
async def delete_source(source_id: str): ...

@router.post("/{source_id}/test")
async def test_source(source_id: str): ...

# api/contents.py
router = APIRouter(prefix="/api/contents", tags=["contents"])

@router.get("/", response_model=list[ContentResponse])
async def list_contents(
    node_id: str | None = None,
    page: int = 1,
    size: int = 20,
    sort_by: str = "created_at",
    order: str = "desc"
): ...

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str): ...
```

### 前端组件

#### 1. 页面结构

```typescript
// app/layout.tsx - 主布局
interface LayoutProps {
  children: React.ReactNode;
}

// 包含：
// - 顶部导航栏（Logo、导航链接、用户菜单）
// - 侧边栏（金字塔列表、快捷操作）
// - 主内容区

// app/page.tsx - 首页（信息流）
// 展示最新内容列表，支持筛选和搜索

// app/pyramid/page.tsx - 金字塔列表
// 展示所有金字塔卡片

// app/pyramid/[id]/page.tsx - 金字塔详情
// 展示金字塔可视化和节点详情

// app/sources/page.tsx - 信息源管理
// 展示信息源列表和管理操作
```

#### 2. 核心组件

```typescript
// components/pyramid/PyramidCanvas.tsx
// 使用 ReactFlow 渲染金字塔可视化
interface PyramidCanvasProps {
  pyramidId: string;
  onNodeClick: (nodeId: string) => void;
  onNodeSelect: (nodeId: string) => void;
}

// components/pyramid/PyramidNode.tsx
// 自定义 ReactFlow 节点组件
interface PyramidNodeProps {
  data: {
    id: string;
    name: string;
    description: string;
    contentCount: number;
    healthScore: number;
  };
  selected: boolean;
}

// components/pyramid/NodeDetailPanel.tsx
// 节点详情侧边面板
interface NodeDetailPanelProps {
  nodeId: string;
  onClose: () => void;
  onEdit: () => void;
}

// components/pyramid/PyramidCard.tsx
// 金字塔卡片组件
interface PyramidCardProps {
  pyramid: Pyramid;
  onClick: () => void;
}

// components/feed/FeedList.tsx
// 信息流列表组件
interface FeedListProps {
  nodeId?: string;
  viewMode: 'compact' | 'detailed';
}

// components/feed/FeedItem.tsx
// 信息流条目组件
interface FeedItemProps {
  content: ContentItem;
  viewMode: 'compact' | 'detailed';
  onClick: () => void;
}

// components/sources/SourceList.tsx
// 信息源列表组件
interface SourceListProps {
  onSelect: (sourceId: string) => void;
  onAdd: () => void;
}

// components/sources/SourceForm.tsx
// 信息源表单组件
interface SourceFormProps {
  source?: InformationSource;
  onSubmit: (data: SourceCreate | SourceUpdate) => void;
  onCancel: () => void;
}

// components/sources/SourceCard.tsx
// 信息源卡片组件
interface SourceCardProps {
  source: InformationSource;
  onEdit: () => void;
  onTest: () => void;
  onDelete: () => void;
}
```

#### 3. API 客户端

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  pyramids: {
    list: () => fetch(`${API_BASE}/api/pyramids`).then(r => r.json()),
    get: (id: string) => fetch(`${API_BASE}/api/pyramids/${id}`).then(r => r.json()),
    create: (data: PyramidCreate) => fetch(`${API_BASE}/api/pyramids`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    update: (id: string, data: PyramidUpdate) => fetch(`${API_BASE}/api/pyramids/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    delete: (id: string) => fetch(`${API_BASE}/api/pyramids/${id}`, { method: 'DELETE' }),
    getVisualization: (id: string) => fetch(`${API_BASE}/api/pyramids/${id}/visualization`).then(r => r.json()),
  },
  nodes: {
    get: (id: string) => fetch(`${API_BASE}/api/nodes/${id}`).then(r => r.json()),
    create: (data: NodeCreate) => fetch(`${API_BASE}/api/nodes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    update: (id: string, data: NodeUpdate) => fetch(`${API_BASE}/api/nodes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    move: (id: string, data: NodeMove) => fetch(`${API_BASE}/api/nodes/${id}/move`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    delete: (id: string) => fetch(`${API_BASE}/api/nodes/${id}`, { method: 'DELETE' }),
    getContents: (id: string, page = 1, size = 20) => 
      fetch(`${API_BASE}/api/nodes/${id}/contents?page=${page}&size=${size}`).then(r => r.json()),
  },
  sources: {
    list: (status?: string) => fetch(`${API_BASE}/api/sources${status ? `?status=${status}` : ''}`).then(r => r.json()),
    get: (id: string) => fetch(`${API_BASE}/api/sources/${id}`).then(r => r.json()),
    create: (data: SourceCreate) => fetch(`${API_BASE}/api/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    update: (id: string, data: SourceUpdate) => fetch(`${API_BASE}/api/sources/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    delete: (id: string) => fetch(`${API_BASE}/api/sources/${id}`, { method: 'DELETE' }),
    test: (id: string) => fetch(`${API_BASE}/api/sources/${id}/test`, { method: 'POST' }).then(r => r.json()),
  },
  contents: {
    list: (params: { nodeId?: string; page?: number; size?: number; sortBy?: string; order?: string }) => {
      const query = new URLSearchParams();
      if (params.nodeId) query.set('node_id', params.nodeId);
      if (params.page) query.set('page', String(params.page));
      if (params.size) query.set('size', String(params.size));
      if (params.sortBy) query.set('sort_by', params.sortBy);
      if (params.order) query.set('order', params.order);
      return fetch(`${API_BASE}/api/contents?${query}`).then(r => r.json());
    },
    get: (id: string) => fetch(`${API_BASE}/api/contents/${id}`).then(r => r.json()),
  },
};
```

## 数据模型

### 数据库 ER 图

```
┌─────────────────┐       ┌─────────────────┐
│    pyramids     │       │  pyramid_nodes  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │
│ name            │  │    │ pyramid_id (FK) │──┐
│ description     │  └───>│ parent_id (FK)  │──┤ (self-ref)
│ created_at      │       │ name            │  │
│ updated_at      │       │ description     │<─┘
│ is_deleted      │       │ level           │
└─────────────────┘       │ sort_order      │
                          │ created_at      │
                          │ updated_at      │
                          │ is_deleted      │
                          └────────┬────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│source_node_mapping│    │content_node_mapping │    │                     │
├───────────────────┤    ├─────────────────────┤    │                     │
│ id (PK)           │    │ id (PK)             │    │                     │
│ source_id (FK)    │    │ content_id (FK)     │    │                     │
│ node_id (FK)      │    │ node_id (FK)        │    │                     │
│ weight            │    │ confidence          │    │                     │
│ created_at        │    │ is_primary          │    │                     │
└────────┬──────────┘    │ created_at          │    │                     │
         │               └──────────┬──────────┘    │                     │
         │                          │               │                     │
         ▼                          ▼               │                     │
┌─────────────────────┐    ┌─────────────────┐     │                     │
│information_sources  │    │  content_items  │     │                     │
├─────────────────────┤    ├─────────────────┤     │                     │
│ id (PK)             │    │ id (PK)         │     │                     │
│ name                │    │ source_id (FK)  │─────┘                     │
│ source_type         │    │ title           │                           │
│ config (JSON)       │    │ url             │                           │
│ status              │    │ summary         │                           │
│ health_score        │    │ raw_content     │                           │
│ created_at          │    │ tags (JSON)     │                           │
│ updated_at          │    │ quality_score   │                           │
│ last_crawled_at     │    │ validation_status│                          │
│ is_deleted          │    │ published_at    │                           │
└─────────────────────┘    │ created_at      │                           │
                           │ updated_at      │                           │
                           │ is_deleted      │                           │
                           └─────────────────┘                           │
```

### 金字塔模板数据

```python
# 预设金字塔模板
PYRAMID_TEMPLATES = {
    "ai-dev-tools": {
        "name": "AI 开发工具链",
        "description": "AI 应用开发相关的工具、框架和库",
        "nodes": [
            {"name": "IDE 与编辑器", "children": [
                {"name": "AI 代码助手"},
                {"name": "智能补全插件"},
            ]},
            {"name": "开发框架", "children": [
                {"name": "LLM 框架"},
                {"name": "向量数据库"},
                {"name": "RAG 框架"},
            ]},
            {"name": "部署工具", "children": [
                {"name": "模型服务化"},
                {"name": "推理优化"},
            ]},
        ]
    },
    "agent-ecosystem": {
        "name": "Agent 生态",
        "description": "AI Agent 相关的框架、工具和应用",
        "nodes": [
            {"name": "Agent 框架", "children": [
                {"name": "单 Agent 框架"},
                {"name": "多 Agent 框架"},
            ]},
            {"name": "工具调用", "children": [
                {"name": "Function Calling"},
                {"name": "MCP 协议"},
            ]},
            {"name": "Agent 应用", "children": [
                {"name": "编程助手"},
                {"name": "研究助手"},
                {"name": "自动化工具"},
            ]},
        ]
    },
    "prompt-engineering": {
        "name": "Prompt 工程",
        "description": "提示词设计、优化和评估方法",
        "nodes": [
            {"name": "提示词技术", "children": [
                {"name": "Few-shot Learning"},
                {"name": "Chain of Thought"},
                {"name": "ReAct"},
            ]},
            {"name": "优化方法", "children": [
                {"name": "自动优化"},
                {"name": "人工优化"},
            ]},
            {"name": "评估方法", "children": [
                {"name": "自动评估"},
                {"name": "人工评估"},
            ]},
        ]
    },
    "model-capabilities": {
        "name": "模型应用能力",
        "description": "大模型的各种应用能力",
        "nodes": [
            {"name": "文本能力", "children": [
                {"name": "文本生成"},
                {"name": "文本理解"},
                {"name": "翻译"},
            ]},
            {"name": "代码能力", "children": [
                {"name": "代码生成"},
                {"name": "代码理解"},
                {"name": "代码修复"},
            ]},
            {"name": "多模态能力", "children": [
                {"name": "图像理解"},
                {"name": "图像生成"},
                {"name": "语音处理"},
            ]},
        ]
    },
    "hotspot-tracking": {
        "name": "热点追踪",
        "description": "AI 领域的热点话题和动态",
        "nodes": [
            {"name": "新模型发布"},
            {"name": "重大更新"},
            {"name": "行业动态"},
            {"name": "研究突破"},
        ]
    },
}
```

## 正确性属性

*正确性属性是系统应该在所有有效执行中保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 金字塔创建完整性
*For any* 有效的金字塔创建请求（包含名称和描述），创建操作应返回包含唯一 ID、正确名称、正确描述、创建时间戳的金字塔对象。
**Validates: Requirements 1.1**

### Property 2: 金字塔更新一致性
*For any* 已存在的金字塔和有效的更新数据，更新操作后查询该金字塔应返回更新后的值，且其他字段保持不变。
**Validates: Requirements 1.2**

### Property 3: 金字塔删除级联
*For any* 包含节点的金字塔，删除金字塔后，该金字塔及其所有节点都应被标记为已删除，且不再出现在列表查询结果中。
**Validates: Requirements 1.3**

### Property 4: 金字塔列表完整性
*For any* 数据库中的非删除金字塔集合，列表查询应返回所有这些金字塔，且每个金字塔包含基本信息和健康度摘要。
**Validates: Requirements 1.4**

### Property 5: 节点创建层级正确性
*For any* 有效的节点创建请求，如果指定了父节点，则新节点的层级应等于父节点层级加 1；如果未指定父节点（根节点），则层级应为 0。
**Validates: Requirements 2.1**

### Property 6: 节点更新一致性
*For any* 已存在的节点和有效的更新数据，更新操作后查询该节点应返回更新后的值，且层级和父节点关系保持不变。
**Validates: Requirements 2.2**

### Property 7: 节点删除级联
*For any* 包含子节点的节点，删除该节点后，该节点及其所有后代节点都应被标记为已删除。
**Validates: Requirements 2.3**

### Property 8: 节点移动子树保持
*For any* 节点移动操作，移动后该节点的所有子节点应保持原有的相对层级关系，且子节点的层级值应根据新位置正确更新。
**Validates: Requirements 2.4**

### Property 9: 可视化数据完整性
*For any* 金字塔，可视化数据应包含该金字塔的所有非删除节点，且每个节点包含位置、层级、连接关系信息。
**Validates: Requirements 3.1**

### Property 10: 健康度评分范围
*For any* 金字塔，健康度评分应在 0-100 范围内，且评分应反映金字塔结构的平衡性。
**Validates: Requirements 3.3**

### Property 11: 信息源创建完整性
*For any* 有效的信息源创建请求，创建操作应返回包含唯一 ID、正确类型、正确配置的信息源对象，且初始状态为"discovered"。
**Validates: Requirements 4.1**

### Property 12: 信息源更新一致性
*For any* 已存在的信息源和有效的更新数据，更新操作后查询该信息源应返回更新后的配置值。
**Validates: Requirements 4.4**

### Property 13: 信息源删除内容保留
*For any* 关联了内容的信息源，删除信息源后，关联的内容应保留但其来源标记应更新为已删除状态。
**Validates: Requirements 4.5**

### Property 14: 事务回滚一致性
*For any* 包含多个写入操作的事务，如果任一操作失败，所有已执行的操作应被回滚，数据库状态应与事务开始前一致。
**Validates: Requirements 27.2**

### Property 15: 递归查询完整性
*For any* 金字塔的节点树查询，返回的节点集合应包含该金字塔的所有非删除节点，且层级关系正确反映父子关系。
**Validates: Requirements 27.3**

### Property 16: 模板创建结构一致性
*For any* 预设模板，使用该模板创建的金字塔应包含模板定义的所有节点，且节点的层级结构与模板定义一致。
**Validates: Requirements 38.2**

## 错误处理

### API 错误响应格式

```python
class ErrorResponse(BaseModel):
    code: str           # 错误码
    message: str        # 错误信息
    details: dict = {}  # 详细信息

# 错误码定义
ERROR_CODES = {
    "PYRAMID_NOT_FOUND": "金字塔不存在",
    "NODE_NOT_FOUND": "节点不存在",
    "SOURCE_NOT_FOUND": "信息源不存在",
    "CONTENT_NOT_FOUND": "内容不存在",
    "INVALID_PARENT_NODE": "无效的父节点",
    "CIRCULAR_REFERENCE": "检测到循环引用",
    "TEMPLATE_NOT_FOUND": "模板不存在",
    "VALIDATION_ERROR": "数据验证失败",
    "DATABASE_ERROR": "数据库操作失败",
}
```

### 错误处理策略

| 错误类型 | 处理方式 | HTTP 状态码 |
|---------|---------|------------|
| 资源不存在 | 返回 404 错误 | 404 |
| 数据验证失败 | 返回详细验证错误 | 422 |
| 循环引用检测 | 拒绝操作并返回错误 | 400 |
| 数据库错误 | 回滚事务，返回 500 | 500 |
| 未授权访问 | 返回 401 错误 | 401 |

### 前端错误处理

```typescript
// lib/api.ts
class ApiError extends Error {
  code: string;
  details: Record<string, unknown>;
  
  constructor(code: string, message: string, details: Record<string, unknown> = {}) {
    super(message);
    this.code = code;
    this.details = details;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json();
    throw new ApiError(error.code, error.message, error.details);
  }
  return response.json();
}
```

## 测试策略

### 测试类型

1. **单元测试**：测试各服务层的业务逻辑
2. **属性测试**：验证正确性属性
3. **集成测试**：测试 API 端点
4. **前端组件测试**：测试 React 组件

### 属性测试配置

- 使用 Hypothesis 库进行属性测试
- 每个属性测试运行至少 100 次迭代
- 测试标签格式：`Feature: ai-radar-iteration-1, Property N: {property_text}`

### 测试覆盖范围

| 模块 | 单元测试 | 属性测试 | 集成测试 |
|-----|---------|---------|---------|
| PyramidService | ✓ | ✓ | ✓ |
| NodeService | ✓ | ✓ | ✓ |
| SourceService | ✓ | ✓ | ✓ |
| API Routes | - | - | ✓ |
| 前端组件 | ✓ | - | - |

### 测试数据生成策略

```python
# 使用 Hypothesis 生成测试数据
from hypothesis import strategies as st

# 金字塔名称策略
pyramid_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P')),
    min_size=1,
    max_size=100
)

# 节点树策略
def node_tree_strategy(max_depth=3, max_children=5):
    return st.recursive(
        st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'description': st.text(max_size=200),
        }),
        lambda children: st.fixed_dictionaries({
            'name': st.text(min_size=1, max_size=50),
            'description': st.text(max_size=200),
            'children': st.lists(children, max_size=max_children),
        }),
        max_leaves=max_depth
    )
```
