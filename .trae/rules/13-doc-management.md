# 文档管理规范

## 目录结构

```
docs/
├── *.md                 # 全局文档（禁止AI修改）
├── progress/YYYY-MM-DD.md
├── features/{SPEC_ID}/
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
└── bug_fix/
    └── {YYYYMMDD}-{问题简述}-fix.md
```

## 命名规范

| 类型 | 正确 ✅ | 错误 ❌ |
|------|---------|---------|
| 功能目录 | `ITER01/` | `ITER01_骨架/` |
| 文档文件 | `design.md` | `设计文档.md` |
| 进展日志 | `2026-02-11.md` | `进展-02-11.md` |
| 修复记录 | `20260211-crawl-fix.md` | `抓取修复.md` |

## 禁止事项

- ❌ 功能目录名加中文
- ❌ 使用中文文件名
- ❌ 在 docs 根目录创建功能文档
