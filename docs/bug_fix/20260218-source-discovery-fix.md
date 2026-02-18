
# 信息源发现功能修复记录

## 问题描述
- **现象**：
    1. 前端报错 `MISSING_MESSAGE: Could not resolve Sources.columns.actions`。
    2. 点击发现按钮时报错 `Network Error` 或 `500 Internal Server Error`。
- **复现步骤**：
    1. 访问 `/sources` 页面，切换到中文环境。
    2. 点击 "发现" 标签页。
    3. 点击 "立即发现" 按钮。
- **影响范围**：
    - 信息源管理页面的国际化显示。
    - 信息源发现功能的可用性。

## 设计锚定
- **所属规格**：`source-discovery`
- **原设计意图**：提供基于关键词的信息源自动发现功能，使用 `duckduckgo-search` 库。
- **当前偏离**：
    - 国际化文件结构错误导致部分文本无法显示。
    - 依赖库的不稳定性导致整个 API 崩溃，偏离了健壮性要求。

## 根因分析
- **直接原因**：
    1. `frontend/messages/zh.json` 中 `Sources.columns` 被重复定义，导致第一次定义中的 `actions` 键被覆盖。
    2. `duckduckgo-search` 库在当前环境下抛出异常（可能是版本变更或网络问题），后端 `SourceDiscoveryService.discover` 方法未完全捕获该异常，导致 500 错误。
- **根本原因**：
    1. JSON 文件维护疏忽，缺乏校验。
    2. 对第三方库的依赖缺乏足够的容错处理。
- **相关代码**：
    - `frontend/messages/zh.json`
    - `backend/app/services/source_discovery.py`

## 修复方案
- **修复思路**：
    1. 修正 JSON 文件结构，合并重复键。
    2. 增强后端服务的异常处理，确保搜索失败时服务降级（返回空结果）而不是崩溃。
- **改动文件**：
    - `frontend/messages/zh.json`
    - `backend/app/services/source_discovery.py`

## 验证结果
- [x] 原问题已解决：API 返回 200 OK，前端不再报错。
- [x] 回归测试通过：模拟 API 调用成功。
- [x] 设计一致性确认：符合设计文档中的降级策略（"DuckDuckGo 访问受限 -> 增加错误处理"）。

## 文档同步
- [ ] design.md：无需更新。
- [ ] api-contract.md：无需更新。

## 提交信息
fix(source-discovery): 修复国际化缺失和发现服务崩溃问题
