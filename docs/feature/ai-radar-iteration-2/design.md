# 设计文档 - 迭代 2：信息抓取

## 概述

本设计文档描述 AI Radar 系统迭代 2 的技术实现方案。迭代 2 的目标是实现动态信息源管理和内容抓取校验机制。

## 架构设计

### 抓取系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        抓取调度器                                │
│           (SchedulerService / TaskRegistry)                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │  RSS_Fetcher  │ │  API_Fetcher  │ │  Web_Fetcher  │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            └─────────────────┼─────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        去重服务                                  │
│                  (DeduplicationService)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        校验流水线                                │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Hard_Validator │  Soft_Validator │    Cross_Validator          │
│   (规则校验)    │   (AI 校验)     │     (交叉验证)              │
└─────────────────┴────────┬────────┴─────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        内容处理                                  │
├─────────────────────────┬───────────────────────────────────────┤
│   AI_Summary_Service    │      Content_Classifier               │
│     (摘要生成)          │        (内容分类)                     │
└─────────────────────────┴───────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储                                  │
│                    (Content_Items)                              │
└─────────────────────────────────────────────────────────────────┘
```

### 信息源生命周期状态机

```
                    ┌──────────────┐
                    │  discovered  │ ← 新创建
                    └──────┬───────┘
                           │ 首次抓取成功
                           ▼
                    ┌──────────────┐
                    │   verified   │
                    └──────┬───────┘
                           │ 连续3次成功
                           ▼
              ┌───────────────────────────┐
              │          active           │ ←──────────────┐
              └─────────────┬─────────────┘                │
                            │ 失败率>30%                   │ 恢复正常
                            ▼                              │
              ┌───────────────────────────┐                │
              │        monitoring         │ ───────────────┘
              └─────────────┬─────────────┘
                            │ 连续7天异常
                            ▼
              ┌───────────────────────────┐
              │        adjusting          │ → 生成 Change_Proposal
              └─────────────┬─────────────┘
                            │ 人工判定无效
                            ▼
              ┌───────────────────────────┐
              │         retired           │ → 停止抓取
              └───────────────────────────┘
```

## 目录结构

```
backend/
├── app/
│   ├── services/
│   │   ├── fetchers/                # 抓取引擎
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # 抓取器基类
│   │   │   ├── rss.py               # RSS 抓取器
│   │   │   ├── api.py               # API 抓取器
│   │   │   └── web.py               # 网页抓取器
│   │   ├── validator/               # 校验引擎
│   │   │   ├── __init__.py
│   │   │   ├── hard_validator.py    # 硬性校验
│   │   │   ├── soft_validator.py    # 软性校验（AI）
│   │   │   └── cross_validator.py   # 交叉验证
│   │   ├── scheduler/               # 调度器
│   │   │   ├── scheduler_service.py # 调度服务
│   │   │   └── tasks.py             # 任务定义
│   │   ├── ai_service.py            # AI 服务
│   │   ├── content_processor.py     # 内容处理
│   │   ├── lifecycle_manager.py     # 生命周期管理
│   │   ├── auto_discovery.py        # 自动发现 (SourceDiscoveryService)
│   │   ├── whitelist_service.py     # 白名单管理
│   │   ├── source_template_service.py # 信息源模板服务 (新增)
│   │   └── ...
│   ├── models/
│   │   ├── crawl_job.py             # 抓取任务记录
│   │   ├── domain_whitelist.py      # 域名白名单
│   │   ├── discovered_domain.py     # 发现的域名
│   │   └── ...
```

## 数据模型

### 抓取任务记录

```python
class CrawlJob(Base):
    __tablename__ = "crawl_jobs"
    
    id: str                    # UUID
    source_id: str             # 信息源 ID
    status: str                # running/success/failed
    started_at: datetime       # 开始时间
    ended_at: datetime | None  # 结束时间
    items_fetched: int         # 抓取条目数
    items_new: int             # 新增条目数
    items_duplicate: int       # 重复条目数
    error_message: str | None  # 错误信息
    response_time_ms: int | None  # 响应时间
```

### 域名白名单

```python
class DomainWhitelist(Base):
    __tablename__ = "domain_whitelist"
    
    id: str                    # UUID
    domain: str                # 域名（支持通配符）
    credibility: str           # authoritative/normal/unverified
    reason: str                # 添加原因
    created_at: datetime
    is_deleted: bool
