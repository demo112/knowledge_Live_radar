# 前端测试 Skill

> 本 Skill 指导 LLM 在前端项目中编写和运行测试。

---

## 元信息

```yaml
name: frontend-testing
description: 前端测试执行与编写指导
type: execution
triggers:
  - 写测试
  - 运行测试
  - 测试失败
  - 验证代码
dependencies:
  - test-driven-development
  - code-verification
```

---

## 触发场景

| 场景 | 说明 |
|------|------|
| 新功能开发 | 需要写测试验证功能 |
| Bug 修复 | 需要写测试复现 Bug |
| 代码验证 | 需要运行测试确认正确性 |
| 重构 | 需要运行测试确认无回归 |

---

## 前置检查

在执行测试相关操作前，必须确认：

### 1. 测试环境是否就绪

```bash
# 检查测试命令是否存在
cat package.json | grep "test"

# 预期输出应包含：
# "test": "vitest --run"  (Web/Shared)
# 或
# "test": "jest"  (App)
```

### 2. 确定目标包

| 包 | 路径 | 测试命令 |
|----|------|----------|
| shared | packages/shared | `pnpm --filter @attendance/shared test` |
| web | packages/web | `pnpm --filter @attendance/web test` |
| app | packages/app | `pnpm --filter @attendance/app test` |

---

## 测试类型判断

根据代码类型选择测试类型：

| 代码类型 | 测试类型 | 文件命名 |
|----------|----------|----------|
| 工具函数 | 单元 + 属性 | `*.test.ts` + `*.property.test.ts` |
| 自定义 Hook | 单元 | `*.test.ts` |
| 业务逻辑 | 单元 + 属性 | `*.test.ts` + `*.property.test.ts` |
| 组件 | 单元/集成 | `*.test.tsx` / `*.integration.test.tsx` |
| 页面流程 | 集成 | `*.integration.test.tsx` |

---

## 执行流程

### 场景 A：为新代码写测试

```
1. 确定代码类型和测试类型
2. 创建测试文件（与源码同目录）
3. 编写测试（遵循 AAA 模式）
4. 运行测试确认通过
```

**测试文件位置规则（co-location）：**

```
src/utils/date.ts           → src/utils/date.test.ts
src/hooks/useAuth.ts        → src/hooks/useAuth.test.ts
src/components/Button.tsx   → src/components/Button.test.tsx
```

### 场景 B：运行现有测试

```bash
# 运行单个文件
pnpm --filter @attendance/web test -- --run src/utils/date.test.ts

# 运行整个包
pnpm --filter @attendance/web test -- --run

# 运行所有包
pnpm test
```

### 场景 C：测试失败处理

```
1. 阅读失败信息
2. 定位失败原因（代码问题 or 测试问题）
3. 如果是代码问题 → 触发 problem-fixing
4. 如果是测试问题 → 修复测试
5. 重新运行确认通过
```

---

## 测试模板

### 单元测试模板

```typescript
import { describe, it, expect } from 'vitest'; // 或 jest
import { targetFunction } from './target';

describe('targetFunction', () => {
  it('正常情况：描述预期行为', () => {
    // Arrange
    const input = { /* ... */ };
    
    // Act
    const result = targetFunction(input);
    
    // Assert
    expect(result).toBe(/* expected */);
  });

  it('边界情况：描述边界行为', () => {
    // ...
  });

  it('异常情况：描述异常处理', () => {
    // ...
  });
});
```

### 属性测试模板

```typescript
import { describe, it } from 'vitest';
import fc from 'fast-check';
import { encode, decode } from './codec';

describe('codec 契约验证', () => {
  it('往返属性：decode(encode(x)) === x', () => {
    fc.assert(
      fc.property(fc.string(), (input) => {
        return decode(encode(input)) === input;
      })
    );
  });

  it('幂等属性：encode(encode(x)) === encode(x)', () => {
    fc.assert(
      fc.property(fc.string(), (input) => {
        return encode(encode(input)) === encode(input);
      })
    );
  });
});
```

### React 组件测试模板

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('渲染文本', () => {
    render(<Button>点击</Button>);
    expect(screen.getByText('点击')).toBeInTheDocument();
  });

  it('点击触发回调', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>点击</Button>);
    
    fireEvent.click(screen.getByText('点击'));
    
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

### React Native 组件测试模板

```typescript
import { describe, it, expect } from '@jest/globals';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { Button } from './Button';

describe('Button', () => {
  it('渲染文本', () => {
    render(<Button>点击</Button>);
    expect(screen.getByText('点击')).toBeTruthy();
  });

  it('点击触发回调', () => {
    const onPress = jest.fn();
    render(<Button onPress={onPress}>点击</Button>);
    
    fireEvent.press(screen.getByText('点击'));
    
    expect(onPress).toHaveBeenCalledTimes(1);
  });
});
```

---

## 与其他 Skill 的协作

| Skill | 协作方式 |
|-------|----------|
| test-driven-development | TDD 流程中调用本 Skill 运行测试 |
| code-verification | 契约验证时调用本 Skill 运行属性测试 |
| problem-fixing | 修复后调用本 Skill 验证修复 |
| verification-before-completion | 完成前调用本 Skill 确认测试通过 |

---

## 常见问题处理

### Q1: 测试命令不存在

**原因：** 测试环境未配置

**处理：** 提示用户先完成测试基础设施搭建

### Q2: 测试超时

**原因：** 异步操作未正确处理

**处理：** 检查 async/await，增加超时时间

### Q3: Mock 不生效

**原因：** MSW 未正确配置

**处理：** 检查 setup.ts 和 handlers

### Q4: 原生模块报错（App 端）

**原因：** 原生模块未 mock

**处理：** 在 jest-setup.ts 中添加 mock

---

## 输出格式

### 测试运行报告

```markdown
## 测试运行结果

| 指标 | 值 |
|------|-----|
| 总数 | {N} |
| 通过 | {X} |
| 失败 | {Y} |
| 跳过 | {Z} |

### 失败详情（如有）

| 测试 | 原因 |
|------|------|
| {测试名} | {失败原因} |
```
