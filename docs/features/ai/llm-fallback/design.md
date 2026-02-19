# Design: LLM Service Fallback Mechanism

## 需求映射

| Story | 实现方式 |
|-------|---------|
| Story 1: Local First Strategy | Modify `AIService` to initialize two clients (Local/Cloud). Logic to try Local first. |
| Story 2: Automatic Fallback | `AIService.chat_completion` wraps calls in try-catch. If Local fails (Connection/Timeout), switch to Cloud. |
| Story 3: Configuration Management | Update `ConfigurationService` defaults to include `ai.local.*` and `ai.strategy`. |

## Configuration Update

### `backend/app/services/config/configuration_service.py`

Update `_get_defaults` to include:

```python
{
    # ... existing configs ...
    "ai.strategy": "local_first", # local_first, cloud_only, local_only
    
    # Local Config
    "ai.local.base_url": "http://localhost:11434/v1",
    "ai.local.model": "qwen2.5:7b",
    "ai.local.timeout": 5.0, # Fail fast
    "ai.local.enabled": True,
    
    # Cloud Config (mapped from existing ai.* for backward compatibility)
    "ai.cloud.base_url": "https://api.siliconflow.cn/v1",
    "ai.cloud.api_key": "", # from ai.api_key if not set
    "ai.cloud.model": "deepseek-ai/DeepSeek-V3",
}
```

## API Definition

No new external APIs. `AIService` internal API remains the same:

```python
async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> Optional[str]:
    # ...
```

## File Changes

| File | Operation | Content |
|------|-----------|---------|
| `backend/app/services/config/configuration_service.py` | Modify | Add new default configuration keys. |
| `backend/app/services/ai_service.py` | Modify | Implement `DualClientAIService` logic. |

## Implementation Details

### `AIService` Refactor

1.  **Initialization**:
    -   Load `ai.strategy`.
    -   Initialize `self._local_client` (AsyncOpenAI) if enabled.
    -   Initialize `self._cloud_client` (AsyncOpenAI) if enabled.

2.  **Execution Logic**:
    -   If `strategy == "local_only"`: Call local.
    -   If `strategy == "cloud_only"`: Call cloud.
    -   If `strategy == "local_first"`:
        -   Try local with short timeout.
        -   If `APITimeoutError` or `APIConnectionError`: Log warning, Call cloud.
        -   If successful: Return result.

3.  **Concurrency Control**:
    -   Add `asyncio.Semaphore` for local client (e.g., limit 4 concurrent requests) to prevent system freeze.
    -   If semaphore is full, treat as "busy" and fallback to cloud immediately.

## Impact Analysis

| Feature | Impact | Risk |
|---------|--------|------|
| AI Content Classification | Will now use local LLM by default. May be slower or lower quality depending on local model. | Medium |
| Search (Boolean Query) | No impact (logic is regex/sql based). | Low |
| Cost | Should decrease significantly. | Low |

## Decisions

-   **Timeout**: Default local timeout set to 5s. If local takes longer, we assume it's overloaded and switch to cloud (which might cost money but ensures responsiveness).
-   **Model**: Default local model is `qwen2.5:7b` (popular, efficient). User needs to pull it manually `ollama pull qwen2.5:7b`.

## Risks

-   **Local Model Quality**: Local model might be worse than Cloud (DeepSeek-V3).
    -   *Mitigation*: User can switch strategy to `cloud_only` or change local model.
-   **Ollama Not Installed**:
    -   *Mitigation*: Connection error fallback handles this gracefully.
