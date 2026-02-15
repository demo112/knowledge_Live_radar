from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid

class BatchCleanRequest(BaseModel):
    dry_run: bool = False
    chinese_ratio_threshold: float = 0.2

class CleanDetail(BaseModel):
    id: str
    title: str
    reason: str

class BatchCleanData(BaseModel):
    total_scanned: int
    deleted_count: int
    details: List[CleanDetail] = []

class BatchCleanResponse(BaseModel):
    success: bool = True
    data: BatchCleanData

class BatchSummarizeRequest(BaseModel):
    target_ids: Optional[List[uuid.UUID]] = None
    overwrite: bool = True

class BatchSummarizeData(BaseModel):
    task_id: str
    message: str

class BatchSummarizeResponse(BaseModel):
    success: bool = True
    data: BatchSummarizeData

class BatchDeleteRequest(BaseModel):
    ids: List[uuid.UUID]

class BatchDeleteData(BaseModel):
    deleted_count: int

class BatchDeleteResponse(BaseModel):
    success: bool = True
    data: BatchDeleteData

# Metabolism Schemas

class MetabolismRunResponse(BaseModel):
    processed: int
    to_deprecated: int
    to_archived: int

class MetabolismSuggestionItem(BaseModel):
    id: str
    title: str
    score: float
    age_days: int
    reason: str

class MetabolismSuggestionResponse(BaseModel):
    items: List[MetabolismSuggestionItem]

class MetabolismCleanupRequest(BaseModel):
    ids: List[uuid.UUID]

class MetabolismCleanupResponse(BaseModel):
    deleted_count: int
