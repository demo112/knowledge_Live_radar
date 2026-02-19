# Knowledge Radar 文档地图 (Documentation Map)

> **文档原则**: 本项目遵循 **Feature-Centric** 文档架构。`docs/features/` 是系统功能的 **SSOT (Single Source of Truth)**。

## 📚 核心文档索引

| 目录 | 说明 | 适用场景 |
|------|------|----------|
| **[features/](./features/README.md)** | **功能矩阵 (SSOT)** | **查阅具体功能需求、设计、状态** (开发首选) |
| [requirements.md](./requirements.md) | 系统级需求总纲 | 了解系统愿景、核心哲学、顶层架构 |
| [api-contract.md](./api-contract.md) | API 契约 | 前后端接口对接标准 |
| [database-design.md](./database-design.md) | 数据库设计 | 数据模型与ER图 |
| [project-roadmap.md](./project-roadmap.md) | 项目路线图 | 查看宏观迭代计划 |
| [deployment.md](./deployment.md) | 部署指南 | 系统部署与环境配置 |

## 🗄 历史归档与日志

| 目录 | 说明 |
|------|------|
| `feature/` | **历史迭代归档** (Iteration 1-5)。记录了每个迭代的原始需求，仅作参考。 |
| `archive/analysis/` | **历史分析文档**。项目早期的技术分析与调研记录。 |
| `bug_fix/` | **Bug 修复记录**。记录了具体的 Bug 修复过程与复盘。 |
| `progress/` | **每日进度日志**。开发过程中的流水账记录。 |
| `issues/` | **问题记录**。特定问题的详细排查记录。 |

## 🧭 如何使用文档

### 1. 我想了解某个具体功能（如“金字塔进化”）
请直接前往 **[docs/features/README.md](./features/README.md)**，在功能矩阵中找到对应模块，点击进入其 `requirements.md`。

### 2. 我想了解系统的核心设计理念
请阅读 **[core-philosophy.md](./core-philosophy.md)** 和 **[requirements.md](./requirements.md)**。

### 3. 我想了解历史迭代详情
请查阅 `feature/` 目录下的对应迭代文件夹。

### 4. 我是 LLM，我该看哪里？
- **了解当前系统能力**：只看 `docs/features/` 下的文档。
- **了解系统原则**：看 `docs/requirements.md` 和 `docs/core-philosophy.md`。
- **忽略**：`feature/` (除非用户明确问历史)、`bug_fix/`、`progress/`。

---

**维护者注意**：
- 新增功能必须在 `docs/features/` 下创建新目录。
- 任何功能变更必须同步更新 `docs/features/{module}/requirements.md`。
- `docs/features/README.md` 必须保持最新。
