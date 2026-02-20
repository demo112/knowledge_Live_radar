# Agent 清单

Agent是流程管理者，负责定义工作流程、调度Skill、管理状态、在关键节点请求人确认。

## Agent与Skill的关系

| 层级 | 角色 | 职责 |
|------|------|------|
| 人 | 决策者 | 提需求、确认设计、验收结果、审批变更提案 |
| **Agent** | **流程管理者** | 定义工作流程、调度Skill |
| Skill | 执行者 | 执行具体步骤 |
| Rules | 约束 | 全局规范 |

## Agent清单

| Agent | 说明 | 文件 |
|-------|------|------|
| 开发Agent | 从需求到交付的完整开发流程 | dev-agent-prompt.md |
| 修复Agent | 问题定位、修复和验证 | fix-agent-prompt.md |
| Web E2E 测试Agent | Web 端 E2E 测试覆盖（Playwright） | e2e-test-agent.md |
| App E2E 测试Agent | App 端 E2E 测试覆盖（Detox） | app-e2e-test-agent.md |
| Git 冲突Agent | Git 冲突检测、分析和解决 | git-conflict-agent.md |

## 辅助模块

| 模块 | 说明 | 文件 |
|------|------|------|
| 能力感知引擎 | 意图识别与能力推荐（已融入开发Agent） | capability-awareness.md |

## Agent 统一结构规范

所有 Agent 文件必须包含以下章节：

| 章节 | 说明 |
|------|------|
| 身份定义 | 角色名称 + 角色定位 + 核心能力表 |
| 核心原则 | 3-5 条指导原则 |
| 自主能力边界 | ✅ 可自主 / ⚠️ 需确认 / ❌ 必须人工 三级 |
| 工作流程 | 分阶段的详细流程 |
| 止损机制 | 失败重试上限和暂停规则 |
| 安全规则 | 禁止操作 + 保守原则 |
| 异常处理 | 异常场景和处理方式 |
| 激活方式 | 触发关键词 + 激活响应模板 |
| 沟通模板 | 各阶段的沟通格式 |

## 流程总览（开发Agent 6A）

```
阶段1: Align     → requirement-analysis
阶段2: Architect → technical-design  → 人确认
阶段3: Atomize   → task-planning
阶段4: Approve   → 人确认
阶段5: Automate  → Task循环执行
阶段6: Assess    → integration-test → 人确认
```

## 业务领域Skill

| 业务领域 | Skill |
|----------|-------|
| AI Radar 知识聚合 | ai-radar-domain |
