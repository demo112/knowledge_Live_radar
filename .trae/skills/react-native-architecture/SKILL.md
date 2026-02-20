---
name: react-native-architecture
description: "[参考层] React Native 生产级架构模式，包含导航、状态管理、原生模块和离线优先架构。来源：wshobson/agents"
type: reference
applies_to: app
---

# React Native 架构

> 来源: [wshobson/agents](https://skills.sh/wshobson/agents/react-native-architecture)

React Native + Expo 的生产级开发模式，包含导航、状态管理、原生模块和离线优先架构。

---

## 项目结构

```
src/
├── app/                    # Expo Router 页面
│   ├── (auth)/            # 认证组
│   ├── (tabs)/            # Tab 导航
│   └── _layout.tsx        # 根布局
├── components/
│   ├── ui/                # 可复用 UI 组件
│   └── features/          # 功能特定组件
├── hooks/                 # 自定义 hooks
├── services/              # API 和原生服务
├── stores/                # 状态管理
├── utils/                 # 工具函数
└── types/                 # TypeScript 类型
```

---

## Expo vs Bare React Native

| 特性 | Expo | Bare RN |
|------|------|---------|
| 设置复杂度 | 低 | 高 |
| 原生模块 | EAS Build | 手动链接 |
| OTA 更新 | 内置 | 手动设置 |
| 构建服务 | EAS | 自定义 CI |
| 自定义原生代码 | Config plugins | 直接访问 |

---

## 快速开始

```bash
# 创建新 Expo 项目
npx create-expo-app@latest my-app -t expo-template-blank-typescript

# 安装必要依赖
npx expo install expo-router expo-status-bar react-native-safe-area-context
npx expo install @react-native-async-storage/async-storage
npx expo install expo-secure-store expo-haptics
```

### 根布局

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router'
import { ThemeProvider } from '@/providers/ThemeProvider'
import { QueryProvider } from '@/providers/QueryProvider'

export default function RootLayout() {
  return (
    <QueryProvider>
      <ThemeProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
        </Stack>
      </ThemeProvider>
    </QueryProvider>
  )
}
```

---

## 模式 1: Expo Router 导航

### Tab 布局

```typescript
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router'
import { Home, Search, User, Settings } from 'lucide-react-native'
import { useTheme } from '@/hooks/useTheme'

export default function TabLayout() {
  const { colors } = useTheme()

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: { backgroundColor: colors.background },
        headerShown: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => <Home size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="search"
        options={{
          title: 'Search',
          tabBarIcon: ({ color, size }) => <Search size={size} color={color} />,
        }}
      />
    </Tabs>
  )
}
```

### 编程式导航

```typescript
import { router } from 'expo-router'

// 编程式导航
router.push('/profile/123')
router.replace('/login')
router.back()

// 带参数
router.push({
  pathname: '/product/[id]',
  params: { id: '123', referrer: 'home' },
})
```

---

## 模式 2: 认证流程

```typescript
// providers/AuthProvider.tsx
import { createContext, useContext, useEffect, useState } from 'react'
import { useRouter, useSegments } from 'expo-router'
import * as SecureStore from 'expo-secure-store'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  signIn: (credentials: Credentials) => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const segments = useSegments()
  const router = useRouter()

  // 路由保护
  useEffect(() => {
    if (isLoading) return

    const inAuthGroup = segments[0] === '(auth)'

    if (!user && !inAuthGroup) {
      router.replace('/login')
    } else if (user && inAuthGroup) {
      router.replace('/(tabs)')
    }
  }, [user, segments, isLoading])

  async function signIn(credentials: Credentials) {
    const { token, user } = await api.login(credentials)
    await SecureStore.setItemAsync('authToken', token)
    setUser(user)
  }

  async function signOut() {
    await SecureStore.deleteItemAsync('authToken')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
```

---

## 模式 3: 离线优先 + React Query

```typescript
// providers/QueryProvider.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister'
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client'
import AsyncStorage from '@react-native-async-storage/async-storage'
import NetInfo from '@react-native-community/netinfo'
import { onlineManager } from '@tanstack/react-query'

// 同步在线状态
onlineManager.setEventListener((setOnline) => {
  return NetInfo.addEventListener((state) => {
    setOnline(!!state.isConnected)
  })
})

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 1000 * 60 * 60 * 24, // 24 小时
      staleTime: 1000 * 60 * 5, // 5 分钟
      retry: 2,
      networkMode: 'offlineFirst',
    },
  },
})

