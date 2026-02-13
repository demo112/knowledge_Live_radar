---
name: evolution-loop
description: "进化循环实现指南：健康评估、重构建议、热点管理、漂移检测、策略自适应的实质化实现参考。"
type: reference
applies_to: server
triggers:
  - 进化
  - 健康
  - 重构
  - 热点
  - 漂移
  - 策略
  - 自适应
---

# 进化循环实现指南

AI Radar 的核心差异化能力在于「自进化」。本 Skill 提供进化循环各环节的实现参考，帮助将桩代码转化为实质逻辑。

---

## 进化循环全景

```
感知(抓取) → 理解(校验+分类) → 评估(健康检测) → 建议(重构/策略) → 审批 → 执行 → 反馈
```

每个环节都必须有实质逻辑，不允许空壳通过。

---

## 模块一：健康评估器 (Health Evaluator)

### 当前问题
`activity_score = 100` 硬编码，无真实计算。

### 实现要求

#### 金字塔健康度

```python
async def evaluate_pyramid_health(self, pyramid_id: int) -> HealthReport:
    """评估金字塔健康度，返回 0-100 分"""

    # 1. 深度平衡性（各分支深度差异）
    depths = await self._get_branch_depths(pyramid_id)
    max_depth = max(depths) if depths else 0
    min_depth = min(depths) if depths else 0
    depth_balance = 100 - (max_depth - min_depth) * 15  # 每层差异扣 15 分

    # 2. 节点覆盖度（空节点 vs 过载节点）
    node_stats = await self._get_node_content_stats(pyramid_id)
    empty_ratio = node_stats["empty_count"] / max(node_stats["total_count"], 1)
    coverage_score = 100 - empty_ratio * 100

    # 3. 更新活跃度（近 7 天内容更新频率）
    recent_count = await self._get_recent_content_count(pyramid_id, days=7)
    total_nodes = node_stats["total_count"]
    activity_score = min(100, (recent_count / max(total_nodes, 1)) * 100)

    # 综合评分
    overall = depth_balance * 0.3 + coverage_score * 0.4 + activity_score * 0.3
    return HealthReport(
        overall=round(overall),
        depth_balance=round(depth_balance),
        coverage=round(coverage_score),
        activity=round(activity_score),
        issues=self._identify_issues(depth_balance, coverage_score, activity_score),
    )
```

#### 信息源健康度

```python
async def evaluate_source_health(self, source_id: int) -> SourceHealthReport:
    """评估信息源健康度"""

    # 1. 可达性：最近 N 次抓取的成功率
    jobs = await self._get_recent_crawl_jobs(source_id, limit=10)
    success_rate = sum(1 for j in jobs if j.status == "completed") / max(len(jobs), 1)

    # 2. 更新频率：实际更新间隔 vs 预期间隔
    frequency_score = await self._evaluate_update_frequency(source_id)

    # 3. 内容质量：最近内容的平均质量分
    avg_quality = await self._get_avg_content_quality(source_id, limit=20)

    # 4. 响应时间：平均响应时间评分
    avg_response = await self._get_avg_response_time(source_id)
    response_score = max(0, 100 - avg_response / 100)  # 每 100ms 扣 1 分

    overall = success_rate * 30 + frequency_score * 0.25 + avg_quality * 0.25 + response_score * 0.2
    return SourceHealthReport(overall=round(overall), ...)
```

---

## 模块二：重构建议器 (Restructure Advisor)

### 当前问题
空壳，无检测和建议逻辑。

### 实现要求

```python
async def analyze_and_suggest(self, pyramid_id: int) -> list[ChangeProposal]:
    """分析金字塔结构问题，生成重构建议"""
    proposals = []

    # 1. 检测过载节点（内容数 > 阈值）→ 建议拆分
    overloaded = await self._find_overloaded_nodes(pyramid_id, threshold=50)
    for node in overloaded:
        proposals.append(ChangeProposal(
            type="node_split",
            target_id=node.id,
            reason=f"节点 '{node.name}' 包含 {node.content_count} 条内容，建议拆分",
            suggestion=await self._ai_suggest_split(node),
        ))

    # 2. 检测空节点（30天无内容）→ 建议删除或合并
    empty = await self._find_empty_nodes(pyramid_id, days=30)
    for node in empty:
        sibling = await self._find_merge_candidate(node)
        if sibling:
            proposals.append(ChangeProposal(type="node_merge", ...))
        else:
            proposals.append(ChangeProposal(type="node_delete", ...))

    # 3. 检测层级过深（> 5 层）→ 建议扁平化
    deep_branches = await self._find_deep_branches(pyramid_id, max_depth=5)
    for branch in deep_branches:
        proposals.append(ChangeProposal(type="flatten", ...))

    # 4. 检测同级节点过多（> 10 个）→ 建议分组
    wide_nodes = await self._find_wide_nodes(pyramid_id, max_children=10)
    for node in wide_nodes:
        proposals.append(ChangeProposal(type="group", ...))

    return proposals
```

---

## 模块三：热点管理器 (Hotspot Manager)

### 当前问题
空壳，无生命周期管理。

### 实现要求

