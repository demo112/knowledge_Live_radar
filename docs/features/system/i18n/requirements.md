# Requirements: 国际化基础设施 (I18n)

## Overview

I18n (Internationalization) 是系统走向多语言支持的基础。通过构建统一的国际化框架，实现界面文本、后端数据（如枚举值、错误信息）的中英文切换，提升系统的全球化适应能力。本方案采用 `next-intl` (Frontend) 和标准的 JSON 资源文件管理方式。

## User Stories

### Story 1: 多语言界面切换

As a 用户, I want 能够在中英文界面之间自由切换, So that 我可以使用熟悉的语言操作 Knowledge Radar。

**Acceptance Criteria:**

- [ ] AC1: 语言切换器
  - **Given**: 系统顶部导航栏
  - **When**: 用户点击语言切换按钮 (Language Switcher)
  - **Then**: 
    - 下拉显示 "中文 (简体)" 和 "English"
    - 点击后页面刷新，URL 变为 `/[locale]/...` (如 `/zh/dashboard` 或 `/en/dashboard`)
    - 界面文本即时更新为对应语言

- [ ] AC2: 路由语言前缀
  - **Given**: 用户访问根路径 `/`
  - **When**: 首次进入系统
  - **Then**: 
    - 系统根据浏览器首选语言自动重定向到 `/zh` 或 `/en`
    - 默认语言为 `zh` (中文)

### Story 2: 界面文本国际化

As a 开发者, I want 将所有界面硬编码文本提取到资源文件中, So that 可以统一管理和翻译。

**Acceptance Criteria:**

- [ ] AC1: 资源文件提取
  - **Given**: `frontend/messages/zh.json` 和 `frontend/messages/en.json`
  - **When**: 开发新页面或组件
  - **Then**: 
    - 不再使用硬编码的中文字符串
    - 使用 `useTranslations('Namespace')` 获取翻译函数 `t`
    - 键名采用 `camelCase` (如 `dashboardTitle`, `saveButton`)

- [ ] AC2: 动态插值
  - **Given**: 需要显示带变量的文本 (如 "已加载 10 条数据")
  - **When**: 调用翻译函数
  - **Then**: 
    - 支持 `{count}` 等变量插值 (`t('loadedCount', {count: 10})`)
    - 正确处理复数形式 (Pluralization)

### Story 3: 后端枚举与错误信息国际化

As a 系统, I want 后端返回的枚举值和错误信息也能支持多语言, So that 前端展示一致且友好的提示。

**Acceptance Criteria:**

- [ ] AC1: 枚举值映射
  - **Given**: 后端返回的状态码 (如 `PENDING`, `EXECUTED`)
  - **When**: 前端展示状态标签
  - **Then**: 
    - 使用 `messages/*.json` 中的 `Status` 命名空间进行映射
    - 显示为 "待处理" 或 "已执行"

- [ ] AC2: 错误信息标准化
  - **Given**: API 调用失败返回错误码 (如 `ERR_NETWORK`)
  - **When**: 前端捕获错误
  - **Then**: 
    - 使用 `messages/*.json` 中的 `Errors` 命名空间查找对应翻译
    - 显示友好的错误提示信息 (如 "网络连接失败，请检查您的网络设置")

## Technical Design

- **Frontend Framework**: `next-intl`
- **Routing**: App Router (`app/[locale]/...`)
- **Middleware**: 处理 Locale 重定向与 Cookie 持久化
- **Resource Format**: JSON (Key-Value pairs, nested namespaces)

## Constraints

- **性能**: 国际化不应显著影响页面加载速度 (SSR/SSG 支持)。
- **一致性**: 所有新增页面必须同步更新中英文资源文件，禁止部分硬编码。
- **回退策略**: 如果某种语言缺失特定翻译，应回退到默认语言 (中文) 显示。

## Metadata

- 规模: 中
- 涉及模块: `frontend-core`, `i18n`
- 涉及端: Frontend
- 状态: 规划中 (Draft)
