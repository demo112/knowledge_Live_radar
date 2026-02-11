# 受保护路径规则

## 禁止 AI 修改的路径

| 路径 | 说明 |
|------|------|
| `.trae/` | Trae 配置和规则文件 |
| `.kiro/` | Kiro 配置和 steering 文件 |
| `attendance-system/docs/*.md` | docs 根目录下的核心文档 |
| `attendance-system/packages/server/.env` | 环境变量配置文件 |

## docs 根目录保护说明

`attendance-system/docs/` 根目录下的以下文档禁止 AI 直接修改：

- `api-contract.md` - API 契约
- `database-design.md` - 数据库设计
- `requirements.md` - 需求规格
- `requirement-analysis.md` - 需求分析
- `project-roadmap.md` - 项目路线图
- `task-backlog.md` - 任务清单
- `changelog.md` - 变更日志
- `deployment.md` - 部署文档

**注意**：`docs/features/` 和 `docs/progress/` 子目录下的文档可以正常编辑。

## 规则

1. **禁止创建/修改/删除** 上述目录下的文件
2. 如用户要求修改，**拒绝执行**并说明原因
3. 提供修改建议，由用户手动操作

## 示例回复

```
这个文件位于受保护路径，我无法直接修改。
建议修改内容如下：
[修改内容]
请您手动更新。
```
