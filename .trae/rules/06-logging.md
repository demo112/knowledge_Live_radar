# 日志规范

## 级别
| 级别 | 用途 |
|------|------|
| ERROR | 错误，需要关注（AI 服务失败、抓取异常等） |
| WARNING | 警告，可能有问题（健康度低、校验未通过等） |
| INFO | 重要信息（抓取完成、审批操作、状态变更等） |
| DEBUG | 调试信息（AI 调用详情、校验过程等） |

## Python 后端日志

### 格式
```python
import logging
logger = logging.getLogger(__name__)

# 格式: [时间] [级别] [模块] 消息 {上下文}
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
```

### 必须记录的场景
| 场景 | 级别 | 内容 |
|------|------|------|
| API 请求入口 | INFO | 路径、参数 |
| AI 服务调用 | INFO/ERROR | 输入摘要、输出摘要、耗时 |
| 抓取任务执行 | INFO | 信息源、抓取数量、成功率 |
| 校验流程 | INFO | 校验类型、结果、分数 |
| 审批操作 | INFO | 操作类型、提案ID、操作者 |
| 状态变更 | INFO | 实体类型、旧状态、新状态 |
| 定时任务 | INFO | 任务名、开始/结束、结果 |
| 错误 | ERROR | 完整堆栈、上下文、重试信息 |

### 禁止记录
- API Key、数据库密码等敏感信息
- 用户完整输入内容（仅记录摘要）

## TypeScript 前端日志

- 开发环境使用 `console` 调试
- 生产环境通过 API 上报关键错误
- 禁止在生产代码中保留 `console.log`

## 强制执行 (DoD)
- **后端禁止使用 `print()`**：必须使用 `logging` 模块
- **统一工具**：后端使用 Python `logging`，前端使用统一的 logger 工具
