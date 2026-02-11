---
name: expo-dev-client
description: "[参考层] EAS Build 开发客户端指南，用于测试原生代码变更。来源：expo/skills"
type: reference
applies_to: app
---

# Expo Dev Client

> 来源: [expo/skills](https://skills.sh/expo/skills/expo-dev-client)

使用 EAS Build 创建开发客户端，用于在物理设备上测试原生代码变更。

---

## 重要：何时需要开发客户端

只有当应用需要自定义原生代码时才创建开发客户端。大多数应用在 Expo Go 中运行良好。

**仅在以下情况需要 dev client：**
- 本地 Expo 模块（自定义原生代码）
- Apple targets（widgets、app clips、extensions）
- Expo Go 中没有的第三方原生模块

**先尝试 Expo Go**：`npx expo start`，如果一切正常，就不需要 dev client。

---

## EAS 配置

确保 `eas.json` 有 development profile：

```json
{
  "cli": {
    "version": ">= 16.0.1",
    "appVersionSource": "remote"
  },
  "build": {
    "production": {
      "autoIncrement": true
    },
    "development": {
      "autoIncrement": true,
      "developmentClient": true
    }
  },
  "submit": {
    "production": {},
    "development": {}
  }
}
```

关键设置：
- `developmentClient: true` - 打包 expo-dev-client
- `autoIncrement: true` - 自动递增构建号
- `appVersionSource: "remote"` - 使用 EAS 作为版本号来源

---

## 构建 TestFlight

一条命令构建 iOS dev client 并提交到 TestFlight：

```bash
eas build -p ios --profile development --submit
```

这会：
1. 在云端构建开发客户端
2. 自动提交到 App Store Connect
3. 构建完成后发送邮件通知

收到 TestFlight 邮件后：
1. 从 TestFlight 下载构建
2. 启动应用查看 expo-dev-client UI
3. 连接本地 Metro bundler 或扫描二维码

---

## 本地构建

在本机构建开发客户端：

```bash
# iOS（需要 Xcode）
eas build -p ios --profile development --local

# Android
eas build -p android --profile development --local
```

输出：
- iOS: `.ipa` 文件
- Android: `.apk` 或 `.aab` 文件

---

## 安装本地构建

### iOS 模拟器

```bash
# 解压 .tar.gz 找到 .app
tar -xzf build-*.tar.gz
xcrun simctl install booted ./path/to/App.app
```

### iOS 设备（需要签名）

```bash
# 使用 Xcode Devices 窗口或 ideviceinstaller
ideviceinstaller -i build.ipa
```

### Android

```bash
adb install build.apk
```

---

## 按平台构建

```bash
# 仅 iOS
eas build -p ios --profile development

# 仅 Android
eas build -p android --profile development

# 两个平台
eas build --profile development
```

---

## 检查构建状态

```bash
# 列出最近构建
eas build:list

# 查看构建详情
eas build:view
```

---

## 使用 Dev Client

安装后，dev client 提供：
- **开发服务器连接** - 输入 Metro bundler URL 或扫描二维码
- **构建信息** - 查看原生构建详情
- **启动器 UI** - 切换开发服务器

连接本地开发：

```bash
# 启动 Metro bundler
npx expo start --dev-client

# 用 dev client 扫描二维码或手动输入 URL
```

---

## 故障排除

### 签名错误

```bash
eas credentials
```

### 清除构建缓存

```bash
eas build -p ios --profile development --clear-cache
```

### 检查 EAS CLI 版本

```bash
eas --version
eas update
```

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| app-debugging | 调试时可能需要 dev client |
| expo-native-ui | 原生 UI 开发参考 |
| expo-networking | 网络请求最佳实践 |
