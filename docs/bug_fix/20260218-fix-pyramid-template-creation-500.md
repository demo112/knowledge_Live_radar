# 修复使用模板创建金字塔 500 错误

## 问题描述
- **现象**：使用模板创建金字塔时，前端报错 `Request failed with status code 500`。
- **复现步骤**：
  1. 调用 `POST /api/v1/pyramids/from-template/{templateId}` 接口。
  2. 后端抛出 `fastapi.exceptions.ResponseValidationError`。
- **影响范围**：金字塔模板创建功能。

## 设计锚定
- **所属规格**：知识金字塔管理 (Pyramid Management)
- **原设计意图**：创建金字塔后应返回包含完整节点结构的详情响应。
- **当前偏离**：`TemplateService.import_template` 返回的 `Pyramid` 对象中 `nodes` 关系未加载，导致 Pydantic 模型验证时触发 SQLAlchemy 异步延迟加载错误。

## 根因分析
- **直接原因**：SQLAlchemy `MissingGreenlet` 错误。
- **根本原因**：在异步环境中，尝试访问未加载的关联关系 (`nodes`)。`create_pyramid` 返回的对象未加载 `nodes`，而后续虽然创建了节点，但原对象状态未更新。
- **相关代码**：`backend/app/services/template_service.py` 中的 `import_template` 方法。

## 修复方案
- **修复思路**：在 `import_template` 方法最后，调用 `pyramid_service.get_pyramid_details(pyramid.id)` 重新加载包含节点的金字塔对象。
- **改动文件**：`backend/app/services/template_service.py`

## 验证结果
- [x] 原问题已解决：使用 curl 调用接口成功返回包含节点的 JSON 数据。
- [x] 回归测试通过：手动验证接口返回结构正确。
- [x] 设计一致性确认：符合返回完整金字塔详情的设计。

## 文档同步
- [ ] design.md：无需更新。
- [ ] api-contract.md：无需更新。

## 提交信息
fix(pyramid): 修复使用模板创建金字塔时的 500 错误

原因：修复 SQLAlchemy 异步延迟加载导致的 ResponseValidationError。
变更：在 import_template 中重新加载包含节点的金字塔对象。
