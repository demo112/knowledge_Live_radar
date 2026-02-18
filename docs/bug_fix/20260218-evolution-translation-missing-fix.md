# Evolution 翻译缺失修复记录

## 问题描述
- **现象**：前端控制台报错 `MISSING_MESSAGE: Could not resolve 'Evolution' in messages for locale 'zh'`。
- **复现步骤**：访问金字塔详情页，查看 EvolutionPanel 组件。
- **影响范围**：中文环境下 EvolutionPanel 组件无法显示翻译文本。

## 设计锚定
- **所属规格**：前端国际化 (i18n)
- **原设计意图**：所有 UI 文本应通过 `next-intl` 进行国际化，`zh.json` 应包含所有使用的 namespace。
- **当前偏离**：`zh.json` 文件存在语法错误（提前闭合），导致 `Evolution` section 未被正确解析，且存在重复的 `Settings` block。

## 根因分析
- **直接原因**：`frontend/messages/zh.json` 文件在第 1173 行附近存在多余的闭合大括号，导致文件结构损坏。
- **根本原因**：可能是之前的合并或编辑操作不当，导致文件内容截断或拼接错误。
- **相关代码**：`frontend/messages/zh.json`

## 修复方案
- **修复思路**：修复 JSON 语法错误，移除多余的闭合括号，并清理文件末尾重复的 `Settings` block。
- **改动文件**：`frontend/messages/zh.json`

## 验证结果
- [x] 原问题已解决：验证脚本确认 `Evolution` key 存在且包含所需字段。
- [x] 回归测试通过：JSON 语法校验通过。
- [x] 设计一致性确认：符合 i18n 规范。

## 文档同步
- [ ] design.md：无需更新
- [ ] api-contract.md：无需更新

## 提交信息
fix(i18n): 修复 zh.json 语法错误导致的 Evolution 翻译缺失
