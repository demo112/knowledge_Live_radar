# AI 驱动建议系统规格

## Why

当前系统存在两大问题：

### 问题一：硬编码建议散落各处

| 场景 | 文件 | 硬编码内容 |
|------|------|-----------|
| 金字塔健康评估 | `health_evaluator.py` | `empty_nodes_desc`, `low_activity_desc` 等键名 |
| 结构重构建议 | `restructure_advisor.py` | 阈值判断 + 固定文案 |
| 系统健康检测 | `health_detector.py` | 固定问题描述（中文硬编码） |
| 内容代谢建议 | `metabolism_service.py` | 固定清理建议 |
| 概念漂移检测 | `drift_detector.py` | 内联 Prompt，非模板化 |
| 信息源生命周期 | `lifecycle_manager.py` | 固定失败原因描述 |
| 提案生成 | `proposal_generator.py` | 固定原因描述 |

**核心问题**：建议笼统、无法针对具体问题、不可被 AI 执行。

### 问题二：AI 调用架构混乱

当前存在两套并行的 AI 调用体系：

| 组件 | 位置 | 状态 |
|------|------|------|
| `AIClient` | `app/core/ai/client.py` | ✅ 新架构，统一入口 |
| `AIFacade` | `app/core/ai/facade.py` | ✅ 新架构，能力门面 |
| `Processors` | `app/core/ai/processors/` | ✅ 新架构，领域处理器 |
| `AIService` | `app/services/ai_service.py` | ⚠️ 旧架构，功能重复 |
| `PromptManager` | `app/services/prompt/prompt_manager.py` | ⚠️ 旧架构，与 prompt_loader 重复 |

**核心问题**：零星调用、重复代码、难以维护。

## What Changes

### 核心变更

#### 1. 统一 AI 调用组件

- **废弃** `app/services/ai_service.py`，统一使用 `app/core/ai/` 架构
- **废弃** `app/services/prompt/prompt_manager.py`，统一使用 `app/core/ai/prompt_loader.py`
- **扩展** `AIFacade`，新增建议生成能力
- **新增** `SuggestionProcessor`，专门处理建议生成

#### 2. 建议生成标准化

- **新增** `AISuggestion` 统一数据模型（action_type, target_id, params 等）
- **新增** Prompt 模板：
  - `pyramid_health_analysis.md` - 金字塔健康分析
  - `source_health_analysis.md` - 信息源健康分析
  - `content_metabolism_analysis.md` - 内容代谢分析
  - `concept_drift_analysis.md` - 概念漂移分析
- **改造** 所有硬编码建议场景，改为调用 `AIFacade`

#### 3. 建议执行器

- **新增** `SuggestionExecutor` 服务，解析 AI 建议并执行
- **复用** 现有 `DecisionExecutor` 的执行逻辑

### **BREAKING** 变更

- `HealthReport.suggestions` 字段格式从 `string[]` 改为 `AISuggestion[]`
- `Approval.reason` 字段改为 AI 生成的结构化内容
- 前端需要适配新的建议数据结构

## Impact

### 受影响的代码

**需要废弃的文件**：
- `backend/app/services/ai_service.py`
- `backend/app/services/prompt/prompt_manager.py`

**需要改造的文件**：
- `backend/app/services/health_evaluator.py`
- `backend/app/services/evolution/restructure_advisor.py`
- `backend/app/services/evolution/health_detector.py`
- `backend/app/services/metabolism_service.py`
- `backend/app/services/evolution/drift_detector.py`
- `backend/app/services/lifecycle_manager.py`
- `backend/app/services/proposal_generator.py`
- `backend/app/services/validator/soft_validator.py`
- `backend/app/services/concept_extractor.py`

**需要新增的文件**：
- `backend/app/core/ai/processors/suggestion.py`
- `backend/app/core/ai/prompts/pyramid_health_analysis.md`
- `backend/app/core/ai/prompts/source_health_analysis.md`
- `backend/app/core/ai/prompts/content_metabolism_analysis.md`
- `backend/app/core/ai/prompts/concept_drift_analysis.md`
- `backend/app/services/suggestion_executor.py`

**前端适配**：
- `frontend/src/components/pyramid/HealthDashboard.tsx`
- `frontend/messages/en.json`

## ADDED Requirements

### Requirement: 统一 AI 调用架构

系统应提供统一的 AI 调用组件，所有 AI 调用都通过 `AIFacade` 进行。

#### Scenario: AI 调用统一入口
- **GIVEN** 任意业务场景需要调用 AI
- **WHEN** 调用 `AIFacade` 的对应方法
- **THEN** 请求被路由到正确的 Processor，使用正确的 Prompt 模板

