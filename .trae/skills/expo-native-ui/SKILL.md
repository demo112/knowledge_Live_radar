---
name: expo-native-ui
description: "[参考层] Expo原生UI构建指南，供 code-implementation 编写 App 代码时参考。来源：expo/skills"
type: reference
applies_to: app
---

# Expo 原生 UI

> 来源: [expo/skills](https://skills.sh/expo/skills/building-native-ui)

Expo UI指南，用于构建原生iOS/Android界面。

---

## 激活方式

### 触发场景

- 构建**Expo应用UI**
- 配置**路由和导航**
- 实现**原生组件**
- 设置**样式和主题**

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心关键词 | Expo、原生UI、移动端界面 |
| 导航类 | 路由、导航、Tab、Stack |
| 组件类 | Modal、Sheet、Link |

---

## 运行应用

**关键：总是先尝试Expo Go，再创建自定义构建。**

大多数Expo应用在Expo Go中无需自定义原生代码即可工作。

```bash
# 使用Expo Go启动
npx expo start
# 用Expo Go应用扫描二维码
```

**何时需要自定义构建：**
- 使用Expo Go中没有的原生模块
- 自定义原生代码
- 特定原生配置

---

## 路由结构

标准应用布局（tabs和stacks）：

```
app/
  _layout.tsx — <NativeTabs />
  (index,search)/
    _layout.tsx — <Stack />
    index.tsx — 主列表
    search.tsx — 搜索视图
```

### 根布局（Native Tabs）

```typescript
// app/_layout.tsx
import { NativeTabs, Icon, Label } from "expo-router/unstable-native-tabs";
import { Theme } from "../components/theme";

export default function Layout() {
  return (
    <Theme>
      <NativeTabs>
        <NativeTabs.Trigger name="(index)">
          <Icon sf="list.dash" />
          <Label>Items</Label>
        </NativeTabs.Trigger>
        <NativeTabs.Trigger name="(search)" role="search" />
      </NativeTabs>
    </Theme>
  );
}
```

### Stack布局

```typescript
// app/(index,search)/_layout.tsx
import { Stack } from "expo-router/stack";
import { PlatformColor } from "react-native";

export default function Layout({ segment }) {
  const screen = segment.match(/\((.*)\)/)?.[1]!;
  const titles: Record<string, string> = { index: "Items", search: "Search" };

  return (
    <Stack
      screenOptions={{
        headerTransparent: true,
        headerShadowVisible: false,
        headerLargeTitle: true,
        headerBlurEffect: "none",
        headerBackButtonDisplayMode: "minimal",
      }}
    >
      <Stack.Screen name={screen} options={{ title: titles[screen] }} />
    </Stack>
  );
}
```

---

## 导航

### Link组件

```typescript
import { Link } from 'expo-router';

// 基本链接
<Link href="/path" />

// 包装自定义组件
<Link href="/path" asChild>
  <Pressable>...</Pressable>
</Link>
```

### Link预览（iOS）

```typescript
<Link href="/settings">
  <Link.Trigger>
    <Pressable>
      <Card />
    </Pressable>
  </Link.Trigger>
  <Link.Preview />
</Link>
```

### 上下文菜单

```typescript
import { Link } from "expo-router";

<Link href="/settings" asChild>
  <Link.Trigger>
    <Pressable>
      <Card />
    </Pressable>
  </Link.Trigger>
  <Link.Menu>
    <Link.MenuAction
      title="分享"
      icon="square.and.arrow.up"
      onPress={handleSharePress}
    />
    <Link.MenuAction
      title="删除"
      icon="trash"
      destructive
      onPress={handleDeletePress}
    />
  </Link.Menu>
</Link>
```

### Modal展示

```typescript
<Stack.Screen name="modal" options={{ presentation: "modal" }} />
```

### Sheet展示

```typescript
<Stack.Screen
  name="sheet"
  options={{
    presentation: "formSheet",
    sheetGrabberVisible: true,
    sheetAllowedDetents: [0.5, 1.0],
    contentStyle: { backgroundColor: "transparent" },
  }}
/>
```

---

## 样式

遵循Apple Human Interface Guidelines。

### 阴影（CSS boxShadow）

```typescript
// ✅ 使用CSS boxShadow
<View style={{ boxShadow: "0 1px 2px rgba(0, 0, 0, 0.05)" }} />

// 支持'inset'阴影
<View style={{ boxShadow: "inset 0 1px 2px rgba(0, 0, 0, 0.1)" }} />

// ❌ 永远不要使用旧版React Native shadow或elevation样式
```

### 页面标题

```typescript
<Stack.Screen options={{ title: "首页" }} />
```

---

## 最佳实践

1. **先尝试Expo Go** - 仅在必要时创建自定义构建
2. **使用原生组件** - 优先使用平台原生UI元素
3. **遵循HIG** - iOS的Apple Human Interface Guidelines
4. **添加上下文菜单** - 用预览和菜单增强导航
5. **使用CSS boxShadow** - 不要用旧版shadow属性
