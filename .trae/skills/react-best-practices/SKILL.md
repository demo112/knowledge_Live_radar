---
name: react-best-practices
description: "[参考层] React性能优化指南，供 code-implementation 编写 Web 代码时参考。来源：vercel-labs/agent-skills"
type: reference
applies_to: web
---

# React 最佳实践

> 来源: [vercel-labs/agent-skills](https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices)

React和Next.js应用的综合性能优化指南，由Vercel维护。包含8个类别的57条规则，按影响优先级排序。

---

## 激活方式

### 触发场景

- 编写新的**React/Next.js组件**
- 审查或重构**现有代码**
- **优化性能**
- 调试**慢渲染**

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心关键词 | React、组件、性能、优化 |
| 问题类 | 慢、卡顿、重渲染、包大小 |
| 技术类 | memo、useMemo、useCallback、懒加载 |

---

## 规则类别（按优先级）

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 消除瀑布流 | 关键 | async- |
| 2 | 包大小优化 | 关键 | bundle- |
| 3 | 服务端性能 | 高 | server- |
| 4 | 客户端数据获取 | 中高 | client- |
| 5 | 重渲染优化 | 中 | rerender- |
| 6 | 渲染性能 | 中 | rendering- |
| 7 | JavaScript性能 | 中低 | js- |
| 8 | 高级模式 | 低 | advanced- |

---

## 1. 消除瀑布流（关键）

```typescript
// ❌ 坏：顺序获取（瀑布流）
const user = await fetchUser(id);
const posts = await fetchPosts(user.id);
const comments = await fetchComments(posts[0].id);

// ✅ 好：并行获取
const [user, posts] = await Promise.all([
  fetchUser(id),
  fetchPosts(id)
]);
```

- **并行数据获取**：对独立请求使用`Promise.all()`
- **预加载关键数据**：在组件渲染前开始获取
- **避免顺序await**：不要不必要地链式依赖请求
- **使用Suspense边界**：启用流式和渐进加载

---

## 2. 包大小优化（关键）

```typescript
// ❌ 坏：桶导入（导入整个库）
import { Button } from '@/components';

// ✅ 好：直接导入
import { Button } from '@/components/Button';

// ✅ 好：重组件动态导入
const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <Skeleton />,
  ssr: false
});
```

- **避免桶导入**：直接从源文件导入
- **动态导入**：使用`next/dynamic`或`React.lazy()`代码分割
- **Tree shaking**：确保库支持ES模块
- **分析包**：使用`@next/bundle-analyzer`

---

## 3. 服务端性能（高）

```typescript
// 服务端组件（默认）
async function UserProfile({ id }: { id: string }) {
  const user = await fetchUser(id); // 在服务端运行
  return <div>{user.name}</div>;
}

// 客户端组件（仅在需要时）
'use client';
function InteractiveButton() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

- **使用服务端组件**：默认RSC，仅在需要时添加'use client'
- **缓存昂贵操作**：使用`unstable_cache`或React cache
- **流式传输**：使用Suspense渐进加载
- **Edge运行时**：对延迟敏感的路由使用edge

---

## 4. 客户端数据获取（中高）

```typescript
import useSWR from 'swr';

function Profile() {
  const { data, error, isLoading } = useSWR('/api/user', fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 60000,
  });

  if (isLoading) return <Skeleton />;
  if (error) return <Error />;
  return <div>{data.name}</div>;
}
```

- **SWR/React Query**：用于客户端缓存和重新验证
- **乐观更新**：在服务器确认前更新UI
- **预获取**：在hover/focus时预加载数据
- **Stale-while-revalidate**：获取新数据时显示缓存数据

---

## 5. 重渲染优化（中）

```typescript
// ❌ 坏：内联对象导致重渲染
<Component style={{ color: 'red' }} />

// ✅ 好：稳定引用
const style = useMemo(() => ({ color: 'red' }), []);
<Component style={style} />

// ❌ 坏：内联函数导致重渲染
<Button onClick={() => handleClick(id)} />

// ✅ 好：记忆化回调
const handleButtonClick = useCallback(() => handleClick(id), [id]);
<Button onClick={handleButtonClick} />
```

- **记忆化**：适当使用`useMemo`、`useCallback`、`React.memo`
- **状态就近**：将状态保持在使用它的地方附近
- **Context拆分**：拆分context避免不必要的重渲染
- **稳定引用**：避免在渲染中创建新对象/数组

---

## 6. 渲染性能（中）

```typescript
import { FixedSizeList } from 'react-window';

function VirtualList({ items }) {
  return (
    <FixedSizeList
      height={400}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>{items[index].name}</div>
      )}
    </FixedSizeList>
  );
}
```

- **虚拟化**：长列表使用`react-window`或`react-virtual`
- **防抖/节流**：限制昂贵操作
- **CSS-in-JS**：优先使用零运行时方案（Tailwind, CSS Modules）
- **图片优化**：使用`next/image`并正确设置尺寸

---

## 性能检查清单

发布前：
- [ ] 热路径中没有桶导入
- [ ] 重组件已代码分割
- [ ] 尽可能使用服务端组件
- [ ] 列表已虚拟化（如果>100项）
- [ ] 图片使用next/image并设置sizes
- [ ] 没有不必要的重渲染（React DevTools）
- [ ] 包大小已分析和优化
