# AI 能力补全 - 需求文档

## 简介

本 spec 旨在补全 AI Radar 系统中缺失的核心 AI 能力，使系统能够真正运行起来。当前系统虽然有大量代码，但关键的 AI 配置入口和核心流程串联缺失，导致 AI 功能无法使用。

## 背景

### 当前问题

1. **P0 - AI 配置缺失**：没有任何 UI 入口配置大模型 API Key、Base URL、模型名等，所有 AI 调用都是空转
2. **P1 - 流程断裂**：内容处理后没有自动触发分类，批量分类 API 未实现
3. **P2 - 功能不完整**：信息源生命周期管理、回滚机制未实现

### 实施优先级

按照阻塞程度和影响范围，实施顺序为：
1. AI 模型配置系统（P0）
2. 内容处理自动分类（P1）
3. 批量自动分类 API（P1）
4. 信息源生命周期管理（P2）
5. 回滚机制（P2）

## 术语表

- **AI_Config（AI 配置）**: 大模型服务的配置信息，包括 API Key、Base URL、模型名、温度等参数
- **Auto_Classification（自动分类）**: 使用向量相似度将内容自动归类到金字塔节点的过程
- **Source_Lifecycle（信息源生命周期）**: 信息源从发现到淘汰的完整状态流转过程
- **Snapshot（快照）**: 金字塔结构在某个时间点的完整状态备份
- **Rollback（回滚）**: 将金字塔结构恢复到历史快照状态的操作

## 需求

### 需求 1：AI 模型配置管理

**用户故事：** 作为系统管理员，我希望能够在界面上配置大模型服务参数，以便系统能够调用 AI 服务。

#### 验收标准

1. WHEN 系统启动时 THEN Configuration_Service SHALL 在默认配置中注册以下 AI 相关配置项：
   - `ai.api_key`: API 密钥（字符串，默认为空）
   - `ai.base_url`: API 基础 URL（字符串，默认 `https://api.siliconflow.cn/v1`）
   - `ai.model`: 模型名称（字符串，默认 `deepseek-ai/DeepSeek-V3`）
   - `ai.temperature`: 默认温度（浮点数，默认 `0.3`）
   - `ai.max_retries`: 最大重试次数（整数，默认 `3`）
   - `ai.enabled`: AI 功能总开关（布尔值，默认 `false`）

2. WHEN 管理员通过 API 获取配置 THEN Configuration_Service SHALL 对 `ai.api_key` 进行脱敏处理，只显示前4位和后4位，中间用 `***` 替代

3. WHEN 管理员更新 `ai.api_key` 且新值包含 `***` THEN Configuration_Service SHALL 跳过更新，保持原值不变

4. WHEN 管理员更新 AI 配置 THEN Configuration_Service SHALL 验证配置值的有效性：
   - `ai.base_url` 必须是有效的 URL
   - `ai.temperature` 必须在 0.0 到 2.0 之间
   - `ai.max_retries` 必须是正整数

5. WHEN AI 配置变更 THEN Configuration_Service SHALL 记录变更历史到 ConfigHistory 表

### 需求 2：AI 服务动态配置

**用户故事：** 作为系统，我需要从配置服务动态读取 AI 参数，以便支持运行时切换模型而无需重启。

#### 验收标准

1. WHEN AIService 初始化时 THEN AIService SHALL 从 Configuration_Service 读取 `ai.enabled` 配置

2. WHEN `ai.enabled` 为 `false` THEN AIService SHALL 将 `client` 设置为 `None`

3. WHEN `ai.enabled` 为 `true` THEN AIService SHALL 从 Configuration_Service 读取 `ai.api_key` 和 `ai.base_url` 并初始化 OpenAI 客户端

4. WHEN AIService.chat_completion 被调用 THEN AIService SHALL 检查 `ai.enabled` 配置，如果为 `false` 则直接返回 `None`

5. WHEN AIService.chat_completion 被调用 THEN AIService SHALL 从 Configuration_Service 读取最新的 `ai.model`、`ai.temperature`、`ai.max_retries` 参数

