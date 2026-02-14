from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceTemplateConfigField(BaseModel):
    name: str
    label: str
    type: str  # text, number, boolean, select
    required: bool = True
    default: Optional[Any] = None
    options: Optional[List[Dict[str, str]]] = None  # List of {label: "X", value: "Y"}
    description: Optional[str] = None

class SourceTemplate(BaseModel):
    id: str
    name: str
    description: str
    source_type: str  # RSS, API, WEB
    config_schema: List[SourceTemplateConfigField]
    default_config: Dict[str, Any]
