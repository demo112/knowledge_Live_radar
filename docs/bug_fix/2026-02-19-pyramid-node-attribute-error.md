# 问题: Discovery error "type object 'PyramidNode' has no attribute 'updated_at'"

## 基本信息

| 项目 | 内容 |
|------|------|
| 发现日期 | 2026-02-19 |
| 状态 | 已解决 |
| 严重程度 | 高 |
| 解决日期 | 2026-02-19 |

## 描述

用户在使用 "Discover New Sources" 功能时，前端报错：`Discovery error: "type object 'PyramidNode' has no attribute 'updated_at'"`。

## 复现步骤

1. 进入信息源页面。
2. 点击 "Discover New Sources"。
3. 观察控制台错误或界面提示。

## 影响

导致发现流程中断，无法生成关键词，进而无法搜索新源。

## 根因分析

在 `backend/app/services/source_discovery.py` 中，`_get_keywords` 方法试图按 `PyramidNode.updated_at` 排序来选取节点。
然而，`PyramidNode` 模型（定义在 `backend/app/models/pyramid.py`）并没有 `updated_at` 字段。它只有 `last_content_at`, `status`, `health_score` 等。

## 解决方案

修改 `_get_keywords` 方法中的排序逻辑，不再使用不存在的 `updated_at`。
根据代码注释中的策略 "Prioritize leaf nodes and nodes with fewer contents"（优先选择内容较少的节点），改为使用 `content_count` 字段进行升序排序。

```python
# Old
query = query.order_by(PyramidNode.updated_at.desc()).limit(10)

# New
query = query.order_by(PyramidNode.content_count.asc()).limit(10)
```

## 预防措施

- 在使用模型属性前，确认模型定义中是否存在该属性。
- 增加针对 `source_discovery` 服务的单元测试，覆盖 `_get_keywords` 逻辑。

## 相关文件

- `backend/app/services/source_discovery.py`
- `backend/app/models/pyramid.py`
