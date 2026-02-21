# 任务列表

## 阶段 1: 数据模型重构与迁移
- [ ] 任务 1.1: 实现新数据模型
    - [ ] 在 `backend/app/models/knowledge.py` 中创建 `KnowledgeNode`, `KnowledgeCluster`, `ClusterNodeMembership`, `NodeRelation`
    - [ ] 更新 `ContentNodeRelation` 和 `SourceNodeRelation` (在各自文件中) 以指向 `KnowledgeNode` (使用条件逻辑或新字段支持迁移)
    - [ ] 在 `backend/app/schemas/knowledge.py` 中创建 Pydantic schemas
- [ ] 任务 1.2: 数据库迁移脚本
    - [ ] 生成 Alembic 迁移脚本以创建新表
    - [ ] 创建数据迁移脚本：将 `Pyramid` 转换为 `KnowledgeCluster`，`PyramidNode` 转换为 `KnowledgeNode`
    - [ ] 创建关系迁移脚本：将父子关系转换为 `is_part_of` 关系，迁移内容/信源关联
- [ ] 任务 1.3: 后端 CRUD 服务
    - [ ] 实现 `KnowledgeService` 用于节点和簇的 CRUD
    - [ ] 实现 `RelationService` 用于管理节点连接
    - [ ] 在 `backend/app/routers/knowledge.py` 中创建 API 端点

## 阶段 2: AI 认知模型
- [ ] 任务 2.1: 认知模型生成
    - [ ] 实现 `CognitiveModelService`，通过 LLM 根据节点名称/描述生成模型
    - [ ] 集成 `Concept` 表以填充初始模型数据
- [ ] 任务 2.2: 内容分类引擎
    - [ ] 实现三阶段分类逻辑：向量粗筛 -> 规则引擎精筛 -> LLM 消歧
    - [ ] 更新 `ContentProcessor` 以使用新的分类引擎
- [ ] 任务 2.3: 模型进化
    - [ ] 实现反馈循环，根据用户修正更新认知模型

## 阶段 3: 知识图谱管理
- [ ] 任务 3.1: 簇与关系发现
    - [ ] 实现 `KnowledgeDiscoveryService`，基于节点凝聚力建议新簇
    - [ ] 实现基于内容共现的关系发现
- [ ] 任务 3.2: 图谱查询优化
    - [ ] 优化图谱遍历的 SQL 查询 (使用 CTE)
    - [ ] 实现图谱可视化数据的缓存

## 阶段 4: 意图式创建
- [ ] 任务 4.1: 意图理解
    - [ ] 实现 `IntentService` 解析用户自然语言输入
    - [ ] 设计 LLM 提示词，从意图生成图谱结构
- [ ] 任务 4.2: 预览与调整 API
    - [ ] 实现 `POST /api/v1/intent/create` 和预览逻辑
    - [ ] 实现 `POST /api/v1/intent/refine` 用于对话式调整
    - [ ] 实现 `POST /api/v1/intent/confirm` 以实例化结构

## 阶段 5: 前端重构
- [ ] 任务 5.1: 知识图谱 UI
    - [ ] 使用 `react-force-graph` 或类似库创建 `GraphView` 组件
    - [ ] 实现簇视图用于聚合展示
    - [ ] 创建知识管理页面 (`/knowledge`)
- [ ] 任务 5.2: 意图创建 UI
    - [ ] 创建 "意图输入" 组件
    - [ ] 创建 "结构预览" 组件，包含交互式图谱
    - [ ] 实现 "调整" 聊天界面
- [ ] 任务 5.3: 清理与切换
    - [ ] 在导航中用知识图谱视图替换金字塔视图
    - [ ] 移除旧的金字塔组件

## 任务依赖
- 任务 1.2 依赖 任务 1.1
- 任务 1.3 依赖 任务 1.1
- 任务 2.1 依赖 任务 1.3
- 任务 2.2 依赖 任务 2.1
- 任务 4.1 依赖 任务 1.3
- 任务 5.1 依赖 任务 1.3
