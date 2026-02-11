# 需求文档 - 迭代 1：骨架搭建

## 概述

本文档描述 AI Radar 系统迭代 1 的需求。迭代 1 的核心目标是搭建系统骨架，包括前后端基础架构、核心数据模型和基本 UI 框架。

## 迭代目标

1. 搭建前后端基础架构（Next.js + FastAPI）
2. 实现核心数据模型（金字塔、节点、信息源、内容）
3. 实现基本 UI 框架（金字塔可视化、信息流、管理界面骨架）
4. 完成数据库设计与基础 API

## 技术栈

- 前端：Next.js + Tailwind CSS + ReactFlow
- 后端：Python FastAPI
- 数据库：PostgreSQL（生产）或 SQLite（开发）
- 部署：本地开发环境

## 需求

### 需求 1：知识金字塔核心管理

**用户故事：** 作为知识管理员，我希望能够创建和管理多个独立但可关联的知识金字塔，以便系统化地组织 AI 应用领域的知识。

#### 验收标准

1.1 WHEN 管理员创建新金字塔 THEN Knowledge_Pyramid_Manager SHALL 创建包含唯一标识、名称、描述、创建时间、根节点的金字塔实例
1.2 WHEN 管理员编辑金字塔基本信息 THEN Knowledge_Pyramid_Manager SHALL 更新金字塔的名称和描述
1.3 WHEN 管理员删除金字塔 THEN Knowledge_Pyramid_Manager SHALL 移除金字塔及其所有节点、关联的信息源映射，并归档相关内容
1.4 WHEN 管理员查询金字塔列表 THEN Knowledge_Pyramid_Manager SHALL 返回所有金字塔的基本信息和健康度摘要
1.5 WHEN 管理员查询单个金字塔详情 THEN Knowledge_Pyramid_Manager SHALL 返回金字塔完整结构、统计信息和健康度详情
1.6 THE Knowledge_Pyramid_Manager SHALL 支持预设的金字塔模板（AI 开发工具链、Agent 生态、Prompt 工程、模型应用能力、热点追踪）

### 需求 2：金字塔节点管理

**用户故事：** 作为知识管理员，我希望能够灵活管理金字塔中的节点，以便精细化组织知识结构。

#### 验收标准

2.1 WHEN 管理员添加节点 THEN Pyramid_Node_Manager SHALL 在指定父节点下创建包含唯一标识、名称、描述、层级、排序权重的新节点
2.2 WHEN 管理员编辑节点 THEN Pyramid_Node_Manager SHALL 更新节点的名称、描述和排序权重
2.3 WHEN 管理员删除节点 THEN Pyramid_Node_Manager SHALL 移除该节点及其所有子节点，并将关联内容标记为待重新分类
2.4 WHEN 管理员移动节点 THEN Pyramid_Node_Manager SHALL 将节点移动到新的父节点下，保持其子节点关系不变
2.5 WHEN 查询节点详情 THEN Pyramid_Node_Manager SHALL 返回节点信息、子节点列表、关联内容数量、关联信息源列表

### 需求 3：金字塔可视化与健康度

**用户故事：** 作为用户，我希望能够直观地查看金字塔结构和健康状态，以便快速了解知识组织情况。

#### 验收标准

3.1 WHEN 用户请求金字塔可视化数据 THEN Visualization_Service SHALL 返回包含节点位置、层级、连接关系的可渲染数据结构
3.2 WHEN 用户请求特定节点的子树 THEN Visualization_Service SHALL 返回以该节点为根的子树可视化数据
3.3 WHEN 系统计算金字塔健康度 THEN Health_Evaluator SHALL 评估深度平衡性（各分支深度差异）并返回 0-100 的评分
3.4 WHEN 系统计算金字塔健康度 THEN Health_Evaluator SHALL 评估节点覆盖度（是否有空节点或过载节点）并返回 0-100 的评分
3.5 WHEN 系统计算金字塔健康度 THEN Health_Evaluator SHALL 评估更新活跃度（近期内容更新频率）并返回 0-100 的评分
3.6 WHEN 健康度低于阈值 THEN Health_Evaluator SHALL 生成具体的问题描述和改进建议
3.7 THE Visualization_Service SHALL 支持按健康度、内容数量、更新时间对节点进行颜色编码

### 需求 4：信息源基础管理

**用户故事：** 作为系统管理员，我希望能够添加和配置各类信息源，以便从多渠道获取 AI 领域信息。

#### 验收标准

