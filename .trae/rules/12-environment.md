# 环境配置规范

## 后端环境变量
```bash
# 应用
APP_ENV=development
APP_PORT=8000
APP_DEBUG=true

# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_radar
# 开发环境可用 SQLite
# DATABASE_URL=sqlite:///./ai_radar.db

# AI 服务（硅基流动）
SILICONFLOW_API_KEY=your-api-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-V3
SILICONFLOW_MAX_TOKENS=4096
SILICONFLOW_TEMPERATURE=0.7

# 日志
LOG_LEVEL=INFO

# 抓取配置
CRAWL_CONCURRENT_LIMIT=5
CRAWL_DEFAULT_TIMEOUT=30
CRAWL_RESPECT_ROBOTS_TXT=true
```

## 前端环境变量
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Radar
```

## 环境区分
| 环境 | 数据库 | AI 服务 | 日志级别 |
|------|--------|---------|----------|
| development | SQLite | 真实调用（限频） | DEBUG |
| test | SQLite（内存） | Mock | WARNING |
| production | PostgreSQL | 真实调用 | INFO |
