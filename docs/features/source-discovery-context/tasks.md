# 任务清单：自适应信息源发现

## 核心任务

- [x] Task 1: 实现金字塔结构快照提取
  - **目标**: 从数据库提取金字塔的树状结构（Nodes, Levels, Relationships）
  - **实现**: `SourceDiscoveryService._get_structure_snapshot`
  - **验证**: 单元测试验证结构完整性（无深度限制，包含 node_type）

- [x] Task 2: 实现自适应查询生成逻辑
  - **目标**: 集成 AI 服务，根据结构快照生成多维度搜索查询（Macro/Meso/Micro）
  - **实现**: `DiscoveryProcessor.generate_adaptive_queries` 和 `adaptive_query_generation.md`
  - **验证**: 模拟 AI 响应验证查询生成格式

- [x] Task 3: 更新信息源发现流程
  - **目标**: 将静态关键词搜索替换为 AI 驱动的自适应搜索流程
  - **实现**: `SourceDiscoveryService.discover_stream` 重构
  - **验证**: 集成测试验证完整流程（提取 -> 生成 -> 搜索 -> 过滤 -> 提案）

- [x] Task 4: 优化审批提案生成
  - **目标**: 在审批提案中包含上下文信息（Scope, Intent, Reason）
  - **实现**: `Approval` 模型兼容性修复和数据填充
  - **验证**: 验证生成的 Approval 对象包含正确的 `reason` 和 `data`

## 验证计划

1. **结构提取验证**
   - 确认包含所有层级节点
   - 确认包含 node_type 信息

2. **查询生成验证**
   - 确认生成 Macro/Meso/Micro 三类查询
   - 确认 fallback 机制有效

3. **流程集成验证**
   - 确认整个 pipeline 跑通无异常
   - 确认最终生成 Approval 记录
