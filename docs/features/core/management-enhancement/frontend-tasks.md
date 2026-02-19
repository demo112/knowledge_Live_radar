# Frontend Tasks: Core Management Enhancement

## 概览

| 指标 | 值 |
|------|-----|
| 总任务数 | 6 |
| 涉及模块 | api, components, pages |
| 预计总时间 | 60 分钟 |

## 任务清单

#### Task 1: API Client & Types
| 属性 | 值 |
|------|-----|
| 文件 | `frontend/src/lib/api.ts`<br>`frontend/src/types/index.ts` |
| 操作 | 修改 |
| 内容 | 添加 `getHealth`, `getVisualization`, `nodeApi` (split/link), `mergeNodes` 接口定义及相关 TypeScript 类型 |
| 验证 | 编译通过，无类型错误 |

#### Task 2: HealthDashboard 组件
| 属性 | 值 |
|------|-----|
| 文件 | `frontend/src/components/pyramid/HealthDashboard.tsx` |
| 操作 | 新增 |
| 内容 | 展示健康度评分、指标详情卡片、改进建议列表 |
| 验证 | 能够正确渲染 Mock 数据 |

#### Task 3: NodeActionDialogs 组件
| 属性 | 值 |
|------|-----|
| 文件 | `frontend/src/components/pyramid/NodeActions.tsx` |
| 操作 | 新增 |
| 内容 | 实现拆分 (Split)、合并 (Merge)、关联 (Link) 的表单弹窗 |
| 验证 | 弹窗正常弹出，表单验证逻辑正确 |

#### Task 4: PyramidVisualizer 组件
| 属性 | 值 |
|------|-----|
| 文件 | `frontend/src/components/pyramid/PyramidVisualizer.tsx` |
| 操作 | 新增 |
| 内容 | 集成 ReactFlow，加载后端数据，处理节点点击和右键菜单 |
| 验证 | 能够渲染节点图，节点可交互 |

#### Task 5: 页面集成
| 属性 | 值 |
|------|-----|
| 文件 | `frontend/src/app/(dashboard)/pyramid/[id]/page.tsx` |
| 操作 | 修改 |
| 内容 | 引入 HealthDashboard 和 PyramidVisualizer，替换原有占位内容 |
| 验证 | 页面完整展示，功能流程跑通 |

#### Task 6: 验证与优化
| 属性 | 值 |
|------|-----|
| 文件 | - |
| 操作 | 验证 |
| 内容 | 执行完整流程：查看健康度 -> 可视化查看 -> 拆分节点 -> 合并节点 -> 关联节点 |
| 验证 | 所有操作成功，UI 反馈正常 |
