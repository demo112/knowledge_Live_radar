# Design: 内容新陈代谢系统

## Database Schema Changes

### `ContentItem` Table

| Field | Type | Description |
|-------|------|-------------|
| `lifecycle_status` | Enum | `ACTIVE`, `DEPRECATED`, `ARCHIVED`, `DELETED` (Default: `ACTIVE`) |
| `metabolism_score` | Float | Calculated score (0-100) |
| `last_accessed_at` | DateTime | Last time content was viewed or referenced |
| `access_count` | Integer | Total views + references |

**Indexes**:
- `idx_content_lifecycle` on `(lifecycle_status, metabolism_score)`
- `idx_content_last_accessed` on `(last_accessed_at)`

## Algorithm Design

### Metabolism Score Formula
```python
def calculate_score(quality_score, days_old, popularity):
    # 1. Base: Quality Score (0-100, default 50 if unknown)
    base = quality_score or 50.0
    
    # 2. Decay: Halflife of 180 days (approx 6 months)
    # Score drops to 50% after 180 days if no popularity boost
    decay = math.exp(-days_old / 180.0)
    
    # 3. Boost: Logarithmic boost from popularity
    # max boost = 1.5x (e.g., for 1000+ views)
    boost = 1.0 + (0.1 * math.log1p(popularity))
    
    final_score = base * decay * boost
    return min(100.0, max(0.0, final_score))
```

### Transition Logic
1. **To Deprecated**: `status=ACTIVE` AND `score < 40` AND `days_old > 30`
2. **To Archived**: `status=DEPRECATED` AND `last_accessed > 30 days ago` AND `days_old > 90`
3. **To Deleted (Suggestion)**: `status=ARCHIVED` AND `score < 20` AND `days_old > 180`

## API Design

### System Management
- `POST /api/v1/system/metabolism/run`: Manually trigger the daily job.
- `GET /api/v1/system/metabolism/suggestions`: Get list of items suggested for deletion.
  - Returns: `{ "items": [{ "id": "...", "title": "...", "reason": "Score 15 < 20", "score": 15.0 }] }`
- `POST /api/v1/system/metabolism/cleanup`: Confirm deletion of items.
  - Body: `{ "ids": ["..."] }`

## Module Structure

```
backend/app/
  services/
    metabolism_service.py  # Core logic
  routers/
    system.py             # Add metabolism endpoints
  models/
    content.py            # Update model
  scheduler/
    tasks.py              # Add scheduled task
```
