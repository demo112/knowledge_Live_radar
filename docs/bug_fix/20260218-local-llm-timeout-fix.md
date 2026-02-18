# 本地LLM连接超时修复记录

## 问题描述
- **现象**：在设置界面测试本地LLM连接时，虽然配置正确，但点击“测试连接”按钮后显示超时失败。
- **复现步骤**：
  1. 进入设置界面。
  2. 启用AI功能，选择“Local First”策略。
  3. 配置本地LLM（如Ollama），Base URL设为 `http://localhost:11434/v1`。
  4. 点击“测试连接”按钮。
  5. 如果本地模型加载较慢（超过10秒），测试会失败并提示超时。
- **影响范围**：所有使用本地LLM的用户，尤其是模型冷启动较慢的情况。

## 设计锚定
- **所属规格**：AI配置与集成
- **原设计意图**：用户可以配置本地LLM的超时时间，系统应尊重该配置。
- **当前偏离**：
  1. 后端 `AITestService` 硬编码了 10.0 秒的超时时间，忽略了用户配置。
  2. 本地LLM的默认超时时间为 5.0 秒，对于冷启动来说过短。

## 根因分析
- **直接原因**：`backend/app/services/ai_test_service.py` 中 `AsyncOpenAI` 客户端初始化时使用了硬编码的 `timeout=10.0`。
- **根本原因**：代码实现未对接配置服务中的超时参数，且默认超时参数设置不合理。
- **相关代码**：`backend/app/services/ai_test_service.py`

## 修复方案
- **修复思路**：
  1. 修改 `AITestService`，使其从配置服务读取 `ai.local.timeout` (本地) 或 `ai.timeout` (云端)。
  2. 将本地LLM的默认超时时间从 5.0 秒增加到 30.0 秒，以适应模型加载延迟。
- **改动文件**：
  - `backend/app/services/ai_test_service.py`: 使用配置的超时时间。
  - `backend/app/services/config/configuration_service.py`: 更新默认配置。
  - `frontend/src/components/settings/ai-config-form.tsx`: 更新前端默认值。
  - `backend/tests/unit/test_ai_test_service.py`: 更新并增加单元测试。

## 验证结果
- [x] 原问题已解决：单元测试验证了 `AsyncOpenAI` 使用了配置的超时时间。
- [x] 回归测试通过：所有相关单元测试通过。
- [x] 设计一致性确认：代码现在符合“用户可配置超时时间”的设计意图。

## 文档同步
- [ ] design.md：无需更新
- [ ] api-contract.md：无需更新

## 提交信息
fix(ai): 修复本地LLM连接测试超时问题，支持自定义超时时间
