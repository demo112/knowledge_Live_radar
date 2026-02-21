# 下一代知识架构规格说明书 (Next-Gen Knowledge Architecture Spec)

## 背景 (Why)
现有金字塔（Pyramid）体系基于树状结构，难以表达复杂的知识网络关系（多维关联、跨领域交叉）。随着知识量的增长，需要一种更灵活、更智能的架构来组织知识。
本次重构将引入**知识图谱簇（Knowledge Graph Cluster）**、**AI 认知模型**和**意图式创建**三大支柱，完全替代金字塔体系，实现从"人工构建层级"到"AI 辅助图谱演化"的跃迁。

## 变更内容 (What Changes)

### 核心架构变更
- **废弃**：完全废弃 `Pyramid` 和 `PyramidNode` 的树状层级结构。
- **新增**：引入 `KnowledgeNode`（知识节点）、`KnowledgeCluster`（知识簇）和 `NodeRelation`（图谱关系）。
- **新增**：引入 AI 认知模型（Cognitive Model），作为节点和簇的"理解能力"。
- **新增**：引入意图式创建（Intent-Driven Creation），通过自然语言生成知识结构。

### 数据库变更
- **新增表**：
    - `knowledge_nodes`: 替代 `pyramid_nodes`，去除树状字段。
    - `knowledge_clusters`: 替代 `pyramids`，管理节点聚合。
    - `cluster_node_memberships`: 多对多关系，支持节点跨簇。
    - `node_relations`: 增强的节点间关系（类型、权重、证据）。
- **修改表**：
    - `content_node_relations`: 外键指向 `knowledge_nodes`。
    - `source_node_relations`: 外键指向 `knowledge_nodes`。
- **迁移**：提供从 Pyramid 到 Knowledge Graph 的完整数据迁移脚本。

### API 变更
- **新增**：`/api/v1/knowledge/*` (图谱管理), `/api/v1/intent/*` (意图创建)。
- **废弃**：`/api/v1/pyramids/*` 相关接口。

## 影响范围 (Impact)
- **受影响的规格**: 
    - `pyramid-internal-evolution`: 被新的图谱演化取代。
    - `ai-driven-suggestions`: 升级为基于认知模型的推荐。
- **受影响的代码**:
    - 后端: `app/models`, `app/services/pyramid_service.py`, `app/routers/pyramids.py`.
    - 前端: `src/app/(dashboard)/pyramid`, `src/components/pyramid`.
- **破坏性变更**: 
    - 现有的金字塔数据结构将被转换，API 将不兼容，需前端同步升级。

## 新增需求 (ADDED Requirements)

### 需求：知识图谱核心
系统应支持基于图谱的知识组织方式。
#### 场景：节点管理
- **当** 用户创建或 AI 生成节点时
- **那么** 节点应包含 AI 认知模型，并可关联到多个簇。

### 需求：AI 认知模型
每个节点和簇应具有 AI 认知模型，用于内容理解和自动分类。
#### 场景：内容分类
- **当** 新内容进入系统时
- **那么** 系统应利用三阶段分类流水线（向量粗筛→规则引擎精筛→LLM消歧）进行内容分类。

### 需求：意图式创建
系统应支持通过自然语言描述快速构建知识结构。
#### 场景：通过意图创建
- **当** 用户输入"追踪 MCP 协议生态"时
- **那么** 系统应生成包含相关节点、关系和簇的预览结构供确认。

## 修改的需求 (MODIFIED Requirements)

### 需求：内容与信源关联
内容和信源的关联目标从金字塔节点变更为知识节点。
- **迁移**: 现有关联数据需迁移至新表。

## 移除的需求 (REMOVED Requirements)

### 需求：金字塔层级
金字塔层级结构（Parent-Child, Level, Path）将被移除。
**原因**: 树状结构限制了知识的表达，且维护成本高。
**迁移**: 转换为图谱中的 `is_part_of` 关系。
