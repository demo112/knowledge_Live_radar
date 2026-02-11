---
name: web-debugging
description: "Web 端 (React + Vite) 调试技巧"
type: platform-specific
---

# Web 端调试 (React + Vite)

> 适用于 attendance-system/packages/web

---

## 触发场景

- Web 端页面白屏/报错
- React 组件渲染问题
- Vite 构建/HMR 问题
- API 请求失败
- 状态管理异常

---

## 调试工具链

### 1. Vite 开发服务器日志

```bash
# 启动时查看详细日志
npm run dev -- --debug

# 查看依赖预构建问题
npm run dev -- --force
```

### 2. 浏览器 DevTools

| 面板 | 用途 |
|------|------|
| Console | 错误日志、console.log |
| Network | API 请求、资源加载 |
| Sources | 断点调试、调用栈 |
| React DevTools | 组件树、Props/State |
| Performance | 渲染性能分析 |

### 3. React DevTools 关键功能

```
- Components 面板：查看组件层级、props、state
- Profiler 面板：分析渲染性能
- Highlight updates：高亮重渲染的组件
```

---

## 常见问题调试

### 白屏/页面崩溃

```
1. 打开 Console 查看错误
2. 检查 Network 是否有 JS 加载失败
3. 检查 React 错误边界是否捕获了错误
4. 检查路由配置
```

### Vite HMR 不生效

```bash
# 清除缓存重启
rm -rf node_modules/.vite
npm run dev
```

### API 请求问题

```typescript
// 添加请求拦截器日志
axios.interceptors.request.use(config => {
  console.log('=== Request ===', config.url, config.data);
  return config;
});

axios.interceptors.response.use(
  res => {
    console.log('=== Response ===', res.config.url, res.data);
    return res;
  },
  err => {
    console.error('=== Error ===', err.config?.url, err.response?.data);
    return Promise.reject(err);
  }
);
```

### React 状态问题

```typescript
// 使用 useEffect 追踪状态变化
useEffect(() => {
  console.log('State changed:', { state1, state2 });
}, [state1, state2]);
```

### 构建错误

```bash
# 查看详细构建日志
npm run build -- --debug

# 分析打包体积
npm run build -- --analyze
```

---

## 诊断埋点模板

```typescript
// 组件生命周期追踪
const ComponentName = () => {
  console.log('=== Render: ComponentName ===');
  
  useEffect(() => {
    console.log('=== Mount: ComponentName ===');
    return () => console.log('=== Unmount: ComponentName ===');
  }, []);
  
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

# 构建验证
npm run build

# 预览构建结果
npm run preview
```

---

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| systematic-debugging | 遵循四阶段调查法 |
| problem-fixing | 修复流程的平台实现 |
| vite-patterns | Vite 最佳实践参考 |
| react-best-practices | React 最佳实践参考 |
