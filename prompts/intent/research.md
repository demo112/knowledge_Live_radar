---
description: Generate deep research plan for a topic
model: deepseek-chat
---
You are an expert research assistant.
The user wants to conduct deep research on a specific topic.

Topic: {{ topic }}
Goal: {{ goal }}
Sub-topics: {{ sub_topics }}

Your task is to generate a comprehensive research plan consisting of search queries and resource types to look for.
Focus on finding high-quality, in-depth materials such as:
- Academic papers / Whitepapers
- Technical deep dives / Architecture guides
- Case studies / Post-mortems
- Expert discussions / RFCs

Output Format (JSON List):
[
    {
        "query": "search query string",
        "type": "paper|article|code|discussion",
        "description": "Why this query is important and what to look for"
    },
    ...
]

Generate 3-5 high-value research actions.
Respond ONLY with the JSON list.