4.1 WHEN 管理员添加 RSS 信息源 THEN Information_Source_Manager SHALL 创建包含 URL、名称、更新检查频率、关联节点列表的信息源记录
4.2 WHEN 管理员添加 API 信息源 THEN Information_Source_Manager SHALL 创建包含端点 URL、认证方式、请求头、请求参数、响应解析规则的信息源记录
4.3 WHEN 管理员添加网页爬取信息源 THEN Information_Source_Manager SHALL 创建包含目标 URL、CSS/XPath 选择器、分页规则、抓取深度的信息源记录
4.4 WHEN 管理员编辑信息源 THEN Information_Source_Manager SHALL 更新信息源的配置参数
4.5 WHEN 管理员删除信息源 THEN Information_Source_Manager SHALL 移除信息源记录，保留已抓取的内容但标记来源已删除
4.6 WHEN 管理员查询信息源列表 THEN Information_Source_Manager SHALL 返回所有信息源的基本信息、状态、健康度
4.7 WHEN 管理员测试信息源 THEN Information_Source_Manager SHALL 执行一次测试抓取并返回结果预览
4.8 THE Information_Source_Manager SHALL 为每个信息源类型提供配置模板和示例

### 需求 5：信息流浏览界面

**用户故事：** 作为终端用户，我希望能够方便地浏览最新信息，以便快速获取 AI 领域动态。

#### 验收标准

5.1 WHEN 用户访问信息流页面 THEN Feed_View SHALL 展示按时间倒序排列的内容列表
5.2 WHEN 用户选择快速浏览模式 THEN Feed_View SHALL 展示标题、摘要、来源、时间的紧凑视图
5.3 WHEN 用户选择深度阅读模式 THEN Feed_View SHALL 展示完整摘要、标签、校验状态、相关内容
5.4 WHEN 用户点击内容条目 THEN Feed_View SHALL 展示内容详情页，包含原文链接和完整校验报告
5.5 WHEN 用户筛选内容 THEN Feed_View SHALL 支持按金字塔节点、时间范围过滤
5.6 THE Feed_View SHALL 支持无限滚动加载
5.7 THE Feed_View SHALL 显示内容的验证状态标识（多源确认/单源/待验证）

### 需求 6：金字塔可视化界面

**用户故事：** 作为用户，我希望能够通过可视化界面探索知识金字塔，以便直观了解知识结构。

#### 验收标准

6.1 WHEN 用户访问金字塔可视化页面 THEN Pyramid_View SHALL 展示可交互的金字塔结构图
6.2 WHEN 用户点击节点 THEN Pyramid_View SHALL 高亮该节点并展示节点详情面板
6.3 WHEN 用户展开节点 THEN Pyramid_View SHALL 显示该节点的子节点
6.4 WHEN 用户折叠节点 THEN Pyramid_View SHALL 隐藏该节点的子节点
6.5 WHEN 用户拖拽画布 THEN Pyramid_View SHALL 平移视图
6.6 WHEN 用户缩放画布 THEN Pyramid_View SHALL 调整视图缩放级别
6.7 WHEN 用户切换金字塔 THEN Pyramid_View SHALL 加载并展示选中金字塔的结构
6.8 THE Pyramid_View SHALL 使用颜色编码显示节点健康度
6.9 THE Pyramid_View SHALL 显示节点间的关联关系连线

### 需求 7：信息源管理界面

**用户故事：** 作为管理员，我希望能够通过界面管理所有信息源，以便维护信息获取渠道。

#### 验收标准

7.1 WHEN 管理员访问信息源管理页面 THEN Source_Management_View SHALL 展示所有信息源的列表视图
7.2 WHEN 管理员查看信息源列表 THEN Source_Management_View SHALL 显示名称、类型、状态、健康度、最后更新时间
7.3 WHEN 管理员点击信息源 THEN Source_Management_View SHALL 展示详细配置和历史抓取记录
7.4 WHEN 管理员添加信息源 THEN Source_Management_View SHALL 展示配置表单，根据类型显示不同字段
7.5 WHEN 管理员编辑信息源 THEN Source_Management_View SHALL 展示可编辑的配置表单
7.6 WHEN 管理员测试信息源 THEN Source_Management_View SHALL 执行测试抓取并展示结果预览
7.7 THE Source_Management_View SHALL 支持按类型、状态、健康度筛选信息源
7.8 THE Source_Management_View SHALL 显示信息源健康度趋势图

### 需求 8：数据持久化

**用户故事：** 作为系统，我需要可靠地存储所有数据，以便保证数据的完整性和可恢复性。

#### 验收标准

