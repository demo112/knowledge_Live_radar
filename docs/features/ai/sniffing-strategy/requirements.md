# Requirements: 嗅探优先的爬取策略 (Sniffing Strategy)

## Overview

调整现有的爬虫策略，从"高速全量爬取"转变为"低频拟人嗅探"。核心目标是**发现更新**而非暴力抓取，通过模拟人类行为、降低频率、增加随机性等手段，最大程度避免被目标网站屏蔽（403/429）。系统应能长期稳定地监控信息源，即使牺牲抓取速度也在所不惜。

## User Stories

### Story 1: 拟人化嗅探配置

As a 系统管理员, I want 系统能够模拟人类的浏览行为, so that 降低被目标网站识别为机器人的风险

**Acceptance Criteria:**

- [ ] AC1: User-Agent 轮询
  - **Given**: 爬虫引擎准备请求目标 URL
  - **When**: 发起 HTTP 请求
  - **Then**: 请求头中的 `User-Agent` 应从预置的主流浏览器 UA 池中随机选择，而不是使用固定的 Python/httpx 标识

- [ ] AC2: 请求间隔随机化
  - **Given**: 对同一个域名连续发起多次请求
  - **When**: 执行连续请求
  - **Then**: 两次请求之间的间隔应包含随机抖动（例如 `base_delay ± random_jitter`），避免出现机械的固定频率

- [ ] AC3: 引用页（Referer）伪造
  - **Given**: 爬虫引擎请求内页
  - **When**: 发起请求
  - **Then**: 请求头中的 `Referer` 应合理设置为该域名的首页或上一级页面

### Story 2: 自适应速率控制

As a 爬虫引擎, I want 根据目标网站的反馈自动调整抓取频率, so that 在遇到限流时能够自动避让

**Acceptance Criteria:**

- [ ] AC1: 429/403 自动避让
  - **Given**: 目标网站返回 429 (Too Many Requests) 或 403 (Forbidden)
  - **When**: 接收到响应
  - **Then**: 系统应暂停对该域名的抓取，进入"冷却期"（如 1-2 小时），并在冷却期结束后以更低的频率重试

- [ ] AC2: 嗅探模式（Sniffing Mode）
  - **Given**: 定时检查信息源
  - **When**: 执行检查
  - **Then**: 优先检查 `Last-Modified` / `ETag` 或仅抓取 RSS/入口页，仅当发现有新内容时才触发进一步的详情页抓取

### Story 3: 慢速抓取策略

As a 系统管理员, I want 默认采用慢速抓取, so that 减少对目标服务器的压力并隐藏自身

**Acceptance Criteria:**

- [ ] AC1: 默认长间隔
  - **Given**: 新增一个信息源
  - **When**: 初始化爬取策略
  - **Then**: 默认检查间隔应较长（如 1-4 小时），除非人工特别指定高频

- [ ] AC2: 任务队列优先级调整
  - **Given**: 系统中有多个待抓取任务
  - **When**: 调度器分发任务
  - **Then**: 确保并发度控制在较低水平（如全局并发 < 5，单域名并发 = 1），优先处理"嗅探"任务而非"全量下载"任务

## Constraints

- **性能约束**: 放弃高吞吐量指标，接受抓取延迟（从分钟级容忍到小时级）。
- **技术约束**: 暂时不引入 Headless Browser (Playwright/Selenium) 以保持架构轻量，优先通过协议层（HTTP Headers/TLS）优化。
- **合规约束**: 严格遵守 `robots.txt` 规则（如果配置开启）。

## Out of Scope

- **验证码识别**: 遇到验证码直接放弃或报警，不尝试破解。
- **JS 动态渲染**: 暂时仅支持服务端渲染页面或 API，复杂的 SPA 放在后续通过 Headless 方案解决。
- **IP 代理池**: 本次迭代暂不引入付费代理池，依靠低频策略复用本机 IP。

## Assumptions

- 目标网站主要是通过请求频率和 UA 特征进行反爬。
- 用户接受信息的实时性有所降低（不是毫秒级新闻，而是知识雷达）。