6. WHEN AI 配置变更 THEN AIService SHALL 在下次调用时自动使用新配置，无需重启服务

7. WHEN `ai.api_key` 为空或 `ai.enabled` 为 `false` THEN 所有依赖 AI 的功能 SHALL 返回降级结果：
   - Soft_Validator 返回 `(True, {"reason": "Skipped (AI disabled)"})`
   - AI_Summary_Service 返回空摘要和空标签
   - Concept_Extractor 返回空列表

### 需求 3：AI 连通性测试

**用户故事：** 作为管理员，我希望能够测试 AI 配置是否正确，以便验证配置后立即知道是否可用。

#### 验收标准

1. WHEN 管理员调用 `POST /api/v1/config/ai/test` THEN AI_Test_Service SHALL 使用当前配置的 API Key、Base URL、Model 发送一个简单的测试请求

2. WHEN 测试请求成功 THEN AI_Test_Service SHALL 返回：
   ```json
   {
     "success": true,
     "latency_ms": <响应时间>,
     "model": "<使用的模型名>",
     "message": "AI 服务连接成功"
   }
   ```

3. WHEN 测试请求失败 THEN AI_Test_Service SHALL 返回：
   ```json
   {
     "success": false,
     "error": "<错误信息>",
     "message": "AI 服务连接失败"
   }
   ```

4. THE AI_Test_Service SHALL 使用简单的 prompt（如 "Hello"）进行测试，避免消耗过多 token

5. THE AI_Test_Service SHALL 设置较短的超时时间（10秒），避免长时间等待

### 需求 4：前端 AI 配置界面

**用户故事：** 作为管理员，我希望在设置页面有专门的 AI 配置区域，以便方便地配置和测试 AI 服务。

#### 验收标准

1. WHEN 管理员访问设置页面 THEN Settings_Page SHALL 显示「AI 模型配置」标签页

2. WHEN 管理员切换到「AI 模型配置」标签 THEN Settings_Page SHALL 显示以下表单字段：
   - API Key（password 类型输入框，显示脱敏值）
   - Base URL（text 类型输入框）
   - 模型名称（text 类型输入框）
   - 温度（number 类型输入框或 slider，范围 0.0-2.0）
   - 最大重试次数（number 类型输入框，范围 1-10）
   - 启用 AI 功能（checkbox）

3. WHEN 管理员点击「测试连接」按钮 THEN Settings_Page SHALL 调用 `/api/v1/config/ai/test` 接口并显示测试结果

4. WHEN 测试成功 THEN Settings_Page SHALL 显示绿色成功提示和响应时间

5. WHEN 测试失败 THEN Settings_Page SHALL 显示红色错误提示和错误信息

6. WHEN 管理员点击「保存」按钮 THEN Settings_Page SHALL 依次更新所有 AI 配置项

7. WHEN 配置保存成功 THEN Settings_Page SHALL 显示成功提示并刷新配置数据

8. THE Settings_Page SHALL 在 API Key 输入框旁显示提示文本："留空则禁用 AI 功能"

### 需求 5：侧边栏导航补充

**用户故事：** 作为用户，我希望能够从侧边栏快速访问设置页面，以便方便地管理系统配置。

#### 验收标准

1. WHEN 用户查看侧边栏 THEN Dashboard_Layout SHALL 在导航列表中显示「设置」菜单项

2. THE 设置菜单项 SHALL 使用 Settings 图标（lucide-react）

3. THE 设置菜单项 SHALL 链接到 `/settings` 路径

4. THE 设置菜单项 SHALL 位于导航列表的底部，在「健康」菜单项之后

### 需求 6：内容处理自动分类

**用户故事：** 作为系统，我需要在内容处理完成后自动触发分类，以便内容能够自动归类到金字塔节点。

#### 验收标准

1. WHEN ContentProcessor.process_source 完成内容保存 THEN ContentProcessor SHALL 对每个新保存的 ContentItem 调用 EvolutionEngine.auto_classify_content

2. WHEN 自动分类成功链接到节点 THEN ContentProcessor SHALL 记录链接数量到日志

