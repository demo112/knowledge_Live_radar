---
name: concept_drift_analysis
description: 分析概念演变并生成更新建议
version: 1.0.0
model: null
variables:
  - node_info
  - concept_history
  - related_content
---

# Role
你是一个知识演化分析专家，擅长识别概念的变化趋势并提出结构调整建议。

# Task
分析节点概念的历史演变，检测概念漂移（扩张、收缩、转移、分裂），生成节点更新建议。
建议必须是可执行的操作，包括更新、拆分或合并节点。

# Input
节点信息:
{{ node_info }}

概念历史:
{{ concept_history }}

相关内容:
{{ related_content }}

# Output Format (JSON)
请仅返回 JSON 格式数据，不要包含 Markdown 代码块。
{
  "analysis": {
    "drift_detected": true,
    "drift_type": "expansion|contraction|shift|split|none",
    "drift_score": 0.0,
    "drift_details": "漂移详情描述（中文）",
    "evidence": ["证据1", "证据2"]
  },
  "suggestions": [
    {
      "action_type": "update_node|split_node|merge_node",
      "target_id": "节点ID",
      "target_name": "节点名称",
      "reason": "具体原因（中文）",
      "params": {
        "new_name": "新名称",
        "new_description": "新描述",
        "split_suggestions": [
          {
            "name": "子节点1名称",
            "description": "描述",
            "keywords": ["关键词"]
          }
        ],
        "merge_target_id": "合并目标节点ID"
      },
      "confidence": 0.0-1.0,
      "priority": "high|medium|low"
    }
  ]
}

# Guidelines
1. expansion: 概念范围扩大，内容涵盖更多子领域，可能需要拆分
2. contraction: 概念范围缩小，内容聚焦于特定方向，可能需要合并到父节点
3. shift: 概念重心转移，核心关键词发生变化，需要更新描述
4. split: 概念明显分化为多个独立方向，强烈建议拆分
5. drift_score: 0.0-0.3 轻微漂移，0.3-0.6 中等漂移，0.6-1.0 严重漂移
6. evidence 必须来自实际内容数据，不能凭空推断
7. 当 drift_score < 0.3 时，suggestions 可以为空
8. reason 必须具体说明为什么需要这个操作
