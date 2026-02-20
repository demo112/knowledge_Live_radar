# 微信公众号信息源支持 Spec

## Why
用户希望将微信公众号作为信息源补充到系统中，并提供了具体的文章链接作为示例。目前系统对微信公众号的支持（`WECHAT_MP`）仅依赖 RSSHub 的基础实现，且不支持直接通过文章链接添加公众号，使用门槛较高。

## What Changes
- **后端 (Backend)**:
  - 增强 `SourceService`，支持解析微信文章 URL 提取公众号信息（名称/ID）。
  - 优化 `RSSHubFetcher`，使其能处理公众号 ID 或名称，并映射到正确的 RSSHub 路由（如 `/wechat/gzh/{id}`）。
  - 实现一个工具函数 `extract_wechat_info`，尝试从文章 HTML 中提取 `nickname` 或 `__biz` 值。
  - 添加这两个示例公众号为系统默认/初始信息源。

- **前端 (Frontend)**:
  - 在“添加信息源”对话框中，针对 `WECHAT_MP` 类型，允许用户输入“文章链接”作为替代“公众号ID”的方式，系统自动解析。

## Impact
- **Affected specs**: Source Management
- **Affected code**: 
  - `backend/app/services/source_service.py`
  - `backend/app/services/fetchers/rsshub.py`
  - `backend/app/routers/sources.py`
  - `frontend/src/components/source/add-source-dialog.tsx` (假设存在)

## ADDED Requirements
### Requirement: 通过文章链接添加微信公众号
系统应允许用户输入一篇微信公众号文章的 URL，系统自动提取该公众号的名称或 ID，并创建对应的 `WECHAT_MP` 类型信息源。

#### Scenario: 用户输入文章链接
- **WHEN** 用户在添加源界面选择“微信公众号”并输入文章链接 `https://mp.weixin.qq.com/s/...`
- **THEN** 系统解析链接，提取公众号名称（如 "Rowboat"），并自动填入名称字段，将 ID/名称填入 URL 字段（供 RSSHub 使用）。

## MODIFIED Requirements
### Requirement: RSSHub 抓取逻辑
优化 `RSSHubFetcher`，确保其能正确处理中文名称或 BizID 的编码，以适配 RSSHub 的 `/wechat/gzh/` 接口。
