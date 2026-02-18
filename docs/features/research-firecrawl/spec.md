# Firecrawl 深度分析方案

## 1. 分析背景
Knowledge Radar 项目的核心能力之一是“知识聚合”，依赖强大的网页抓取和内容解析能力。目前的 `crawl_engine.py` 仅为框架，亟需实质化实现。Firecrawl 是一个专为 LLM 设计的网页抓取工具，能够将网页转换为高质量的 Markdown 或结构化数据。本分析旨在评估 Firecrawl 是否能作为项目的抓取引擎解决方案。

## 2. 分析目标
1. **全面理解 Firecrawl 能力**：掌握其核心功能、高级特性及局限性。
2. **剖析技术架构**：明确其技术栈、依赖组件及系统架构，评估维护成本。
3. **评估集成可行性**：对比 Cloud API、Self-hosted 和参考复刻三种方案的优劣。
4. **输出决策建议**：为 Knowledge Radar 的抓取引擎选型提供明确建议。

## 3. 分析维度

### 3.1 功能特性 (Features)
- **基础能力**：Crawl (全站), Scrape (单页), Map (URL发现), Search (搜索)。
- **数据质量**：Markdown 转换效果，结构化数据提取 (JSON Schema/Prompt)，截图，PDF/DOCX 解析。
- **高级特性**：动态内容渲染 (JS), 反爬虫对抗 (Proxies), 交互操作 (Actions), 缓存机制。
- **限制**：并发限制，速率限制，支持的浏览器类型。

### 3.2 技术架构 (Architecture)
- **后端语言**：确认核心服务语言 (Node.js/TypeScript vs Python)。
- **核心组件**：浏览器自动化 (Playwright/Puppeteer), 任务队列 (Redis/BullMQ), 数据库 (PostgreSQL/Supabase)。
- **架构模式**：单体 vs 微服务，API Gateway，Worker 节点扩展性。

### 3.3 部署与运维 (DevOps)
- **部署方式**：Docker Compose 支持，K8s 支持。
- **资源消耗**：CPU/内存基线，浏览器实例的资源开销。
- **依赖服务**：是否强依赖第三方服务 (如外部代理池、OpenAI API)。

### 3.4 协议与合规 (License & Compliance)
- **开源协议**：AGPL-3.0 的传染性风险分析。
- **商用限制**：Self-hosted 版本的功能限制 (如 Cloud-only features)。
- **数据隐私**：抓取数据的存储与合规性。

## 4. 集成方案评估

### 方案 A：SaaS 集成 (Cloud API)
- **优点**：零运维，快速接入，按量付费。
- **缺点**：数据隐私风险，长期成本高，依赖外部服务稳定性。

### 方案 B：私有化部署 (Self-hosted)
- **优点**：数据私有，无 API 费用，完全掌控。
- **缺点**：运维复杂 (维护 Browser 集群)，资源消耗大，需处理反爬虫。

### 方案 C：参考复刻 (Python Re-implementation)
- **优点**：完全契合项目技术栈 (Python)，轻量级，可定制。
- **缺点**：开发工作量大，需自行解决 JS 渲染和反爬问题。

## 5. 交付物
- **深度分析报告**：`docs/research/firecrawl-analysis.md`
    - 包含详细的功能对比表、架构图解（Mermaid）、集成方案决策矩阵。
- **架构建议书**：针对 `crawl_engine` 的技术选型建议。
