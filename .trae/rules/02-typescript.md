# 代码规范

## TypeScript（前端）

### 编译配置
- strict: true
- noImplicitAny: true
- strictNullChecks: true
- noImplicitReturns: true

### 强制规则 (ESLint)
- 禁止 `any`，使用 `unknown` 或具体类型 (Warn)
- 所有函数必须显式声明返回类型 (Warn)
- 禁止 `!` 断言，使用类型守卫或可选链 (Warn)
- 禁止未使用的变量 (unused-vars) (Warn)

### 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | `getPyramidById` |
| 类/接口/类型 | PascalCase | `PyramidNode` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 文件名 | kebab-case | `pyramid-view.tsx` |
| 目录名 | kebab-case | `knowledge-pyramid` |

## Python（后端）

### 代码风格
- 遵循 PEP 8
- 使用 Black 格式化（行宽 88）
- 使用 isort 排序 import
- 使用 mypy 类型检查

### 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | snake_case | `get_pyramid_by_id` |
| 类 | PascalCase | `PyramidNode` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 文件名 | snake_case | `pyramid_service.py` |
| 目录名 | snake_case | `knowledge_pyramid` |

### 类型注解
- 所有函数参数和返回值必须有类型注解
- 使用 Pydantic 模型定义数据结构
- 使用 `Optional` / `Union` 处理可选类型