```python
async def update_hotspot_lifecycle(self) -> list[HotspotUpdate]:
    """更新所有热点的生命周期状态"""
    updates = []

    # 1. 检测新兴热点：近 3 天内容频率超过阈值的话题
    emerging = await self._detect_emerging_topics(days=3, min_frequency=5)
    for topic in emerging:
        if not await self._is_existing_hotspot(topic):
            hotspot = await self._create_hotspot(topic, status="emerging")
            updates.append(HotspotUpdate(hotspot=hotspot, action="created"))

    # 2. 状态流转
    all_hotspots = await self._get_active_hotspots()
    for hotspot in all_hotspots:
        new_status = await self._evaluate_status_transition(hotspot)
        if new_status != hotspot.status:
            await self._update_status(hotspot, new_status)
            updates.append(HotspotUpdate(hotspot=hotspot, action=f"{hotspot.status}->{new_status}"))

    return updates

async def _evaluate_status_transition(self, hotspot: Hotspot) -> str:
    """评估热点状态是否需要流转"""
    recent_count = await self._get_topic_frequency(hotspot.topic, days=3)
    prev_count = await self._get_topic_frequency(hotspot.topic, days=7, offset=3)

    growth_rate = (recent_count - prev_count) / max(prev_count, 1)

    match hotspot.status:
        case "emerging":
            return "hot" if growth_rate > 0.5 else ("archived" if recent_count == 0 else "emerging")
        case "hot":
            return "mature" if growth_rate < 0.1 else "hot"
        case "mature":
            return "cooling" if growth_rate < -0.3 else "mature"
        case "cooling":
            return "archived" if recent_count == 0 else "cooling"
        case _:
            return hotspot.status
```

---

## 模块四：漂移检测器 (Drift Detector)

### 当前问题
空壳，无上下文监测。

### 实现要求

```python
async def detect_concept_drift(self) -> list[DriftReport]:
    """检测术语含义变化"""
    reports = []

    # 获取所有被追踪的关键术语
    tracked_terms = await self._get_tracked_terms()

    for term in tracked_terms:
        # 获取该术语最近的使用上下文
        recent_contexts = await self._get_recent_contexts(term, days=30)
        historical_contexts = await self._get_historical_contexts(term, days=90, offset=30)

        if not recent_contexts or not historical_contexts:
            continue

        # 调用 AI 比较上下文变化
        drift_analysis = await self._ai_compare_contexts(
            term=term.name,
            recent=recent_contexts,
            historical=historical_contexts,
        )

        if drift_analysis.drift_detected:
            reports.append(DriftReport(
                term=term,
                old_meaning=drift_analysis.old_meaning,
                new_meaning=drift_analysis.new_meaning,
                confidence=drift_analysis.confidence,
                evidence=drift_analysis.evidence,
            ))
            # 生成更新提案
            await self._create_drift_proposal(term, drift_analysis)

    return reports
```

---

## 模块五：策略适配器 (Strategy Adapter)

### 当前问题
空壳，无自适应逻辑。

### 实现要求

```python
async def adapt_strategies(self) -> list[StrategyChange]:
    """根据抓取效果自适应调整策略"""
    changes = []

    sources = await self._get_active_sources()
    for source in sources:
        stats = await self._get_crawl_stats(source.id, days=7)

        # 1. 频率调整：实际更新频率 vs 当前抓取频率
        if stats.actual_update_interval > source.crawl_interval * 2:
            # 更新太少，降低抓取频率
            new_interval = min(source.crawl_interval * 1.5, 86400)  # 最多每天一次
            changes.append(StrategyChange(
                source_id=source.id,
                field="crawl_interval",
                old_value=source.crawl_interval,
                new_value=new_interval,
                reason="信息源更新频率低于抓取频率",
            ))

        # 2. 超时调整：响应时间趋势
        if stats.avg_response_time > source.timeout * 0.8:
            new_timeout = min(source.timeout * 1.5, 60)
            changes.append(StrategyChange(
                source_id=source.id,
                field="timeout",
                old_value=source.timeout,
                new_value=new_timeout,
                reason="响应时间接近超时阈值",
            ))

        # 3. 质量过滤调整
        if stats.low_quality_ratio > 0.5:
            changes.append(StrategyChange(
                source_id=source.id,
                field="quality_threshold",
                old_value=source.quality_threshold,
                new_value=min(source.quality_threshold + 10, 80),
                reason="低质量内容占比过高",
            ))

    # 重大变更生成提案，小调整直接执行
    for change in changes:
        if change.is_major:
            await self._create_strategy_proposal(change)
        else:
            await self._apply_change(change)

    return changes
```

---

## 模块六：决策执行器 (Decision Executor)

### 当前问题
仅处理 2 种提案类型。

### 需要支持的全部类型

```python
async def execute_proposal(self, proposal: ChangeProposal) -> ExecutionResult:
    """执行审批通过的变更提案"""
    match proposal.type:
        case "node_add":
            return await self._execute_node_add(proposal)
        case "node_delete":
            return await self._execute_node_delete(proposal)
        case "node_split":
            return await self._execute_node_split(proposal)
        case "node_merge":
            return await self._execute_node_merge(proposal)
        case "node_rename":
            return await self._execute_node_rename(proposal)
        case "node_move":
            return await self._execute_node_move(proposal)
        case "source_add":
            return await self._execute_source_add(proposal)
        case "source_remove":
            return await self._execute_source_remove(proposal)
        case "source_adjust":
            return await self._execute_source_adjust(proposal)
        case "strategy_change":
            return await self._execute_strategy_change(proposal)
        case "flatten":
            return await self._execute_flatten(proposal)
        case "group":
            return await self._execute_group(proposal)
        case _:
            raise ValueError(f"未知提案类型: {proposal.type}")
```

---

## 实现检查清单

开发进化循环相关功能时，确认：

- [ ] 健康评估器有真实计算逻辑（非硬编码）
- [ ] 重构建议器能检测至少 4 种结构问题
- [ ] 热点管理器实现完整的 5 状态流转
- [ ] 漂移检测器能调用 AI 比较上下文变化
- [ ] 策略适配器能根据统计数据调整至少 3 种参数
- [ ] 决策执行器支持全部提案类型
- [ ] 每个模块都有日志记录
- [ ] 每个模块的异常都被正确处理
