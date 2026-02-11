---
name: expo-api-routes
description: "[参考层] Expo API Routes 指南，在 Expo 应用中创建服务端 API。来源：expo/skills"
type: reference
applies_to: app
---

# Expo API Routes

> 来源: [expo/skills](https://skills.sh/expo/skills/expo-api-routes)

在 Expo 应用中创建服务端 API 路由。

---

## 何时使用 API Routes

**适用场景：**
- 需要服务端逻辑
- 隐藏 API 密钥
- 代理外部 API
- 简单的后端功能

**不适用场景：**
- 复杂的后端逻辑（使用专门的后端服务）
- 需要数据库的场景（考虑云数据库）
- 高性能要求

---

## 文件结构

API 路由放在 `app` 目录，使用 `+api.ts` 后缀：

```
app/
  api/
    hello+api.ts          → GET /api/hello
    users+api.ts          → /api/users
    users/[id]+api.ts     → /api/users/:id
  (tabs)/
    index.tsx
```

---

## 基本 API Route

```typescript
// app/api/hello+api.ts
export function GET(request: Request) {
  return Response.json({ message: "Hello from Expo!" });
}
```

---

## HTTP 方法

为每个 HTTP 方法导出命名函数：

```typescript
// app/api/items+api.ts
export function GET(request: Request) {
  return Response.json({ items: [] });
}

export async function POST(request: Request) {
  const body = await request.json();
  return Response.json({ created: body }, { status: 201 });
}

export async function PUT(request: Request) {
  const body = await request.json();
  return Response.json({ updated: body });
}

export async function DELETE(request: Request) {
  return new Response(null, { status: 204 });
}
```

---

## 动态路由

```typescript
// app/api/users/[id]+api.ts
export function GET(request: Request, { id }: { id: string }) {
  return Response.json({ userId: id });
}
```

---

## 请求处理

### 查询参数

```typescript
export function GET(request: Request) {
  const url = new URL(request.url);
  const page = url.searchParams.get("page") ?? "1";
  const limit = url.searchParams.get("limit") ?? "10";

  return Response.json({ page, limit });
}
```

### Headers

```typescript
export function GET(request: Request) {
  const auth = request.headers.get("Authorization");

  if (!auth) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  return Response.json({ authenticated: true });
}
```

### JSON Body

```typescript
export async function POST(request: Request) {
  const { email, password } = await request.json();

  if (!email || !password) {
    return Response.json({ error: "Missing fields" }, { status: 400 });
  }

  return Response.json({ success: true });
}
```

---

## 环境变量

使用 `process.env` 获取服务端密钥：

```typescript
// app/api/ai+api.ts
export async function POST(request: Request) {
  const { prompt } = await request.json();

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const data = await response.json();
  return Response.json(data);
}
```

---

## CORS Headers

为 Web 客户端添加 CORS：

```typescript
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

export function OPTIONS() {
  return new Response(null, { headers: corsHeaders });
}

export function GET() {
  return Response.json({ data: "value" }, { headers: corsHeaders });
}
```

---

## 错误处理

```typescript
export async function POST(request: Request) {
  try {
    const body = await request.json();
    // 处理...
    return Response.json({ success: true });
  } catch (error) {
    console.error("API error:", error);
    return Response.json({ error: "Internal server error" }, { status: 500 });
  }
}
```

---

## 本地测试

启动带 API routes 的开发服务器：

```bash
npx expo serve
```

在 `http://localhost:8081` 启动本地服务器。

用 curl 测试：

```bash
curl http://localhost:8081/api/hello
curl -X POST http://localhost:8081/api/users -H "Content-Type: application/json" -d '{"name":"Test"}'
```

---

## 部署到 EAS Hosting

### 前置条件

```bash
npm install -g eas-cli
eas login
```

### 部署

```bash
eas deploy
```

这会构建并部署 API routes 到 EAS Hosting（Cloudflare Workers）。

### 生产环境变量

```bash
# 创建密钥
eas env:create --name OPENAI_API_KEY --value sk-xxx --environment production
```

---

## EAS Hosting 运行时限制

API routes 运行在 Cloudflare Workers 上，有以下限制：

**缺失/受限的 API：**
- 无文件系统访问
- 无 Node.js 原生模块
- 无长时间运行的进程

**使用 Web API 替代：**

```typescript
// 使用 Web Crypto 替代 Node crypto
const hash = await crypto.subtle.digest(
  "SHA-256",
  new TextEncoder().encode("data")
);

// 使用 fetch 替代 node-fetch
const response = await fetch("https://api.example.com");
```

**数据库选项：**
- Turso (SQLite)
- Supabase
- PlanetScale
- Neon

---

## 从客户端调用

```typescript
// 从 React Native 组件
const response = await fetch("/api/hello");
const data = await response.json();

// 带 body
const response = await fetch("/api/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "John" }),
});
```

---

## 常见模式

### 认证中间件

```typescript
// utils/auth.ts
export async function requireAuth(request: Request) {
  const token = request.headers.get("Authorization")?.replace("Bearer ", "");

  if (!token) {
    throw new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  return { userId: "123" };
}

// app/api/protected+api.ts
import { requireAuth } from "../../utils/auth";

export async function GET(request: Request) {
  const { userId } = await requireAuth(request);
  return Response.json({ userId });
}
```

### 代理外部 API

```typescript
// app/api/weather+api.ts
export async function GET(request: Request) {
  const url = new URL(request.url);
  const city = url.searchParams.get("city");

  const response = await fetch(
    `https://api.weather.com/v1/current?city=${city}&key=${process.env.WEATHER_API_KEY}`
  );

  return Response.json(await response.json());
}
```

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| expo-networking | 客户端网络请求 |
| react-native-architecture | 整体架构模式 |
| nodejs-backend-patterns | 后端模式参考 |