3. WHEN 自动分类失败 THEN ContentProcessor SHALL 记录错误但不影响整体抓取流程

4. THE ContentProcessor SHALL 在 CrawlJob 记录中新增字段 `items_classified`（整数，默认 0）记录自动分类的内容数量

5. WHEN 抓取任务完成 THEN ContentProcessor SHALL 在日志中输出：`"Job {job_id} completed. New: {new}, Classified: {classified}, Dupe: {duplicate}, Failed: {failed}"`

### 需求 7：批量自动分类 API

**用户故事：** 作为管理员，我希望能够批量处理历史未分类内容，以便将存量内容归类到金字塔节点。

#### 验收标准

1. WHEN 管理员调用 `POST /api/v1/evolution/classify/batch` THEN Batch_Classification_Service SHALL 查询所有未链接到任何节点的 ContentItem

2. WHEN 查询到未分类内容 THEN Batch_Classification_Service SHALL 在后台任务中循环调用 EvolutionEngine.auto_classify_content

3. WHEN 批量分类任务启动 THEN API SHALL 立即返回：
   ```json
   {
     "status": "accepted",
     "message": "批量分类任务已启动",
     "total_items": <待分类内容数量>
   }
   ```

4. WHEN 批量分类任务完成 THEN Batch_Classification_Service SHALL 记录分类结果到日志：
   - 总处理数量
   - 成功分类数量
   - 失败数量

5. THE Batch_Classification_Service SHALL 支持 `limit` 参数限制单次处理的内容数量（默认 100）

6. THE Batch_Classification_Service SHALL 支持 `pyramid_id` 参数只处理特定金字塔的内容

7. WHEN 批量分类任务运行时 THEN Batch_Classification_Service SHALL 防止重复启动相同任务

### 需求 8：信息源生命周期状态机

**用户故事：** 作为系统，我需要管理信息源的生命周期状态，以便自动维护信息源质量。

#### 验收标准

1. WHEN 新信息源被创建 THEN InformationSource.status SHALL 默认设置为 `"DISCOVERED"`

2. WHEN SourceLifecycleManager.verify_source 被调用 THEN SourceLifecycleManager SHALL 执行测试抓取

3. WHEN 测试抓取成功 THEN SourceLifecycleManager SHALL 将状态更新为 `"VERIFYING"` 并安排试运行

4. WHEN 试运行期间（3次抓取）成功率 >= 80% THEN SourceLifecycleManager SHALL 将状态更新为 `"ACTIVE"`

5. WHEN ACTIVE 状态的信息源连续失败 3 次 THEN SourceLifecycleManager SHALL 将状态更新为 `"MONITORING"`

6. WHEN MONITORING 状态的信息源恢复正常（连续成功 2 次）THEN SourceLifecycleManager SHALL 将状态恢复为 `"ACTIVE"`

7. WHEN MONITORING 状态的信息源连续失败 5 次 THEN SourceLifecycleManager SHALL 将状态更新为 `"ADJUSTING"` 并生成策略调整提案

8. WHEN ADJUSTING 状态的信息源连续失败 10 次 THEN SourceLifecycleManager SHALL 将状态更新为 `"DEAD"` 并停止抓取

9. WHEN 状态变更发生 THEN SourceLifecycleManager SHALL 记录状态变更历史：
   - 变更时间
   - 旧状态
   - 新状态
   - 变更原因

10. THE SourceLifecycleManager SHALL 在定时任务中每小时检查一次所有非 DEAD 状态的信息源

### 需求 9：信息源生命周期集成

**用户故事：** 作为系统，我需要在抓取流程中集成生命周期管理，以便自动更新信息源状态。

#### 验收标准

1. WHEN ContentProcessor.process_source 成功完成 THEN ContentProcessor SHALL 调用 SourceLifecycleManager.on_crawl_success

2. WHEN ContentProcessor.process_source 失败 THEN ContentProcessor SHALL 调用 SourceLifecycleManager.on_crawl_failure

3. WHEN SourceLifecycleManager.on_crawl_success 被调用 THEN SourceLifecycleManager SHALL 重置 error_count 为 0

