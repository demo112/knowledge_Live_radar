---
name: ai-service-reliability
description: "AI 服务调用可靠性模式：重试、降级、队列、结构化输出、prompt 管理。适用于硅基流动 API 集成。"
type: reference
applies_to: server
triggers:
  - AI服务
  - 硅基流动
  - LLM
  - 大模型
  - prompt
  - 重试
  - 降级
---

# AI 服务可靠性模式

AI Radar 依赖硅基流动 API 实现内容评估、摘要生成、概念提取等功能。本 Skill 提供 AI 服务调用的可靠性保障模式。

---

## 核心原则

1. **永远不信任 AI 输出** - 必须验证和解析结构化输出
2. **永远假设会失败** - 每次调用都要有重试和降级方案
3. **永远记录调用** - 输入、输出、耗时、token 用量全部记录

---

## 基础调用模式

```python
import httpx
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

class AIServiceClient:
    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-ai/DeepSeek-V3"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """基础聊天调用"""
        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

---

## 重试与降级

```python
import asyncio

async def call_with_retry(
    self,
    messages: list[dict],
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs,
) -> str | None:
    """指数退避重试 + 降级"""
    for attempt in range(max_retries):
        try:
            result = await self.chat(messages, **kwargs)
            return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # 限流：等待更长时间
                delay = base_delay * (3 ** attempt)
                logger.warning(f"AI 服务限流，等待 {delay}s")
                await asyncio.sleep(delay)
            elif e.response.status_code >= 500:
                # 服务端错误：正常重试
                delay = base_delay * (2 ** attempt)
                logger.warning(f"AI 服务错误 {e.response.status_code}，重试 {attempt+1}/{max_retries}")
                await asyncio.sleep(delay)
            else:
                raise  # 4xx 非限流错误不重试
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            delay = base_delay * (2 ** attempt)
            logger.warning(f"AI 服务连接问题: {e}，重试 {attempt+1}/{max_retries}")
            await asyncio.sleep(delay)

    logger.error("AI 服务调用失败，已达最大重试次数")
    return None  # 降级：返回 None，调用方决定如何处理
```

---

## 结构化输出解析

```python
import json
from typing import TypeVar, Type
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

async def call_structured(
    self,
    messages: list[dict],
    response_model: Type[T],
    **kwargs,
) -> T | None:
    """调用 AI 并解析为结构化对象"""
    # 在 prompt 中要求 JSON 输出
    system_msg = messages[0]["content"] if messages[0]["role"] == "system" else ""
    system_msg += "\n\n请严格以 JSON 格式输出，不要包含其他文字。"
    messages[0] = {"role": "system", "content": system_msg}

    raw = await self.call_with_retry(messages, **kwargs)
    if not raw:
        return None

    try:
        # 尝试提取 JSON（AI 可能包裹在 markdown 代码块中）
        json_str = raw
        if "```json" in raw:
            json_str = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            json_str = raw.split("```")[1].split("```")[0].strip()

        data = json.loads(json_str)
        return response_model.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"AI 输出解析失败: {e}\n原始输出: {raw[:500]}")
        return None
```

---

## Prompt 模板管理

```python
# app/prompts/templates.py

CONTENT_QUALITY_PROMPT = """你是一个内容质量评估专家。请评估以下内容的质量。

## 评估维度
1. 信息密度 (0-100): 内容中有价值信息的占比
2. 原创性 (0-100): 内容的独特性和原创程度
3. 一致性 (0-100): 标题与正文的一致程度
4. 广告检测: 是否为广告或营销内容 (true/false)
5. 时效性 (0-100): 信息的时效价值

## 待评估内容
标题: {title}
正文: {content}
来源: {source}

## 输出格式 (JSON)
{{
    "information_density": <int>,
    "originality": <int>,
    "consistency": <int>,
    "is_advertisement": <bool>,
    "timeliness": <int>,
    "overall_score": <int>,
    "comment": "<一句话评语>"
}}"""

SUMMARY_PROMPT = """请为以下内容生成 100-200 字的中文摘要，并提取 3-5 个关键标签。

## 内容
{content}

## 输出格式 (JSON)
{{
    "summary": "<摘要>",
    "tags": ["<标签1>", "<标签2>", ...]
}}"""

CONCEPT_EXTRACT_PROMPT = """从以下内容中提取关键概念。

## 内容
{content}

## 输出格式 (JSON)
{{
    "concepts": [
        {{"name": "<概念名>", "type": "<类型: tool/framework/method/model/concept>", "confidence": <0.0-1.0>}},
        ...
    ]
}}"""

CROSS_VALIDATION_PROMPT = """比较以下两段内容，判断它们是否在描述相同的事实。

## 内容 A
{content_a}

## 内容 B
{content_b}

## 输出格式 (JSON)
{{
    "same_topic": <bool>,
    "consistency": <0-100>,
    "conflicts": ["<冲突点1>", ...],
    "comment": "<分析说明>"
}}"""
```

---

## 任务队列（AI 服务不可用时）

```python
class AITaskQueue:
    """AI 服务不可用时，将任务加入队列稍后重试"""

    async def enqueue(self, task_type: str, payload: dict) -> int:
        """将任务加入待处理队列"""
        task = AITask(
            type=task_type,
            payload=json.dumps(payload),
            status="pending",
            created_at=datetime.utcnow(),
        )
        self.db.add(task)
        await self.db.commit()
        logger.info(f"AI 任务入队: {task_type}, id={task.id}")
        return task.id

    async def process_pending(self, batch_size: int = 10):
        """处理待执行的队列任务"""
        tasks = await self._get_pending_tasks(limit=batch_size)
        for task in tasks:
            try:
                await self._execute_task(task)
                task.status = "completed"
            except Exception as e:
                task.retry_count += 1
                if task.retry_count >= 3:
                    task.status = "failed"
                    logger.error(f"AI 任务最终失败: {task.id}, {e}")
                else:
                    task.status = "pending"
                    logger.warning(f"AI 任务重试: {task.id}, 第 {task.retry_count} 次")
        await self.db.commit()
```

---

## 调用日志记录

```python
async def chat_with_logging(self, messages: list[dict], **kwargs) -> str:
    """带完整日志的 AI 调用"""
    import time
    start = time.time()
    input_text = json.dumps(messages, ensure_ascii=False)[:1000]

    try:
        result = await self.chat(messages, **kwargs)
        elapsed = time.time() - start
        logger.info(
            f"AI 调用成功 | 耗时: {elapsed:.2f}s | "
            f"输入: {len(input_text)}字 | 输出: {len(result)}字"
        )
        return result
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"AI 调用失败 | 耗时: {elapsed:.2f}s | 错误: {e}")
        raise
```

---

## 检查清单

调用 AI 服务时确认：

- [ ] 有重试机制（至少 3 次，指数退避）
- [ ] 有降级方案（AI 不可用时不阻塞主流程）
- [ ] 输出有结构化解析和验证
- [ ] 有完整的调用日志（输入摘要、输出长度、耗时）
- [ ] Prompt 使用模板管理，不硬编码在业务代码中
- [ ] 超时设置合理（默认 60s）
- [ ] 限流错误有特殊处理（更长的等待时间）
