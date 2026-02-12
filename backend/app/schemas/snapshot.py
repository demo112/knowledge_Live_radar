from uuid import UUID
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict

class SnapshotBase(BaseModel):
    version: str
    reason: Optional[str] = None
    data: Dict[str, Any]

class SnapshotCreate(SnapshotBase):
    pass

class SnapshotResponse(SnapshotBase):
    id: UUID
    pyramid_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SnapshotSummaryResponse(BaseModel):
    id: UUID
    pyramid_id: UUID
    version: str
    reason: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
