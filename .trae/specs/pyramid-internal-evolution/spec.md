# 金字塔内生进化能力规格 (Pyramid Internal Evolution)

## Why

当前系统的金字塔进化逻辑（分析、优化、建议）被封装在外部的 `EvolutionEngine` 中，作为一个全局的定时任务运行。这种设计存在以下问题：
1.  **无法按需触发**：用户无法针对特定的金字塔立即运行分析或优化。
2.  **逻辑割裂**：金字塔的核心能力散落在 `EvolutionEngine`、`RestructureAdvisor` 等外部服务中，不符合领域驱动设计（DDD）中聚合根的思想。
3.  **交互受限**：前端无法直接调用金字塔的进化能力，必须等待后台任务调度。

用户期望金字塔的分析、优化、建议和实施能力应该是**内生**的，即金字塔自身具备的能力，而非外部强加的。

## What Changes

### 核心变更

将金字塔进化的核心能力下沉到 `PyramidService`（作为金字塔领域的服务门面），并通过 API 暴露给前端。

#### 1. 金字塔服务增强 (`PyramidService`)
在 `PyramidService` 中增加以下能力（通过组合 `RestructureAdvisor` 和 `DriftDetector` 实现）：
-   `analyze_structure(pyramid_id)`: 触发结构分析，生成优化建议。
-   `detect_drift(pyramid_id)`: 触发概念漂移检测，生成更新建议。
-   `get_optimization_suggestions(pyramid_id)`: 获取当前金字塔待处理的优化建议（Approval）。
-   `apply_suggestion(pyramid_id, suggestion_id)`: 执行某条具体的优化建议。

#### 2. API 接口增强 (`PyramidRouter`)
在 `/api/v1/pyramids/{id}` 下新增以下端点：
-   `POST /analyze`: 触发结构与内容分析（同步或异步返回分析结果摘要）。
-   `GET /suggestions`: 获取该金字塔的优化建议列表。
-   `POST /suggestions/{suggestion_id}/apply`: 采纳并执行某条建议。
-   `POST /suggestions/{suggestion_id}/reject`: 拒绝某条建议。

#### 3. 进化引擎重构 (`EvolutionEngine`)
`EvolutionEngine` 不再直接调用 `RestructureAdvisor`，而是作为**调度器**，遍历所有活跃金字塔并调用 `PyramidService.analyze_structure` 和 `PyramidService.detect_drift`。

## Impact

-   **受影响的代码**:
    -   `backend/app/services/pyramid_service.py`: 新增进化相关方法。
    -   `backend/app/routers/pyramids.py`: 新增 API 端点。
    -   `backend/app/services/evolution/evolution_engine.py`: 重构为调用 Service。
    -   `backend/app/services/evolution/decision_executor.py`: (如果存在) 逻辑整合进 Service 或被 Service 调用。

## ADDED Requirements

### Requirement: 金字塔结构分析能力
系统应允许对指定金字塔触发结构分析。

#### Scenario: 手动触发分析
-   **WHEN** 用户在前端点击"分析金字塔"
-   **THEN** 调用 `POST /api/v1/pyramids/{id}/analyze`
-   **THEN** 系统分析金字塔结构，生成优化建议（如拆分、合并节点），并返回分析摘要。

### Requirement: 优化建议管理
系统应提供金字塔专属的优化建议列表。

#### Scenario: 查看建议
-   **WHEN** 用户访问金字塔详情页
-   **THEN** 调用 `GET /api/v1/pyramids/{id}/suggestions`
-   **THEN** 展示待处理的结构优化与概念漂移建议。

### Requirement: 建议实施能力
系统应允许直接采纳并执行优化建议。

#### Scenario: 采纳拆分建议
-   **GIVEN** 一条"拆分节点A"的建议
-   **WHEN** 用户点击"采纳"
-   **THEN** 调用 `POST /api/v1/pyramids/{id}/suggestions/{id}/apply`
-   **THEN** 系统自动执行节点拆分操作，更新金字塔结构，并将建议标记为"已执行"。

## MODIFIED Requirements

### Requirement: 进化引擎调度
**原逻辑**: `EvolutionEngine` 直接实例化 Advisor 进行分析。
**新逻辑**: `EvolutionEngine` 遍历金字塔，调用 `PyramidService` 的分析接口。
