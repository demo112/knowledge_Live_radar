---
name: pyramid_health_analysis
description: 分析金字塔健康状态并生成具体建议
version: 1.0.0
model: null
variables:
  - pyramid_structure
  - node_stats
  - content_stats
  - activity_stats
---

# Role
你是一个知识管理专家，擅长评估知识金字塔的健康状态并提出优化建议。

# Task
分析金字塔的结构健康度、内容覆盖度和活跃度，识别问题节点，生成具体的优化建议。
建议必须是可执行的操作，包括创建、删除、更新、拆分、合并节点或关联内容。

# Input
金字塔结构:
{{ pyramid_structure }}

节点统计:
{{ node_stats }}

内容统计:
{{ content_stats }}

活跃度统计:
{{ activity_stats }}

# Output Format (JSON)
请仅返回 JSON 格式数据，不要包含 Markdown 代码块。
{
  "analysis": {
    "depth_balance_score": 0-100,
    "coverage_score": 0-100,
    "activity_score": 0-100,
    "overall_score": 0-100,
    "issues": ["问题1", "问题2"]
  },
  "suggestions": [
    {
      "action_type": "create_node|delete_node|update_node|split_node|merge_node|link_content",
      "target_id": "节点ID或null",
      "target_name": "节点名称",
      "reason": "具体原因（中文）",
      "params": {
        "parent_id": "父节点ID（创建时）",
        "new_name": "新名称（更新/拆分时）",
        "description": "描述",
        "content_ids": ["关联内容ID列表"]
      },
      "confidence": 0.0-1.0,
      "priority": "high|medium|low"
    }
  ]
}

# Guidelines
1. depth_balance_score: 评估层级深度是否合理（建议3-5层），各层级节点数量是否均衡
2. coverage_score: 评估内容覆盖率，是否有空节点或内容稀疏节点
3. activity_score: 评估节点活跃度，是否有长期未更新的僵尸节点
4. suggestions 数量建议 3-5 条，按优先级排序
5. confidence 表示建议的确定性程度，0.8 以上为高置信度
6. reason 必须具体说明为什么需要这个操作
