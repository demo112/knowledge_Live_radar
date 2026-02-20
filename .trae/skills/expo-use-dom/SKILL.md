---
name: expo-use-dom
description: "[参考层] Expo DOM 组件指南，在原生应用中使用 Web 代码。来源：expo/skills"
type: reference
applies_to: app
---

# Expo DOM 组件

> 来源: [expo/skills](https://skills.sh/expo/skills/use-dom)

DOM 组件允许 Web 代码在原生平台的 webview 中运行，同时在 Web 上原样渲染。这使得可以在 Expo 应用中使用 recharts、react-syntax-highlighter 等 Web 专用库。

---

## 何时使用 DOM 组件

**适用场景：**
- 需要使用 Web 专用库（如图表库、代码高亮）
- 渲染复杂 HTML/CSS 内容
- 复用现有 Web 组件

**不适用场景：**
- 需要原生性能的组件
- 简单 UI 元素
- 需要深度原生集成

---

## 基本 DOM 组件

创建带 `'use dom';` 指令的新文件：

```typescript
// components/WebChart.tsx
"use dom";

export default function WebChart({
  data,
}: {
  data: number[];
  dom: import("expo/dom").DOMProps;
}) {
  return (
    <div style={{ padding: 20 }}>
      <h2>Chart Data</h2>
      <ul>
        {data.map((value, i) => (
          <li key={i}>{value}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## DOM 组件规则

1. **必须有 `'use dom';` 指令** - 文件顶部
2. **单一默认导出** - 每个文件一个 React 组件
3. **独立文件** - 不能内联定义或与原生组件混合
4. **可序列化 props** - 字符串、数字、布尔值、数组、普通对象
5. **CSS 在组件文件中** - DOM 组件运行在隔离上下文

---

## dom Prop

每个 DOM 组件接收特殊的 `dom` prop 用于 webview 配置：

```typescript
"use dom";

interface Props {
  content: string;
  dom: import("expo/dom").DOMProps;
}

export default function MyComponent({ content }: Props) {
  return <div>{content}</div>;
}
```

### 常用 dom Prop 选项

```typescript
// 禁用 body 滚动
<DOMComponent dom={{ scrollEnabled: false }} />

// 流入刘海区域（禁用安全区域）
<DOMComponent dom={{ contentInsetAdjustmentBehavior: "never" }} />

// 手动控制尺寸
<DOMComponent dom={{ style: { width: 300, height: 400 } }} />

// 组合选项
<DOMComponent
  dom={{
    scrollEnabled: false,
    contentInsetAdjustmentBehavior: "never",
    style: { width: '100%', height: 500 }
  }}
/>
```

---

## 暴露原生操作给 Webview

通过 props 传递异步函数：

```typescript
// app/index.tsx (原生)
import { Alert } from "react-native";
import DOMComponent from "@/components/dom-component";

export default function Screen() {
  return (
    <DOMComponent
      showAlert={async (message: string) => {
        Alert.alert("From Web", message);
      }}
      saveData={async (data: { name: string; value: number }) => {
        console.log("Saving:", data);
        return { success: true };
      }}
    />
  );
}

// components/dom-component.tsx
"use dom";

interface Props {
  showAlert: (message: string) => Promise<void>;
  saveData: (data: { name: string; value: number }) => Promise<{ success: boolean }>;
  dom?: import("expo/dom").DOMProps;
}

export default function DOMComponent({ showAlert, saveData }: Props) {
  const handleClick = async () => {
    await showAlert("Hello from the webview!");
    const result = await saveData({ name: "test", value: 42 });
    console.log("Save result:", result);
  };

  return <button onClick={handleClick}>Trigger Native Action</button>;
}
```

---

## 使用 Web 库

### 代码高亮

```typescript
// components/syntax-highlight.tsx
"use dom";

import SyntaxHighlighter from "react-syntax-highlighter";
import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";

interface Props {
  code: string;
  language: string;
  dom?: import("expo/dom").DOMProps;
}

export default function SyntaxHighlight({ code, language }: Props) {
  return (
    <SyntaxHighlighter language={language} style={docco}>
      {code}
    </SyntaxHighlighter>
  );
}
```

### 图表

```typescript
// components/chart.tsx
"use dom";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

interface Props {
  data: Array<{ name: string; value: number }>;
  dom: import("expo/dom").DOMProps;
}

export default function Chart({ data }: Props) {
  return (
    <LineChart width={400} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
}
```

---

## Expo Router 在 DOM 组件中

```typescript
"use dom";

import { Link, useRouter } from "expo-router";

export default function Navigation({
  dom,
}: {
  dom: import("expo/dom").DOMProps;
}) {
  const router = useRouter();

  return (
    <nav>
      <Link href="/about">About</Link>
      <button onClick={() => router.push("/settings")}>Settings</button>
    </nav>
  );
}
```

### 需要 Props 的 Router API

这些 hooks 在 DOM 组件中不能直接使用：
- `useLocalSearchParams`
- `useGlobalSearchParams`
- `usePathname`
- `useSegments`

**解决方案**：在原生父组件中读取，通过 props 传递：

```typescript
// app/[id].tsx (原生)
import { useLocalSearchParams, usePathname } from "expo-router";
import DOMComponent from "@/components/dom-component";

export default function Screen() {
  const { id } = useLocalSearchParams();
  const pathname = usePathname();

  return <DOMComponent id={id as string} pathname={pathname} />;
}
```

---

## 平台行为

| 平台 | 行为 |
|------|------|
| iOS | 在 WKWebView 中渲染 |
| Android | 在 WebView 中渲染 |
| Web | 原样渲染（无 webview 包装） |

在 Web 上，`dom` prop 被忽略。

---

## 从原生组件使用

```typescript
// app/index.tsx
import { View, Text } from "react-native";
import WebChart from "@/components/web-chart";
import CodeBlock from "@/components/code-block";

export default function HomeScreen() {
  return (
    <View style={{ flex: 1 }}>
      <Text>Native content above</Text>

      <WebChart data={[10, 20, 30, 40, 50]} dom={{ style: { height: 300 } }} />

      <CodeBlock
        code="const x = 1;"
        language="javascript"
        dom={{ scrollEnabled: true }}
      />

      <Text>Native content below</Text>
    </View>
  );
}
```

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| expo-native-ui | 原生 UI 组件指南 |
| react-native-patterns | React Native 最佳实践 |
| app-debugging | 调试技巧 |
