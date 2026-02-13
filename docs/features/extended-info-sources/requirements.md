# Requirements: 扩展信息源类型 (Extended Information Sources)

## Overview

当前系统的四种基础信息源类型（RSS, API, Web Crawl, User Contribution）无法满足用户对主流封闭生态内容（如微信公众号）和流媒体内容（视频平台）的获取需求。
本需求旨在扩展信息源类型，通过集成第三方服务或增强爬虫能力，支持国内外的公众号、长/短视频平台及技术社区，丰富知识雷达的输入源。

## User Stories

### Story 1: 支持微信公众号 (WeChat Official Accounts)

As a 知识管理者, I want 订阅微信公众号的文章, so that 我可以获取封闭生态内的优质内容

**Acceptance Criteria:**

- [ ] AC1: 添加公众号源
  - **Given**: 用户在添加源页面
  - **When**: 选择类型为 "WeChat Public Account"，输入公众号名称或 ID
  - **Then**: 系统识别并保存该源，初始状态为 "Pending"
- [ ] AC2: 抓取公众号文章
  - **Given**: 一个有效的公众号源
  - **When**: 触发抓取任务
  - **Then**: 获取最新发布的文章列表（标题、摘要、发布时间、原文链接），并尝试获取正文内容
- [ ] AC3: 异常处理
  - **Given**: 公众号被封禁或反爬策略生效
  - **When**: 抓取失败
  - **Then**: 记录错误日志，源状态更新为 "Error" 并提示原因

### Story 2: 支持长视频平台 (Bilibili & YouTube)

As a 视频学习者, I want 订阅 Bilibili 或 YouTube 的 UP 主/频道, so that 我可以将视频内容纳入知识库

**Acceptance Criteria:**

- [ ] AC1: 添加 Bilibili UP 主
  - **Given**: 用户拥有 UP 主的主页链接或 ID
  - **When**: 添加源并选择 "Bilibili User"
  - **Then**: 系统验证 UP 主存在并保存
- [ ] AC2: 添加 YouTube 频道
  - **Given**: 用户拥有 YouTube Channel ID
  - **When**: 添加源并选择 "YouTube Channel"
  - **Then**: 系统验证频道存在并保存
- [ ] AC3: 抓取视频元数据
  - **Given**: 视频源有更新
  - **When**: 触发抓取
  - **Then**: 获取视频标题、简介、封面图、发布时间、视频链接
- [ ] AC4: 获取视频字幕 (Transcript)
  - **Given**: 视频包含 CC 字幕
  - **When**: 抓取详情
  - **Then**: 提取字幕文本作为内容正文，用于后续 AI 分析

### Story 3: 支持技术社区 (Juejin, Medium, Dev.to)

As a 开发者, I want 订阅掘金或 Medium 的专栏/标签, so that 我能追踪技术动态

**Acceptance Criteria:**

- [ ] AC1: 平台适配器
  - **Given**: 支持掘金 (Juejin) 和 Medium
  - **When**: 输入专栏 URL
  - **Then**: 自动识别平台类型并配置对应的解析规则
- [ ] AC2: 内容提取
  - **Given**: 社区文章页面
  - **When**: 抓取内容
  - **Then**: 去除广告和评论，仅保留正文 Markdown/HTML

### Story 4: 统一适配器架构 (Adapter Architecture)

As a 开发者, I want 一个易扩展的适配器架构, so that 我可以轻松添加更多平台支持

**Acceptance Criteria:**

- [ ] AC1: 插件化接口
  - **Given**: 定义标准的 `SourceAdapter` 接口
  - **Then**: 实现 fetch, parse, validate 方法
- [ ] AC2: 配置化
  - **Given**: 新的源类型
  - **Then**: 可以通过配置文件或数据库配置其爬取策略（频率、并发限制）

## Constraints

- **反爬虫风险**: 微信公众号和视频平台有严格的反爬策略。建议优先通过 RSSHub 等中间件或第三方 API 解决，而非直接编写脆弱的爬虫。
- **视频内容**: 暂不进行视频下载和本地转码（成本过高），仅依赖平台提供的字幕或简介。
- **版权问题**: 抓取内容仅用于个人知识库构建，需遵守 `robots.txt` 和相关法律法规。

## Out of Scope

- **短视频 (Douyin/TikTok)**: 由于内容碎片化且缺乏结构化字幕，且反爬极严，暂不纳入第一阶段（除非通过 RSSHub 仅获取标题）。
- **视频转文字 (ASR)**: 暂不集成 Whisper 等本地模型进行语音转文字，仅依赖平台字幕。

## Assumptions

以下假设需用户确认：
- [ ] 接受使用 RSSHub (自建或公共服务) 作为部分平台的中间层。
- [ ] 视频源主要关注字幕内容，若无字幕则仅索引元数据。
- [ ] 公众号抓取接受一定的延迟（非实时）。

## Metadata

- 规模: 中
- 涉及模块: backend/crawl_engine, frontend/source_manager
- 创建时间: 2026-02-13
