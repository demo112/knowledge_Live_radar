---
name: 概念提取
description: 从内容中提取关键概念
model: null
---

你是一个知识图谱专家。请从以下内容中提取关键概念。

标题: {{ title }}
内容: {{ content }}

请提取以下类型的概念：
1. 技术（如 Python、React、Docker）
2. 工具（如 VS Code、Git、Jira）
3. 方法/实践（如 敏捷开发、TDD、CI/CD）
4. 组织/公司（如 Google、OpenAI）
5. 核心概念（如 机器学习、知识图谱）

重要要求：
- 输出必须使用简体中文
- 将所有概念名称和描述翻译成中文

返回 JSON 格式：
{
  "concepts": [
    {
      "name": "概念名称（中文）",
      "type": "technology|tool|method|organization|concept",
      "description": "简短描述（中文，最多20字）",
      "confidence": 0.95
    }
  ]
}
