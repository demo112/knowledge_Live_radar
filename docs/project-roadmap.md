# 项目路线图 (Project Roadmap)

> **最后更新**: 2026-02-20
> **核心原则**: AI-First (AI优先), Evolution-Driven (进化驱动)
> **状态**: 🟢 进行中

## 总体规划 (Master Plan)

### 核心演进路线 (Mindmap)

```mermaid
mindmap
  root((AI Radar))
    迭代0: AI核心基座
      AIFacade层
      Prompt管理
      结构化输出
      提案系统基础
    迭代1: 智能骨架
      AI辅助创建金字塔
      可视化交互
      变更审批流
    迭代2: 全源感知
      Firecrawl引擎
      AI内容清洗
      三层校验机制
    迭代3: 认知进化
      健康度监测
      自动重构提案
      概念漂移检测
    迭代4: 生产就绪
      容器化部署
      性能优化
      全链路监控
```

### 里程碑时间轴 (Timeline)

```mermaid
timeline
    title AI Radar 项目里程碑
    2026-02-20 : 迭代0 (AI Core)
               : 建立 AI 认知中枢
    2026-03-01 : 迭代1 (Smart Skeleton)
               : AI 辅助生成金字塔
    2026-03-15 : 迭代2 (Perception)
               : 全源抓取与智能清洗
    2026-03-25 : 迭代3 (Evolution)
               : 结构自进化与重构
    2026-04-05 : Release v1.0
               : 生产环境上线
```

## 详细迭代计划 (Gantt)

```mermaid
gantt
    title AI Radar 迭代开发计划
    dateFormat  YYYY-MM-DD
    axisFormat  %m-%d
    excludes    weekends

    section 迭代 0: AI核心基座 (Current)
    AI Facade架构设计       :active,    ai1, 2026-02-20, 2d
    Prompt管理系统          :           ai2, after ai1, 2d
    结构化输出(Pydantic)    :           ai3, after ai2, 2d
    提案(Proposal)数据模型  :           ai4, after ai3, 2d
    
    section 迭代 1: 智能骨架
    AI生成金字塔结构        :           sk1, after ai4, 3d
    ReactFlow可视化交互     :           sk2, after sk1, 4d
    变更审批流(前端+后端)   :           sk3, after sk2, 3d
    
    section 迭代 2: 全源感知
    Firecrawl抓取引擎       :           pc1, 2026-03-08, 4d
    AI内容清洗与摘要        :           pc2, after pc1, 3d
    三层校验(硬/软/交叉)    :           pc3, after pc2, 3d
    
    section 迭代 3: 认知进化
    健康度监测引擎          :           ev1, 2026-03-18, 3d
    结构重构提案(Split/Merge):          ev2, after ev1, 4d
    概念漂移检测            :           ev3, after ev2, 3d
    
    section 迭代 4: 生产就绪
    容器化与CI/CD           :           pr1, 2026-03-28, 3d
    Redis缓存与性能优化      :           pr2, after pr1, 3d
    全链路日志与监控        :           pr3, after pr2, 2d
```

## 迭代详情

### 迭代 0: AI核心基座 (AI Core Infrastructure)
> **目标**: 建立"AI-First"的技术底座，确保所有业务功能都能调用统一的 AI 能力。

- **核心任务**:
    - [ ] **AI Facade**: 封装 LLM 调用，支持多模型切换 (SiliconFlow/DeepSeek)。
    - [ ] **Prompt Manager**: 建立 Prompt 模板版本管理机制。
    - [ ] **Structured Output**: 封装 `Instructor` 或类似库，确保 AI 输出严格符合 Pydantic Schema。
    - [ ] **Proposal System**: 定义 `ChangeProposal` 和 `AISuggestion` 的数据库模型。

### 迭代 1: 智能骨架 (Smart Skeleton)
> **目标**: 实现"AI 提议 -> 人类决策"的交互闭环，完成金字塔的智能创建。

- **核心任务**:
    - [ ] **AI-Assisted Creation**: 用户输入意图 -> AI 生成金字塔结构 JSON。
    - [ ] **Visual Interaction**: 前端使用 ReactFlow 展示 AI 生成的结构，允许用户微调。
    - [ ] **Approval Workflow**: 实现"提案-审批-执行"的状态流转。

### 迭代 2: 全源感知 (Intelligent Perception)
> **目标**: 接入外部信息源，并利用 AI 进行高质量清洗。

- **核心任务**:
    - [ ] **Crawl Engine**: 集成 Firecrawl，处理动态网页。
    - [ ] **AI Processing**: 对抓取内容进行摘要、标签提取、情感分析。
    - [ ] **Validation Pipeline**: 实现硬性规则 + AI 软性校验。

### 迭代 3: 认知进化 (Cognitive Evolution)
> **目标**: 让系统具备生命力，能主动发现结构问题。

- **核心任务**:
    - [ ] **Health Monitor**: 定期扫描金字塔，计算节点健康度 (信息熵/拥挤度)。
    - [ ] **Evolution Strategy**: 实现节点拆分 (Split) 和合并 (Merge) 的算法策略。
    - [ ] **Drift Detection**: 识别新出现的概念热点。

## 价值与复杂度分析

```mermaid
quadrantChart
    title 功能模块价值 vs 复杂度
    x-axis Low Complexity --> High Complexity
    y-axis Low Value --> High Value
    quadrant-1 "高价值 / 高复杂度 (攻坚)"
    quadrant-2 "高价值 / 低复杂度 (速赢)"
    quadrant-3 "低价值 / 低复杂度 (填充)"
    quadrant-4 "低价值 / 高复杂度 (避免)"

    "AI Facade": [0.3, 0.9]
    "AI生成结构": [0.4, 0.85]
    "可视化交互": [0.6, 0.7]
    "Firecrawl引擎": [0.7, 0.8]
    "自动重构提案": [0.8, 0.95]
    "审批流": [0.4, 0.6]
    "监控告警": [0.5, 0.4]
```

## 资源需求

- **LLM Token**: 预计开发期每日消耗 1M Tokens (DeepSeek-V3)。
- **Crawl Service**: Firecrawl API额度或自建服务。
- **Database**: PostgreSQL (生产) / SQLite (开发)。

## 风险评估

| 风险类别 | 风险描述 | 缓解措施 |
|----------|----------|----------|
| **AI 幻觉** | AI 生成错误的金字塔结构或分类 | 必须经过**可视化确认**和**人工审批** (HitL)。 |
| **结构稳定性** | 频繁的自动重构导致用户迷失 | 限制重构频率，保留历史版本快照。 |
| **抓取反爬** | 目标站点反爬策略升级 | 使用 Firecrawl 代理池，设置礼貌抓取间隔。 |
