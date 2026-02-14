# 信息源配置指南

Knowledge Radar 支持多种类型的信息源。为了获取最佳体验，建议按照以下分类进行配置。

## 1. 内置源与原生 RSS (已自动配置)

系统已内置了主流 AI 媒体和技术博客的 RSS 源，包括：
- **AI 媒体**: 机器之心、量子位、36氪、智东西
- **技术博客**: 科学空间、阮一峰、CoolShell、美团技术团队
- **官方动态**: OpenAI, Google, Anthropic, HuggingFace

这些源开箱即用，无需额外配置。

## 2. 桥接源 (需额外服务)

对于微信公众号、知乎、B站等不提供原生 RSS 的平台，需要使用桥接服务。

### 2.1 微信公众号 (WeWe RSS)

**推荐方案**: 使用 [WeWe RSS](https://github.com/cooderl/wewe-rss) 将公众号转为 RSS。

1. **部署 WeWe RSS**:
   ```bash
   # 使用 Docker 部署
   docker run -d --name wewe-rss -p 4000:4000 -v $(pwd)/data:/app/data cooderl/wewe-rss-sqlite
   ```
2. **获取 RSS 链接**:
   - 登录 WeWe RSS 后台
   - 添加公众号
   - 复制生成的 RSS 链接 (例如: `http://localhost:4000/feed/wechat/jiqizhixin`)

3. **添加到 Knowledge Radar**:
   - 可以在 `backend/seed_sources.py` 中取消注释相关模板
   - 或在系统界面中手动添加。

### 2.2 知乎/B站/微博 (RSSHub)

**推荐方案**: 使用 [RSSHub](https://docs.rsshub.app/)。

1. **使用公共实例 (不稳定)**:
   - 知乎日报: `https://rsshub.app/zhihu/daily`
   - *注意: 公共实例常因反爬虫策略而无法访问。*

2. **自建 RSSHub (推荐)**:
   ```bash
   docker run -d --name rsshub -p 1200:1200 diygod/rsshub
   ```
   - 使用自建地址: `http://localhost:1200/zhihu/daily`

## 3. 常见问题

- **RSSHub 访问超时**: 公共实例 `rsshub.app` 在国内可能无法访问，建议自建或使用代理。
- **公众号更新延迟**: WeWe RSS 依赖后台定时刷新，可能有一段时间延迟。
