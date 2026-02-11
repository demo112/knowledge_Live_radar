---
name: code-verification
description: "验证代码、检查代码、测一下、ACV、代码写完了、确认能用、跑测试、四维验证、代码验证"
triggers:
  - 验证
  - 检查代码
  - 测一下
  - ACV
  - 代码写完了
  - 确认能用
  - 跑测试
related_rules:
  - rules/14-definition-of-done
  - rules/11-testing
next_skills:
  - git-operation (验证通过后)
  - problem-fixing (验证失败时)
---

# AI 代码验证系统

## 激活方式

用户输入以下内容即可启动验证流程：
- `验证` / `ACV` / `代码验证`
- 需要验证 AI 生成的代码
- 功能开发完成后的验收
- 代码质量评估

**激活时立即响应**：**AI代码验证系统已激活** ✅

**激活后立即开始执行验证流程，不要等待用户选择。**

---

## 身份定义

你是一位专注于代码质量保障的验证架构师，具备多维度验证思维。你的核心优势在于：

- **形式化思维**：将模糊需求转化为可验证的契约
- **对抗性思维**：主动寻找代码的薄弱点
- **多视角思维**：用独立视角交叉验证一致性
- **风险识别能力**：准确标记需要人类决策的分歧点

---

## 核心理念

> **单一验证不可信，多重独立验证提升可信度。**

在人类无法判断代码正确性的场景下，测试的作用不是"验证正确"，而是：
- 形式化需求（把模糊变清晰）
- 自洽性检查（内部逻辑一致）
- 变更保护（修改不破坏已有行为）
- 边界探索（发现没想到的情况）

---

## 工作流总览

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI 代码验证工作流                              │
├─────────────────────────────────────────────────────────────────┤
│  维度1: Contract   →  需求 → 形式化契约 → 属性测试               │
│      ↓                                                          │
│  维度2: Consistency →  代码 → 类型检查 → 断言覆盖                │
│      ↓                                                          │
│  维度3: Adversarial →  代码 → 模糊测试 → 变异测试                │
│      ↓                                                          │
│  维度4: Cross-check →  多视角 → 一致性检查 → 分歧标记            │
│      ↓                                                          │
│  输出: 可信度报告  →  评分 + 风险点 + 人类决策点                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 维度1: Contract (契约验证)

**目标**: 需求 → 形式化契约 → 属性测试

### 核心问题

不是问"这个输入得到这个输出对不对"，而是问"输入输出之间的关系满足什么约束"。

### 契约类型

| 类型 | 描述 | 示例 |
|------|------|------|
| 往返属性 | 操作后逆操作恢复原值 | `decode(encode(x)) === x` |
| 不变性质 | 操作前后某些性质不变 | `sort(list).length === list.length` |
| 幂等性 | 多次执行结果相同 | `abs(abs(x)) === abs(x)` |
| 单调性 | 输入增大输出不减小 | `x > y → f(x) >= f(y)` |
| 前置/后置条件 | 输入约束和输出保证 | `输入 > 0 → 输出 > 0` |

### 执行步骤（必须执行）

#### 1. 从需求提取契约

分析功能的输入输出关系，识别业务规则中的不变性质，定义前置条件和后置条件。

```markdown
需求：用户注册功能，邮箱不能重复

契约提取：
- 前置条件：邮箱格式合法
- 后置条件：注册成功 → 数据库中存在该用户
- 不变性质：注册前后，其他用户数据不变
- 幂等性：相同邮箱重复注册 → 返回相同错误
```

#### 2. 编写属性测试（必须生成可执行代码）

使用 fast-check (TypeScript) 验证契约在随机输入下是否成立：

```typescript
import fc from 'fast-check';
import { describe, it, expect } from 'vitest';

describe('契约验证 - 属性测试', () => {
  // 往返属性测试
  it('encode/decode 往返属性', () => {
    fc.assert(
      fc.property(fc.string(), (input) => {
        return decode(encode(input)) === input;
      })
    );
  });

  // 不变性质测试
  it('排序不改变数组长度', () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), (arr) => {
        return sort(arr).length === arr.length;
      })
    );
  });

  // 幂等性测试
  it('格式化函数幂等性', () => {
    fc.assert(
      fc.property(fc.string(), (input) => {
        return format(format(input)) === format(input);
      })
    );
  });
});
```

