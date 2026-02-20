# 信息源发现模型配置错误修复记录

## 问题描述
- **现象**：信息源发现（Discovery）功能在执行自适应查询生成时失败，报错 `Model does not exist` (400) 或 `model 'deepseek-chat' not found` (404)。
- **复现步骤**：触发信息源发现任务，或直接调用 `DiscoveryProcessor.generate_adaptive_queries`。
- **影响范围**：信息源发现功能完全不可用。

## 设计锚定
- **所属规格**：source-discovery-context
- **原设计意图**：应使用系统配置的默认模型或支持的模型。
- **当前偏离**：`prompts/discovery/adaptive_query_generation.md` 硬编码了 `model: deepseek-chat`，而当前环境（SiliconFlow）不支持该模型名称（应为 `deepseek-ai/DeepSeek-V3`），且 Local 模式也不支持该模型。

## 根因分析
- **直接原因**：Prompt 模板 Frontmatter 中指定了无效的 `model: deepseek-chat`。
- **根本原因**：`DiscoveryProcessor` 优先使用 Prompt 中的模型配置，且未做有效性校验或回退。
- **相关代码**：`prompts/discovery/adaptive_query_generation.md`

## 修复方案
- **修复思路**：移除 Prompt 模板中的 `model` 指定，使其回退到系统默认配置的模型。
- **改动文件**：
  - `prompts/discovery/adaptive_query_generation.md`
  - `docs/features/source-discovery-context/design.md` (同步文档)

## 验证结果
- [x] 原问题已解决：验证脚本确认 `DiscoveryProcessor` 调用 AI Client 时 `model` 参数为 `None`，将使用默认配置。
- [x] 回归测试通过：`verify_fix_discovery.py` 执行成功。
- [x] 设计一致性确认：文档已同步更新。

## 文档同步
- [x] design.md：已更新
- [ ] api-contract.md：无需更新

## 提交信息
fix(discovery): 移除自适应查询生成Prompt中的无效模型配置