const asyncStoragePersister = createAsyncStoragePersister({
  storage: AsyncStorage,
  key: 'REACT_QUERY_OFFLINE_CACHE',
})

export function QueryProvider({ children }: { children: React.ReactNode }) {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister: asyncStoragePersister }}
    >
      {children}
    </PersistQueryClientProvider>
  )
}
```

### 乐观更新

```typescript
export function useCreateProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.createProduct,
    onMutate: async (newProduct) => {
      await queryClient.cancelQueries({ queryKey: ['products'] })
      const previous = queryClient.getQueryData(['products'])

      queryClient.setQueryData(['products'], (old: Product[]) => [
        ...old,
        { ...newProduct, id: 'temp-' + Date.now() },
      ])

      return { previous }
    },
    onError: (err, newProduct, context) => {
      queryClient.setQueryData(['products'], context?.previous)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}
```

---

## 模式 4: 原生模块集成

### Haptics

```typescript
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

export const haptics = {
  light: () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  },
  success: () => {
    if (Platform.OS !== "web") {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  },
  error: () => {
    if (Platform.OS !== "web") {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  },
};
```

### 生物识别

```typescript
import * as LocalAuthentication from "expo-local-authentication";

export async function authenticateWithBiometrics(): Promise<boolean> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  if (!hasHardware) return false;

  const isEnrolled = await LocalAuthentication.isEnrolledAsync();
  if (!isEnrolled) return false;

  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: "Authenticate to continue",
    fallbackLabel: "Use passcode",
  });

  return result.success;
}
```

---

## 模式 5: 平台特定代码

```typescript
import { Platform, StyleSheet } from 'react-native'

const styles = StyleSheet.create({
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 4,
      },
    }),
  },
})
```

---

## 模式 6: 性能优化

```typescript
import { FlashList } from '@shopify/flash-list'
import { memo, useCallback } from 'react'

// 记忆化列表项
const ProductItem = memo(function ProductItem({
  item,
  onPress,
}: {
  item: Product
  onPress: (id: string) => void
}) {
  const handlePress = useCallback(() => onPress(item.id), [item.id, onPress])

  return (
    <Pressable onPress={handlePress} style={styles.item}>
      <FastImage source={{ uri: item.image }} style={styles.image} />
      <Text style={styles.title}>{item.name}</Text>
    </Pressable>
  )
})

export function ProductList({ products, onProductPress }: ProductListProps) {
  const renderItem = useCallback(
    ({ item }: { item: Product }) => (
      <ProductItem item={item} onPress={onProductPress} />
    ),
    [onProductPress]
  )

  return (
    <FlashList
      data={products}
      renderItem={renderItem}
      estimatedItemSize={100}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={5}
    />
  )
}
```

---

## EAS Build & Submit

```json
// eas.json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": {
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "production": {
      "autoIncrement": true
    }
  }
}
```

```bash
# 构建命令
eas build --platform ios --profile development
eas build --platform android --profile preview

# 提交到商店
eas submit --platform ios
eas submit --platform android

# OTA 更新
eas update --branch production --message "Bug fixes"
```

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| react-native-patterns | 性能优化详细指南 |
| expo-native-ui | Expo UI 组件指南 |
| expo-networking | 网络请求最佳实践 |
| app-debugging | 调试技巧 |
