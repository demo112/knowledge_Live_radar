# 变更日志

所有项目的显著变更将记录在此文件中。

## [Unreleased]

### Added
- **金字塔进化**: 实现基于向量相似度的内容自动归类 (Auto-Classification) 和聚类发现 (Clustering)。
- **E2E测试**: 增加 Playwright 自动化测试覆盖进化流程。
- **AI 核心能力**: 集成硅基流动 API，实现基于 Prompt 的智能内容处理。
- **AI 质量评估**: 使用 SoftValidator 对内容进行多维度打分（信息密度、逻辑性等）。
- **智能内容增强**: 自动生成内容摘要 (Summary)、提取关键标签 (Tags) 和核心概念 (Concepts)。
- **前端智能展示**: 信息流卡片展示 AI 摘要、标签和概念；审批流展示 AI 置信度。
- **Prompt 管理**: 支持 YAML 格式的 Prompt 模板管理和自动同步。
- 扩展信息源类型: 支持微信公众号 (WECHAT_MP)、B站UP主 (BILIBILI_USER)、掘金专栏 (JUEJIN_COLUMN) 等，集成 RSSHub 适配器
- 核心管理增强: 知识金字塔节点拆分 (Split)、合并 (Merge) 和跨金字塔关联 (Link) 功能
- 核心管理增强: 多维度金字塔健康度评估 (Health Evaluation)
- 核心管理增强: ReactFlow 兼容的金字塔可视化数据接口 (Visualization)
- 初始化项目文档结构
- 创建需求文档 (requirements.md)
- 创建需求分析 (requirement-analysis.md)
- 创建数据库设计 (database-design.md)
- 创建 API 契约 (api-contract.md)
- 创建项目路线图 (project-roadmap.md)
- 创建任务清单 (task-backlog.md)
- 创建部署文档 (deployment.md)

### Changed
- 重构 `project-roadmap.md`，使用 Mermaid 图表（Mindmap, Timeline, Gantt, Quadrant, State）替代纯文本规划

### Fixed
- 修复健康报告页面 404 错误 (创建 `frontend/src/app/(dashboard)/health/page.tsx`)
- 修复 `project-roadmap.md` 中 Mermaid 象限图的语法错误 (Lexical error)