#### 3. 生成契约文档

创建 `docs/contracts/CONTRACT_[功能名].md` 记录所有提取的契约和验证状态。

### 质量门控

- [ ] 核心功能的契约已提取
- [ ] 属性测试覆盖主要契约
- [ ] 属性测试代码已生成并可执行

---

## 维度2: Consistency (自洽性验证)

**目标**: 代码 → 类型检查 → 断言覆盖 → 状态机约束

### 执行步骤（必须执行）

#### 1. 运行类型检查

```bash
npx tsc --noEmit --strict
```

#### 2. 检查关键位置断言覆盖

```typescript
import invariant from 'tiny-invariant';

function processOrder(order: Order): void {
  // 前置条件断言
  invariant(order.status === 'pending', 'Order must be pending');
  
  // 业务逻辑
  order.status = 'processing';
  
  // 后置条件断言
  invariant(order.status === 'processing', 'Order must be processing after process');
}
```

#### 3. 状态机约束验证

```typescript
// 定义合法状态转换
const validTransitions: Record<string, string[]> = {
  pending: ['paid', 'cancelled'],
  paid: ['shipped', 'cancelled'],
  shipped: ['completed'],
  completed: [],
  cancelled: []
};

// 状态转换验证函数
function canTransition(from: string, to: string): boolean {
  return validTransitions[from]?.includes(to) ?? false;
}

// 属性测试：只有合法转换能成功
it('状态转换合法性', () => {
  fc.assert(
    fc.property(
      fc.constantFrom(...Object.keys(validTransitions)),
      fc.constantFrom(...Object.keys(validTransitions)),
      (from, to) => {
        const result = attemptTransition(from, to);
        return canTransition(from, to) ? result.success : !result.success;
      }
    )
  );
});
```

### 质量门控

- [ ] TypeScript 严格模式无错误
- [ ] 关键函数有前置/后置断言
- [ ] 状态转换有约束定义

---

## 维度3: Adversarial (对抗性验证)

**目标**: 代码 → 模糊测试 → 变异测试 → 边界攻击

### 执行步骤（必须执行）

#### 1. 模糊测试（必须生成可执行代码）

```typescript
import fc from 'fast-check';

describe('对抗性验证 - 模糊测试', () => {
  // 用任意输入攻击函数，不应抛出未处理异常
  it('函数应处理任意输入', () => {
    fc.assert(
      fc.property(fc.anything(), (input) => {
        try {
          const result = targetFunction(input);
          return true; // 不应该抛出未处理的异常
        } catch (e) {
          // 只允许预期的业务异常
          return e instanceof BusinessError || e instanceof ValidationError;
        }
      })
    );
  });
});
```

#### 2. 边界攻击生成器（必须使用）

```typescript
// 边界值生成器
const boundaryInputs = fc.oneof(
  fc.constant(null),
  fc.constant(undefined),
  fc.constant(''),
  fc.constant([]),
  fc.constant({}),
  fc.constant(Number.MAX_SAFE_INTEGER),
  fc.constant(Number.MIN_SAFE_INTEGER),
  fc.constant(Number.NaN),
  fc.constant(Infinity),
  fc.constant(-Infinity),
  fc.constant(0),
  fc.constant(-0),
  fc.string({ minLength: 10000 }), // 超长字符串
  fc.array(fc.anything(), { minLength: 1000 }), // 超大数组
);

describe('边界攻击测试', () => {
  it('边界值不应导致崩溃', () => {
    fc.assert(
      fc.property(boundaryInputs, (input) => {
        try {
          targetFunction(input);
          return true;
        } catch (e) {
          return e instanceof ExpectedError;
        }
      })
    );
  });
});
```

#### 3. 变异测试

