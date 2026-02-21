# Requirements: 系统增加 Embedding 模型支持

## Overview

目前系统仅支持本地 `SentenceTransformer` 和 `Dummy` 哈希两种 Embedding 方式。为了提升语义检索的准确性，并利用高性能云端模型（如 SiliconFlow 提供的 BGE/BCE 系列），需要扩展系统以支持 OpenAI 兼容接口的 Embedding 服务，重点集成 SiliconFlow。

此功能将允许通过配置切换 Embedding 提供商，支持更高维度的语义向量，从而提升知识金字塔的聚类和检索效果。

## User Stories

### Story 1: 支持 SiliconFlow Embedding API

As a 系统管理员, I want 配置使用 SiliconFlow 的 Embedding 服务, so that 我可以使用更强大的语义向量模型（如 BAAI/bge-m3）

**Acceptance Criteria:**

- [ ] AC1: 配置 SiliconFlow Embedding
  - **Given**: 系统配置文件 `config.py` 或环境变量中设置了 `EMBEDDING_PROVIDER=siliconflow` 和 `SILICONFLOW_API_KEY`
  - **When**: 系统启动并初始化 `VectorService`
  - **Then**: 系统成功加载基于 OpenAI 接口的 Embedding Function，指向 SiliconFlow 的 API 端点

- [ ] AC2: 支持自定义模型名称
  - **Given**: 配置文件中设置了 `EMBEDDING_MODEL=BAAI/bge-m3`
  - **When**: 调用 Embedding 服务
  - **Then**: API 请求中的 `model` 参数正确传递为 `BAAI/bge-m3`

- [ ] AC3: 维度适配
  - **Given**: 使用了不同维度的模型（如 bge-m3 为 1024 维，而本地模型为 384 维）
  - **When**: 初始化 ChromaDB 集合
  - **Then**: 能够正确处理不同维度的向量存储（需注意：切换模型需要重建数据库或新集合）

### Story 2: Embedding 提供商切换架构

As a 开发者, I want 统一的 Embedding 接口工厂, so that 我可以轻松切换本地模型和云端 API

**Acceptance Criteria:**

- [ ] AC1: 抽象 Embedding Factory
  - **Given**: 代码中定义了 `get_embedding_function(provider, model_name)`
  - **When**: 传入 `provider="local"`
  - **Then**: 返回 `SentenceTransformerEmbeddingFunction`

- [ ] AC2: SiliconFlow 实现
  - **Given**: 传入 `provider="siliconflow"`
  - **When**: 调用工厂方法
  - **Then**: 返回配置好 API Key 和 Base URL 的 `OpenAIEmbeddingFunction` (ChromaDB 内置或自定义实现)

### Story 3: 错误处理与降级

As a 系统, I want 在云端 API 失败时有明确反馈, so that 我知道检索服务不可用

**Acceptance Criteria:**

- [ ] AC1: API 连接失败处理
  - **Given**: 配置了 SiliconFlow 但网络不通或 Key 无效
  - **When**: 尝试生成 Embedding
  - **Then**: 记录 ERROR 日志，抛出明确异常，而不是静默失败或返回全零向量

## Constraints

- **数据兼容性**：切换 Embedding 模型会导致旧向量失效。本需求**不包含**自动迁移旧数据的功能。切换模型后，需手动清除 `chroma_db` 或重新索引数据。
- **性能**：云端 API 会有网络延迟，需设置合理的超时时间（建议 10s）。
- **成本**：使用 SiliconFlow API 会产生 Token 消耗，需在文档中提示。

## Out of Scope

- 自动重新索引旧数据（Re-indexing）
- 多模型共存（即同时使用两种 Embedding）
- 本地模型微调

## Assumptions

以下假设已与用户确认：
- [x] 用户拥有 SiliconFlow API Key
- [x] 用户接受切换模型需要清空旧向量数据
- [x] 主要支持 OpenAI 兼容接口（SiliconFlow 使用此标准）

## Metadata

- 规模：小
- 涉及模块：backend/services/vector_service, backend/config
- 涉及端：Backend
- 创建时间：2026-02-21
- 状态：待确认