#### Scenario: Prompt 模板统一管理
- **GIVEN** 一个 Prompt 模板文件（.md）
- **WHEN** 系统启动或模板更新
- **THEN** 模板被加载到内存，可通过 `prompt_loader.render_prompt(name, variables)` 获取

### Requirement: AI 建议数据模型

系统应提供统一的建议数据模型 `AISuggestion`：

```python
class AISuggestion(Base):
    id: UUID
    action_type: str  # create_node/delete_node/update_node/split_node/merge_node/link_content/update_strategy/archive_content
    target_type: str  # pyramid_node/information_source/content_item
    target_id: UUID
    target_name: str  # 便于用户识别
    reason: str       # AI 生成的原因（人类可读）
    params: dict      # 执行参数（AI 可执行）
    confidence: float
    status: str       # pending/approved/executed/rejected
    pyramid_id: UUID  # 关联的金字塔（可选）
    source_id: UUID   # 关联的信息源（可选）
    created_at: datetime
    expires_at: datetime  # 建议有效期
```

#### Scenario: 建议生成
- **GIVEN** 一个分析场景（金字塔健康、信息源健康等）
- **WHEN** 调用 `AIFacade.generate_suggestions(scene, context)`
- **THEN** 返回结构化建议列表，每条建议包含完整的执行参数

#### Scenario: 建议执行
- **GIVEN** 一条已审批的 AI 建议
- **WHEN** 用户点击"执行"
- **THEN** 系统解析 `action_type` 和 `params`，调用对应的执行器完成操作

### Requirement: Prompt 模板 - 金字塔健康分析

系统应提供 `pyramid_health_analysis` Prompt 模板：

```markdown
---
name: pyramid_health_analysis
description: 分析金字塔健康状态并生成具体建议
variables:
  - pyramid_structure
  - node_stats
  - content_stats
  - activity_stats
---

# Role
你是一个知识管理专家，负责分析知识金字塔的健康状态。

# Task
分析提供的金字塔数据，识别问题并生成具体的改进建议。

# Input
## 金字塔结构
{{ pyramid_structure }}

## 节点统计
{{ node_stats }}

## 内容统计
{{ content_stats }}

## 活跃度统计
{{ activity_stats }}

# Output Format (JSON)
{
  "analysis": {
    "depth_balance_score": 0-100,
    "coverage_score": 0-100,
    "activity_score": 0-100,
    "overall_score": 0-100
  },
  "suggestions": [
    {
      "action_type": "create_node|delete_node|update_node|split_node|merge_node|link_content",
      "target_id": "节点ID或null",
      "target_name": "节点名称",
      "reason": "具体原因（中文）",
      "params": { /* 执行参数 */ },
      "confidence": 0.0-1.0
    }
  ]
}
```

### Requirement: Prompt 模板 - 信息源健康分析

系统应提供 `source_health_analysis` Prompt 模板，分析信息源失败原因并生成调整建议。

### Requirement: Prompt 模板 - 内容代谢分析

系统应提供 `content_metabolism_analysis` Prompt 模板，分析内容质量并生成归档建议。

### Requirement: Prompt 模板 - 概念漂移分析

系统应提供 `concept_drift_analysis` Prompt 模板，分析概念演变并生成更新建议。

## MODIFIED Requirements

### Requirement: 金字塔健康评估

**原需求**：根据硬编码阈值生成建议键名

**修改后**：调用 `AIFacade.analyze_pyramid_health(pyramid_id)` 生成具体建议

### Requirement: 结构重构建议

**原需求**：使用硬编码阈值（MAX_CHILDREN=10, MAX_DEPTH=5）判断

**修改后**：由 AI 分析结构并生成建议，阈值作为 Prompt 上下文参考

### Requirement: 系统健康检测

**原需求**：硬编码中文问题描述

**修改后**：调用 AI 生成具体问题描述和建议

### Requirement: 内容代谢建议

**原需求**：固定条件判断生成清理建议

**修改后**：调用 AI 分析内容价值并生成归档建议

### Requirement: 概念漂移检测

**原需求**：内联 Prompt，非模板化

**修改后**：使用 `concept_drift_analysis.md` 模板

### Requirement: 信息源生命周期管理

**原需求**：固定失败原因描述

**修改后**：调用 AI 分析失败原因并生成调整建议

## REMOVED Requirements

### Requirement: 旧 AI 服务

**Reason**: 统一使用 `app/core/ai/` 架构

**Migration**: 
- 删除 `app/services/ai_service.py`
- 删除 `app/services/prompt/prompt_manager.py`
- 更新所有引用，改为使用 `AIFacade`

### Requirement: 硬编码建议键名

**Reason**: 所有建议改为 AI 生成

**Migration**: 
- 删除 `en.json` 中的 `Health.empty_nodes_desc` 等键
- 前端直接显示 AI 生成的 `reason` 字段
