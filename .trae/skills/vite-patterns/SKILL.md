---
name: vite-patterns
description: "[参考层] Vite构建工具指南，供 code-implementation 编写 Web 代码时参考。来源：antfu/skills"
type: reference
applies_to: web
---

# Vite 模式

> 来源: [antfu/skills](https://skills.sh/antfu/skills/vite)

Vite是现代前端开发构建工具，具有原生ES模块的即时服务器启动、闪电般的HMR和使用Rolldown/Rollup的优化生产构建。

基于Vite 6.x。

---

## 激活方式

### 触发场景

- 配置**Vite项目**
- 设置**环境变量**
- 开发**Vite插件**
- 优化**构建配置**

### 触发关键词

| 类别 | 关键词 |
|------|--------|
| 核心关键词 | Vite、构建、打包 |
| 配置类 | vite.config、环境变量、代理 |
| 优化类 | 分包、懒加载、预构建 |

---

## 核心配置

### 基本配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
```

### 环境变量

```bash
# .env
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App
```

```typescript
// 代码中使用
const apiUrl = import.meta.env.VITE_API_URL;
const isDev = import.meta.env.DEV;
const isProd = import.meta.env.PROD;
```

### 路径别名

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
    },
  },
});
```

### 代理配置

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
```

---

## CSS处理

### CSS Modules

```typescript
// Component.module.css
.button {
  background: blue;
}

// Component.tsx
import styles from './Component.module.css';

function Component() {
  return <button className={styles.button}>Click</button>;
}
```

---

## 构建优化

### 手动分包

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash', 'date-fns'],
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
});
```

### Glob导入

```typescript
// 导入目录中的所有模块
const modules = import.meta.glob('./modules/*.ts');

// 立即加载
const modules = import.meta.glob('./modules/*.ts', { eager: true });

// 带查询
const images = import.meta.glob('./assets/*.png', { query: '?url' });
```

---

## 插件开发

```typescript
// my-plugin.ts
import type { Plugin } from 'vite';

export function myPlugin(): Plugin {
  return {
    name: 'my-plugin',
    
    // 服务器启动时调用
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        // 自定义中间件
        next();
      });
    },
    
    // 转换代码
    transform(code, id) {
      if (id.endsWith('.custom')) {
        return {
          code: transformCustomFile(code),
          map: null,
        };
      }
    },
  };
}
```

---

## CLI命令

```bash
# 启动开发服务器
vite

# 生产构建
vite build

# 预览生产构建
vite preview

# 指定配置文件
vite --config my-config.js

# 指定模式
vite build --mode staging
```

---

## 最佳实践

1. **使用TypeScript配置**：`vite.config.ts`获得类型安全
2. **利用HMR**：除非必要不要禁用
3. **优化依赖**：预构建大型依赖
4. **使用别名**：路径别名使导入更清晰
5. **分割chunks**：手动分包获得更好的缓存
6. **环境模式**：为dev/staging/prod分离配置
