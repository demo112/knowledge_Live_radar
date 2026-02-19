# 需求文档框架现状分析与改进建议

## 1. 现状评估 (Current State Assessment)

经过对 `docs/` 目录的扫描与分析，发现当前项目的需求文档存在以下核心问题：

### 1.1 结构混乱 (Structural Entropy)
- **目录二义性**：同时存在 `docs/feature/` (单数) 和 `docs/features/` (复数) 两个目录。
  - `docs/feature/`：实际上存放的是 **迭代计划 (Iterations)**，如 `ai-radar-iteration-1`。
  - `docs/features/`：存放的是 **功能模块 (Components)**，如 `ai-capabilities`。
- **维度混杂**：
  - “按时间切分”的文档（迭代）与“按功能切分”的文档（模块）共存。
  - 导致无法快速回答：“当前系统的【金字塔管理】功能包含哪些具体规则？”因为规则可能散落在 `iteration-1`, `iteration-2` 和 `features/pyramid-evolution` 中。

### 1.2 缺乏唯一信息源 (No Single Source of Truth)
- `docs/requirements.md` 内容偏向原则和愿景，未包含具体功能细节。
- 具体的功能定义分散在各个子目录中，且没有一个 **Master Index** (总索引) 来串联所有功能。
- **LLM 上下文丢失**：当 LLM 需要了解系统全貌时，无法通过一个入口文件找到所有相关的需求文档，导致回答基于猜测或不完整信息。

### 1.3 格式不统一 (Inconsistent Formatting)
- **格式 A**：User Story + Acceptance Criteria (GWT) (如 `ai-capabilities`)
- **格式 B**：传统需求列表 (如 `iteration-1`)
- **格式 C**：仅有设计笔记或任务列表
- 这种不一致性增加了自动化解析和人工阅读的认知负荷。

## 2. 改进方案：构建系统化需求框架

为了解决上述问题，建议重构需求文档体系，建立以 **功能模块** 为核心的唯一信息源。

### 2.1 核心原则
1.  **Feature-Centric (功能为中心)**：文档应描述“系统现在有什么功能”，而不是“我们在某个月做了什么”。
2.  **SSOT (唯一信息源)**：每个功能模块有且仅有一个对应的需求文件。
3.  **Living Documentation (活文档)**：文档随代码变更而更新，保持与代码一致。

### 2.2 新目录结构建议

```
docs/
├── features/                  # [SSOT] 功能需求总目录
│   ├── README.md              # [核心] 功能矩阵索引 (Feature Matrix)
│   ├── core/                  # 核心业务域
│   │   ├── pyramid-management.md
│   │   ├── source-management.md
│   │   └── ...
│   ├── ai/                    # AI 能力域
│   │   ├── content-analysis.md
│   │   ├── quality-check.md
│   │   └── ...
│   └── system/                # 系统支撑域
│       ├── auth.md
│       ├── notification.md
│       └── ...
├── iterations/                # [历史] 迭代过程记录 (原 docs/feature/)
│   ├── iteration-1/
│   └── ...
└── requirements.md            # [入口] 系统级需求总纲 (保持不变，链接到 features/README.md)
```

### 2.3 统一文档模板

每个 `features/*.md` 文件必须遵循标准模板：

```markdown
# Feature: {功能名称}

## 1. 概述 (Overview)
简述功能目标和价值。

## 2. 用户故事 (User Stories)
### Story 1: {名称}
As a... I want... So that...

**Acceptance Criteria (GWT):**
- [ ] AC1: {场景}
  - **Given**: ...
  - **When**: ...
  - **Then**: ...

## 3. 数据模型 (Data Model)
简要描述涉及的实体和字段。

## 4. 约束 (Constraints)
性能、安全、权限等约束。
```

## 3. 迁移计划 (Migration Plan)

1.  **Step 1: 建立索引**
    - 创建 `docs/features/README.md`，梳理当前所有已识别的功能模块。
2.  **Step 2: 目录规范化**
    - 将 `docs/feature/` 重命名为 `docs/iterations/`，明确其历史记录的性质。
    - 将 `docs/features/` 下的散乱文件按业务域（Core, AI, System）分类整理。
3.  **Step 3: 内容合并**
    - 遍历 `iterations` 中的文档，将“已上线”的功能需求合并到 `features` 对应的模块文档中。
    - 确保 `features` 中的文档反映系统的**当前状态**。

## 4. 给 LLM 的优化

通过 `docs/features/README.md`，我们可以为 LLM 提供一个清晰的导航图：
- 当用户问“金字塔功能”时，LLM 查阅 `README.md` -> 找到 `features/core/pyramid-management.md`。
- 这样确保了上下文的精准和完整。
