# Agent 清单

Agent是流程管理者，负责定义工作流程、调度Skill、管理状态、在关键节点请求人确认。

## Agent与Skill的关系

| 层级 | 角色 | 职责 |
|------|------|------|
| 人 | 决策者 | 提需求、确认设计、验收结果 |
| **Agent** | **流程管理者** | 定义工作流程、调度Skill |
| Skill | 执行者 | 执行具体步骤 |
| Rules | 约束 | 全局规范 |

## Agent清单

| Agent | 说明 | 文件 |
|-------|------|------|
| 开发Agent | 从需求到交付的完整开发流程 | dev-agent-prompt.md |

## 流程总览

```
阶段1: Align     → requirement-analysis
阶段2: Architect → technical-design  → 🔴 人确认
阶段3: Atomize   → task-planning
阶段4: Approve   → 🔴 人确认
阶段5: Automate  → Task循环执行
阶段6: Assess    → integration-test → 🔴 人确认
```

### Task执行循环

```
code-implementation → code-logging → code-verification → git-operation
        ↑                                    ↓
        └──────────── problem-fixing ←───────┘（如验证失败）
```

## 止损机制

| 规则 | 说明 |
|------|------|
| 3次上限 | 同一问题同一思路最多尝试3次 |
| 范围限制 | 改动 > 3个文件触发止损 |
| 核心保护 | 涉及核心逻辑触发止损 |
| 人介入 | 止损触发后通知人决定 |

## 业务领域Skill

Agent 是通用的流程管理者，业务知识通过 Skill 注入：

| 业务领域 | Skill |
|----------|-------|
| 考勤系统 | attendance-domain |
