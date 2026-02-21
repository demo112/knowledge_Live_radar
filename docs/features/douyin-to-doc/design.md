# Design: 抖音视频转文档组件 (Douyin Video to Document)

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: 将抖音视频转换为文档 | API: `POST /api/v1/tools/douyin/convert`<br>组件: `DouyinConverterPage`, `DouyinInput` |
| AC1: 成功处理有效链接 | Service: `DouyinService` 集成 `yt-dlp` 下载, `AIClient` 转录与摘要 |
| AC2: 处理无效链接 | Service: `DouyinService` 校验 URL 格式 |
| AC3: 内容组织结构 | Service: `DouyinService` 调用 LLM 整理 Markdown |

## 数据模型

本功能不涉及持久化存储，无需新增数据库模型。

## API定义

### POST /api/v1/tools/douyin/convert

提交抖音分享链接，生成结构化文档。

**Request:**
```typescript
interface DouyinConvertRequest {
  url: string // 抖音分享链接
}
```

**Response:**
```typescript
interface DouyinConvertResponse {
  success: boolean
  data?: {
    title: string
    markdown: string // 完整的 Markdown 文档
    metadata: {
      duration: number // 秒
      author: string
      original_url: string
    }
  }
  error?: { code: string, message: string }
}
```

**错误码:**
| 错误码 | 说明 |
|--------|------|
| ERR_TOOL_INVALID_URL | 无效的抖音链接 |
| ERR_TOOL_DOWNLOAD_FAILED | 视频下载失败 |
| ERR_TOOL_TRANSCRIPTION_FAILED | 音频转录失败 |
| ERR_TOOL_PROCESSING_FAILED | 处理过程异常 |

## 文件变更清单

| 文件 | 操作 | 内容 |
|------|------|------|
| backend/requirements.txt | 修改 | 新增 `yt-dlp` |
| backend/app/core/ai/client.py | 修改 | 新增 `audio_transcriptions` 方法 (调用 OpenAI 兼容接口) |
| backend/app/schemas/tools.py | 新增 | `DouyinConvertRequest`, `DouyinConvertResponse` Schema 定义 |
| backend/app/services/douyin_service.py | 新增 | `DouyinService` 类，实现下载、转录、文档生成逻辑 |
| backend/app/routers/tools.py | 新增 | `POST /douyin/convert` 路由处理 |
| backend/app/main.py | 修改 | 注册 `tools` 路由 |
| frontend/src/app/[locale]/(dashboard)/tools/douyin/page.tsx | 新增 | 抖音转文档工具页面 |
| frontend/src/components/tools/DouyinInput.tsx | 新增 | URL 输入组件 |
| frontend/src/components/tools/DocViewer.tsx | 新增 | Markdown 文档展示组件 |
| frontend/src/app/[locale]/(dashboard)/layout.tsx | 修改 | 新增导航菜单项 "工具/抖音转文档" |
| frontend/messages/zh.json | 修改 | 新增相关国际化文本 |
| frontend/messages/en.json | 修改 | 新增相关国际化文本 |

## 引用的已有代码

- `backend/app/core/ai/client.py` - AI 客户端（需扩展音频能力）
- `backend/app/core/ai/prompt_loader.py` - Prompt 管理（需新增 prompt 模板）
- `frontend/src/components/ui/*` - 基础 UI 组件

## 影响分析

| 已有功能 | 影响 | 风险等级 |
|---------|------|---------|
| AIClient | 增加音频转录方法，不影响现有 Chat 功能 | 低 |
| 导航栏 | 增加一个菜单项 | 低 |

## 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 视频下载 | `yt-dlp` | 开源、活跃、支持抖音、功能强大 |
| ASR 服务 | SiliconFlow API (OpenAI 兼容) | 复用现有 API Key，无需本地部署重型模型，速度快 |
| 文档生成 | DeepSeek V3 (via SiliconFlow) | 现有集成，效果好，成本低 |
| 临时文件 | 本地临时目录 | 简单高效，处理完即删，无需对象存储 |

## 风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| 抖音反爬策略升级 | `yt-dlp` 下载失败 | 保持 `yt-dlp` 更新，提示用户重试 |
| 视频无语音 | 转录为空 | 提示用户"视频无语音内容"，仅根据元数据生成文档 |
| SiliconFlow ASR 不可用 | 转录失败 | 错误处理，未来可增加本地 `faster-whisper` 作为 fallback |

## 需要人决策

- [ ] 无需决策，方案清晰。
