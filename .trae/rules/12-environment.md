# 环境配置规范

## 环境变量
```bash
NODE_ENV=development
PORT=3000
DATABASE_URL=mysql://user:pass@host:3306/db
REDIS_URL=redis://host:6379
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=7d
LOG_LEVEL=info
```

## 环境区分
| 环境 | 用途 |
|------|------|
| development | 本地开发 |
| test | 测试 |
| production | 生产 |
