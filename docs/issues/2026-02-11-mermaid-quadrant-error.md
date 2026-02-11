# 问题记录: Mermaid quadrantChart 语法解析错误

## 基本信息

| 项目 | 内容 |
|------|------|
| 发现日期 | 2026-02-11 |
| 状态 | 已解决 |
| 严重程度 | 中 |
| 解决日期 | 2026-02-11 |

## 描述

在 `docs/project-roadmap.md` 中使用 Mermaid `quadrantChart` 时，出现 `Lexical error`，导致图表无法渲染。报错提示在数据项起始位置（如“金字塔管理”）存在无法识别的文本。

## 复现步骤

1. 在 Markdown 文件中编写 `quadrantChart`。
2. 在 `quadrant-1...4` 定义后紧接着编写数据项（如 `Label: [x, y]`），不留空行。
3. 使用包含中文或特殊字符（如 `&`）且未加引号的标签。

## 影响

导致项目路线图可视化失败，用户无法直观查看模块价值分布。

## 根因分析

1. **格式规范**：Mermaid `quadrantChart` 的词法解析器要求在象限定义区域与数据点区域之间必须有一个空行，否则会将数据点误认为配置项。
2. **字符处理**：对于非 ASCII 字符（如中文）或特殊符号（如 `&`），解析器可能无法正确识别边界，需要使用双引号 `""` 明确标识字符串边界。

## 解决方案

1. **添加空行**：在 `quadrant-4` 定义行之后添加一个空行。
2. **强制引号**：为所有数据项标签和象限显示文本添加双引号。
3. **符号优化**：将 `&` 替换为更安全的 `/` 或空格。

## 预防措施

- 在编写 Mermaid 复杂图表（尤其是较新的图表类型如 quadrantChart）时，严格遵守“配置与数据分离”的空行原则。
- 对于所有包含中文的 Mermaid 标签，养成加双引号的习惯。
- 建立文档回归检查机制，修改后立即在预览中确认渲染结果。

## 相关文件

- [project-roadmap.md](file:///c:/Users/Administrator/Documents/Win_trae_projects/ongoing/knowledge_live_radar/knowledge_Live_radar/docs/project-roadmap.md)