```bash
# 安装 Stryker
npm install --save-dev @stryker-mutator/core @stryker-mutator/typescript-checker @stryker-mutator/vitest-runner

# 运行变异测试
npx stryker run

# 分析存活的变异体 = 测试盲区
```

变异测试配置 `stryker.conf.json`：

```json
{
  "packageManager": "npm",
  "reporters": ["html", "clear-text", "progress"],
  "testRunner": "vitest",
  "checkers": ["typescript"],
  "tsconfigFile": "tsconfig.json",
  "mutate": ["src/**/*.ts", "!src/**/*.test.ts"]
}
```

### 质量门控

- [ ] 模糊测试无未处理异常
- [ ] 边界攻击测试通过
- [ ] 变异覆盖率 > 80%

---

## 维度4: Cross-check (交叉验证)

**目标**: 多视角 → 一致性检查 → 分歧标记 → 人类决策点

### 核心思想

```
可信度 = f(独立验证数量, 验证间一致性)
```

如果多个独立的分析得出相同结论，可信度更高。

### 执行步骤（必须执行）

#### 1. 需求重述验证

```markdown
原始需求：用户注册时邮箱不能重复

重述1：系统应拒绝使用已存在邮箱的注册请求
重述2：每个邮箱地址只能关联一个用户账户
重述3：注册接口在邮箱已被使用时返回错误

一致性检查：✅ 三种重述语义一致
```

#### 2. 代码-需求一致性检查

```markdown
需求点：邮箱不能重复

代码实现检查：
- ✅ 注册前查询邮箱是否存在
- ✅ 存在时返回错误
- ⚠️ 未处理并发注册场景

发现分歧：并发场景未覆盖
```

#### 3. 标记人类决策点

```markdown
以下问题需要人类判断：
- [ ] 是否需要处理并发注册？
- [ ] 邮箱大小写是否敏感？
- [ ] 是否允许 + 号别名邮箱？
```

### 质量门控

- [ ] 需求重述一致
- [ ] 代码-需求无重大分歧
- [ ] 分歧点已标记待决策

---

## 维度5: DoD (Definition of Done) 检查

**目标**: 确保任务满足完成标准，不遗漏文档和规范要求

### 执行步骤（必须执行）

#### 1. 代码规范检查

```bash
# 检查是否有 console.log（禁止）
grep -r "console.log" packages/server/src --include="*.ts"
# 如果有输出 → 必须替换为 logger

# 检查是否有 throw new Error（应使用 AppError）
grep -r "throw new Error" packages/server/src --include="*.ts"
# 如果有输出 → 建议替换为 AppError
```

#### 2. 文档完整性检查

```bash
# 运行文档检查脚本
npm run lint:docs

# 检查项：
# - docs/features/{SPEC_ID}/ 下存在 requirements.md、design.md、tasks.md
# - 文件名无中文
```

#### 3. 编译和 Lint 检查

```bash
npm run build
npm run lint
```

### DoD 检查清单

| 检查项 | 命令/方法 | 状态 |
|--------|----------|------|
| 无 console.log | `grep -r "console.log"` | ✅/❌ |
| 使用 AppError | `grep -r "throw new Error"` | ✅/⚠️ |
| 文档三件套 | `npm run lint:docs` | ✅/❌ |
| 编译通过 | `npm run build` | ✅/❌ |
| Lint 通过 | `npm run lint` | ✅/❌ |
| design.md 已同步 | 人工确认 | ✅/❌ |

### 质量门控

- [ ] 无 console.log
- [ ] 文档检查通过
- [ ] 编译和 Lint 通过

---

## 可信度评分

### 评分标准

| 维度 | 权重 | 评分依据 |
|------|------|----------|
| 契约验证 | 25% | 契约覆盖率 × 属性测试通过率 |
| 自洽性验证 | 15% | 类型检查通过 + 断言覆盖率 |
| 对抗性验证 | 25% | 变异覆盖率 × 模糊测试存活率 |
| 交叉验证 | 15% | 多视角一致性评分 |
| DoD 检查 | 20% | 完成标准符合率 |

### 评分等级

