# Design: AI-First Architecture Refactoring

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: AI 辅助创建金字塔 | **Backend**: 新增 `AIFacade.suggest_pyramid_structure`，`POST /api/v1/pyramids/suggest` <br> **Frontend**: 新增 `AIReasoningDisplay` 组件，`PyramidStructurePreview` 组件 |
| Story 2: 信息源智能分析 | **Backend**: 新增 `AIFacade.analyze_source`，`POST /api/v1/sources/analyze` <br> **Frontend**: 新增 `SourceAnalysisCard` 组件 |
| Story 3: 内容实时分类 | **Backend**: 修改 `InputProcessor` 为同步返回或短轮询，新增 `AIFacade.classify_content` <br> **Frontend**: 新增 `ContentClassificationResult` 组件 |
| Story 4: 节点变更影响分析 | **Backend**: 新增 `AIFacade.analyze_node_change`，`POST /api/v1/nodes/{id}/impact` <br> **Frontend**: 新增 `ImpactAnalysisDialog` 组件 |
| Story 6: 搜索意图理解 | **Backend**: 新增 `AIFacade.understand_search_intent`，集成到 `SearchService` <br> **Frontend**: 搜索结果页展示 Intent 理解结果 |

## 核心架构变更：AI Core Layer

为了实现"强感知"和"统一管理"，我们将引入 `app.core.ai` 模块，作为所有 AI 能力的统一出口。

```
backend/app/core/ai/
├── facade.py          # AIFacade: 业务层调用的唯一入口
├── client.py          # AIClient: 封装 LLM 调用（Cloud/Local），支持流式
├── prompt_loader.py   # PromptLoader: 负责加载 Markdown 格式的 Prompt
├── prompts/           # Prompt 模板目录 (Markdown 格式)
│   ├── pyramid_structure.md
│   ├── content_classification.md
│   ├── source_analysis.md
│   └── search_intent.md
└── processors/        # 具体的处理逻辑
    ├── pyramid.py     # 金字塔相关处理
    ├── content.py     # 内容/信息源相关处理
    └── search.py      # 搜索相关处理
```

### Prompt 管理规范 (Markdown)

Prompt 将以 `.md` 文件形式存储在 `backend/app/core/ai/prompts/` 目录下，使用 Frontmatter 管理元数据。

**示例: `pyramid_structure.md`**

```markdown
---
name: pyramid_structure
description: 生成金字塔结构建议
version: 1.0.0
model: gpt-4o
variables:
  - name
  - description
---

# Role
你是一个知识管理专家，擅长构建结构化的知识体系。

# Task
根据用户提供的名称和描述，生成一个金字塔形的知识结构。

# Input
名称: {{ name }}
描述: {{ description }}

# Output Format (JSON)
{
  "structure": { ... },
  "reasoning": "..."
}
```

## 数据模型设计

我们需要扩展现有的模型以存储 AI 的元数据（Reasoning, Confidence 等）。

### 1. 扩展 `ContentItem` (已存在，需增强)

```python
# backend/app/models/content.py

class ContentItem(Base):
    # ... 现有字段 ...
    
    # 新增/增强 AI 元数据字段
    ai_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # 结构示例:
    # {
    #   "classification_reason": "Based on keywords X and Y...",
    #   "confidence": 0.95,
    #   "processing_time_ms": 1200,
    #   "model_version": "gpt-4o-mini-2024-07-18"
    # }
```

### 2. 新增 `AISuggestion` (用于两阶段确认)

```python
# backend/app/models/ai_suggestion.py

from sqlalchemy import Column, String, DateTime, func, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # pyramid_structure, content_classification, etc.
    input_hash: Mapped[str] = mapped_column(String(64), index=True) # 用于缓存查找
    
    # AI 输出
    data: Mapped[dict] = mapped_column(JSON, nullable=False)       # 建议的具体内容
    reasoning: Mapped[str] = mapped_column(String, nullable=True)  # AI 的思考过程/理由
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True) # 建议有效期
```

## API 定义

### 1. 金字塔结构建议 (Create with AI)

**POST /api/v1/pyramids/suggest**

