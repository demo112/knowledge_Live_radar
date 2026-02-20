---
name: expo-networking
description: "[参考层] Expo网络请求指南，供 code-implementation 编写 App 代码时参考。来源：expo/skills"
type: reference
applies_to: app
---

# Expo 网络请求

> 来源: [expo/skills](https://skills.sh/expo/skills/native-data-fetching)

Expo网络指南，用于API请求、数据获取、缓存和网络调试。

---

## 激活方式

### 触发场景

- 实现**API请求**
- 配置**数据获取**
- 处理**认证Token**
- 实现**离线支持**

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心关键词 | 网络请求、API、fetch |
| 库类 | React Query、SWR、axios |
| 功能类 | 认证、缓存、离线 |

---

## 偏好

- 简单请求使用`fetch` API
- 复杂应用使用React Query (TanStack Query)
- Token存储在`expo-secure-store`
- 网络状态使用`@react-native-community/netinfo`

---

## 基本Fetch用法

### 简单GET请求

```typescript
const fetchUser = async (userId: string) => {
  const response = await fetch(`https://api.example.com/users/${userId}`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};
```

### POST请求

```typescript
const createUser = async (userData: UserData) => {
  const response = await fetch("https://api.example.com/users", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }

  return response.json();
};
```

---

## React Query

### 设置

```typescript
// app/_layout.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5分钟
      retry: 2,
    },
  },
});

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <Stack />
    </QueryClientProvider>
  );
}
```

### 获取数据

```typescript
import { useQuery } from "@tanstack/react-query";

function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => fetchUser(userId),
  });

  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;

  return <Profile user={data} />;
}
```

### Mutations

```typescript
import { useMutation, useQueryClient } from "@tanstack/react-query";

function CreateUserForm() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const handleSubmit = (data: UserData) => {
    mutation.mutate(data);
  };

  return <Form onSubmit={handleSubmit} isLoading={mutation.isPending} />;
}
```

---

## 认证

### Token管理

```typescript
import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "auth_token";

export const auth = {
  getToken: () => SecureStore.getItemAsync(TOKEN_KEY),
  setToken: (token: string) => SecureStore.setItemAsync(TOKEN_KEY, token),
  removeToken: () => SecureStore.deleteItemAsync(TOKEN_KEY),
};

// 认证fetch包装器
const authFetch = async (url: string, options: RequestInit = {}) => {
  const token = await auth.getToken();

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: token ? `Bearer ${token}` : "",
    },
  });
};
```

---

## 离线支持

### 检查网络状态

```typescript
import NetInfo from "@react-native-community/netinfo";

function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    return NetInfo.addEventListener((state) => {
      setIsOnline(state.isConnected ?? true);
    });
  }, []);

  return isOnline;
}
```

### React Query离线优先

```typescript
import { onlineManager } from "@tanstack/react-query";
import NetInfo from "@react-native-community/netinfo";

// 同步React Query与网络状态
onlineManager.setEventListener((setOnline) => {
  return NetInfo.addEventListener((state) => {
    setOnline(state.isConnected ?? true);
  });
});
// 离线时查询会暂停，在线时恢复
```

---

## 环境变量

```bash
# .env
EXPO_PUBLIC_API_URL=https://api.example.com
```

```typescript
// 代码中使用
const API_URL = process.env.EXPO_PUBLIC_API_URL;

const fetchUsers = async () => {
  const response = await fetch(`${API_URL}/users`);
  return response.json();
};
```

---

## 错误处理

```typescript
class ApiError extends Error {
  constructor(message: string, public status: number, public code?: string) {
    super(message);
    this.name = "ApiError";
  }
}

const fetchWithErrorHandling = async (url: string, options?: RequestInit) => {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        error.message || "请求失败",
        response.status,
        error.code
      );
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError("网络错误", 0, "NETWORK_ERROR");
  }
};
```

---

## 常见错误

```typescript
// ❌ 错误：没有错误处理
const data = await fetch(url).then((r) => r.json());

// ✅ 正确：检查响应状态
const response = await fetch(url);
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const data = await response.json();

// ❌ 错误：在AsyncStorage存储token
await AsyncStorage.setItem("token", token); // 不安全！

// ✅ 正确：使用SecureStore存储敏感数据
await SecureStore.setItemAsync("token", token);
```

---

## 决策树

```
网络请求问题
  |-- 基本fetch?
  |   \-- 使用fetch API + 错误处理
  |
  |-- 需要缓存/状态管理?
  |   |-- 复杂应用 -> React Query
  |   \-- 简单需求 -> SWR或自定义hooks
  |
  |-- 认证?
  |   |-- Token存储 -> expo-secure-store
  |   \-- Token刷新 -> 实现刷新流程
  |
  |-- 离线支持?
  |   |-- 检查状态 -> NetInfo
  |   \-- 请求队列 -> React Query持久化
  |
  \-- 性能?
      |-- 缓存 -> React Query + staleTime
      |-- 去重 -> React Query自动处理
      \-- 取消 -> AbortController
```
