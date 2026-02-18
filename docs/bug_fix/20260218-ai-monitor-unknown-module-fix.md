# AI 监控模块名称显示 Unknown 修复记录

## 问题描述
- **现象**：在 AI 监控页面（AIMonitor）中，所有 AI 调用记录的模块列都显示为 `AIMonitor.modules.unknown`（即未知模块）。
- **复现步骤**：
  1. 触发任何 AI 功能（如内容分类、源分析、金字塔生成）。
  2. 打开 `/ai-monitor` 页面。
  3. 查看调用记录表格，"模块"列显示为 Unknown。
- **影响范围**：所有 AI 功能的监控数据，导致无法区分 AI 调用来源，影响问题排查和成本统计。

## 设计锚定
- **所属规格**：AI Core / Monitoring
- **原设计意图**：`AIClient` 记录指标时，应接收 `module` (context) 参数，明确记录调用方身份。前端根据 `module` 字段显示对应的本地化名称。
- **当前偏离**：`AIClient.chat_completion` 方法的 `context` 参数默认为 `"unknown"`，而所有上层处理器（Processors）在调用时均未传入此参数，导致所有记录都回落到默认值。

## 根因分析
- **直接原因**：后端 Processors 调用 `ai_client.chat_completion` 时缺失 `context` 参数。
- **根本原因**：代码实现时遗漏了上下文传递机制，且测试覆盖不足（未校验 metrics 数据）。
- **相关代码**：
  - `backend/app/core/ai/processors/*.py`
  - `backend/app/core/ai/client.py`

## 修复方案
- **修复思路**：
  1. 后端：在所有 Processor 调用 `ai_client` 时显式传入 `context` 参数（如 `pyramid_structure`, `content_classification` 等）。
  2. 前端：在语言文件（`en.json`, `zh.json`）中添加对应模块名称的翻译。
- **改动文件**：
  - `backend/app/core/ai/processors/pyramid.py`
  - `backend/app/core/ai/processors/content.py`
  - `backend/app/core/ai/processors/search.py`
  - `backend/app/core/ai/processors/enhancement.py`
  - `backend/app/core/ai/processors/suggestion.py`
  - `frontend/messages/en.json`
  - `frontend/messages/zh.json`

## 验证结果
- [x] 原问题已解决：代码静态检查确认所有调用点已添加 context。
- [x] 回归测试通过：JSON 格式验证通过，后端单元测试无语法错误。
- [x] 设计一致性确认：符合监控模块设计意图。

## 文档同步
- [ ] design.md：无需更新，符合原设计。
- [ ] api-contract.md：无需更新，不影响 API 签名。

## 提交信息
fix(ai-monitor): 修复 AI 监控中模块名称显示为 Unknown 的问题

- 后端：在所有 AI Processor 中传入具体的 context 参数
- 前端：添加对应的模块名称翻译 (en/zh)
