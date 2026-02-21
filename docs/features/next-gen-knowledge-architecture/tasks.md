# 任务清单：下一代知识架构

> **关联文档**:
> - [Requirements](requirements.md)
> - [Design](design.md)

## 阶段 1: 核心模型与数据迁移 (Done)

- [x] **任务 1.1: 实现新数据模型 (KnowledgeNode, KnowledgeCluster, Relations)**
    - [x] 创建 SQLAlchemy 2.0 模型 (`app/models/knowledge.py`)
    - [x] 实现 Soft Delete (`BaseRepository` 支持)
    - [x] 创建 Alembic 迁移脚本
    - [x] 验证数据库 Schema

- [x] **任务 1.2: 基础 CRUD 服务**
    - [x] 实现 `KnowledgeService` (CRUD, Search, Stats)
    - [x] 实现 `ClusterService`
    - [x] 单元测试 `test_knowledge_service.py`

## 阶段 2: AI 认知模型升级 (In Progress)

- [x] **任务 2.1: 认知模型生成服务**
    - [x] 集成 `AIFacade` 生成认知模型 (Summary, Core Concepts)
    - [x] 实现 `generate_cognitive_model` 方法
    - [x] API 端点 `/knowledge/nodes/{id}/cognitive-model`

- [x] **任务 2.2: 内容分类引擎升级**
    - [x] 升级 `VectorService` 支持 KnowledgeNode 向量存储
    - [x] 升级 `EvolutionEngine.auto_classify_content` 使用 KnowledgeNode
    - [x] 替换 Legacy PyramidNode 依赖
    - [x] 集成测试 `test_evolution_knowledge.py`

- [x] **任务 2.3: 模型进化反馈循环**
    - [x] 实现 `EvolutionEngine.evolve_node_model`
    - [x] 基于新关联内容更新 AI 认知模型
    - [x] 触发机制：关联内容 > N 或 时间 > T

## 阶段 3: 簇与关系发现 (Done)

- [x] **任务 3.1: 簇与关系发现服务**
    - [x] 实现 `DiscoveryService`
    - [x] 基于向量相似度发现潜在关系 (Node-Node)
    - [x] 基于内容共现发现潜在簇 (Content Cluster -> KnowledgeCluster)

- [x] **任务 3.2: 图谱查询优化**
    - [x] 实现图谱遍历查询 (BFS/DFS limit depth)
    - [x] 优化 `get_related_nodes` 查询性能

## 阶段 4: 意图驱动架构 (In Progress)

- [x] **任务 4.1: 意图理解服务**
    - [x] 定义 Intent Schema (Learn, Research, Track, Create)
    - [x] 实现 `IntentProcessor` (Prompt Engineering)
    - [x] 提供 `/intents/parse` 接口

- [x] **任务 4.2: 意图驱动执行引擎**
    - [x] 实现 `ActionGenerator` (根据意图生成 Action List)
    - [x] 针对 `Learn` 意图：生成知识图谱结构
    - [x] 针对 `Research` 意图：生成深度搜索任务

## 阶段 5: 前端重构与清理 (Done)

- [x] **任务 5.1: 知识图谱前端 UI**
    - [x] ReactFlow 图谱展示组件
    - [x] 节点详情侧边栏 (展示认知模型)

- [x] **任务 5.2: 意图创建前端 UI**
    - [x] 意图输入框与引导交互
    - [x] 生成结果预览

- [x] **任务 5.3: 清理旧代码与切换**
    - [x] 标记 Pyramid 相关 API 为 Deprecated
    - [ ] 数据库迁移：旧数据导入新架构 (Optional)
    - [ ] 移除旧表 (Pyramids, PyramidNodes)
