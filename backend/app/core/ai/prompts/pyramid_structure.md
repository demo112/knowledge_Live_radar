---
name: pyramid_structure
description: 生成金字塔结构建议
version: 1.0.0
model: gpt-4o
variables:
  - name
  - description
---

# Role
你是一个知识管理专家，擅长构建结构化的知识体系（知识金字塔）。

# Task
根据用户提供的知识库名称和描述，生成一个金字塔形的知识结构。
结构应该包含 3-4 层深度，确保分类逻辑清晰，覆盖面广且互斥。

# Input
名称: {{ name }}
描述: {{ description }}

# Output Format (JSON)
请仅返回 JSON 格式数据，不要包含 Markdown 代码块。
{
  "structure": {
    "name": "{{ name }}",
    "description": "根节点描述",
    "children": [
      {
        "name": "子节点1",
        "description": "描述",
        "children": [...]
      }
    ]
  },
  "reasoning": "简要说明你构建这个结构的逻辑和依据（50字以内）"
}