4. WHEN SourceLifecycleManager.on_crawl_failure 被调用 THEN SourceLifecycleManager SHALL 增加 error_count

5. WHEN error_count 达到状态转换阈值 THEN SourceLifecycleManager SHALL 自动执行状态转换

6. WHEN 状态转换为 MONITORING 或 ADJUSTING THEN SourceLifecycleManager SHALL 发送通知给管理员

### 需求 10：快照回滚功能

**用户故事：** 作为管理员，我希望能够回滚到历史快照，以便恢复错误的变更。

#### 验收标准

1. WHEN SnapshotService.create_snapshot 被调用 THEN SnapshotService SHALL 保存金字塔的完整结构到 JSON：
   - 所有节点的 id、name、description、level、parent_id
   - 所有内容关联关系（ContentNodeRelation）
   - 快照创建时间和原因

2. WHEN 管理员调用 `POST /api/v1/pyramids/{pyramid_id}/rollback/{snapshot_id}` THEN SnapshotService.rollback SHALL 执行回滚操作

3. WHEN 回滚操作开始 THEN SnapshotService SHALL 创建当前状态的快照作为回滚前备份

4. WHEN 回滚操作执行 THEN SnapshotService SHALL：
   - 软删除所有当前节点（设置 is_deleted=True）
   - 从快照 JSON 重建节点结构
   - 恢复内容关联关系
   - 保持 ContentItem 本身不变

5. WHEN 回滚成功 THEN SnapshotService SHALL 返回：
   ```json
   {
     "success": true,
     "message": "回滚成功",
     "restored_nodes": <恢复的节点数量>,
     "backup_snapshot_id": <回滚前备份的快照ID>
   }
   ```

6. WHEN 回滚失败 THEN SnapshotService SHALL 回滚数据库事务并返回错误信息

7. THE SnapshotService SHALL 在回滚前验证快照数据的完整性

8. THE SnapshotService SHALL 记录回滚操作到审计日志

### 需求 11：前端快照历史界面

**用户故事：** 作为管理员，我希望能够查看快照历史并执行回滚，以便管理金字塔版本。

#### 验收标准

1. WHEN 管理员访问金字塔详情页 THEN Pyramid_Detail_Page SHALL 显示「历史快照」标签页

2. WHEN 管理员切换到「历史快照」标签 THEN Pyramid_Detail_Page SHALL 显示快照列表：
   - 创建时间
   - 创建原因
   - 节点数量
   - 操作按钮（查看详情、回滚）

3. WHEN 管理员点击「查看详情」THEN Pyramid_Detail_Page SHALL 显示快照的节点结构预览

4. WHEN 管理员点击「回滚」THEN Pyramid_Detail_Page SHALL 显示确认对话框：
   - 警告信息："回滚将恢复到该快照的状态，当前结构将被替换"
   - 确认按钮
   - 取消按钮

5. WHEN 管理员确认回滚 THEN Pyramid_Detail_Page SHALL 调用回滚 API 并显示进度

6. WHEN 回滚成功 THEN Pyramid_Detail_Page SHALL 显示成功提示并刷新金字塔数据

7. WHEN 回滚失败 THEN Pyramid_Detail_Page SHALL 显示错误信息

## 非功能需求

### 性能要求

1. AI 配置更新应在 1 秒内生效
2. AI 连通性测试应在 10 秒内返回结果
3. 单个内容的自动分类应在 5 秒内完成
4. 批量分类每秒应处理至少 2 个内容项
5. 快照创建应在 10 秒内完成（对于 1000 个节点的金字塔）
6. 快照回滚应在 30 秒内完成（对于 1000 个节点的金字塔）

### 安全要求

1. API Key 在数据库中应加密存储（可选，首期可明文）
2. API Key 在 API 响应中必须脱敏
3. 回滚操作必须记录审计日志
4. 配置变更必须记录操作者和变更历史

### 可靠性要求

1. AI 服务不可用时，系统其他功能应正常运行
2. 批量分类任务失败不应影响其他任务
3. 回滚操作失败应保持当前状态不变
4. 状态转换应是原子操作，避免中间状态

