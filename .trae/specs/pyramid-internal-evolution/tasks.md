# Tasks

- [x] Task 1: 扩展 PyramidService 实现进化能力
  - [x] SubTask 1.1: 在 `PyramidService` 中集成 `RestructureAdvisor`，实现 `analyze_structure` 方法。
  - [x] SubTask 1.2: 在 `PyramidService` 中集成 `DriftDetector`，实现 `detect_drift` 方法。
  - [x] SubTask 1.3: 实现 `get_optimization_suggestions` 方法，查询 `Approval` 表中针对该金字塔的建议。
  - [x] SubTask 1.4: 实现 `apply_suggestion` 方法，根据建议类型（split/merge/move）调用相应的 Service 方法并更新 Approval 状态。
  - [x] SubTask 1.5: 实现 `reject_suggestion` 方法，更新 Approval 状态为 rejected。

- [x] Task 2: 增强 Pyramid API 接口
  - [x] SubTask 2.1: 新增 `POST /api/v1/pyramids/{id}/analyze` 接口，触发分析。
  - [x] SubTask 2.2: 新增 `GET /api/v1/pyramids/{id}/suggestions` 接口，获取建议列表。
  - [x] SubTask 2.3: 新增 `POST /api/v1/pyramids/{id}/suggestions/{suggestion_id}/apply` 接口，执行建议。
  - [x] SubTask 2.4: 新增 `POST /api/v1/pyramids/{id}/suggestions/{suggestion_id}/reject` 接口，拒绝建议。

- [x] Task 3: 重构 EvolutionEngine
  - [x] SubTask 3.1: 修改 `EvolutionEngine.run_cycle`，使其调用 `PyramidService` 的新方法，而不是直接使用 Advisor。

- [x] Task 4: 验证与测试
  - [x] SubTask 4.1: 编写测试用例验证 `PyramidService.analyze_structure` 能生成建议。
  - [x] SubTask 4.2: 编写测试用例验证 `PyramidService.apply_suggestion` 能正确执行拆分/合并操作。
  - [x] SubTask 4.3: 验证 API 接口的连通性。

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 1
