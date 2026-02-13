# 文件组织规范

```
ai-radar/
├── frontend/                    # Next.js 前端
│   ├── src/
│   │   ├── app/                 # Next.js App Router 页面
│   │   │   ├── (dashboard)/     # 仪表盘布局组
│   │   │   │   ├── feed/        # 信息流浏览
│   │   │   │   ├── pyramid/     # 金字塔可视化
│   │   │   │   ├── sources/     # 信息源管理
│   │   │   │   ├── approval/    # 审批中心
│   │   │   │   └── health/      # 健康报告
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/          # 共享组件
│   │   │   ├── ui/              # 基础 UI 组件
│   │   │   ├── pyramid/         # 金字塔相关组件
│   │   │   ├── feed/            # 信息流相关组件
│   │   │   └── common/          # 通用组件
│   │   ├── hooks/               # 自定义 Hooks
│   │   ├── lib/                 # 工具库（API 客户端等）
│   │   ├── types/               # TypeScript 类型定义
│   │   └── stores/              # 状态管理
│   ├── public/
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── backend/                     # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   │   ├── pyramid.py       # 金字塔 & 节点
│   │   │   ├── source.py        # 信息源
│   │   │   ├── content.py       # 内容条目
│   │   │   ├── approval.py      # 审批 & 变更提案
│   │   │   ├── hotspot.py       # 热点话题
│   │   │   └── system.py        # 系统配置 & 日志
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── routers/             # API 路由
│   │   │   ├── pyramids.py
│   │   │   ├── nodes.py
│   │   │   ├── sources.py
│   │   │   ├── contents.py
│   │   │   ├── approvals.py
│   │   │   ├── health.py
│   │   │   └── system.py
│   │   ├── services/            # 业务逻辑
│   │   │   ├── pyramid_service.py
│   │   │   ├── crawl_engine.py
│   │   │   ├── validator/       # 校验模块
│   │   │   │   ├── hard_validator.py
│   │   │   │   ├── soft_validator.py
│   │   │   │   └── cross_validator.py
│   │   │   ├── ai_service.py    # AI 服务集成
│   │   │   ├── evolution_engine.py
│   │   │   ├── health_monitor.py
│   │   │   └── scheduler.py     # 定时任务
│   │   ├── utils/               # 工具函数
│   │   └── middleware/          # 中间件
│   ├── alembic/                 # 数据库迁移
│   ├── tests/                   # 测试
│   ├── requirements.txt
│   └── pyproject.toml
│
├── docs/                        # 项目文档
│   ├── features/{SPEC_ID}/
│   ├── progress/
│   └── bug_fix/
│
├── e2e/                         # 端到端测试
│   ├── fixtures/                # 测试固件
│   ├── pages/                   # 页面对象模型 (POM)
│   ├── tests/                   # 测试用例
│   └── playwright.config.ts     # Playwright 配置
│
├── docker-compose.yml
└── README.md
```

**重要**：前后端代码独立维护。frontend 和 backend 各自管理自己的类型和工具函数。E2E 测试统一在根目录 `e2e/` 下管理。
