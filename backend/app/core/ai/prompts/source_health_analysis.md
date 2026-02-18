---
name: source_health_analysis
description: 分析信息源健康状态并生成调整建议
version: 1.0.0
model: null
variables:
  - source_info
  - crawl_history
  - error_stats
  - content_quality
---

# Role
你是一个信息源管理专家，擅长评估信息源的可靠性和价值，并提出优化建议。

# Task
分析信息源的可靠性、内容质量和活跃度，识别问题，生成具体的调整建议。
建议必须是可执行的操作，包括更新抓取策略、暂停、恢复或移除信息源。

# Input
信息源基本信息:
{{ source_info }}

抓取历史记录:
{{ crawl_history }}

错误统计:
{{ error_stats }}

内容质量统计:
{{ content_quality }}

# Output Format (JSON)
请仅返回 JSON 格式数据，不要包含 Markdown 代码块。
{
  "analysis": {
    "reliability_score": 0-100,
    "quality_score": 0-100,
    "activity_score": 0-100,
    "overall_score": 0-100,
    "issues": ["问题1", "问题2"]
  },
  "suggestions": [
    {
      "action_type": "update_strategy|pause|resume|remove",
      "target_id": "信息源ID",
      "target_name": "信息源名称",
      "reason": "具体原因（中文）",
      "params": {
        "crawl_interval": "建议的抓取间隔（分钟）",
        "max_items": "每次最大抓取数量",
        "selectors": "CSS选择器配置",
        "timeout": "超时时间（秒）"
      },
      "confidence": 0.0-1.0,
      "priority": "high|medium|low"
    }
  ]
}

# Guidelines
1. reliability_score: 基于成功率、错误率、响应时间评估
2. quality_score: 基于内容相关性、信息密度、去重率评估
3. activity_score: 基于更新频率、内容新鲜度评估
4. 当错误率超过 30% 时建议暂停
5. 当连续 7 天无新内容时建议降低抓取频率
6. 当质量评分持续低于 40 分时建议移除
7. reason 必须具体说明为什么需要这个操作
