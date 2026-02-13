# Design: i18n 基础设施建设

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 支持中英文切换 | 引入 `next-intl`，配置 Middleware 和 Routing |
| Story 2: 界面文本国际化 | 提取硬编码文本到 `messages/*.json`，使用 `useTranslations` 替换 |
| Story 3: 后端枚举值国际化 | 在 `messages/*.json` 中定义枚举映射，前端动态查找 |
| Story 4: 路由语言前缀 | 采用 `/[locale]/...` 路由结构 |

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `frontend/messages/zh.json` | 新增 | 中文资源文件（包含通用、导航、状态、页面文本） |
| `frontend/messages/en.json` | 新增 | 英文资源文件 |
| `frontend/src/i18n/request.ts` | 新增 | next-intl 请求配置 (App Router) |
| `frontend/src/i18n/routing.ts` | 新增 | 路由配置 (locales, defaultLocale) |
| `frontend/src/middleware.ts` | 新增 | 路由中间件，处理 locale 重定向 |
| `frontend/src/app/[locale]/layout.tsx` | 新增 | 根布局，包含 `NextIntlClientProvider` |
| `frontend/src/app/[locale]/page.tsx` | 新增 | 根页面重定向或首页 |
| `frontend/src/app/layout.tsx` | 删除 | 废弃旧根布局 (移至 `[locale]/layout.tsx`) |
| `frontend/src/app/(dashboard)/**` | 移动 | 移至 `frontend/src/app/[locale]/(dashboard)/**` |
| `frontend/next.config.ts` | 修改 | 集成 `next-intl` 插件 |
| `frontend/src/components/LanguageSwitcher.tsx` | 新增 | 语言切换组件 |

## 关键技术设计

### 1. 目录结构重构

```
frontend/src/app/
├── [locale]/              <-- 新增动态路由段
│   ├── (dashboard)/       <-- 现有 dashboard 路由移入此处
│   │   └── ...
│   ├── layout.tsx         <-- 根布局 (包含 Provider)
│   └── page.tsx
├── api/                   <-- API 路由保持不变 (不需要 i18n)
└── layout.tsx             <-- 删除原根布局
```

### 2. 资源文件结构 (`messages/zh.json`)

```json
{
  "Common": {
    "loading": "加载中...",
    "save": "保存",
    "cancel": "取消",
    "delete": "删除"
  },
  "Navigation": {
    "dashboard": "仪表板",
    "pyramid": "知识金字塔"
  },
  "Status": {
    "active": "活跃",
    "paused": "暂停",
    "pending": "待处理"
  },
  "Errors": {
    "network_error": "网络错误，请稍后重试",
    "not_found": "未找到资源"
  }
}
```

### 3. 枚举值映射方案

不再使用 `lib/constants.ts` 中的硬编码 Map，改为在组件中动态获取翻译。

**Before:**
```typescript
// lib/constants.ts
export const STATUS_MAP = { executed: '已执行' };

// Component
{STATUS_MAP[item.status]}
```

**After:**
```typescript
// Component
const t = useTranslations('Status');
{t(item.status)} // item.status = 'executed' -> t('executed') -> "已执行"
```

### 4. 中间件配置 (`middleware.ts`)

```typescript
import createMiddleware from 'next-intl/middleware';
import {routing} from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  // Match only internationalized pathnames
  matcher: ['/', '/(zh|en)/:path*']
};
```

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 所有页面路由 | URL 将变为 `/zh/dashboard` 等 | 中 (需确保 Link 组件自动处理) |
| API 请求 | 无影响 (API 路由在 `/api` 下，通常排除在 middleware matcher 外) | 低 |
| 硬编码文本 | 需要逐个页面替换为 `t(...)` | 低 (工作量大，但逻辑简单) |
| 静态图片/资源 | 无影响 | 低 |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| 路由重构导致 404 | 页面无法访问 | 严格测试 Middleware 配置；保留旧文件直到验证通过 |
| 动态内容未翻译 | 混合显示中英文 | 建立 `BackendEnum` 翻译命名空间，覆盖所有后端枚举 |
| `useParams` 变化 | 获取路由参数逻辑改变 | 检查所有 `useParams` 调用，确保兼容 `[locale]` |

## 需要人决策

- [x] 默认语言：中文 (`zh`)
- [x] 支持语言：中文 (`zh`) + 英文 (`en`)
- [ ] 是否需要持久化语言选择 (Cookie/LocalStorage)？ -> `next-intl` 中间件默认支持 Cookie
