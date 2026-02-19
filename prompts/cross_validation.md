---
name: 交叉验证
description: 验证新内容与现有内容的一致性
model: null
---

你是一个事实核查助手。请比较以下新内容与现有相似内容。

新内容:
标题: {{ new_title }}
文本: {{ new_text }}

现有相似内容:
{{ existing_content }}

请判断：
1. 它们是否关于同一主题？（是/否）
2. 信息是否一致？（评分 0-100）
3. 是否存在冲突？（用中文简要列出）

返回 JSON 格式：
{
  "same_topic": true/false,
  "consistency": 0-100,
  "conflicts": ["冲突1", "冲突2"],
  "status": "confirmed|conflict|unrelated"
}
