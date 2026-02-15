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

### 禁止启动阻塞式服务 ⚠️ 严格执行

**绝对禁止的操作：**
- ❌ 启动任何 HTTP 服务器（`python -m http.server`、`coverage serve`、`pytest-html-reporter serve` 等）
- ❌ 自动打开浏览器查看报告
- ❌ 任何会输出 `Serving HTML report at http://localhost:xxxx` 的命令
- ❌ 任何需要按 Ctrl+C 退出的命令
- ❌ 任何阻塞终端的交互式命令
- ❌ Playwright `reporter: 'html'`（默认失败时启动服务器），必须使用 `reporter: [['html', { open: 'never' }]]`

**正确的做法：**
- ✅ 只生成静态 HTML 文件：`pytest --cov=backend --cov-report=html --cov-report=term`
- ✅ 测试命令执行完毕后立即退出，返回到命令提示符
- ✅ 报告文件保存到磁盘，不启动服务器

**验证方法：**
运行测试命令后，应该立即看到命令提示符（如 `$` 或 `%`），而不是看到 "Serving..." 或 "Press Ctrl+C" 等提示。

**错误示例：**
```bash
# ❌ 错误：会启动服务器阻塞
pytest --cov=backend --cov-report=html && python -m http.server 9323
pytest-html report.html --self-contained-html --serve

# ❌ 错误：会阻塞终端
Serving HTML report at http://localhost:9323. Press Ctrl+C to quit.
```

**正确示例：**
```bash
# ✅ 正确：只生成文件，立即退出
pytest --cov=backend --cov-report=html --cov-report=term
pytest --html=report.html --self-contained-html

# 命令执行后应该立即返回到提示符
$ _
```

## AI 服务测试
- 使用 Mock 替代真实 AI 调用
- 测试 Prompt 模板的格式正确性
- 测试重试和降级逻辑
