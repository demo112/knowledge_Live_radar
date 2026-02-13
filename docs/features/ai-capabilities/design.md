# Design: AI Core Capabilities

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: AI 质量评估 (软性校验) | **Service**: `SoftValidator` 重构，调用 `AIService` 获取结构化评分。<br>**Prompt**: `soft_validation` 模板。 |
| Story 2: 智能摘要生成 | **Service**: `AIService.generate_summary`。<br>**Model**: `ContentItem` 新增 `summary` 字段。 |
| Story 3: 关键概念提取 | **Service**: `AIService.extract_concepts`。<br>**Model**: `ContentItem` 新增 `concepts` 字段 (JSON)。 |
| Story 4: 自动标签分类 | **Service**: `AIService.generate_tags`。<br>**Model**: `ContentItem` 新增 `tags` 字段 (JSON)。 |
| Story 5: Prompt 模板管理 | **Service**: `PromptManager` (已存在)。<br>**Data**: `prompt_templates` 表 (已存在)。 |
| Story 6: 错误处理与降级 | **Infra**: `AIService` 实现指数退避重试 (Tenacity)。 |
| Story 7: 成本控制 (令牌桶) | **Infra**: `AIService` 内部实现简单的令牌桶或并发限制 (Semaphore)。 |

## 数据模型

### 1. ContentItem 扩展
需要扩展 `ContentItem` 表以存储 AI 生成的元数据。

```python
# backend/app/models/content.py

class ContentItem(Base):
    # ... 现有字段 ...
    
    # 新增 AI 生成字段
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)  # 存储标签列表
    concepts: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)  # 存储关键概念列表
    
    # AI 处理状态 (可选，用于异步处理追踪)
    ai_processed: Mapped[bool] = mapped_column(Boolean, default=False)
```

### 2. ValidationResult (现有)
复用 `backend/app/models/content.py` 中的 `ValidationResult`。
`soft_result` 字段将存储结构化的 JSON 数据：
```json
{
  "score": 85,
  "reason": "内容详实，逻辑清晰，包含具体代码示例。",
  "dimensions": {
    "information_density": 9,
    "logic_coherence": 8
  }
}
```

## 核心服务设计

### AIService 增强 (`backend/app/services/ai_service.py`)

增强 `AIService` 以支持结构化输出和特定任务。

```python
class AIService:
    async def chat_completion_json(self, messages: List[Dict], model: str) -> Dict[str, Any]:
        """强制返回 JSON 并解析"""
        # 实现逻辑：
        # 1. 在 system prompt 中强制要求 JSON 格式
        # 2. 调用 chat_completion
        # 3. 使用 json_repair 或标准 json 解析响应
        # 4. 错误重试
        pass

    async def validate_content_soft(self, content: str, title: str) -> Dict[str, Any]:
        """执行软性校验，返回分数和理由"""
        # 调用 PromptManager 获取 'soft_validation' 模板
        # 组装 messages
        # 调用 chat_completion_json
        pass

    async def generate_summary(self, content: str) -> str:
        pass

    async def extract_concepts(self, content: str) -> List[str]:
        pass

    async def generate_tags(self, content: str) -> List[str]:
        pass
```

### SoftValidator 重构 (`backend/app/services/validator/soft_validator.py`)

```python
class SoftValidator(BaseValidator):
    async def validate(self, content: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        # 1. 准备数据
        # 2. 调用 AIService.validate_content_soft
        # 3. 解析结果：score >= 60 则为 True
        # 4. 返回 (is_valid, result_json)
        pass
```

## API 定义

无需新增公开 API，主要通过内部 Service 调用。
现有的 `SourceService` 在抓取流程中会调用这些 Service。

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/app/models/content.py` | 修改 | 新增 `summary`, `tags`, `concepts`, `ai_processed` 字段 |
| `backend/alembic/versions/xxxx_add_ai_fields.py` | 新增 | 数据库迁移脚本 |
| `backend/app/services/ai_service.py` | 修改 | 实现 `chat_completion_json`, `validate_content_soft`, `generate_summary` 等方法 |
| `backend/app/services/validator/soft_validator.py` | 修改 | 重构校验逻辑，集成 `AIService` 的结构化输出 |
| `backend/app/core/prompts.py` | 新增 | (可选) 定义默认的 Prompt 模板内容，用于初始化系统 |

## 技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| **JSON 解析** | 强制 System Prompt + `json.loads` | SiliconFlow/DeepSeek 对 JSON Mode 支持良好，配合 Prompt 约束即可，无需引入复杂的 Output Parser 库。 |
| **Prompt 管理** | 数据库存储 (`PromptManager`) | 允许运行时调整 Prompt 而无需重启服务，方便调优。 |
| **异步处理** | 暂同步调用 | 当前抓取量不大，直接在抓取流程中串行调用 AI。未来可剥离为 Celery/APScheduler 任务。 |

## 风险分析

| 风险 | 影响 | 应对 |
|------|------|------|
| **AI 响应超时** | 抓取任务卡死 | 设置严格的超时时间 (e.g., 30s)，超时默认视为通过或跳过 AI 处理。 |
| **JSON 解析失败** | 校验失败 | 增加重试机制 (最多 3 次)，失败后降级为默认分数。 |
| **Token 消耗过大** | 成本超支 | 限制输入文本长度 (e.g., 截取前 2000 字符)。 |

## 需要决策

- [ ] **默认 Prompt**: 是否需要在系统启动时自动注入默认的 Prompt 模板到数据库？(建议：是，方便开箱即用)
