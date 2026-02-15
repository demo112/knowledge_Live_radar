# AI 摘要内容杂乱修复记录

## 问题描述
- **现象**：前端动态页面（Feed）中，AI 摘要显示了未渲染的 HTML 标签（如 `&lt;h3&gt;`），内容显得杂乱且格式错误。
- **复现步骤**：
  1. 抓取包含 HTML 格式内容的 RSS 源。
  2. 触发 AI 摘要生成。
  3. 查看前端 Feed 页面。
- **影响范围**：前端动态页面、所有包含 AI 摘要的内容展示。

## 设计锚定
- **所属规格**：`clean-and-summary`
- **原设计意图**：提供简洁、经过 AI 处理的核心观点摘要。
- **当前偏离**：AI 摘要生成逻辑与 Prompt 不匹配，导致摘要生成失败并回退到包含原始 HTML 的内容文本，且前端未对 HTML 标签进行过滤。

## 根因分析
- **直接原因**：
  1. 后端 `generate_summary` 预期返回 JSON，但 Prompt 仅要求返回纯文本，导致解析失败。
  2. 解析失败后，摘要字段为空，前端回退到展示原始 `content_text`。
  3. `content_text` 包含来自源站的 HTML 标签。
- **根本原因**：后端 Prompt 定义与 AI 服务解析逻辑不一致；前端渲染缺乏安全性与清洁度处理。
- **相关代码**：
  - [summary_generation.yaml](file:///Users/cooperd/Documents/Ai_code/knowledge_radar/knowledge_Live_radar/backend/app/prompts/summary_generation.yaml)
  - [ai_service.py](file:///Users/cooperd/Documents/Ai_code/knowledge_radar/knowledge_Live_radar/backend/app/services/ai_service.py)
  - [feed/page.tsx](file:///Users/cooperd/Documents/Ai_code/knowledge_radar/knowledge_Live_radar/frontend/src/app/[locale]/(dashboard)/feed/page.tsx)

## 修复方案
- **修复思路**：
  1. **Prompt 升级**：强制 AI 返回 JSON 格式，并明确禁止输出 HTML 标签。
  2. **后端鲁棒性**：在 `generate_summary` 中增加非 JSON 响应的回退处理。
  3. **前端清洗**：增加 `stripHtml` 工具函数，确保摘要和回退文本在展示前经过清洗。
- **改动文件**：
  - `backend/app/prompts/summary_generation.yaml`
  - `backend/app/services/ai_service.py`
  - `frontend/src/lib/utils.ts`
  - `frontend/src/app/[locale]/(dashboard)/feed/page.tsx`

## 验证结果
- [x] 原问题已解决：测试脚本验证 AI 现在能正确返回 JSON 摘要。
- [x] 回归测试通过：前端编译通过，且具备 HTML 清洗能力。
- [x] 设计一致性确认：摘要现在更加简洁且无杂乱标签。

## 文档同步
- [ ] design.md：无需更新
- [ ] api-contract.md：无需更新

## 提交信息
fix(ai): 修复 AI 摘要内容杂乱及 HTML 标签未过滤问题
