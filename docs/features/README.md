# 功能矩阵索引 (Feature Matrix)

> **SSOT (Single Source of Truth)**: 本文档是系统功能的唯一索引源。所有功能需求均在此列出，链接至具体的 `requirements.md` 或相关设计文档。

## 1. 核心业务域 (Core Domain)

| 功能模块 | 目录 | 核心文档 | 状态 | 描述 |
|----------|------|----------|------|------|
| **清洗与摘要** | `core/clean-and-summary` | [Requirements](./core/clean-and-summary/requirements.md) | ✅ | 内容自动清洗与智能摘要生成 |
| **内容代谢** | `core/content-metabolism` | [Requirements](./core/content-metabolism/requirements.md) | ✅ | 内容生命周期管理与过期处理 |
| **核心管理增强** | `core/management-enhancement` | [Requirements](./core/management-enhancement/requirements.md) | ✅ | 金字塔、节点、信源管理的核心增强 |
| **金字塔进化** | `core/pyramid-evolution` | [Requirements](./core/pyramid-evolution/requirements.md) | ✅ | 金字塔结构的自进化与优化建议 |
| **信源发现** | `core/source-discovery` | [Requirements](./core/source-discovery/requirements.md) | ✅ | 自动发现新信源机制 |
| **扩展信源** | `core/extended-info-sources` | [Requirements](./core/extended-info-sources/requirements.md) | ✅ | 支持更多类型的信源接入 (微信/视频/社区) |
| **发现可视化** | `core/discovery-visualization` | [Requirements](./core/discovery-visualization/requirements.md) | ✅ | 信源发现过程的可视化展示 (SSE) |
| **微信集成** | `core/wechat-integration` | [Requirements](./core/wechat-integration/requirements.md) | ✅ | 微信生态集成与推送 |

## 2. AI 能力域 (AI Domain)

| 功能模块 | 目录 | 核心文档 | 状态 | 描述 |
|----------|------|----------|------|------|
| **AI 能力集** | `ai/capabilities` | [Requirements](./ai/capabilities/requirements.md) | ✅ | 基础 AI 能力定义（分类、打分等） |
| **执行增强** | `ai/execution-enhancement` | [Requirements](./ai/execution-enhancement/requirements.md) | ✅ | AI 执行流程的稳定性与效率优化 |
| **AI First 重构** | `ai/first-refactor` | [Requirements](./ai/first-refactor/requirements.md) | ✅ | 基于 AI First 原则的架构重构 |
| **LLM 降级策略** | `ai/llm-fallback` | [Requirements](./ai/llm-fallback/requirements.md) | ✅ | 多模型降级与高可用策略 |
| **嗅探策略** | `ai/sniffing-strategy` | [Requirements](./ai/sniffing-strategy/requirements.md) | ✅ | 智能内容嗅探策略 |
| **AI 建议系统** | `ai/suggestions` | [Requirements](./ai/suggestions/requirements.md) | ✅ | 统一的 AI 建议生成与执行框架 |
| **认知进化** | `ai/cognitive-evolution` | [Requirements](./ai/cognitive-evolution/requirements.md) | ✅ | 系统认知能力的进化机制与审批流 |
| **监控仪表盘** | `ai/monitor-dashboard` | [Requirements](./ai/monitor-dashboard/requirements.md) | ✅ | AI 服务运行状态监控 |

## 3. 系统支撑域 (System Domain)

| 功能模块 | 目录 | 核心文档 | 状态 | 描述 |
|----------|------|----------|------|------|
| **抓取引擎** | `system/crawl-engine` | [Requirements](./system/crawl-engine/requirements.md) | ✅ | 核心抓取引擎设计 (Firecrawl/RSS) |
| **国际化** | `system/i18n` | [Requirements](./system/i18n/requirements.md) | ✅ | 多语言支持基础设施 |
| **FireCrawl 集成** | `system/research-firecrawl` | [Requirements](./system/research-firecrawl/requirements.md) | ✅ | 私有化 Firecrawl 部署与集成 |

## 状态说明

- ✅ **已定义 (Defined)**: 需求文档完整，已确认
- 🚧 **进行中 (In Progress)**: 正在设计或开发中
- 📝 **草稿 (Draft)**: 仅有初步想法或简单记录
- ⚙️ **技术设计 (Technical)**: 仅有技术设计文档
- 🔬 **调研 (Research)**: 技术调研阶段

---

**维护指南**:
1. 新增功能模块时，请在此表中添加记录。
2. 优先链接 `requirements.md`，若无则链接 `design.md` 或 `spec.md`。
3. 保持状态更新，以便了解系统全貌。
