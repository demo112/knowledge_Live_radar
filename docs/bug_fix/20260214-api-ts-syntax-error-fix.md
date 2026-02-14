# API.ts 语法错误修复记录

## 问题描述
- **现象**：构建报错 `Parsing ecmascript source code failed` at `./src/lib/api.ts:151:5`.
- **复现步骤**：运行 `npm run build` 或 `next build`.
- **影响范围**：前端构建失败.

## 设计锚定
- **所属规格**：前端 API 客户端.
- **原设计意图**：提供 `sourceApi` 和 `configApi` 对象供前端调用后端接口.
- **当前偏离**：`sourceApi.getTemplates` 缺少闭合括号，且文件末尾存在重复的垃圾代码.

## 根因分析
- **直接原因**：
    1. `frontend/src/lib/api.ts` 中 `sourceApi.getTemplates` 方法缺少 `},` 闭合.
    2. 文件末尾存在重复的 `getAll`, `update`, `testAIConnection` 代码块（无对象包裹）.
- **根本原因**：代码编辑或合并时的错误.
- **相关代码**：`frontend/src/lib/api.ts`.

## 修复方案
- **修复思路**：
    1. 为 `getTemplates` 添加闭合.
    2. 将末尾的 `testAIConnection` 方法合并回 `configApi`.
    3. 删除末尾的垃圾代码.
    4. 移除未使用的导入 `SynonymBulkCreate`.
- **改动文件**：`frontend/src/lib/api.ts`.

## 验证结果
- [x] 原问题已解决 (Lint 通过，无解析错误)
- [x] 回归测试通过 (Lint 检查 api.ts 无警告)
- [x] 设计一致性确认

## 文档同步
- [ ] design.md：无需更新
- [ ] api-contract.md：无需更新

## 提交信息
fix(frontend): 修复 api.ts 语法错误及清理垃圾代码
