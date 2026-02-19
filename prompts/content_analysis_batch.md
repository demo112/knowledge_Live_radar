---
description: Batch content analysis for tags, concepts, and summary
system_prompt: You are a helpful assistant that categorizes content.
variables:
  - title
  - url
  - content_preview
---
Analyze the following content and provide:
1. A list of relevant tags (max 5).
2. A list of key concepts (max 5).
3. A brief summary (1-2 sentences).

Return ONLY a JSON object with keys: "tags", "concepts", "summary".

Title: {{ title }}
URL: {{ url }}
Content Preview:
{{ content_preview }}
