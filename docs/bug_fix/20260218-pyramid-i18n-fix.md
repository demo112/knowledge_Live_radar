# 修复 Pyramid 页面国际化缺失问题

## 问题描述
- **现象**：访问金字塔列表页面时，控制台报错 `MISSING_MESSAGE: Could not resolve Pyramid.loading` 等多个翻译缺失错误。
- **复现步骤**：
  1. 启动前端服务
  2. 访问 `/pyramid` 页面
  3. 观察控制台错误信息
- **影响范围**：金字塔列表页面的文本显示异常（显示为 key 名）。

## 设计锚定
- **所属规格**：前端国际化 (i18n)
- **原设计意图**：使用 `next-intl` 进行国际化，通过 JSON 文件管理多语言资源。
- **当前偏离**：`page.tsx` 中使用的 namespace 为 `Pyramid`，但 JSON 文件中相关 key 位于 `Pyramid.List` 下。

## 根因分析
- **直接原因**：`useTranslations('Pyramid')` 加载了 `Pyramid` 下的所有资源，但代码中直接访问 `loading`、`title` 等 key，而这些 key 实际上嵌套在 `List` 对象中。
- **根本原因**：代码与翻译文件的结构不匹配。
- **相关代码**：`frontend/src/app/[locale]/(dashboard)/pyramid/page.tsx`

## 修复方案
- **修复思路**：将 `useTranslations` 的 namespace 修改为 `Pyramid.List`，使代码中的 key 能够正确映射到 JSON 文件中的位置。
- **改动文件**：
  - `frontend/src/app/[locale]/(dashboard)/pyramid/page.tsx`
  - `frontend/src/app/[locale]/(dashboard)/contents/page.tsx` (顺手修复一处构建错误)

## 验证结果
- [x] 原问题已解决：命名空间匹配，key 可正确解析。
- [x] 回归测试通过：`npm run build` 通过。
- [x] 设计一致性确认：符合 i18n 规范。

## 提交信息
fix(pyramid): 修复金字塔列表页翻译缺失问题
