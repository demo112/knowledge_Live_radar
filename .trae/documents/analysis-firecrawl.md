# Firecrawl 开源项目分析计划

## 1. 目标
全方位分析 GitHub 开源项目 [Firecrawl](https://github.com/firecrawl/firecrawl)，评估其核心能力、技术架构及适用场景，并制定将其集成到 AI Radar 项目 (`knowledge_Live_radar`) 的可行性方案。

## 2. 分析维度

### 2.1 功能特性分析
- **核心能力**：Crawl (全站爬取), Scrape (单页抓取), Search (搜索), Map (URL发现)。
- **数据处理**：HTML 转 Markdown (LLM-ready), 结构化数据提取 (JSON), 截图, PDF/DOCX 解析。
- **高级特性**：动态内容渲染 (JavaScript), 反爬虫对抗 (Proxies), 交互操作 (Actions: wait, click, scroll)。

### 2.2 技术架构与栈分析
- **核心语言**：确认后端服务语言 (TypeScript/Node.js vs Python)。
- **依赖组件**：浏览器自动化工具 (Playwright/Puppeteer), 队列/缓存 (Redis), 数据库。
- **架构设计**：单体 vs 微服务，异步任务处理流程。

### 2.3 部署与运维
- **部署方式**：Docker / Docker Compose 支持情况。
- **资源需求**：CPU/内存消耗预估 (浏览器渲染通常资源密集)。
- **依赖服务**：是否依赖外部服务 (如第三方代理池)。

### 2.4 协议与合规
- **开源协议**：AGPL-3.0 的影响（传染性分析）。
- **商用限制**：Self-hosted 版本的限制 vs Cloud 版本。

## 3. 集成评估 (与 AI Radar 现状对比)

| 维度 | AI Radar (现状) | Firecrawl (引入) | 决策点 |
|------|----------------|------------------|--------|
| **抓取引擎** | `crawl_engine.py` (仅框架/空壳) | 成熟的 Browser-based 爬虫 | 是否直接替换或集成？ |
| **内容清洗** | 基础 HTML 解析 (未完善) | 专为 LLM 优化的 Markdown | 极大提升数据质量 |
| **技术栈** | Python (FastAPI) | 预计 Node.js/TS | 引入异构技术栈的运维成本 |
| **部署** | 简单 Docker | 需 Redis + Headless Browser | 资源消耗显著增加 |

## 4. 交付物
- **分析报告**：`docs/research/firecrawl-analysis.md`
    - 包含详细的功能、架构、部署分析。
    - 提供 3 种集成方案的优劣对比：
        1. **SaaS 模式**：使用 Firecrawl Cloud API (快速集成，有成本)。
        2. **自部署模式**：Docker 部署 Firecrawl 服务 (数据私有，运维复杂)。
        3. **参考复刻模式**：参考其逻辑用 Python 实现轻量版 (完全掌控，开发成本高)。

## 5. 执行步骤
1. **深度调研**：查阅官方文档、GitHub 源码结构（通过搜索辅助）、Issue/Discussions。
2. **撰写报告**：编写 `docs/research/firecrawl-analysis.md`。
3. **架构建议**：基于分析结果，更新 `docs/features/crawl-engine-design.md` (如果存在) 或提供架构演进建议。
