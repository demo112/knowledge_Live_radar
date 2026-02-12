# Design: 手动增删改查 (Pyramids & Sources)

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 知识金字塔 CRUD | 前端页面: `pyramid/page.tsx` 增加创建、编辑、删除弹窗/按钮。调用 `pyramidApi`。 |
| Story 2: 信息源 CRUD | 前端页面: `sources/page.tsx` 增加编辑、删除功能。调用 `sourceApi`。 |

## 数据模型

后端数据模型已存在，无需变更。

- `Pyramid`: `backend/app/models/pyramid.py`
- `InformationSource`: `backend/app/models/source.py`

## API定义

后端 API 已存在，前端需要补充 `api.ts` 中的调用方法。

### `pyramidApi` 扩展
- `update(id: string, data: any)`: `PUT /pyramids/{id}`
- `delete(id: string)`: `DELETE /pyramids/{id}`

### `sourceApi` 扩展
- `update(id: string, data: any)`: `PUT /sources/{id}`
- `delete(id: string)`: `DELETE /sources/{id}`

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `frontend/src/lib/api.ts` | 修改 | 增加 `pyramidApi` 和 `sourceApi` 的 `update` 和 `delete` 方法 |
| `frontend/src/app/(dashboard)/pyramid/page.tsx` | 修改 | 增加“新建”、“编辑”、“删除”按钮和对应的弹窗逻辑 |
| `frontend/src/app/(dashboard)/sources/page.tsx` | 修改 | 增加“编辑”、“删除”按钮和对应的弹窗逻辑 |
| `frontend/src/components/common/ConfirmModal.tsx` | 新增 | (可选) 通用二次确认弹窗组件 |

## 引用的已有代码

- `frontend/src/lib/api.ts` - 基础 API 客户端
- `backend/app/routers/pyramids.py` - 后端金字塔路由
- `backend/app/routers/sources.py` - 后端信息源路由

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 金字塔列表展示 | 无影响 | 低 |
| 信息源列表展示 | 无影响 | 低 |

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 弹窗组件实现 | 使用简单的 React State 控制显示 | 快速实现且逻辑简单 |
| 表单处理 | 使用原生 `useState` 绑定表单 | 减少额外依赖 |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| 删除数据无法恢复 | 用户误删重要金字塔或信息源 | 增加二次确认弹窗 |

## 需要人决策

- [ ] 是否需要引入专门的 UI 库（如 Shadcn UI）来实现弹窗？(建议：暂时使用原生 Tailwind 实现以保持简单)
