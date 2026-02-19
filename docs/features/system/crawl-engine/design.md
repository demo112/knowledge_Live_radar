# Crawl Engine Design

## Overview
Crawl Engine 是 Knowledge Radar 的核心组件，负责从互联网抓取数据。
目前集成了 Firecrawl 作为主要抓取引擎，用于处理 `WEB` 类型的信息源。

## Architecture

```mermaid
graph TD
    User[用户] -->|添加信息源 URL| SourceAPI
    SourceAPI -->|存储| DB[(PostgreSQL)]
    
    Scheduler[定时任务] -->|触发抓取| CrawlEngine
    CrawlEngine -->|分发任务| FetcherFactory
    
    FetcherFactory -->|WEB类型| FirecrawlFetcher
    FetcherFactory -->|RSS类型| RSSFetcher
    
    subgraph "Firecrawl Service (Self-hosted)"
        FirecrawlFetcher -->|HTTP Request| FirecrawlAPI[Firecrawl API]
        FirecrawlAPI -->|能够处理| DynamicJS[动态网页渲染]
        FirecrawlAPI -->|能够处理| AntiBot[反爬虫对抗]
        FirecrawlAPI -->|能够处理| PDFParse[PDF解析]
        FirecrawlAPI -->|任务队列| Redis
        FirecrawlAPI -->|浏览器自动化| PlaywrightService
    end
    
    FirecrawlAPI -->|返回 Markdown| FirecrawlFetcher
    FirecrawlFetcher -->|清洗/结构化| ContentService
    ContentService -->|存入| ContentItem[ContentItem 表]
    ContentItem -->|触发| AIAnalysis[AI 深度分析]
```

## Components

### FirecrawlFetcher
- **职责**: 封装 Firecrawl SDK 调用逻辑，处理 HTTP 请求和响应映射。
- **输入**: URL
- **输出**: ContentItem (Markdown)
- **配置**: `FIRECRAWL_API_URL`, `FIRECRAWL_API_KEY`

### CrawlEngine
- **职责**: 根据 Source 类型选择 Fetcher，执行抓取任务。
- **Web Source**: 使用 `FirecrawlFetcher`。
- **RSS Source**: 使用 `RSSFetcher`。

## Deployment
Firecrawl 服务通过 Docker Compose 部署在本地，包含 API、Worker、Playwright 和 Redis 服务。
详情请参考 [Deployment Guide](../../deployment.md)。
