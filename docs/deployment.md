# 部署文档

## 环境要求

- Docker Engine 24.0+
- Docker Compose v2.0+
- Git

## 架构组件

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| Frontend | `ai-radar-web` | 3000 | Next.js 应用 |
| Backend | `ai-radar-api` | 8000 | FastAPI 应用 |
| Database | `ai-radar-db` | 5432 | PostgreSQL 15 |
| Cache | `ai-radar-redis` | 6379 | Redis 7 (可选) |

## 快速启动

1. **克隆代码**
   ```bash
   git clone <repo_url>
   cd ai-radar
   ```

2. **配置环境变量**
   复制示例配置并修改：
   ```bash
   cp .env.example .env
   ```
   
   关键配置项：
   - `DATABASE_URL`: 数据库连接串
   - `AI_SERVICE_KEY`: 硅基流动 API Key
   - `SECRET_KEY`: JWT 密钥

3. **启动服务**
   ```bash
   docker-compose up -d --build
   ```

4. **初始化数据库**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **访问应用**
   - 前端: http://localhost:3000
   - API 文档: http://localhost:8000/docs

## 数据备份

数据库数据挂载在 `./data/postgres` 目录。
手动备份命令：
```bash
docker-compose exec db pg_dump -U postgres ai_radar > backup.sql
```

## 日志查看

```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
```

## 生产环境注意事项

1. 修改 `docker-compose.yml` 中的密码和端口映射
2. 使用 Nginx 作为反向代理配置 SSL
3. 开启 Docker 容器的自动重启策略 (`restart: always`)
4. 配置定期数据库备份任务
