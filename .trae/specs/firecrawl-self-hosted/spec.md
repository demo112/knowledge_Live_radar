# Firecrawl Self-Hosted Integration Spec

## Why
目前 `crawl_engine.py` 仅为框架，无法处理动态网页且缺乏高质量的 Markdown 提取能力。为了支持 AI Radar 的核心“知识聚合”能力，我们需要引入成熟的网页抓取引擎。
选择 Firecrawl 的 **Self-hosted (私有化部署)** 模式，可以直接获得高质量的 LLM-ready 数据，同时保证数据隐私完全可控，且无外部 API 调用成本。

## What Changes
### Infrastructure
-   修改 `docker-compose.yml`，增加 Firecrawl 相关服务：
    -   `firecrawl-api`: 核心 API 服务
    -   `firecrawl-worker`: 任务队列处理
    -   `playwright-service`: 浏览器自动化服务
    -   `redis`: 任务队列与缓存 (复用或新增)

### Backend
-   **依赖管理**:
    -   `backend/requirements.txt`: 添加 `firecrawl-py` 库。
-   **配置管理**:
    -   `backend/.env`: 添加 `FIRECRAWL_API_URL` (指向本地 Docker 服务) 和 `FIRECRAWL_API_KEY` (自托管可留空或随意填)。
    -   `backend/app/core/config.py`: 映射上述环境变量。
-   **代码实现**:
    -   新增 `backend/app/services/fetchers/firecrawl_fetcher.py`: 封装 Firecrawl SDK 调用逻辑。
    -   修改 `backend/app/services/fetchers/__init__.py`: 注册 fetcher。
    -   修改 `backend/app/services/crawl_engine.py`: 在 `get_fetcher` 中接入 `FirecrawlFetcher` 处理 `WEB` 类型源。

## Impact
-   **Affected Specs**: `docs/features/crawl-engine-design.md` (需更新架构图)
-   **Affected Code**:
    -   `docker-compose.yml` (新增服务)
    -   `backend/app/services/crawl_engine.py` (逻辑变更)
    -   `backend/app/models/source.py` (无直接变更，但数据流入质量提升)

## ADDED Requirements
### Requirement: Local Firecrawl Service
系统必须在本地 Docker 环境中运行 Firecrawl 服务，且能够通过 HTTP 接口访问。

#### Scenario: Service Health
-   **WHEN** 请求 `http://localhost:3002/test`
-   **THEN** 返回 `Hello, world!` 或状态 200。

### Requirement: Web Crawling via Firecrawl
系统必须使用本地 Firecrawl 服务抓取 `WEB` 类型的信息源。

#### Scenario: Fetch Web Page
-   **WHEN** `CrawlEngine` 接收到 `WEB` 类型的 `InformationSource`
-   **THEN** 调用 `FirecrawlFetcher`
-   **AND** `FirecrawlFetcher` 调用本地 Firecrawl API
-   **AND** 返回包含 `content_text` (Markdown) 的抓取结果

## MODIFIED Requirements
### Requirement: Crawl Engine Strategy
原有的 `WEB` 抓取占位逻辑将被替换为 Firecrawl 实现。
**Reason**: 提供真实的抓取能力。
**Migration**: 无需数据迁移，直接替换逻辑。
