# 测试规范

## 测试类型
| 类型 | 位置 | 命名 | 说明 |
|------|------|------|------|
| 单元测试 | 同目录 | `*.test.ts` | 针对函数/类 |
| 集成测试 | `__tests__/` | `*.integration.test.ts` | 针对模块/API |
| E2E测试 | `packages/e2e/` | `*.spec.ts` | 全链路黑盒测试 |

## E2E 测试架构 (Strict)

### 唯一路径
**`packages/e2e/`** 是项目中**唯一**允许存放 E2E 测试代码的地方。
- 禁止在 `packages/web` 或 `packages/app` 中创建 `e2e` 目录。

### 目录结构
| 类型 | 路径 | 技术栈 |
|------|------|--------|
| Web/Server | `tests/*.spec.ts` | Playwright |
| App (Mobile) | `tests/app/*.test.ts` | Maestro / Detox |

### 解耦原则 (Decoupling)
1.  **禁止源码引用**：E2E 测试代码**严禁** import `packages/server`, `packages/web`, `packages/app` 的源代码。
2.  **黑盒测试**：必须通过公开接口（HTTP API）或 UI 交互进行验证。
3.  **配置注入**：端口、URL 等配置必须通过环境变量注入，禁止读取兄弟项目的配置文件（如 `.env`）。
4.  **数据隔离**：测试数据准备和清理必须通过 API 调用实现，禁止直接连接数据库操作。

## 覆盖率要求
| 模块 | 最低覆盖率 |
|------|-----------|
| API接口 | 95% |
| 核心业务逻辑 | 90% |
| 工具函数 | 90% |
