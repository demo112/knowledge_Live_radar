# 金字塔进化引擎技术设计

## 1. 核心架构

金字塔进化引擎（Pyramid Evolution Engine）旨在实现知识结构的自动演化，包括结构优化、新概念发现和语义增强。

系统采用 **"分析-建议-审批-执行"** 的异步闭环架构：

1.  **分析 (Analysis)**: `PyramidHealthProcessor` 定期扫描金字塔，收集结构统计和**内容样本**。
2.  **建议 (Suggestion)**: 调用 LLM (Prompt: `pyramid/health_analysis`) 生成结构化建议 (`AISuggestion`)。
3.  **审批 (Approval)**: 用户或自动策略审批建议。
4.  **执行 (Execution)**: `SuggestionExecutor` 调用 `PyramidService` 执行具体的图操作。

## 2. 数据流设计

### 2.1 内容采样与上下文构建

为了支持 Story 4（语义增强），分析阶段必须采集节点下的具体内容作为 LLM 的上下文。

**变更点**: `SuggestionProcessor._collect_pyramid_data`
- **新增**: 对每个节点采集 3-5 条高关联度内容（Title + Summary）。
- **策略**: 优先采集最近更新、Metabolism Score 高的内容。
- **输出**: 构建 `node_content_samples` 字典，传入 Prompt。

### 2.2 Prompt 协议升级

**文件**: `prompts/pyramid/health_analysis.md`

**输入增强**:
```json
{
  "node_content_samples": {
    "node_id_1": [
      {"title": "...", "summary": "..."}
    ]
  }
}
```

**输出增强**:
- `create_node` / `update_node`: 必须包含 `params.description`，基于内容样本生成。
- `split_node`: `params.children` 必须包含 `[{"name": "...", "description": "..."}]`。
- 新增 `drift_detected` 标识，用于标记因概念漂移产生的建议。

### 2.3 执行参数透传

`AISuggestion.params` 将作为核心载体，存储 LLM 生成的富语义参数。

| Action | Params 结构 | 说明 |
|--------|-------------|------|
| `create_node` | `{ "name": "...", "description": "...", "parent_id": "..." }` | 描述必填 |
| `split_node` | `{ "node_id": "...", "children": [{"name": "...", "description": "..."}] }` | 子节点带描述 |
| `merge_node` | `{ "source_node_ids": [...], "target_node_name": "...", "target_node_description": "..." }` | 合并后节点带描述 |

## 3. 核心组件设计

### 3.1 SuggestionExecutor 重构

目前 `SuggestionExecutor` 直接操作数据库，存在逻辑重复（如 `move_node` 的递归更新未实现）和 Bug（`merge_node` 重复定义）。

**重构方案**:
将 `SuggestionExecutor` 作为 `PyramidService` 的编排层，底层操作全权委托给 `PyramidService`。

- `_execute_create_node` -> `PyramidService.add_node`
- `_execute_split_node` -> `PyramidService.split_node`
- `_execute_merge_node` -> `PyramidService.merge_nodes`
- `_execute_move_node` -> `PyramidService.move_node`

这样可以复用 Service 层已完善的路径计算、递归更新和软删除逻辑。

### 3.2 PyramidService 增强

需要确保 Service 方法支持新的参数：

- `PyramidNodeCreate`: 确保包含 `description`。
- `NodeSplitRequest`: 这里的 `children` 定义需要支持 `description`。
- `NodeMergeRequest`: 增加 `new_node_description` 字段。

## 4. 语义锚定 (Semantic Anchoring)

为了防止 AI "瞎编" 描述，引入语义锚定机制：

1.  **生成时**: Prompt 强制要求描述必须引用 Input 中的内容关键词。
2.  **执行时**: `SuggestionExecutor` 在创建节点后，自动将生成建议时依据的 Content 关联到新节点（如果有明确的来源映射）。

## 5. 任务拆分

1.  **Service 层增强**: 确保 `PyramidService` 和 Pydantic Models 支持 `description` 及复杂操作参数。
2.  **Executor 重构**: 重写 `SuggestionExecutor`，对接 Service 层，修复 `merge` 重复和 `move` 递归问题。
3.  **Processor 升级**: 改造 `_collect_pyramid_data` 增加内容采样。
4.  **Prompt 迭代**: 更新 `health_analysis` Prompt，增加语义生成规则和样本输入插槽。
5.  **验证**: 编写测试用例验证从建议生成到节点创建的描述透传。
