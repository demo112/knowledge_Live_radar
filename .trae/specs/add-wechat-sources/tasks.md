# Tasks

- [x] Task 1: 后端实现微信文章解析与信息源创建逻辑
  - [x] SubTask 1.1: 在 `backend/app/services/fetchers/wechat_utils.py` 中实现 `extract_wechat_info(url)`，尝试提取公众号名称。
  - [x] SubTask 1.2: 更新 `RSSHubFetcher` 以支持更稳健的路径生成（处理 URL 编码等）。
  - [x] SubTask 1.3: 更新 `SourceService.create_source`，支持文章链接解析，**并增加解析失败时的手动输入提示**。
  - [x] SubTask 1.4: 编写单元测试验证解析逻辑。

- [ ] Task 2: 添加用户指定的微信信息源
  - [ ] SubTask 2.1: 获取 `https://mp.weixin.qq.com/s/iULo3kWt0Th82FKoaW4SMQ` 对应的公众号名称。
  - [ ] SubTask 2.2: 获取 `https://mp.weixin.qq.com/s/tq1w6FREMiYoPzTXCsQsKg` 对应的公众号名称。
  - [ ] SubTask 2.3: 使用公众号名称添加为 `WECHAT_MP` 源。

- [ ] Task 3: 前端支持（可选，视后端实现复杂度而定，优先后端）
  - [ ] SubTask 3.1: 检查前端添加源的表单，确保支持 `WECHAT_MP` 类型选择。