获取基于描述的金字塔结构建议。

**Request:**
```typescript
interface PyramidSuggestRequest {
  name: string
  description: string
}
```

**Response:**
```typescript
interface PyramidSuggestResponse {
  suggestion_id: string
  structure: PyramidNodeStructure // 树形结构
  reasoning: string               // AI 的思考过程（用于前端展示）
  confidence: number
}
```

### 2. 确认创建金字塔

**POST /api/v1/pyramids/confirm**

基于建议（可修改）创建金字塔。

**Request:**
```typescript
interface PyramidConfirmRequest {
  suggestion_id: string
  modifications?: PyramidNodeStructure // 用户修改后的结构（可选）
}
```

### 3. 信息源分析 (Add Source)

**POST /api/v1/sources/analyze**

**Request:**
```typescript
interface SourceAnalyzeRequest {
  url: string
}
```

**Response:**
```typescript
interface SourceAnalyzeResponse {
  title: string
  summary: string
  tags: string[]
  suggested_node_id: string // 建议归属的节点 ID
  reasoning: string         // 归类理由
  confidence: number
}
```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/app/core/ai/client.py` | 新增 | 统一的 AI 客户端，支持重试、流式接口 |
| `backend/app/core/ai/prompt_loader.py` | 新增 | 负责加载解析 Markdown Prompt 文件 (Frontmatter + Jinja2) |
| `backend/app/core/ai/prompts/*.md` | 新增 | 各个场景的 Prompt 模板文件 |
| `backend/app/core/ai/facade.py` | 新增 | `AIFacade` 类，定义业务调用的高层接口 |
| `backend/app/core/ai/processors/pyramid.py` | 新增 | 金字塔结构生成逻辑 |
| `backend/app/core/ai/processors/content.py` | 新增 | 内容分析、分类逻辑 |
| `backend/app/models/ai_suggestion.py` | 新增 | `AISuggestion` 模型定义 |
| `backend/app/schemas/ai.py` | 新增 | AI 相关的 Pydantic Schemas (Request/Response) |
| `backend/app/api/pyramids.py` | 修改 | 新增 `suggest` 和 `confirm` 路由 |
| `backend/app/api/sources.py` | 修改 | 新增 `analyze` 路由 |
| `frontend/src/components/ai/AIReasoningDisplay.tsx` | 新增 | 展示 AI 思考过程的 UI 组件 |
| `frontend/src/components/ai/PyramidPreview.tsx` | 新增 | 金字塔结构预览与编辑组件 |

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| `create_pyramid` | 原有直接创建逻辑保留作为底层方法，上层业务逻辑变更 | 中 |
| `create_source` | 增加分析步骤，原有直接创建逻辑需兼容 | 低 |
| `AIService` (旧) | `app.services.ai_service.py` 将被标记为 Deprecated，逐步迁移到 `app.core.ai` | 中 |
| `PromptManager` (旧) | `app.services.prompt.prompt_manager.py` (基于DB) 将被 `PromptLoader` (基于文件) 替代 | 中 |

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| **AI 模块位置** | `app.core.ai` | AI 是核心能力而非普通 Service，需要统一管理 Prompt 和 Client 配置 |
| **交互模式** | 两阶段 (Suggest -> Confirm) | 满足"AI 提议，人类决策"原则，且允许用户在创建前修正 |
| **Prompt 管理** | Markdown 文件 + Frontmatter | **显性管理**：在项目中直接可见；**版本控制**：Git 追踪变更；**易读性**：Markdown 格式更易编写和阅读 |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| AI 响应慢 | 用户等待时间过长 (>5s) | 前端实现流式加载动画；后端设置超时；使用较快模型 (如 GPT-4o-mini) |
| 结构生成不稳定 | 生成的 JSON 格式错误 | 使用 Pydantic 进行 Output Parsing；增加重试机制 |
| 文件 IO 性能 | 每次读取 Prompt 文件可能慢 | 实现内存缓存 (LRU Cache)，仅在开发模式下每次重载 |

## 需要人决策

- [x] **Prompt 存储方式**：确认使用 Markdown 文件管理。
