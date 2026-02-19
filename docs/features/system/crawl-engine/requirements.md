# Requirements: 核心抓取引擎 (Crawl Engine)

## Overview

Crawl Engine 是 Knowledge Radar 的数据摄取心脏，负责从互联网抓取多源异构数据。目前集成了 **Firecrawl (Self-hosted)** 作为主要抓取引擎处理 Web 页面，并保留 RSS 抓取能力。系统通过统一的调度器和 Fetcher 工厂模式，实现高效、稳定的数据获取。

## User Stories

### Story 1: Web 页面深度抓取

As a 系统, I want 能够抓取任意 Web 页面并提取高质量内容, So that AI 可以基于干净的 Markdown 数据进行分析。

**Acceptance Criteria:**

- [ ] AC1: Firecrawl 集成
  - **Given**: 一个标准 URL (如新闻、博客文章)
  - **When**: 触发抓取任务
  - **Then**: 
    - 调用 `FirecrawlFetcher`
    - 通过本地部署的 Firecrawl 服务进行抓取
    - 返回清洗后的 Markdown 内容 (`content_text`)
    - 提取元数据 (Title, Description, Author, Publish Date)

- [ ] AC2: 动态内容渲染
  - **Given**: 一个依赖 JavaScript 渲染的 SPA 页面
  - **When**: 触发抓取
  - **Then**: 
    - Firecrawl 使用 Headless Browser (Playwright) 渲染页面
    - 等待 DOM 加载完成
    - 正确提取渲染后的文本内容

### Story 2: RSS 订阅抓取

As a 系统, I want 能够订阅 RSS 源并定期获取更新, So that 我能及时跟踪特定信源的最新动态。

**Acceptance Criteria:**

- [ ] AC1: RSS 解析
  - **Given**: 一个有效的 RSS/Atom Feed URL
  - **When**: 触发抓取
  - **Then**: 
    - 调用 `RSSFetcher`
    - 解析 XML 结构
    - 提取所有新的 Item
    - 自动去重 (基于 GUID 或 Link)

### Story 3: 抓取任务调度与重试

As a 系统, I want 自动调度抓取任务并处理失败, So that 数据获取过程无需人工干预且具有鲁棒性。

**Acceptance Criteria:**

- [ ] AC1: 定时调度
  - **Given**: 一批已激活的信息源
  - **When**: 到达预定抓取时间 (如每 4 小时)
  - **Then**: 
    - 生成抓取任务队列
    - `CrawlEngine` 逐个执行任务

- [ ] AC2: 错误重试
  - **Given**: 抓取过程中发生网络错误或超时
  - **When**: 任务失败
  - **Then**: 
    - 记录错误日志
    - 标记任务状态为 `FAILED`
    - 根据策略 (如指数退避) 安排重试 (最多 3 次)

## Architecture & Components

- **CrawlEngine**: 核心调度器，负责任务分发。
- **FetcherFactory**: 工厂模式，根据 Source Type (`WEB`, `RSS`) 创建对应的 Fetcher。
- **FirecrawlFetcher**: 封装 Firecrawl SDK，处理 Web 抓取。
- **RSSFetcher**: 封装 feedparser，处理 RSS 抓取。

## Constraints

- **资源限制**: 并发抓取数需限制，避免耗尽服务器资源 (特别是 Firecrawl Playwright)。
- **礼貌原则**: 遵守 `robots.txt` (如果配置开启)，避免对目标站点造成过大压力。
- **内容清洗**: 所有抓取内容必须转换为 Markdown 格式存储。

## Metadata

- 规模: 大
- 涉及模块: `crawl_engine`, `fetchers`, `scheduler`
- 涉及端: Backend
- 状态: 进行中
