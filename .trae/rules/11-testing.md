# 测试规范

## 测试类型

### 后端（Python）
| 类型 | 位置 | 命名 | 工具 |
|------|------|------|------|
| 单元测试 | `backend/tests/unit/` | `test_*.py` | pytest |
| 集成测试 | `backend/tests/integration/` | `test_*.py` | pytest + httpx |
| API 测试 | `backend/tests/api/` | `test_*.py` | pytest + TestClient |

### 前端（TypeScript）
| 类型 | 位置 | 命名 | 工具 |
|------|------|------|------|
| 单元测试 | 同目录 | `*.test.ts` | Jest / Vitest |
| 组件测试 | 同目录 | `*.test.tsx` | Testing Library |

## 测试重点模块

| 模块 | 优先级 | 说明 |
|------|--------|------|
| 校验引擎（硬性/软性/交叉） | P0 | 数据质量核心 |
| 抓取引擎 | P0 | 信息获取核心 |
| 审批流程 | P0 | 人类决策核心 |
| 金字塔 CRUD | P1 | 基础数据管理 |
| AI 服务集成 | P1 | 需 Mock 测试 |
| 健康度计算 | P2 | 评估逻辑 |

## 覆盖率要求
| 模块 | 最低覆盖率 |
|------|-----------|
| API 路由 | 90% |
| 核心服务（校验、抓取、审批） | 90% |
| 工具函数 | 85% |
| 前端组件 | 80% |

## 测试执行规范

### 禁止启动阻塞式服务
- 运行测试或生成覆盖率报告时，**禁止**启动任何本地 HTTP 服务器（如 `python -m http.server`、`coverage serve` 等）来展示报告
- 覆盖率报告只允许生成静态文件（`coverage html` 或 `pytest --cov-report=html`），不得自动打开浏览器或启动服务
- 测试命令必须是非交互式的，执行完毕后立即退出，不得阻塞终端
- 正确示例：`pytest --cov=backend --cov-report=html --cov-report=term`
- 错误示例：生成报告后执行 `python -m http.server 9323` 或任何 `Serving HTML report at http://localhost:xxxx` 的命令

## AI 服务测试
- 使用 Mock 替代真实 AI 调用
- 测试 Prompt 模板的格式正确性
- 测试重试和降级逻辑
