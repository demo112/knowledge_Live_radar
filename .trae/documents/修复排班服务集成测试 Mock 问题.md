# 修复排班服务集成测试 Plan

## 目标
解决 `schedule.integration.test.ts` 中因 Prisma 事务 Mock 不当导致的 `ERR_CREATE_FAILED` 错误，确保测试能正确验证"新排班优先"的冲突处理逻辑。

## 问题分析
- **现象**：测试报错 `ERR_CREATE_FAILED`。
- **原因**：在 `ScheduleService.create` 方法中，事务内执行 `createWithTx` 后会调用 `findFirst` 获取结果。在测试环境中，`findFirst` 的 Mock 返回值未能正确在事务回调（callback）中生效，导致返回 `null`，触发错误抛出。
- **结论**：需调整 `prismaMock` 的配置，确保在事务闭包内 `tx.attSchedule.findFirst` 能正确返回预设的 Mock 对象。

## 执行步骤

### 1. 修正集成测试 (schedule.integration.test.ts)
- **优化 Mock 注入**：
  - 明确区分 `findMany` (用于冲突检测) 和 `findFirst` (用于获取创建结果) 的 Mock 返回值。
  - 移除不必要的 `console.log` 调试代码。
  - 确保 `prismaMock.$transaction` 正确透传 Mock 对象。
- **完善测试用例**：
  - 验证 "无冲突创建" 场景。
  - 验证 "有冲突但强制覆盖" 场景。

### 2. 执行验证
- 运行 `npx vitest run src/modules/attendance/schedule/schedule.integration.test.ts`。
- 确认测试全部通过 (Pass)。

### 3. 后续清理
- 移除 `schedule.service.ts` 中之前添加的临时调试日志。
