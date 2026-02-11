# 日志规范

## 级别
| 级别 | 用途 |
|------|------|
| ERROR | 错误，需要关注 |
| WARN | 警告，可能有问题 |
| INFO | 重要信息 |
| DEBUG | 调试信息 |

## 格式
`[时间] [级别] [模块] [用户ID] 消息 {上下文}`

## WARN/ERROR 必须携带
- request/response（接口场景）
- stack（完整调用堆栈）
- args（各层调用参数）
- context（traceId、时间戳等）

## 禁止记录
密码、Token、身份证号、银行卡号等敏感信息

## 强制执行 (DoD)
- **禁止使用 `console.log` / `console.error`**：生产环境代码必须使用统一的 Logger (ESLint Error)。
- **统一工具**：Server 端使用 `src/common/logger.ts`。
