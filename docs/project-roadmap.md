# 项目路线图

## 总体规划

### 核心演进路线 (Mindmap)

```mermaid
mindmap
  root((AI Radar))
    迭代1: 骨架搭建
      基础设施
      金字塔管理
      审批流基础
    迭代2: 全源感知
      抓取引擎
      多源校验
      信息流界面
    迭代3: 认知进化
      AI摘要与标签
      智能分类
      概念提取
    迭代4: 自我进化
      健康监测
      自动重构
      热点追踪
    迭代5: 生产就绪
      容器化部署
      性能优化
      监控告警
```

### 里程碑时间轴 (Timeline)

```mermaid
timeline
    title AI Radar 项目里程碑
    2026-02-01 : 项目启动
    2026-02-15 : MVP (骨架搭建完成)
               : 支持手动管理金字塔
    2026-02-28 : Alpha (全源感知)
               : 自动抓取与校验上线
    2026-03-15 : Beta (认知进化)
               : AI 分类与提案生成
    2026-03-31 : RC (自我进化)
               : 全功能压力测试
    2026-04-15 : Release v1.0
               : 正式上线
```

## 详细迭代计划 (Gantt)

```mermaid
gantt
    title AI Radar 迭代开发计划
    dateFormat  YYYY-MM-DD
    axisFormat  %m-%d
    excludes    weekends

    section 迭代 1: 骨架搭建
    环境搭建           :done,    des1, 2026-02-01, 2d
    数据库设计与迁移    :done,    des2, 2026-02-03, 3d
    金字塔后端API      :done,    des3, after des2, 4d
    金字塔前端可视化    :done,    des4, after des3, 5d
    审批流基础逻辑      :done,    des5, after des4, 3d

    section 迭代 2: 全源感知
    抓取引擎框架       :done,    perc1, 2026-02-16, 5d
    RSS/API/Web抓取器  :done,    perc2, after perc1, 5d
    三层校验机制       :done,    perc3, after perc2, 4d
    信息流前端界面      :done,    perc4, 2026-02-20, 5d

    section 迭代 3: 认知进化
    AI服务集成         :         cog1, 2026-03-01, 3d
    智能分类与摘要      :         cog2, after cog1, 5d
    概念提取与提案      :         cog3, after cog2, 5d
    用户多模态输入      :         cog4, 2026-03-05, 4d

    section 迭代 4: 自我进化
    健康度评估引擎      :         evo1, 2026-03-16, 5d
    自动重构建议       :         evo2, after evo1, 4d
    热点追踪系统       :         evo3, after evo2, 4d
    抓取策略自适应      :         evo4, 2026-03-20, 5d

    section 迭代 5: 生产就绪
    容器化部署         :         prod1, 2026-04-01, 3d
    性能优化(Redis)    :         prod2, after prod1, 4d
    监控告警体系       :         prod3, after prod2, 3d
    安全加固           :         prod4, 2026-04-10, 3d
```

## 价值与复杂度分析 (Quadrant)

```mermaid
quadrantChart
    title 功能模块价值 vs 复杂度
    x-axis Low Complexity --> High Complexity
    y-axis Low Value --> High Value
    quadrant-1 "High Value / High Complexity"
    quadrant-2 "High Value / Low Complexity"
    quadrant-3 "Low Value / Low Complexity"
    quadrant-4 "Low Value / High Complexity"

    "金字塔管理": [0.3, 0.8]
    "审批流": [0.4, 0.7]
    "抓取引擎": [0.7, 0.9]
    "三层校验": [0.6, 0.85]
    "AI智能分类": [0.8, 0.95]
    "概念提取": [0.9, 0.9]
    "可视化界面": [0.5, 0.6]
    "健康监测": [0.6, 0.5]
    "热点追踪": [0.7, 0.6]
    "多模态输入": [0.5, 0.4]
```

## 状态流转图 (State Diagram)

### 信息源生命周期

```mermaid
stateDiagram-v2
    [*] --> Discovered: 发现
    Discovered --> Verifying: 初始验证
    Verifying --> Active: 验证通过
    Verifying --> Dead: 验证失败
    Active --> Monitoring: 出现异常
    Monitoring --> Active: 恢复正常
    Monitoring --> Adjusting: 持续异常
    Adjusting --> Active: 调整策略成功
    Adjusting --> Dead: 调整失败
    Dead --> [*]
```

### 变更提案审批流

```mermaid
stateDiagram-v2
    [*] --> Pending: AI生成/用户提交
    Pending --> Approved: 管理员批准
    Pending --> Rejected: 管理员拒绝
    Approved --> Executing: 系统执行
    Executing --> Executed: 执行成功
    Executing --> Failed: 执行失败
    Failed --> Pending: 重试/修改
    Rejected --> [*]
    Executed --> [*]
```

## 风险评估 (Risk Assessment)

| 风险类别 | 风险描述 | 可能性 | 影响程度 | 缓解措施 |
|----------|----------|--------|----------|----------|
| **技术风险** | AI 幻觉导致错误分类或摘要 | 中 | 高 | 引入人工审批流 (Human-in-the-loop)；多模型交叉验证 |
| **法律风险** | 抓取数据侵犯版权或违反 robots.txt | 低 | 高 | 严格遵守 robots.txt；建立白名单机制；仅抓取摘要/元数据 |
| **性能风险** | 随着信息源增加，抓取和处理延迟过高 | 高 | 中 | 引入分布式任务队列 (Celery)；实现增量抓取；缓存热点数据 |
| **依赖风险** | 硅基流动 API 不稳定或涨价 | 中 | 中 | 设计适配器模式支持多 LLM 切换；建立本地缓存 |

## 资源需求 (Resource Requirements)

### 人力资源
- **后端开发**: 1人 (Python/FastAPI)
- **前端开发**: 1人 (Next.js/React)
- **产品/测试**: 0.5人 (兼任)

### 基础设施
- **开发环境**: 本地 Docker Desktop
- **生产环境**: 
  - 应用服务器: 2核 4G * 2
  - 数据库: PostgreSQL (云托管或自建)
  - 缓存: Redis (可选)
- **外部服务**:
  - 硅基流动 API (LLM)
  - 代理池 (可选，用于反爬虫)

## 成功度量 (Success Metrics)

| 维度 | 指标 | 目标值 (v1.0) |
|------|------|---------------|
| **覆盖度** | 接入高质量信息源数量 | > 50 个 |
| **准确度** | 自动分类准确率 | > 85% |
| **效率** | 从信息发现到入库的平均延迟 | < 10 分钟 |
| **活跃度** | 每日生成有效提案数量 | > 20 个 |
| **稳定性** | 系统可用性 | > 99.5% |
