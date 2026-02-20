# 金字塔进化引擎任务清单

## 任务概览

本任务旨在实现金字塔的语义增强和结构自适应，确保 AI 建议具备高价值和可执行性。

## 详细任务

### Task 1: 重构 SuggestionExecutor (Refactor SuggestionExecutor)
- [ ] **R1. 统一入口**: 将 `SuggestionExecutor` 的所有节点操作逻辑重构为调用 `PyramidService`。
- [ ] **R2. 修复合并**: 移除重复定义的 `_execute_merge_node`，确保使用支持 `new_node_description` 的版本。
- [ ] **R3. 修复移动**: 实现 `move_node` 的递归路径更新（通过调用 `PyramidService`）。
- [ ] **R4. 参数增强**: 确保 `split_node` 支持从 `params` 中读取 `children` 对象列表（含 `description`），而不仅是名称列表。

### Task 2: 增强健康处理器 (Enhance PyramidHealthProcessor)
- [ ] **P1. 内容采样**: 修改 `_collect_pyramid_data`，为每个节点采集 3-5 条高关联度内容（Title + Summary）。
- [ ] **P2. 构建上下文**: 将采集的内容样本构建为 `node_content_samples` 字典，传入 Prompt。

### Task 3: 升级 Prompt (Update Prompt)
- [ ] **A1. 语义生成**: 更新 `prompts/pyramid/health_analysis.md`，增加规则：必须基于 `node_content_samples` 生成 `description`。
- [ ] **A2. 结构化输出**: 确保输出 JSON 包含 `description` 字段。
- [ ] **A3. 价值验证**: 增加 Prompt 约束，禁止生成无实际内容支撑的空泛建议。

### Task 4: 集成验证 (Integration Verification)
- [ ] **V1. 测试用例**: 编写集成测试 `tests/integration/test_pyramid_evolution.py`。
- [ ] **V2. 场景覆盖**:
  - 创建节点带描述
  - 拆分节点带子节点描述
  - 合并节点带新描述
  - 移动节点路径正确更新

## 测试设计 (TDD)

### Test Case 1: 语义增强的建议生成
- **Given**: 一个名为 "Agent" 的节点，下有 3 条关于 "Autonomous Agents" 的内容。
- **When**: 运行 `analyze_pyramid_health`。
- **Then**: 生成的建议中，`update_node` 或 `split_node` 的 `params` 必须包含准确的 `description`。

### Test Case 2: 复杂的拆分操作
- **Given**: 一个内容过载的节点。
- **When**: 执行 `split_node` 建议。
- **Then**: 新生成的子节点必须包含描述，且内容关联正确迁移。

### Test Case 3: 移动节点的一致性
- **Given**: 一个层级为 2 的节点。
- **When**: 移动到层级为 0 的节点下。
- **Then**: 该节点及其所有子节点的 `path` 和 `level` 必须正确更新。
