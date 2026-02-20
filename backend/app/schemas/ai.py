from typing import Optional, List, Any, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# --- Generic AI Suggestion Schemas ---

class AISuggestionBase(BaseModel):
    type: str
    data: Dict[str, Any]
    reasoning: Optional[str] = None
    confidence: Optional[float] = None

class AISuggestionCreate(AISuggestionBase):
    input_hash: str

class AISuggestionResponse(AISuggestionBase):
    id: UUID
    created_at: datetime
    expires_at: Optional[datetime]

    model_config = {"from_attributes": True}

# --- Pyramid Suggestion Schemas ---

class PyramidNodeStructure(BaseModel):
    name: str
    description: Optional[str] = None
    children: List["PyramidNodeStructure"] = []

class PyramidSuggestRequest(BaseModel):
    name: str
    description: str

class PyramidSuggestResponse(BaseModel):
    suggestion_id: UUID
    structure: PyramidNodeStructure
    reasoning: Optional[str] = None
    confidence: Optional[float] = None

class PyramidConfirmRequest(BaseModel):
    suggestion_id: UUID
    modifications: Optional[PyramidNodeStructure] = None

# --- Source Analysis Schemas ---

class SourceAnalyzeRequest(BaseModel):
    url: str

class SourceAnalyzeResponse(BaseModel):
    title: str
    summary: str
    tags: List[str]
    suggested_node_id: Optional[UUID] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None

# --- Content Classification Schemas ---

class ContentClassificationRequest(BaseModel):
    content: str
    title: Optional[str] = None

class ContentClassificationResponse(BaseModel):
    suggested_node_id: Optional[UUID] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    tags: List[str] = []

# --- Node Impact Analysis Schemas ---

class NodeChangeImpactRequest(BaseModel):
    new_description: str

class NodeChangeImpactResponse(BaseModel):
    requires_reclassification: bool
    impact_score: float # 0-1
    affected_children_ids: List[UUID] = []
    reasoning: str

class NodePlacementResponse(BaseModel):
    best_parent_id: Optional[UUID] = None
    confidence: float
    reasoning: str
    alternative_parent_ids: List[UUID] = []
