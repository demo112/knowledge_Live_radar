# Batch Classification Service

## 概述

批量分类服务 (`BatchClassificationService`) 旨在自动丰富未处理内容条目 (`ContentItem`) 的元数据，并将其链接到知识金字塔中的相关节点。

## 功能

1. **自动丰富 (Enrichment)**:
   - 生成摘要 (`summary`)
   - 提取标签 (`tags`)
   - 提取核心概念 (`concepts`)
2. **自动链接 (Linking)**:
   - 基于提取的元数据，利用 `EvolutionEngine` 自动将内容挂载到匹配的金字塔节点。
3. **状态追踪**:
   - 使用 `ai_processed` 字段标记已处理的内容，防止重复处理。

## API 使用

### 触发批量分类

**Endpoint**: `POST /api/v1/evolution/classify/batch`

**Query Parameters**:
- `limit` (int, default=10): 本次批量处理的最大条目数。

**Response**:
```json
{
  "success": true,
  "data": {
    "processed_count": 10,
    "success_count": 9
  }
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/evolution/classify/batch?limit=5"
```

## 处理流程

服务采用分阶段处理模式以确保数据库会话安全和并发效率：

1. **Phase 1: Fetch (同步/轻量)**
   - 从数据库获取 `ai_processed=False` 的内容条目。
   - 提取必要数据 (ID, Title, Content) 到内存，并在会话结束后分离对象。

2. **Phase 2: AI Processing (异步并发)**
   - 使用 `asyncio.gather` 并发调用 AI 服务。
   - 对每个条目执行：摘要生成、标签提取、概念提取。
   - 包含错误处理和 JSON 解析回退机制。

3. **Phase 3: Update & Link (顺序写入)**
   - 重新获取数据库会话。
   - 逐个更新内容条目的元数据。
   - 调用 `EvolutionEngine.auto_classify_content` 进行节点链接。
   - 提交事务。

## 注意事项

- **并发控制**: 目前通过 `limit` 参数控制单次处理量。AI 服务内部应有令牌桶限流（取决于 `AIService` 实现）。
- **错误处理**: 单个条目的 AI 处理失败不会中断整个批次，失败的条目将保持 `ai_processed=False`，以便下次重试。
