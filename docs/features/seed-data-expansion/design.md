# Design: Seed Data Expansion (2026 Frontier Edition)

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 2026 LLM 模型格局 | 数据文件: `backend/app/data/seed_content_2026.py`, 脚本: `backend/scripts/seed_data.py` |
| Story 2: 智能体认知架构 | 同上 |
| Story 3: 软件 3.0 与新编程范式 | 同上 |
| Story 4: 本地 AI 与隐私基础设施 | 同上 |

## 数据模型

使用现有的 `Pyramid` 和 `PyramidNode` 模型，无需修改数据库 Schema。
利用 `parent_id` 和 `path` 字段构建多层级树状结构。

```python
# backend/app/models/pyramid.py (Existing)
class PyramidNode(Base):
    # ...
    parent_id = Column(UUID, ForeignKey('pyramid_nodes.id'))
    path = Column(String)  # Materialized path: /root_id/parent_id/
    level = Column(Integer)
```

## 数据结构定义 (New)

为了保持代码整洁，将庞大的金字塔数据结构提取到独立的数据文件中。

```python
# backend/app/data/seed_content_2026.py

SEEDED_PYRAMIDS = [
    {
        "name": "2026 LLM 模型格局 (Model Landscape 2026)",
        "description": "2026年大语言模型与算力格局",
        "children": [
            {
                "name": "推理与思考 (System 2 Reasoning)",
                "children": [
                    {"name": "OpenAI o3 / o3-mini (Chain of Thought)"},
                    {"name": "DeepSeek R1 (Reinforcement Learning)"},
                    # ...
                ]
            },
            # ...
        ]
    },
    # ... 其他金字塔
]
```

## 核心逻辑设计

### 递归节点创建

需要在 `seed_data.py` 中实现一个递归函数来处理任意深度的节点结构。

```python
async def create_node_recursive(session, pyramid_id, parent_node, node_data, level=0):
    # 1. 计算 path
    # 2. 创建当前节点
    # 3. 递归创建子节点
```

### 幂等性处理

脚本应支持多次运行而不重复创建相同名称的金字塔。

```python
# 伪代码
existing = await session.execute(select(Pyramid).where(Pyramid.name == pyramid_data["name"]))
if existing:
    logger.info(f"Skipping existing pyramid: {pyramid_data['name']}")
    return
```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/app/data/seed_content_2026.py` | 新增 | 定义 4 个新金字塔的完整 JSON 结构数据 |
| `backend/app/data/__init__.py` | 新增 | 模块初始化文件 |
| `backend/scripts/seed_data.py` | 修改 | 引入数据文件，实现递归创建逻辑，添加幂等性检查 |

## 引用的已有代码

- `backend/app/database.py`: `AsyncSessionLocal`
- `backend/app/models/pyramid.py`: `Pyramid`, `PyramidNode`

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 现有 Demo 金字塔 | 无影响，新金字塔与旧金字塔并存 | 低 |
| 数据库性能 | 增加约 50-100 个节点，对性能无显著影响 | 低 |

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 数据存储方式 | Python List/Dict in Code | 相比 JSON/YAML，直接在 Python 代码中定义更方便维护，支持注释，且无解析开销 |
| 节点层级处理 | 递归函数 | 结构深度不固定，递归是最自然的实现方式 |
| 幂等性策略 | Skip if Exists | 简单有效，防止数据重复。如果需要更新，需手动删除旧金字塔 |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| 路径(Path)计算错误 | 导致树结构断裂或查询失败 | 在递归函数中严格测试路径拼接逻辑 (`parent.path + parent.id + "/"`) |
| 数据库事务失败 | 部分数据写入，导致结构不完整 | 使用 `try...except` 包裹整个金字塔的创建过程，失败时回滚 |

## 需要人决策

- 无