8.1 THE Database_Service SHALL 使用 PostgreSQL（生产环境）或 SQLite（开发环境）存储所有结构化数据
8.2 WHEN 数据写入操作发生 THEN Database_Service SHALL 使用事务确保数据一致性
8.3 WHEN 查询金字塔结构 THEN Database_Service SHALL 使用递归查询高效返回层级关系数据
8.4 WHEN 查询内容列表 THEN Database_Service SHALL 支持分页、排序和多条件过滤
8.5 THE Database_Service SHALL 为常用查询字段建立索引
8.6 THE Database_Service SHALL 支持数据库迁移和版本管理
8.7 THE Database_Service SHALL 实现软删除机制，保留删除记录的历史

### 需求 9：API 接口设计

**用户故事：** 作为前端开发者，我需要清晰的 API 接口，以便实现前后端分离的架构。

#### 验收标准

9.1 THE API_Service SHALL 使用 RESTful 风格设计接口
9.2 THE API_Service SHALL 为所有接口提供 OpenAPI/Swagger 文档
9.3 WHEN 请求成功 THEN API_Service SHALL 返回统一格式的成功响应
9.4 WHEN 请求失败 THEN API_Service SHALL 返回统一格式的错误响应，包含错误码和错误信息
9.5 THE API_Service SHALL 实现请求参数验证
9.6 THE API_Service SHALL 支持 CORS 跨域请求

### 需求 10：迭代开发支持

**用户故事：** 作为开发者，我希望系统支持渐进式开发，以便按迭代计划逐步完善功能。

#### 验收标准

10.1 THE System_Architecture SHALL 支持模块化设计，各模块可独立开发和测试
10.2 THE System_Architecture SHALL 定义清晰的模块接口，支持模块间松耦合
10.3 THE Database_Schema SHALL 支持向后兼容的迁移
10.4 THE System_Architecture SHALL 支持本地开发环境快速启动

### 需求 11：信息源与金字塔节点关联

**用户故事：** 作为系统，我需要维护信息源与金字塔节点的关联关系，以便将抓取的内容正确分类。

#### 验收标准

11.1 WHEN 管理员关联信息源到节点 THEN Source_Node_Mapper SHALL 建立信息源与一个或多个 Pyramid_Node 的映射关系
11.2 WHEN 管理员解除关联 THEN Source_Node_Mapper SHALL 移除指定的映射关系
11.3 WHEN 查询节点关联的信息源 THEN Source_Node_Mapper SHALL 返回该节点直接关联和继承关联的所有信息源
11.4 WHEN 查询信息源关联的节点 THEN Source_Node_Mapper SHALL 返回该信息源关联的所有节点列表
11.5 WHEN 节点被删除 THEN Source_Node_Mapper SHALL 自动清理相关的映射关系
11.6 THE Source_Node_Mapper SHALL 支持关联权重设置，表示信息源与节点的相关程度

### 需求 12：金字塔模板系统

**用户故事：** 作为管理员，我希望能够使用预设模板快速创建金字塔，以便快速启动知识组织。

#### 验收标准

12.1 THE Template_Service SHALL 提供以下预设金字塔模板：
   - AI 开发工具链（IDE、框架、库、部署工具等）
   - Agent 生态（Agent 框架、工具调用、多 Agent 协作等）
   - Prompt 工程（提示词技术、优化方法、评估方法等）
   - 模型应用能力（文本生成、代码生成、多模态等）
   - 热点追踪（新模型发布、重大更新、行业动态等）
12.2 WHEN 管理员选择模板创建金字塔 THEN Template_Service SHALL 基于模板创建完整的节点结构
12.3 THE Template_Service SHALL 支持模板的导入和导出

### 需求 13：错误处理

**用户故事：** 作为系统，我需要优雅地处理错误，以便保持系统稳定运行。

#### 验收标准

13.1 WHEN API 请求发生错误 THEN Error_Handler SHALL 返回结构化的错误响应
13.2 WHEN 数据库操作失败 THEN Error_Handler SHALL 回滚事务并记录错误
13.3 THE Error_Handler SHALL 对不同类型的错误采用不同的处理策略

### 需求 14：日志记录

**用户故事：** 作为管理员，我希望能够查看系统运行日志，以便排查问题。

#### 验收标准

14.1 THE Logging_Service SHALL 记录所有关键操作的日志，包含时间戳、操作类型、操作者、结果
14.2 THE Logging_Service SHALL 支持不同日志级别（DEBUG、INFO、WARNING、ERROR）
14.3 THE Logging_Service SHALL 将日志输出到文件和控制台
14.4 WHEN 发生错误 THEN Logging_Service SHALL 记录完整的错误堆栈和上下文信息

