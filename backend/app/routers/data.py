from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from pydantic import BaseModel

from app.services.data import export_service, import_service, ExportOptions

router = APIRouter(prefix="/data", tags=["data"])

class ExportRequest(BaseModel):
    include_content: bool = False
    include_sources: bool = False
    pyramid_ids: Optional[List[str]] = None

@router.post("/export")
async def export_data(req: ExportRequest):
    options = ExportOptions(
        include_content=req.include_content,
        include_sources=req.include_sources,
        pyramid_ids=req.pyramid_ids
    )
    # Synchronous for now, ideally async task returning ID
    data = await export_service.export_data(options)
    return data

@router.post("/import")
async def import_data(file: UploadFile = File(...)):
    import json
    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {"success": False, "errors": ["Invalid JSON"]}
        
    # Validate
    valid, errors = await import_service.validate_import_data(data)
    if not valid:
        return {"success": False, "errors": errors}
        
    # Detect conflicts
    conflicts = await import_service.detect_conflicts(data)
    if conflicts:
        return {
            "success": False, 
            "conflicts": [c.__dict__ for c in conflicts],
            "message": "Conflicts detected. Please resolve."
        }
        
    # Import directly if no conflicts? Or require confirmation?
    # Here importing directly if no conflicts
    result = await import_service.import_data(data)
    return result.__dict__

@router.post("/import/confirm")
async def import_data_confirm(data: Dict[str, Any], conflict_resolutions: Dict[str, str]):
    # This endpoint receives the data again (heavy) or better, we store uploaded file in temp.
    # For simplicity, assuming client sends data again with resolutions.
    result = await import_service.import_data(data, conflict_resolutions)
    return result.__dict__
