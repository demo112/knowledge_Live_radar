# Definition of Done (DoD)

所有任务在标记为"完成"前，必须满足以下标准：

## 1. 代码质量
- [ ] **Lint 通过**：运行 `npm run lint` 无报错。
- [ ] **无 Console**：生产代码中无 `console.log` / `console.error` (使用 Logger)。
- [ ] **类型安全**：无 `any` (除非显式注明原因)，无 TypeScript 编译错误。

## 2. 测试覆盖
- [ ] **单元测试**：核心业务逻辑有对应的 `.test.ts`。
- [ ] **运行通过**：`npm test` 全部通过。

## 3. 文档同步
- [ ] **文档结构**：功能目录下存在 `requirements.md`, `design.md`, `tasks.md`。
- [ ] **Docs Lint**：运行 `node scripts/docs-lint.js` 通过。
- [ ] **内容更新**：API 变更已同步到 `design.md`。

## 4. Git 规范
- [ ] **Commit Message**：符合 `<type>(<scope>): <中文描述>`。
- [ ] **原子提交**：一个 Commit 只做一件事。

## 5. 验证
- [ ] **本地验证**：功能在本地运行正常。
- [ ] **日志检查**：错误路径有充足的 ERROR/WARN 日志。
