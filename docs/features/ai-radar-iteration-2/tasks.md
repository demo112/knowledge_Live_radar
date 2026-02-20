# 实现计划：AI Radar 迭代 2 - 信息抓取

## 概述

本任务列表描述 AI Radar 系统迭代 2 的实现步骤。目标是实现动态信息源管理、多类型抓取引擎和三层校验机制。

## 任务状态

- [x] 已完成
- [ ] 待办/进行中

## 任务列表

### 1. 数据模型与迁移
- [x] 1.1 创建抓取任务记录模型 (`CrawlJob`)
- [x] 1.2 创建域名白名单模型 (`DomainWhitelist`)
- [x] 1.3 创建发现域名记录模型 (`DiscoveredDomain`)
- [x] 1.4 扩展信息源模型 (添加生命周期字段)
- [x] 1.5 执行数据库迁移

### 2. 基础服务 (Fetchers & AI)
- [x] 2.1 实现 AI 客户端 (`SiliconFlowClient`)
    - [x] 基础聊天接口
    - [x] 指数退避重试
- [x] 2.2 实现 RSS 抓取器 (`RSSFetcher`)
- [x] 2.3 实现 API 抓取器 (`APIFetcher`)
- [x] 2.4 实现网页抓取器 (`WebFetcher`)

### 3. 校验与处理服务
- [x] 3.1 实现硬性校验器 (`HardValidator`)
- [x] 3.2 实现软性校验器 (`SoftValidator`)
- [x] 3.3 实现交叉验证器 (`CrossValidator`)
- [x] 3.4 实现去重服务 (`DeduplicationService`)
- [x] 3.5 实现摘要生成与分类 (`ContentProcessor`, `AIService`)

### 4. 业务逻辑 (核心差异补全)
- [x] 4.1 完善生命周期管理 (`LifecycleManager`)
    - [x] 实现完整的状态机逻辑 (active <-> monitoring <-> adjusting)
    - [x] 实现 `check_monitoring_sources` 定时检查逻辑
    - [x] 实现 `adjusting` 状态生成 ChangeProposal 逻辑
- [x] 4.2 完善自动发现服务 (`SourceDiscoveryService`)
    - [x] 实现 `process_content_links` (提取、计数)
    - [x] 实现 `evaluate_domain` (权威性检查、RSS检测)
    - [x] 集成到 `ContentProcessor` 流程中
- [x] 4.3 实现信息源配置模板 (`SourceTemplateService`)
    - [x] 创建 `services/source_template_service.py`
    - [x] 实现 arXiv RSS 模板
    - [x] 实现 GitHub Trending 模板
    - [x] 实现 HuggingFace Daily Papers 模板
    - [x] 实现通用博客 RSS 模板
- [x] 4.4 完善抓取调度器 (`SchedulerService`)
    - [x] 确认优先级队列实现
    - [x] 确认并发控制实现

### 5. API 接口
- [x] 5.1 抓取任务 API (`crawl_jobs`)
- [x] 5.2 白名单 API (`whitelist`)
- [x] 5.3 仪表板 API (`dashboard`)
- [x] 5.4 信息源模板 API
    - [x] `GET /api/v1/sources/templates`

### 6. 前端界面
- [x] 6.1 增强信息源管理
    - [x] 显示生命周期状态 (Frontend)
    - [x] 显示抓取历史 (Frontend)
    - [x] 集成模板选择功能 (在创建/编辑弹窗中)
- [x] 6.2 增强内容列表
    - [x] 显示校验状态徽章
    - [x] 显示质量分数
- [x] 6.3 仪表板页面
    - [x] 实现统计卡片
    - [x] 实现图表展示

### 7. 集成与测试
- [x] 7.1 编写集成测试
    - [x] 完整抓取流程测试
    - [x] 生命周期状态流转测试
- [x] 7.2 回归测试
    - [x] 验证对原有金字塔功能无影响

## 优先级排序

1. **High**: 4.3 (模板服务) - 阻碍用户方便地添加源
2. **High**: 4.1 (生命周期) - 系统自动化的核心
3. **Medium**: 6.1 (前端增强) - 提升管理体验
4. **Medium**: 4.2 (自动发现) - 增强系统进化能力
