---
name: app-debugging
description: "App 端 (React Native + Expo) 调试技巧"
type: platform-specific
---

# App 端调试 (React Native + Expo)

> 适用于 attendance-system/packages/app

---

## 触发场景

- App 崩溃/白屏
- 原生模块问题
- 网络请求失败
- 导航问题
- 平台差异 (iOS vs Android)

---

## 调试工具链

### 1. Expo 开发工具

```bash
# 启动开发服务器
npx expo start

# 快捷键
# j - 打开 JS Debugger (Chrome)
# m - 打开开发者菜单
# r - 重新加载
# shift+m - 更多选项
```

### 2. React Native Debugger

```
- 设备摇一摇 → "Open JS Debugger"
- 或终端按 j 键
- Chrome DevTools 调试 JS 代码
```

### 3. Expo DevTools 功能

| 功能 | 用途 |
|------|------|
| Element Inspector | 查看组件层级、样式 |
| Network Inspector | 查看网络请求 |
| Performance Monitor | FPS、内存监控 |
| React DevTools | 组件树、Props/State |

### 4. 原生日志

```bash
# iOS 日志 (需要 Xcode)
npx react-native log-ios

# Android 日志
npx react-native log-android
# 或
adb logcat *:S ReactNative:V ReactNativeJS:V
```

---

## 常见问题调试

### App 崩溃

```
1. 查看 Metro bundler 终端输出
2. 查看原生日志 (adb logcat / Xcode console)
3. 检查 Red Screen 错误信息
4. 检查是否是原生模块问题
```

### 网络请求失败

```typescript
// 检查 Android 明文流量限制
// android/app/src/main/AndroidManifest.xml
// android:usesCleartextTraffic="true"

// 添加请求日志
fetch(url, options)
  .then(res => {
    console.log('=== Response ===', res.status);
    return res.json();
  })
  .catch(err => {
    console.error('=== Network Error ===', err.message);
  });
```

### 平台差异问题

```typescript
import { Platform } from 'react-native';

console.log('=== Platform ===', Platform.OS, Platform.Version);

// 平台特定调试
if (Platform.OS === 'ios') {
  console.log('iOS specific debug');
} else {
  console.log('Android specific debug');
}
```

### 导航问题

```typescript
// 追踪导航状态
import { useNavigationState } from '@react-navigation/native';

const routes = useNavigationState(state => state.routes);
console.log('=== Navigation State ===', routes);
```

### 样式问题

```typescript
// 使用 Element Inspector
// 设备摇一摇 → "Toggle Element Inspector"
// 点击组件查看样式

// 或添加边框调试
style={{ borderWidth: 1, borderColor: 'red' }}
```

### Metro Bundler 问题

```bash
# 清除缓存重启
npx expo start --clear

# 或完全重置
rm -rf node_modules
npm install
npx expo start --clear
```

---

## 诊断埋点模板

```typescript
// 组件生命周期追踪
const ScreenName = () => {
  console.log('=== Render: ScreenName ===');
  
  useEffect(() => {
    console.log('=== Mount: ScreenName ===');
    return () => console.log('=== Unmount: ScreenName ===');
  }, []);
  
  useFocusEffect(
    useCallback(() => {
      console.log('=== Focus: ScreenName ===');
      return () => console.log('=== Blur: ScreenName ===');
    }, [])
  );
  
  // ...
};
```

---

## 验证命令

```bash
# 类型检查
npm run typecheck

# Lint 检查
npm run lint

# 在模拟器运行
npx expo run:ios
npx expo run:android

# EAS 构建预览
eas build --profile preview --platform all
```

---

## 平台特定调试

### iOS 特定

```bash
# 打开 iOS 模拟器
npx expo run:ios

# 查看 Xcode 控制台日志
# Xcode → Window → Devices and Simulators
```

### Android 特定

```bash
# 打开 Android 模拟器
npx expo run:android

# 查看 Logcat
adb logcat | grep -E "(ReactNative|ReactNativeJS)"

# 检查 APK 安装问题
adb install -r app.apk
```

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| systematic-debugging | 遵循四阶段调查法 |
| problem-fixing | 修复流程的平台实现 |
| expo-native-ui | Expo UI 最佳实践 |
| expo-networking | Expo 网络请求最佳实践 |
| react-native-patterns | React Native 最佳实践 |
