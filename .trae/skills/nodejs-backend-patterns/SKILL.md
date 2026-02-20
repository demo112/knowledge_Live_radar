---
name: nodejs-backend-patterns
description: "[参考层] Node.js后端开发模式，供 code-implementation 编写 Server 代码时参考。来源：wshobson/agents"
type: reference
applies_to: server
---

# Node.js 后端模式

> 来源: [wshobson/agents](https://skills.sh/wshobson/agents/nodejs-backend-patterns)

构建可扩展、可维护、生产就绪的Node.js后端应用的综合指南。

---

## 激活方式

### 触发场景

- 构建新的**Node.js后端服务**
- 审查或重构**后端代码**
- 实现**认证、缓存或数据库**模式
- 设置**中间件和错误处理**

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心关键词 | 后端、服务端、API、Express |
| 架构类 | 分层架构、依赖注入、中间件 |
| 功能类 | 认证、缓存、数据库、错误处理 |

---

## 分层架构

```
src/
├── controllers/     # 处理HTTP请求/响应
├── services/        # 业务逻辑
├── repositories/    # 数据访问层
├── models/          # 数据模型
├── middleware/      # Express中间件
├── routes/          # 路由定义
├── utils/           # 工具函数
├── config/          # 配置
└── types/           # TypeScript类型
```

### Controller层

```typescript
// controllers/user.controller.ts
import { Request, Response, NextFunction } from "express";
import { UserService } from "../services/user.service";

export class UserController {
  constructor(private userService: UserService) {}

  async createUser(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await this.userService.createUser(req.body);
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  }

  async getUser(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await this.userService.getUserById(req.params.id);
      res.json(user);
    } catch (error) {
      next(error);
    }
  }
}
```

### Service层

```typescript
// services/user.service.ts
import { UserRepository } from "../repositories/user.repository";
import { NotFoundError, ValidationError } from "../utils/errors";
import bcrypt from "bcrypt";

export class UserService {
  constructor(private userRepository: UserRepository) {}

  async createUser(userData: CreateUserDTO): Promise<User> {
    const existingUser = await this.userRepository.findByEmail(userData.email);
    if (existingUser) {
      throw new ValidationError("邮箱已存在");
    }

    const hashedPassword = await bcrypt.hash(userData.password, 10);
    const user = await this.userRepository.create({
      ...userData,
      password: hashedPassword,
    });

    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword as User;
  }
}
```

---

## 中间件模式

### 认证中间件

```typescript
// middleware/auth.middleware.ts
import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { UnauthorizedError } from "../utils/errors";

export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const token = req.headers.authorization?.replace("Bearer ", "");
    if (!token) {
      throw new UnauthorizedError("未提供Token");
    }

    const payload = jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload;
    req.user = payload;
    next();
  } catch (error) {
    next(new UnauthorizedError("无效Token"));
  }
};
```

### 验证中间件 (Zod)

```typescript
// middleware/validation.middleware.ts
import { Request, Response, NextFunction } from "express";
import { AnyZodObject, ZodError } from "zod";
import { ValidationError } from "../utils/errors";

export const validate = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map((err) => ({
          field: err.path.join("."),
          message: err.message,
        }));
        next(new ValidationError("验证失败", errors));
      } else {
        next(error);
      }
    }
  };
};
```

---

## 错误处理

### 自定义错误类

```typescript
// utils/errors.ts
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public errors?: any[]) {
    super(message, 400);
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = "资源未找到") {
    super(message, 404);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = "未授权") {
    super(message, 401);
  }
}
```

### 全局错误处理器

```typescript
// middleware/error-handler.ts
import { Request, Response, NextFunction } from "express";
import { AppError } from "../utils/errors";

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      status: "error",
      message: err.message,
      ...(err instanceof ValidationError && { errors: err.errors }),
    });
  }

  // 生产环境不泄露错误详情
  const message =
    process.env.NODE_ENV === "production"
      ? "内部服务器错误"
      : err.message;

  res.status(500).json({
    status: "error",
    message,
  });
};

// 异步错误包装器
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
```

---

## 数据库模式

### 事务模式

```typescript
// services/order.service.ts
export class OrderService {
  constructor(private db: Pool) {}

  async createOrder(userId: string, items: any[]) {
    const client = await this.db.connect();

    try {
      await client.query("BEGIN");

      // 创建订单
      const orderResult = await client.query(
        "INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING id",
        [userId, calculateTotal(items)]
      );
      const orderId = orderResult.rows[0].id;

      // 创建订单项
      for (const item of items) {
        await client.query(
          "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
          [orderId, item.productId, item.quantity, item.price]
        );
      }

      await client.query("COMMIT");
      return orderId;
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    } finally {
      client.release();
    }
  }
}
```

---

## API响应格式

```typescript
// utils/response.ts
import { Response } from "express";

export class ApiResponse {
  static success<T>(res: Response, data: T, message?: string, statusCode = 200) {
    return res.status(statusCode).json({
      status: "success",
      message,
      data,
    });
  }

  static error(res: Response, message: string, statusCode = 500, errors?: any) {
    return res.status(statusCode).json({
      status: "error",
      message,
      ...(errors && { errors }),
    });
  }

  static paginated<T>(
    res: Response,
    data: T[],
    page: number,
    limit: number,
    total: number
  ) {
    return res.json({
      status: "success",
      data,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
      },
    });
  }
}
```

---

## 最佳实践清单

1. **使用TypeScript**：类型安全防止运行时错误
2. **实现正确的错误处理**：使用自定义错误类
3. **验证输入**：使用Zod或Joi
4. **使用环境变量**：永不硬编码密钥
5. **实现日志**：使用结构化日志（Pino, Winston）
6. **添加限流**：防止滥用
7. **使用HTTPS**：生产环境必须
8. **正确实现CORS**：生产环境不要用*
9. **使用依赖注入**：更容易测试和维护
10. **写测试**：单元、集成、E2E测试
11. **处理优雅关闭**：清理资源
12. **使用连接池**：数据库连接
13. **实现健康检查**：用于监控
14. **使用压缩**：减少响应大小
15. **监控性能**：使用APM工具
