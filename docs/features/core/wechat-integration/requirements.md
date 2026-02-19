# Requirements: 微信公众号信息源支持

## Overview

在 Knowledge Radar 中支持添加微信公众号作为信息源。由于微信生态的封闭性，直接抓取非常困难且不稳定。经过技术调研，我们推荐通过 **RSS 桥接** 的方式接入微信公众号，既能复用系统现有的 RSS 解析能力，又能保证数据获取的稳定性。

## Analysis

### 难点分析

1.  **封闭生态**：微信公众号文章不像普通网页那样开放，官方接口仅面向运营者。
2.  **反爬严格**：搜狗微信搜索等入口有严格的验证码机制，且 IP 容易被封禁。
3.  **维护成本高**：直接模拟浏览器行为（如 Playwright）需要频繁处理页面结构变化和验证码，维护成本极高。

### 解决方案对比

| 方案 | 原理 | 稳定性 | 成本 | 推荐指数 |
|---|---|---|---|---|
| **RSS 桥接 (推荐)** | 使用第三方工具 (如 WeWe RSS) 将公众号转为标准 RSS 链接，系统直接订阅。 | ⭐⭐⭐⭐⭐ | 低 (需部署工具) | ⭐⭐⭐⭐⭐ |
| **Playwright 模拟** | 模拟浏览器访问搜狗搜索抓取。 | ⭐⭐ | 高 (开发+维护) | ⭐⭐ |
| **官方 API** | 使用微信公众平台 API。 | ⭐⭐⭐ | 高 (需认证账号) | ⭐ |

### 推荐方案：WeWe RSS

**WeWe RSS** 是一个开源工具，利用微信读书 (WeChat Read) 的接口生成公众号 RSS。
- **优点**：稳定、免费、支持全文抓取。
- **缺点**：需要用户自行部署一个 Docker 服务（或使用公开服务）。

## User Stories

### Story 1: 通过 RSS URL 添加公众号

As a 用户, I want 将微信公众号的 RSS 链接添加到系统, so that 我可以在 Knowledge Radar 中阅读公众号文章

**Acceptance Criteria:**

- [ ] AC1: 支持添加标准 RSS 链接
  - **Given**: 用户已获取微信公众号的 RSS 链接（例如来自 WeWe RSS）
  - **When**: 用户在“添加信息源”页面输入该 URL，类型选择“RSS”
  - **Then**: 系统成功识别并添加该信源，开始抓取文章

- [ ] AC2: 自动识别 RSS 类型
  - **Given**: 用户输入一个 URL
  - **When**: 点击“检测”
  - **Then**: 系统自动识别其为 RSS 类型，并显示预览文章

### Story 2: 通过文章链接自动解析添加

As a 用户, I want 输入一篇微信公众号文章链接就能自动添加该公众号, so that 我不需要手动查找 RSS 地址或公众号 ID。

**Acceptance Criteria:**

- [ ] AC1: 解析文章链接提取信息
  - **Given**: 用户拥有一篇微信公众号文章链接 (如 `https://mp.weixin.qq.com/s/...`)
  - **When**: 用户在“添加信息源”页面输入该链接，类型选择“WECHAT_MP”
  - **Then**: 
    - 系统自动从 HTML 中提取公众号名称 (`nickname`) 和 BizID (`__biz`)
    - 自动填充“公众号名称”字段
    - 自动生成适配 RSSHub 的 URL (如 `https://rsshub.app/wechat/gzh/{id}`)

- [ ] AC2: 映射到 RSSHub 路由
  - **Given**: 系统成功提取了 BizID 或公众号 ID
  - **When**: 保存信息源
  - **Then**: 
    - 创建类型为 `WECHAT_MP` 的信息源
    - `rss_url` 字段指向正确的 RSSHub 路由
    - 系统立即触发一次抓取验证有效性

### Story 3: (可选) 系统内置 WeWe RSS 集成

> **注意**：此功能作为进阶选项，需要额外的开发工作量。

As a 用户, I want 在系统内直接搜索公众号名称并添加, so that 我不需要自己部署 RSS 工具

**Acceptance Criteria:**

- [ ] AC1: 搜索公众号
  - **Given**: 系统已配置 WeWe RSS 服务地址（作为后端服务）
  - **When**: 用户输入公众号名称
  - **Then**: 系统调用 WeWe RSS 接口搜索，并返回公众号列表

- [ ] AC2: 一键添加
  - **Given**: 搜索结果列表中显示公众号
  - **When**: 用户点击“添加”
  - **Then**: 系统自动获取其 RSS 链接并添加为信源

## Constraints

- **依赖性**：方案严重依赖第三方 RSS 工具（如 WeWe RSS 或 RSSHub）的稳定性。
- **部署要求**：用户可能需要自行部署 WeWe RSS 服务（Docker）。
- **版权风险**：抓取内容仅供个人学习研究，不得用于商业用途。

## Out of Scope

- **不直接破解微信协议**：我们不开发破解微信客户端协议的爬虫。
- **不保证历史全量**：RSS 通常只提供最近的文章，不保证能获取所有历史文章。
- **不处理付费文章**：仅支持公开访问的文章。

## Assumptions

以下假设已与用户确认：
- [x] 用户接受使用 RSS 方式接入微信公众号。
- [x] 用户愿意（或已经）使用 WeWe RSS / RSSHub 等工具。
- [x] 系统现有的 RSS 解析能力足以处理微信 RSS 格式。

## Metadata

- 规模：中
- 涉及模块：source-manager, crawl-engine
- 涉及端：Backend, Frontend
- 创建时间：2026-02-14
- 更新时间：2026-02-19
- 状态：已确认