## 验收测试场景

### 场景 1：首次配置 AI 服务

1. 管理员访问设置页面
2. 切换到「AI 模型配置」标签
3. 输入 API Key、Base URL、模型名
4. 点击「测试连接」，验证配置正确
5. 勾选「启用 AI 功能」
6. 点击「保存」
7. 系统显示保存成功
8. 触发一次内容抓取，验证 AI 摘要、标签、概念提取正常工作

### 场景 2：内容自动分类

1. 系统抓取新内容
2. 内容通过三层校验
3. AI 生成摘要、标签、概念
4. 系统自动调用向量搜索找到相似节点
5. 系统自动创建内容-节点关联
6. 管理员在金字塔可视化中看到新内容已归类

### 场景 3：批量处理历史内容

1. 管理员调用批量分类 API
2. 系统返回任务已启动
3. 后台任务处理所有未分类内容
4. 管理员查看日志确认处理结果
5. 管理员在金字塔中看到历史内容已归类

### 场景 4：信息源生命周期

1. 管理员添加新信息源（状态：DISCOVERED）
2. 系统执行测试抓取（状态：VERIFYING）
3. 试运行成功（状态：ACTIVE）
4. 信息源连续失败 3 次（状态：MONITORING）
5. 信息源恢复正常（状态：ACTIVE）
6. 信息源再次连续失败 5 次（状态：ADJUSTING）
7. 系统生成策略调整提案
8. 信息源连续失败 10 次（状态：DEAD）
9. 系统停止抓取该源

### 场景 5：快照回滚

1. 管理员执行金字塔结构变更
2. 系统自动创建变更前快照
3. 变更执行完成
4. 管理员发现变更有误
5. 管理员访问快照历史
6. 管理员选择变更前快照
7. 管理员点击回滚
8. 系统确认回滚
9. 系统创建回滚前备份快照
10. 系统恢复到历史快照状态
11. 管理员验证结构已恢复

## 实施计划

### 阶段 1：AI 配置系统（2-3 天）

- [ ] 后端：Configuration_Service 注册 AI 配置项
- [ ] 后端：AIService 改造为动态读取配置
- [ ] 后端：实现 AI 连通性测试接口
- [ ] 后端：实现 API Key 脱敏逻辑
- [ ] 前端：Settings 页面新增 AI 配置标签
- [ ] 前端：实现 AI 配置表单和测试功能
- [ ] 前端：侧边栏添加设置菜单项
- [ ] 测试：端到端测试 AI 配置流程

### 阶段 2：内容自动分类（1 天）

- [ ] 后端：ContentProcessor 集成自动分类调用
- [ ] 后端：CrawlJob 模型添加 items_classified 字段
- [ ] 后端：实现批量分类 API
- [ ] 后端：实现批量分类后台任务
- [ ] 测试：验证自动分类功能
- [ ] 测试：验证批量分类功能

### 阶段 3：信息源生命周期（2 天）

- [ ] 后端：创建 SourceLifecycleManager 服务
- [ ] 后端：实现状态转换逻辑
- [ ] 后端：实现状态变更历史记录
- [ ] 后端：ContentProcessor 集成生命周期回调
- [ ] 后端：定时任务集成生命周期检查
- [ ] 测试：验证状态转换逻辑
- [ ] 测试：验证生命周期集成

### 阶段 4：快照回滚（1-2 天）

- [ ] 后端：SnapshotService 实现 rollback 方法
- [ ] 后端：实现快照数据验证
- [ ] 后端：实现回滚 API 端点
- [ ] 后端：实现审计日志记录
- [ ] 前端：金字塔详情页添加快照历史标签
- [ ] 前端：实现快照列表和回滚界面
- [ ] 测试：验证回滚功能
- [ ] 测试：验证回滚失败处理

### 阶段 5：集成测试与文档（1 天）

- [ ] 端到端测试所有功能
- [ ] 性能测试
- [ ] 更新用户文档
- [ ] 更新 API 文档
