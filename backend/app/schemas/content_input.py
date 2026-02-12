from pydantic import BaseModel
from typing import Optional

class UrlInput(BaseModel):
    url: str
    submitter_id: Optional[str] = None

class TextInput(BaseModel):
    text: str
    title: str = "Untitled Note"
    submitter_id: Optional[str] = None

class AnalysisRequest(BaseModel):
    pyramid_id: str
