---
name: proposal_reason
description: Generate a concise reason for a change proposal
variables:
  - match_type
  - concept_name
  - content_title
  - node_name
---

# Role
你是一个知识管理助手。

# Task
为知识金字塔的变更提案生成一个简洁、专业的中文理由。

# Input
匹配类型: {{ match_type }}
概念名称: {{ concept_name }}
内容标题: {{ content_title }}
目标节点: {{ node_name }}

# Guidelines
- 对于 NEW (新概念): 解释从内容中发现了新概念，建议添加。
- 对于 EXACT/SYNONYM (匹配): 解释内容与现有节点相关，建议关联。
- 保持在 50 字以内。
- 使用中文。

# Output Format (JSON)
{
  "reason": "..."
}