```

### 发现的域名记录

```python
class DiscoveredDomain(Base):
    __tablename__ = "discovered_domains"
    
    id: str                    # UUID
    domain: str                # 域名
    occurrence_count: int      # 出现次数
    first_seen_at: datetime    # 首次发现时间
    last_seen_at: datetime     # 最后发现时间
    evaluation_status: str     # pending/evaluated/proposed/rejected
    has_rss: bool | None       # 是否有 RSS
    proposal_id: str | None    # 关联的提案 ID
```

## 组件接口设计

### 信息源模板服务 (SourceTemplateService)

```python
# services/source_template_service.py
class SourceTemplateService:
    def get_templates(self) -> list[dict]:
        """
        获取所有信息源配置模板
        返回:
        [
            {
                "id": "arxiv_rss",
                "name": "arXiv RSS",
                "type": "rss",
                "config_schema": {...},
                "default_config": {
                    "url": "http://export.arxiv.org/rss/cs.AI",
                    "content_selector": "summary"
                }
            },
            {
                "id": "github_trending",
                "name": "GitHub Trending",
                "type": "api",
                "default_config": {...}
            },
            ...
        ]
        """
        pass

    def apply_template(self, template_id: str, params: dict) -> dict:
        """
        应用模板生成配置
        """
        pass
```

### 信息源自动发现服务 (SourceDiscoveryService)

```python
# services/auto_discovery.py
class SourceDiscoveryService:
    async def process_content_links(self, content: str, session: AsyncSession):
        """
        从内容中提取链接，更新 DiscoveredDomain
        1. 提取 URL 域名
        2. 过滤白名单和黑名单
        3. 更新 occurrence_count
        4. 如果 count > threshold，触发 evaluate_domain
        """
        pass

    async def evaluate_domain(self, domain_record: DiscoveredDomain, session: AsyncSession):
        """
        评估域名
        1. 检查是否已有 RSS
        2. 检查域名权威性 (调用 WhitelistService)
        3. 如果通过，生成 ChangeProposal (创建新 Source 提案)
        """
        pass
```

### 生命周期管理器 (LifecycleManager)

```python
# services/lifecycle_manager.py
class LifecycleManager:
    async def update_source_status(self, source: InformationSource, job: CrawlJob, session: AsyncSession):
        """
        根据抓取结果更新状态机
        - FAILED -> error_count++
        - SUCCESS -> error_count=0, verified
        - error_count >= 3 -> status=ERROR (active -> monitoring?)
        - 连续失败检测 -> monitoring
        - 长期失败检测 -> adjusting
        """
        pass

    async def check_monitoring_sources(self, session: AsyncSession):
        """
        定期任务：检查 monitoring 状态的信息源
        - 如果恢复正常 -> active
        - 如果持续异常 -> adjusting
        """
        pass
```

## API 端点

```python
# 信息源模板
GET  /api/v1/sources/templates              # 获取配置模板

# 抓取任务
GET  /api/v1/crawl-jobs                     # 获取任务列表
GET  /api/v1/crawl-jobs/{job_id}            # 获取任务详情
POST /api/v1/sources/{source_id}/crawl      # 触发即时抓取

# 域名白名单
GET  /api/v1/whitelist                      # 获取白名单
POST /api/v1/whitelist                      # 添加
DELETE /api/v1/whitelist/{id}               # 删除

# 仪表板
GET  /api/v1/dashboard/stats                # 综合统计
```

## 技术决策

1.  **模板实现**：使用 `SourceTemplateService` 独立管理信息源模板，不与 `TemplateService` (金字塔模板) 混淆。
2.  **自动发现**：`AutoDiscovery` 从单纯的工具类升级为服务类，负责维护 `DiscoveredDomain` 状态。
3.  **状态机**：在 `LifecycleManager` 中集中管理状态转换逻辑，而不是分散在各个 Fetcher 中。

## 风险点

1.  **抓取频率限制**：需要确保 `WebFetcher` 严格遵守频率限制，避免被封禁。
2.  **AI 成本**：自动发现和内容分类大量调用 AI，需监控 Token 消耗。
