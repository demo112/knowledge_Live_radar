# 并发编辑检测规则

## 核心理念

> **开始前检查，冲突前预防** —— 在修改文件前检测是否有其他人正在修改，避免冲突。

---

## 检测时机

### 必须检测的场景

| 场景 | 说明 |
|------|------|
| 开始新任务 | 任务涉及的文件是否有人修改过 |
| 修改公共代码 | 共享组件、全局类型 |
| 修改数据模型 | SQLAlchemy 模型、Alembic 迁移 |
| 长时间未同步 | 超过 4 小时未 pull |

### 检测命令

```bash
# 检查文件最近 24 小时的修改记录
git log --since="24 hours ago" --oneline -- <file>

# 检查是否有未拉取的远程更新
git fetch origin main
git log HEAD..origin/main --oneline
```

---

## 高风险文件清单

| 文件 | 风险原因 |
|------|----------|
| `backend/app/models/*.py` | 数据模型变更影响全局 |
| `backend/app/config.py` | 配置变更影响所有模块 |
| `backend/app/services/ai_service.py` | AI 服务核心 |
| `frontend/src/lib/*.ts` | 前端公共工具 |
| `frontend/src/types/*.ts` | 全局类型定义 |
| `alembic/versions/*.py` | 数据库迁移脚本 |
