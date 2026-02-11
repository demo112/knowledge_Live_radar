---
name: mobile-android-design
description: "[参考层] Android Material Design 3 和 Jetpack Compose 设计指南。来源：wshobson/agents"
type: reference
applies_to: app
---

# Android 移动端设计

> 来源: [wshobson/agents](https://skills.sh/wshobson/agents/mobile-android-design)

掌握 Material Design 3 (Material You) 和 Jetpack Compose，构建现代、自适应的 Android 应用。

---

## 触发场景

- 构建 **Android 原生 UI**
- 使用 **Jetpack Compose**
- 实现 **Material Design 3**
- 处理 **Android 平台特定问题**

---

## Material Design 3 原则

- **个性化**：动态颜色适应用户壁纸
- **无障碍**：色调调色板确保足够的颜色对比度
- **大屏幕**：平板和折叠屏的响应式布局

---

## Jetpack Compose 布局

### Column 和 Row

```kotlin
// 垂直排列
Column(
    modifier = Modifier.padding(16.dp),
    verticalArrangement = Arrangement.spacedBy(12.dp),
    horizontalAlignment = Alignment.Start
) {
    Text(
        text = "Title",
        style = MaterialTheme.typography.headlineSmall
    )
    Text(
        text = "Subtitle",
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.onSurfaceVariant
    )
}

// 水平排列
Row(
    modifier = Modifier.fillMaxWidth(),
    horizontalArrangement = Arrangement.SpaceBetween,
    verticalAlignment = Alignment.CenterVertically
) {
    Icon(Icons.Default.Star, contentDescription = null)
    Text("Featured")
    Spacer(modifier = Modifier.weight(1f))
    TextButton(onClick = {}) {
        Text("View All")
    }
}
```

### Lazy Lists 和 Grids

```kotlin
// 带 sticky header 的 LazyColumn
LazyColumn {
    items.groupBy { it.category }.forEach { (category, categoryItems) ->
        stickyHeader {
            Text(
                text = category,
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(16.dp),
                style = MaterialTheme.typography.titleMedium
            )
        }
        items(categoryItems) { item ->
            ItemRow(item = item)
        }
    }
}

// 自适应网格
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 150.dp),
    contentPadding = PaddingValues(16.dp),
    horizontalArrangement = Arrangement.spacedBy(12.dp),
    verticalArrangement = Arrangement.spacedBy(12.dp)
) {
    items(items) { item ->
        ItemCard(item = item)
    }
}
```

---

## 导航模式

### Bottom Navigation

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination

                NavigationDestination.entries.forEach { destination ->
                    NavigationBarItem(
                        icon = { Icon(destination.icon, contentDescription = null) },
                        label = { Text(destination.label) },
                        selected = currentDestination?.hierarchy?.any {
                            it.route == destination.route
                        } == true,
                        onClick = {
                            navController.navigate(destination.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = NavigationDestination.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(NavigationDestination.Home.route) { HomeScreen() }
            composable(NavigationDestination.Search.route) { SearchScreen() }
            composable(NavigationDestination.Profile.route) { ProfileScreen() }
        }
    }
}
```

---

## Material 3 主题

### 动态颜色（Android 12+）

```kotlin
val dynamicColorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    val context = LocalContext.current
    if (darkTheme) dynamicDarkColorScheme(context)
    else dynamicLightColorScheme(context)
} else {
    if (darkTheme) DarkColorScheme else LightColorScheme
}
```

### 自定义颜色方案

```kotlin
private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF6750A4),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFEADDFF),
    onPrimaryContainer = Color(0xFF21005D),
    secondary = Color(0xFF625B71),
    onSecondary = Color.White,
    tertiary = Color(0xFF7D5260),
    onTertiary = Color.White,
    surface = Color(0xFFFFFBFE),
    onSurface = Color(0xFF1C1B1F),
)
```

---

## 组件示例

### Cards

```kotlin
@Composable
fun FeatureCard(
    title: String,
    description: String,
    imageUrl: String,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column {
            AsyncImage(
                model = imageUrl,
                contentDescription = null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp),
                contentScale = ContentScale.Crop
            )
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
```

### Buttons

```kotlin
// Filled button（主要操作）
Button(onClick = { }) {
    Text("Continue")
}

// Filled tonal button（次要操作）
FilledTonalButton(onClick = { }) {
    Icon(Icons.Default.Add, null)
    Spacer(Modifier.width(8.dp))
    Text("Add Item")
}

// Outlined button
OutlinedButton(onClick = { }) {
    Text("Cancel")
}

// FAB
FloatingActionButton(
    onClick = { },
    containerColor = MaterialTheme.colorScheme.primaryContainer,
    contentColor = MaterialTheme.colorScheme.onPrimaryContainer
) {
    Icon(Icons.Default.Add, contentDescription = "Add")
}
```

---

## 最佳实践

1. **使用 Material Theme** - 通过 `MaterialTheme.colorScheme` 访问颜色，自动支持深色模式
2. **支持动态颜色** - 在 Android 12+ 启用动态颜色实现个性化
3. **自适应布局** - 使用 `WindowSizeClass` 实现响应式设计
4. **内容描述** - 为所有交互元素添加 `contentDescription`
5. **触摸目标** - 最小 48dp 触摸目标以确保无障碍
6. **状态提升** - 提升状态使组件可复用和可测试
7. **正确使用 remember** - 适当使用 `remember` 和 `rememberSaveable`
8. **预览注解** - 添加不同配置的 `@Preview`

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| react-native-patterns | React Native 性能优化 |
| app-debugging | App 调试技巧 |
| expo-native-ui | Expo 原生 UI 指南 |
