# 信息源测试 Network Error 修复记录

## 问题描述
- **现象**：前端点击"测试"信息源时，控制台报错 `AxiosError: Network Error`，浏览器 Network 面板显示 `net::ERR_FAILED`。
- **复现步骤**：
  1. 进入信息源管理页面
  2. 点击任意 RSS 类型信息源的"测试"按钮
  3. 观察控制台报错
- **影响范围**：信息源测试功能，以及所有使用 RSS 抓取的功能。

## 根因分析
1. **直接原因**：后端抛出未捕获异常导致 500 错误，且未正确附加 CORS 头（或因异常过早抛出导致中间件未处理），导致浏览器拦截响应。
2. **根本原因**：
   - **大小写敏感问题**：`get_fetcher` 函数中对 `type` 的判断是硬编码的小写（`"rss"`），而数据库中存储的是大写（`"RSS"`），导致抛出 `ValueError: Unknown fetcher type: RSS`。
   - **异常处理缺失**：`test_source_manual` 接口未捕获 `crawl_engine.crawl_source` 可能抛出的异常，导致异常直接冒泡到顶层。

## 修复方案
1. **修复 Fetcher 工厂**：修改 `backend/app/services/fetchers/__init__.py`，在判断类型前先转换为小写，支持大小写不敏感。
2. **增加异常处理**：在 `backend/app/routers/sources.py` 的 `test_source_manual` 接口中增加 try-except 块，捕获异常并返回 400 Bad Request，包含具体错误信息。

## 验证结果
- [x] 使用脚本模拟 API 调用，确认不再返回 500 错误。
- [x] 确认返回 400 状态码及清晰的错误信息 JSON。
- [x] 确认 Fetcher 工厂能正确处理 "RSS" 类型。

## 关联组件
- `backend/app/services/crawl_engine.py`: 依赖 Fetcher 工厂，已隐式修复。
- `backend/app/services/content_processor.py`: 依赖 Crawl Engine，已隐式修复。

## 提交信息
fix(backend): 修复信息源测试时的 Network Error 及 RSS 类型大小写问题
