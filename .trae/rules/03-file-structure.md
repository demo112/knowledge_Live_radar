# 文件组织规范

```
packages/
├── server/src/
│   ├── modules/{module}/
│   │   ├── {module}.controller.ts
│   │   ├── {module}.service.ts
│   │   ├── {module}.dto.ts
│   │   └── {module}.test.ts
│   ├── common/        # 服务端公共代码
│   ├── types/         # 服务端类型
│   └── config/        # 配置
├── web/src/
│   ├── pages/components/hooks/utils/types/
└── app/src/
    ├── screens/components/hooks/utils/types/
```

**重要**: 各端代码独立维护，不共享代码。server、web、app 各自管理自己的 types 和 utils。
