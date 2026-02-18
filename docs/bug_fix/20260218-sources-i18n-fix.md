# 设计锚定报告

## 功能定位
- **所属规格**：i18n (Internationalization)
- **设计文档**：`docs/features/i18n/design.md`
- **文档状态**：存在

## 原设计意图

> 提取硬编码文本到 `messages/*.json`，使用 `useTranslations` 替换。
> 资源文件结构 (`messages/zh.json`) 包含 `Common`, `Navigation`, `Status`, `Errors` 等命名空间。
> `Common` 命名空间采用扁平结构（例如 `Common.loading`, `Common.save`）。

**核心设计决策**
1. 使用 `next-intl` 进行国际化。
2. 按模块划分翻译命名空间（如 `Sources`, `Health`）。
3. `Common` 存放通用词汇，尽量复用。

## 偏离分析

| 设计要求 | 实际行为 | 偏离类型 |
|----------|----------|----------|
| `Sources` 模块应有对应的翻译定义 | `messages/*.json` 中缺失 `Sources` 命名空间 | 数据缺失 |
| `Common` 命名空间为扁平结构 | 代码中使用 `Common.actions.create`, `Common.status.loading` 等嵌套结构 | 代码与资源不匹配 |
| 所有界面文本应被翻译 | 界面直接显示 key (如 `Sources.tabs.managed`) | 功能失效 |

## 修复基准线

修复必须满足：
- [ ] 补全 `Sources` 命名空间的所有翻译。
- [ ] 修正代码中对 `Common` 的错误引用，使其匹配现有的扁平结构。
- [ ] 确保中英文翻译文件同步。

## 后续行动

- [ ] 更新 `frontend/messages/zh.json` 和 `en.json`
- [ ] 修正 `frontend/src/app/[locale]/(dashboard)/sources/page.tsx`
