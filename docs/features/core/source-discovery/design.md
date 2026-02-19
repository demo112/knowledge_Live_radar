# Design: 基于金字塔的信息源自动发现

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 触发发现任务 | API: `POST /api/v1/sources/discover`, 组件: `DiscoveryButton` |
| Story 2: 查看待审批源 | API: `GET /api/v1/approvals?type=create_source`, 组件: `DiscoveryList` |
| Story 3: 审批源 | API: `POST /api/v1/approvals/{id}/approve|reject`, 组件: `ApprovalAction` |
| Story 4: 中文优先 | Service: `SourceDiscoveryService` (使用中文关键词 + `lr=lang_zh`) |

## 数据模型

复用现有的 `Approval` 模型，不需要修改表结构，只需定义 `data` 字段的 JSON 结构。

```python
# Approval.data 结构示例 (type="create_source")
{
    "url": "https://tech.example.com/feed",
    "name": "某技术博客",
    "description": "关于 AI 和 Python 的技术博客",
    "source_type": "RSS",
    "tags": ["AI", "Python"],
    "reason": "与节点 '大语言模型' 相关",
    "origin_node_id": "uuid-..."
}
```

## API定义

### POST /api/v1/sources/discover

触发后台发现任务。

**Request:**
```typescript
interface DiscoverRequest {
  pyramid_id?: string // 可选，指定从哪个金字塔发现，不传则扫描所有
}
```

**Response:**
```typescript
interface DiscoverResponse {
  success: boolean
  message: string
  task_id: string
}
```

### GET /api/v1/sources/discovered

获取待审批的发现源（实际上是查询 `approvals` 表的便捷接口）。

**Response:**
```typescript
interface DiscoveredSource {
  id: string // approval_id
  url: string
  name: string
  description: string
  source_type: string
  reason: string
  created_at: string
  status: 'pending' | 'approved' | 'rejected'
}

interface DiscoveredListResponse {
  success: boolean
  data: DiscoveredSource[]
}
```

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| `backend/requirements.txt` | 修改 | 添加 `duckduckgo-search>=5.0.0` |
| `backend/app/schemas/source.py` | 修改 | 添加 `DiscoverRequest`, `DiscoveredSource` |
| `backend/app/services/source_discovery.py` | 新增 | `SourceDiscoveryService` 类，实现搜索和过滤逻辑 |
| `backend/app/routers/sources.py` | 修改 | 添加 `/discover` 和 `/discovered` 端点 |
| `frontend/src/app/[locale]/(dashboard)/sources/page.tsx` | 修改 | 添加 Discovery Tab 和相关 UI |
| `frontend/src/components/sources/DiscoveredSourceList.tsx` | 新增 | 待审批源列表组件 |
| `frontend/src/lib/api.ts` | 修改 | 添加 discovery 相关 API 调用 |

## 核心逻辑：SourceDiscoveryService

```python
class SourceDiscoveryService:
    async def discover(self, pyramid_id: str = None):
        # 1. 获取关键词
        keywords = self._get_keywords(pyramid_id)
        
        # 2. 执行搜索 (DuckDuckGo)
        results = []
        for kw in keywords:
            # 搜索 query: "{kw} 博客 RSS" 或 "{kw} 资讯 feed"
            # 限制语言: zh-cn
            items = await self._search(f"{kw} 博客 RSS", region="cn-zh")
            results.extend(items)
            
        # 3. 过滤和验证
        for item in results:
            if self._is_exists(item.url): continue
            if not self._validate_rss(item.url): continue
            
            # 4. 创建审批提案
            self._create_approval(item)
```

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| 信息源管理 | 增加了一个新的来源渠道 | 低 |
| 审批系统 | 复用了 Approval 表，增加了新的 type | 低 |

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 搜索服务 | `duckduckgo-search` | 免费、无 Key、Python 库支持好，适合演示和轻量级使用 |
| 审批存储 | 复用 `Approval` 表 | 避免创建新表，统一管理所有变更审批 |
| 任务执行 | `BackgroundTasks` | 简单异步，不需要引入 Celery 等重型队列 |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| DuckDuckGo 访问受限 | 无法搜索到结果 | 增加错误处理，若失败则降级为模拟数据或提示用户 |
| 搜索质量差 | 推荐大量无关源 | 优化关键词策略，增加人工审批环节（已包含） |

## 需要人决策

- [ ] 是否同意引入 `duckduckgo-search` 库？
- [ ] 审批通过后，是否默认开启抓取任务？（建议：默认开启）
