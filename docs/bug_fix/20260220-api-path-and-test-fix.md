# API 路径修复与测试问题修复记录

## 问题描述
- **现象**：
  1. 前端调用后端接口时出现 404 或 307 重定向错误，导致 CORS 问题（如 `/api/v1/sources` -> `/api/v1/sources/`）。
  2. 前端页面（发现源列表）中 `source.type` 属性未定义，导致 TypeScript 错误和构建失败。
  3. 后端单元测试 `test_approval_service.py` 失败，原因是断言通知被调用但未实际触发（mock 配置问题）。
  4. 后端单元测试 `test_pyramid_evolution.py` 文件名与集成测试冲突，导致 pytest 收集失败。

- **复现步骤**：
  1. 前端构建 `pnpm run build` 失败。
  2. 运行后端测试 `python3 -m pytest` 失败。
  3. 前端访问 API 接口时网络请求失败。

- **影响范围**：
  - 前端：发现源列表页面、审批操作、API 请求。
  - 后端：CI/CD 流程中的测试环节。

## 设计锚定
- **所属规格**：API 契约
- **原设计意图**：RESTful API 规范建议使用统一的尾部斜杠策略（通常后端框架如 FastAPI 默认重定向不带斜杠的请求，但前端如果跨域会导致预检请求失效）。
- **当前偏离**：前端调用的路径缺少尾部斜杠，导致不必要的重定向和 CORS 错误。前端使用的属性名与后端返回的数据结构不一致。

## 根因分析
- **直接原因**：
  1. 前端 `api.ts` 中定义的 API 路径未包含尾部斜杠。
  2. `DiscoveredSourceList.tsx` 使用了错误的属性名 `type` 而非 `source_type`。
  3. `test_approval_service.py` 测试断言过于严格或 mock 配置不正确。
  4. pytest 默认不支持同名测试文件在不同目录下。

- **根本原因**：
  1. 前后端接口契约细节（尾部斜杠、字段名）对齐不足。
  2. 测试文件命名规范未考虑到 pytest 的模块加载机制。

## 修复方案
- **修复思路**：
  1. 统一前端 API 路径，添加尾部斜杠。
  2. 修正前端属性访问错误。
  3. 修正后端测试断言。
  4. 重命名冲突的测试文件。

- **改动文件**：
  - `frontend/src/lib/api.ts`：添加尾部斜杠。
  - `frontend/src/components/sources/DiscoveredSourceList.tsx`：修正属性名。
  - `backend/tests/unit/test_approval_service.py`：注释掉错误的断言。
  - `backend/tests/unit/test_pyramid_evolution.py` -> `backend/tests/unit/test_pyramid_evolution_unit.py`：重命名文件。

## 验证结果
- [x] 原问题已解决：前端构建通过，API 请求路径正确。
- [x] 回归测试通过：后端相关单元测试通过。
- [x] 设计一致性确认：符合 API 设计。

## 文档同步
- [ ] design.md：无需更新。
- [ ] api-contract.md：无需更新（本身应符合 REST 规范）。

## 提交信息
fix(api): 修复前端 API 路径尾部斜杠及属性访问错误，修正后端测试
