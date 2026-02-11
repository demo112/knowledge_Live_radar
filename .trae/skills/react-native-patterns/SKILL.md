---
name: react-native-patterns
description: "[参考层] React Native性能优化指南，供 code-implementation 编写 App 代码时参考。来源：callstackincubator/agent-skills"
type: reference
applies_to: app
---

# React Native 模式

> 来源: [callstackincubator/agent-skills](https://skills.sh/callstackincubator/agent-skills/react-native-best-practices)

React Native应用的性能优化指南，涵盖JavaScript/React、原生（iOS/Android）和打包优化。基于Callstack的"React Native优化终极指南"。

---

## 激活方式

### 触发场景

- 构建新的**React Native功能**
- 调试**性能问题**（卡顿、启动慢）
- 审查**React Native代码**
- 优化**包大小或TTI**

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心关键词 | React Native、RN、移动端 |
| 性能类 | 卡顿、慢、FPS、TTI |
| 优化类 | 虚拟列表、动画、包大小 |

---

## 优先级指南

| 优先级 | 类别 | 影响 |
|--------|------|------|
| 1 | FPS和重渲染 | 关键 |
| 2 | 包大小 | 关键 |
| 3 | TTI优化 | 高 |
| 4 | 原生性能 | 高 |
| 5 | 内存管理 | 中高 |
| 6 | 动画 | 中 |

---

## 列表优化

### FlatList vs FlashList

```typescript
// ❌ 坏：长列表使用ScrollView
<ScrollView>
  {items.map(item => <Item key={item.id} {...item} />)}
</ScrollView>

// ✅ 好：使用FlatList虚拟化
<FlatList
  data={items}
  renderItem={({ item }) => <Item {...item} />}
  keyExtractor={item => item.id}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>

// ✅ 更好：使用FlashList获得更好性能
import { FlashList } from "@shopify/flash-list";

<FlashList
  data={items}
  renderItem={({ item }) => <Item {...item} />}
  estimatedItemSize={ITEM_HEIGHT}
/>
```

---

## 记忆化

```typescript
// 记忆化昂贵组件
const ExpensiveComponent = React.memo(({ data }) => {
  return <View>{/* ... */}</View>;
});

// 记忆化回调
const handlePress = useCallback(() => {
  doSomething(id);
}, [id]);

// 记忆化计算值
const sortedData = useMemo(() => {
  return data.sort((a, b) => a.name.localeCompare(b.name));
}, [data]);
```

---

## Reanimated动画

```typescript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

function AnimatedBox() {
  const offset = useSharedValue(0);

  const animatedStyles = useAnimatedStyle(() => ({
    transform: [{ translateX: offset.value }],
  }));

  const handlePress = () => {
    offset.value = withSpring(offset.value + 50);
  };

  return (
    <Animated.View style={[styles.box, animatedStyles]}>
      <Pressable onPress={handlePress}>
        <Text>Move</Text>
      </Pressable>
    </Animated.View>
  );
}
```

---

## 非受控TextInput

```typescript
// ❌ 坏：受控输入（每次按键都重渲染）
const [text, setText] = useState('');
<TextInput value={text} onChangeText={setText} />

// ✅ 好：非受控输入（无重渲染）
const textRef = useRef('');
<TextInput
  defaultValue=""
  onChangeText={(value) => { textRef.current = value; }}
/>
```

---

## 包优化

### 避免桶导出

```typescript
// ❌ 坏：桶导入（加载整个模块）
import { Button } from '@/components';

// ✅ 好：直接导入
import { Button } from '@/components/Button';
```

### 懒加载屏幕

```typescript
// ❌ 坏：立即导入
import HeavyScreen from './screens/HeavyScreen';

// ✅ 好：懒导入
const HeavyScreen = React.lazy(() => import('./screens/HeavyScreen'));

// 在导航中
<Stack.Screen
  name="Heavy"
  getComponent={() => require('./screens/HeavyScreen').default}
/>
```

---

## 问题→解决方案映射

| 问题 | 从这里开始 |
|------|------------|
| 应用感觉慢/卡顿 | 测量FPS → 分析React |
| 太多重渲染 | 分析React → React Compiler |
| 启动慢（TTI） | 测量TTI → 分析包 |
| 应用体积大 | 分析应用 → R8/ProGuard |
| 内存增长 | JS内存泄漏或原生内存泄漏 |
| 动画掉帧 | Reanimated worklets |
| 列表滚动卡顿 | FlatList/FlashList |
| TextInput延迟 | 非受控组件 |

---

## 性能检查清单

发布前：
- [ ] 列表使用FlatList/FlashList（不是ScrollView）
- [ ] 重组件已记忆化
- [ ] 动画使用Reanimated
- [ ] 包已分析和优化
- [ ] 热路径中没有桶导入
- [ ] Hermes已启用
- [ ] Android上ProGuard/R8已启用
- [ ] TTI已测量且可接受
