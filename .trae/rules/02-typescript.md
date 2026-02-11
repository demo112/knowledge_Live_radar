# TypeScript 规范

## 编译配置
- strict: true
- noImplicitAny: true
- strictNullChecks: true
- noImplicitReturns: true

## 强制规则 (ESLint)
- 禁止 `any`，使用 `unknown` 或具体类型 (Warn)
- 所有函数必须显式声明返回类型 (Warn)
- 禁止 `!` 断言，使用类型守卫或可选链 (Warn)
- 禁止未使用的变量 (unused-vars) (Warn)

## 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | `getUserById` |
| 类/接口/类型 | PascalCase | `UserService` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 文件名 | kebab-case | `user-service.ts` |
| 目录名 | kebab-case | `user-management` |
