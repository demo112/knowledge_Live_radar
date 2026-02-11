# Skill 清单与映射关系

## 三层架构

```
流程层 (When/What) → 参考层 (How) → 方法论层 (Mindset)
```

## 流程层 Skill（主导开发流程）

| Skill | 触发词 | 关联 Rules | 下一步 |
|-------|--------|-----------|--------|
| requirement-analysis | 需求分析、我想做、能不能实现 | 20-project-overview | → technical-design |
| technical-design | 技术设计、怎么实现、API设计 | 04-api-spec | → task-planning |
| task-planning | 任务拆分、怎么开始、先做什么 | 13-doc-management | → code-implementation |
| code-implementation | 写代码、实现、开始做 | 02-typescript, 03-file-structure | → code-logging |
| code-logging | 检查日志、补日志、console.log | 06-logging | → code-verification |
| code-verification | 验证、测一下、ACV、代码写完了 | 14-definition-of-done | → git-operation / problem-fixing |
| problem-fixing | 报错、bug、跑不起来、失败了 | 14-definition-of-done | → code-verification |
| verification-before-completion | 完成了吗、验收、DoD | 14-definition-of-done | - |
| git-operation | 提交代码、commit、push | 07-git-basic, 08-git-commit | → code-implementation / integration-test |
| git-conflict-resolution | git冲突、合并冲突、conflict | 09-git-conflict | → git-operation |
| integration-test | 集成测试、E2E、完整测试 | 11-testing | → git-operation / problem-fixing |
| doc-sync | 同步文档、更新文档 | 13-doc-management | - |
| project-logging | 记录进度、今日进展 | 13-doc-management | - |

## 参考层 Skill（技术知识库）

编写代码时按模块查阅：

| 模块 | 参考 Skill | 触发词 |
|------|-----------|--------|
| Server (Express/Prisma) | nodejs-backend-patterns | - |
| Web (React/Vite) | react-best-practices, vite-patterns | - |
| App (React Native/Expo) | react-native-patterns, expo-native-ui, expo-networking | - |
| App 调试 | app-debugging, expo-dev-client | - |
| Web 调试 | web-debugging | - |

## 方法论层 Skill（可选）

| Skill | 触发词 | 融入位置 |
|-------|--------|---------|
| systematic-debugging | 系统调试、定位问题、debug | 已融入 problem-fixing |
| test-driven-development | TDD、测试驱动、先写测试 | code-implementation 可选 |

## 业务领域 Skill

| 业务 | Skill | 触发词 |
|------|-------|--------|
| 考勤系统 | attendance-domain | 考勤、打卡、排班、班次 |

## UI 相关 Skill

| Skill | 触发词 |
|-------|--------|
| ui-ux-pro-max | 做界面、UI设计、配色、字体、设计系统 |
| ui-cloning | 截图模仿界面 |
| mobile-android-design | Android 设计规范 |

---

## Skill 与 Rules 联动规则

### 按操作类型加载

| 操作 | 先读 Rules | 先读 Skill |
|------|-----------|-----------|
| 写 Service 代码 | 06-logging, 05-security | nodejs-backend-patterns |
| 写 Controller 代码 | 04-api-spec, 05-security | nodejs-backend-patterns |
| 写测试代码 | 11-testing | test-driven-development |
| 改数据模型 | - | attendance-domain |
| Git 操作 | 07-git-basic, 08-git-commit | git-operation |
| Git 冲突 | 09-git-conflict | git-conflict-resolution |
| 补充日志 | 06-logging | code-logging |

### 按文件类型加载

| 文件 | 先读 Rules |
|------|-----------|
| *.service.ts | 06-logging, 05-security |
| *.controller.ts | 04-api-spec, 05-security |
| *.test.ts | 11-testing |
| schema.prisma | 对照 database-design.md |
| package.json | 01-tech-stack |

---

## 工作流程中的 Skill 调用

```
阶段1: Align     → requirement-analysis + attendance-domain
阶段2: Architect → technical-design + attendance-domain
阶段3: Atomize   → task-planning
阶段4: Approve   → (人工确认)
阶段5: Automate  → code-implementation → code-logging → code-verification → git-operation
                         ↑                                    ↓
                         └──────── problem-fixing ←───────────┘
阶段6: Assess    → integration-test → doc-sync → project-logging
```