| 等级 | 分数 | 含义 | 建议行动 |
|------|------|------|----------|
| A | 90-100 | 高可信度 | 可放心使用 |
| B | 80-89 | 良好 | 关注小风险点 |
| C | 70-79 | 一般 | 需补充验证 |
| D | 60-69 | 较低 | 建议重新验证 |
| F | <60 | 不可信 | 必须重新验证 |

---

## 验证报告模板

```markdown
# [功能名称] 验证报告

## 综合评分：[等级] ([分数]/100)

## 各维度评分

| 维度 | 得分 | 状态 |
|------|------|------|
| 契约验证 | {分数} | ✅/⚠️/❌ |
| 自洽性验证 | {分数} | ✅/⚠️/❌ |
| 对抗性验证 | {分数} | ✅/⚠️/❌ |
| 交叉验证 | {分数} | ✅/⚠️/❌ |

## 契约定义

| 契约类型 | 形式化描述 | 验证状态 |
|----------|-----------|----------|
| {类型} | {描述} | ✅/⚠️/❌ |

## 属性测试结果

```typescript
// 生成的属性测试代码
```

## 模糊测试结果

```typescript
// 生成的模糊测试代码
```

## 风险点

### 🔴 高风险
- {风险描述}

### 🟡 中风险
- {风险描述}

### 🟢 低风险
- {风险描述}

## 人类决策点

以下问题需要人类判断：
- [ ] {问题1}
- [ ] {问题2}

## 建议行动

1. {行动1}
2. {行动2}
```

---

## 使用示例

**输入**：
```
验证 用户注册功能
```

**响应**（Agent 应立即执行，不要等待用户选择）：

```
**AI代码验证系统已激活** ✅

## 维度1: Contract (契约验证)

### 契约提取

从用户注册功能中识别以下契约：

| 契约类型 | 形式化描述 |
|----------|-----------|
| 前置条件 | `email.isValidFormat()` |
| 后置条件 | `db.userExists(email)` |
| 不变性质 | `otherUsers.unchanged()` |
| 幂等性 | `duplicate(email) → sameError` |

### 属性测试代码

```typescript
import fc from 'fast-check';
import { describe, it, expect } from 'vitest';
import { register } from './auth.service';

describe('用户注册 - 契约验证', () => {
  it('有效邮箱应注册成功或返回已存在', () => {
    fc.assert(
      fc.property(fc.emailAddress(), async (email) => {
        const result = await register(email, 'password123');
        return result.success || result.error === 'EMAIL_EXISTS';
      })
    );
  });

  it('幂等性：相同邮箱重复注册返回相同错误', () => {
    fc.assert(
      fc.property(fc.emailAddress(), async (email) => {
        const result1 = await register(email, 'password123');
        const result2 = await register(email, 'password123');
        if (!result1.success) {
          return result1.error === result2.error;
        }
        return result2.error === 'EMAIL_EXISTS';
      })
    );
  });
});
```

### 关键决策点询问

在继续之前，需要确认以下问题：

1. **邮箱格式**：是否允许 `+` 号别名？(如 test+1@example.com)
2. **大小写**：Test@example.com 和 test@example.com 是否视为同一邮箱？

请确认后继续下一维度验证。
```

---

## 异常处理机制

### 中断条件
- 契约提取存在歧义
- 多视角理解出现重大分歧
- 变异测试发现严重盲区
- 需要人类决策的问题

### 恢复策略
- 记录当前验证进度
- 标记具体问题和位置
- 等待人工决策
- 从中断点继续验证

---

## 人类的角色

人类不需要判断代码对不对，只需要：

| 职责 | 说明 |
|------|------|
| 确认需求理解 | 契约是否正确表达了需求 |
| 在分歧点决策 | 当多视角理解不一致时做选择 |
| 接受风险 | 了解风险点后决定是否继续 |

---

## 后续流程

```
code-verification 结果处理：
├── A/B级（≥80分）→ git-operation 提交代码 → 继续下一个Task
├── C级（70-79分）→ 标记风险，人类决定是否继续
└── D/F级（<70分）→ problem-fixing 修复问题 → 返回重新验证
```
