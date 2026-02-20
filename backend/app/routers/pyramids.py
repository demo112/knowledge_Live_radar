from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.pyramid_service import PyramidService
from app.services.snapshot_service import SnapshotService
from app.services.health_evaluator import HealthEvaluator
from app.services.visualization_service import VisualizationService
from app.schemas.pyramid import PyramidCreate, PyramidUpdate, PyramidResponse, PyramidDetailResponse, PyramidNodeCreate, PyramidNodeResponse, NodeMergeRequest
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginatedData
from app.schemas.snapshot import SnapshotSummaryResponse, SnapshotResponse, SnapshotCreateRequest
from app.schemas.suggestion import SuggestionResponse, SuggestionRejectRequest

router = APIRouter(prefix="/pyramids", tags=["pyramids"])

from app.services.template_service import TemplateService

def get_service(db: AsyncSession = Depends(get_db)) -> PyramidService:
    return PyramidService(db)

def get_snapshot_service(db: AsyncSession = Depends(get_db)) -> SnapshotService:
    return SnapshotService(db)

def get_health_evaluator(db: AsyncSession = Depends(get_db)) -> HealthEvaluator:
    return HealthEvaluator(db)

def get_visualization_service(db: AsyncSession = Depends(get_db)) -> VisualizationService:
    return VisualizationService(db)

def get_template_service(service: PyramidService = Depends(get_service)) -> TemplateService:
    return TemplateService(service)

from app.core.ai.facade import ai_facade
from app.schemas.ai import PyramidSuggestRequest, PyramidSuggestResponse, PyramidConfirmRequest

@router.post("/suggest", response_model=SuccessResponse[PyramidSuggestResponse])
async def suggest_pyramid_structure(
    request: PyramidSuggestRequest
):
    """
    Step 1: Get AI suggestion for pyramid structure based on description.
    """
    suggestion = await ai_facade.suggest_pyramid_structure(request.name, request.description)
    return SuccessResponse(data=suggestion)

@router.post("/confirm", response_model=SuccessResponse[PyramidResponse], status_code=status.HTTP_201_CREATED)
async def confirm_pyramid_creation(
    request: PyramidConfirmRequest,
    service: PyramidService = Depends(get_service)
):
    """Confirm and create pyramid based on AI suggestion, with optional modifications."""
    pyramid = await service.create_from_suggestion(request.suggestion_id, request.modifications)
    return SuccessResponse(data=pyramid)

@router.get("/templates", response_model=SuccessResponse[List[dict]])
async def get_templates(
    service: TemplateService = Depends(get_template_service)
):
    """Get available pyramid templates"""
    templates = service.get_templates()
    return SuccessResponse(data=templates)

@router.post("/from-template/{template_id}", response_model=SuccessResponse[PyramidDetailResponse], status_code=status.HTTP_201_CREATED)
async def create_pyramid_from_template(
    template_id: str,
    name: str = None,
    service: TemplateService = Depends(get_template_service)
):
    """Create a new pyramid from a template"""
    pyramid = await service.create_from_template(template_id, name)
    # Re-fetch details to include nodes
    # Assuming service returns the pyramid object but nodes are lazy loaded or need separate fetch if not eagerly loaded in create_from_template return
    # The create_from_template returns the pyramid object.
    # We might want to return full details.
    return SuccessResponse(data=pyramid)

@router.post("/import", response_model=SuccessResponse[PyramidDetailResponse], status_code=status.HTTP_201_CREATED)
async def import_pyramid_template(
    template_data: dict,
    name: str = None,
    service: TemplateService = Depends(get_template_service)
):
    """Import a pyramid from a template JSON"""
    pyramid = await service.import_template(template_data, name)
    return SuccessResponse(data=pyramid)

@router.get("/{id}/export", response_model=SuccessResponse[dict])
async def export_pyramid_template(
    id: UUID,
    service: TemplateService = Depends(get_template_service)
):
    """Export a pyramid as a template JSON"""
    template = await service.export_template(id)
    return SuccessResponse(data=template)

@router.post("", response_model=SuccessResponse[PyramidResponse], status_code=status.HTTP_201_CREATED)
async def create_pyramid(
    schema: PyramidCreate,
    service: PyramidService = Depends(get_service)
):
    pyramid = await service.create_pyramid(schema)
    return SuccessResponse(data=pyramid)

@router.get("", response_model=PaginatedResponse[PyramidResponse])
async def get_pyramids(
    skip: int = 0,
    limit: int = 100,
    service: PyramidService = Depends(get_service)
):
    items = await service.get_all_pyramids(skip, limit)
    # Mock total count for now or implement count in repo
    total = len(items) 
    return PaginatedResponse(data=PaginatedData(items=items, total=total, page=skip//limit + 1 if limit else 1, page_size=limit))

@router.get("/{id}", response_model=SuccessResponse[PyramidDetailResponse])
async def get_pyramid(
    id: UUID,
    service: PyramidService = Depends(get_service)
):
    pyramid = await service.get_pyramid_details(id)
    return SuccessResponse(data=pyramid)

@router.post("/{pyramid_id}/snapshots", response_model=SuccessResponse[SnapshotResponse], status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    pyramid_id: UUID,
    request: SnapshotCreateRequest,
    service: SnapshotService = Depends(get_snapshot_service)
):
    """Create a new snapshot for a pyramid"""
    snapshot = await service.create_snapshot(pyramid_id, request.reason)
    return SuccessResponse(data=snapshot)

@router.get("/{pyramid_id}/snapshots", response_model=PaginatedResponse[SnapshotSummaryResponse])
async def get_snapshots(
    pyramid_id: UUID,
    skip: int = 0,
    limit: int = 20,
    service: SnapshotService = Depends(get_snapshot_service)
):
    """Get all snapshots for a pyramid"""
    snapshots = await service.get_snapshots_by_pyramid(pyramid_id, skip, limit)
    # Note: total count is not implemented in service yet, using len(snapshots) as placeholder
    return PaginatedResponse(
        data=PaginatedData(
            items=snapshots, 
            total=len(snapshots), 
            page=skip//limit + 1 if limit else 1, 
            page_size=limit
        )
    )

@router.get("/{pyramid_id}/snapshots/{snapshot_id}", response_model=SuccessResponse[SnapshotResponse])
async def get_snapshot(
    pyramid_id: UUID,
    snapshot_id: UUID,
    service: SnapshotService = Depends(get_snapshot_service)
):
    """Get snapshot details"""
    snapshot = await service.get_snapshot_by_id(snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    if snapshot.pyramid_id != pyramid_id:
        raise HTTPException(status_code=400, detail="Snapshot does not belong to this pyramid")
    return SuccessResponse(data=snapshot)

@router.post("/{pyramid_id}/rollback/{snapshot_id}", response_model=SuccessResponse[bool])
async def rollback_snapshot(
    pyramid_id: UUID,
    snapshot_id: UUID,
    service: SnapshotService = Depends(get_snapshot_service)
):
    """Rollback pyramid to a snapshot"""
    # Verify snapshot belongs to pyramid
    snapshot = await service.get_snapshot_by_id(snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    if snapshot.pyramid_id != pyramid_id:
        raise HTTPException(status_code=400, detail="Snapshot does not belong to this pyramid")
        
    success = await service.rollback(snapshot_id)
    if not success:
        raise HTTPException(status_code=500, detail="Rollback failed")
        
    return SuccessResponse(data=True)
@router.put("/{id}", response_model=SuccessResponse[PyramidResponse])
async def update_pyramid(
    id: UUID,
    schema: PyramidUpdate,
    service: PyramidService = Depends(get_service)
):
    pyramid = await service.update_pyramid(id, schema)
    return SuccessResponse(data=pyramid)

@router.delete("/{id}", response_model=SuccessResponse[PyramidResponse])
async def delete_pyramid(
    id: UUID,
    service: PyramidService = Depends(get_service)
):
    pyramid = await service.delete_pyramid(id)
    return SuccessResponse(data=pyramid)

@router.get("/{id}/health", response_model=SuccessResponse[dict])
async def get_pyramid_health(
    id: UUID,
    evaluator: HealthEvaluator = Depends(get_health_evaluator)
):
    result = await evaluator.evaluate_pyramid(id)
    return SuccessResponse(data=result)

@router.post("/{id}/analyze", response_model=SuccessResponse[dict])
async def analyze_pyramid(
    id: UUID,
    mode: str = "health",
    service: PyramidService = Depends(get_service),
    evaluator: HealthEvaluator = Depends(get_health_evaluator)
):
    """
    Trigger AI analysis for pyramid.
    
    Args:
        mode: Analysis mode. "health" (default), "structure", or "all".
    """
    result = {}
    
    if mode in ["health", "all"]:
        result["health"] = await evaluator.analyze_with_ai(id)
        
    if mode in ["structure", "all"]:
        suggestions = await service.analyze_structure(id)
        # Return summary of generated suggestions
        result["structure"] = {
            "generated_count": len(suggestions),
            "suggestion_ids": [s.id for s in suggestions] if suggestions else []
        }
        
    return SuccessResponse(data=result)

@router.get("/{id}/suggestions", response_model=SuccessResponse[List[SuggestionResponse]])
async def get_suggestions(
    id: UUID,
    service: PyramidService = Depends(get_service)
):
    """Get pending optimization suggestions"""
    suggestions = await service.get_optimization_suggestions(id)
    return SuccessResponse(data=suggestions)

@router.post("/{id}/suggestions/{suggestion_id}/apply", response_model=SuccessResponse[dict])
async def apply_suggestion(
    id: UUID,
    suggestion_id: UUID,
    service: PyramidService = Depends(get_service)
):
    """Apply an optimization suggestion"""
    # Verify pyramid ownership logic could be added here if needed
    result = await service.apply_suggestion(suggestion_id)
    return SuccessResponse(data=result)

@router.post("/{id}/suggestions/{suggestion_id}/reject", response_model=SuccessResponse[dict])
async def reject_suggestion(
    id: UUID,
    suggestion_id: UUID,
    request: SuggestionRejectRequest,
    service: PyramidService = Depends(get_service)
):
    """Reject an optimization suggestion"""
    result = await service.reject_suggestion(suggestion_id, request.reason)
    return SuccessResponse(data=result)

@router.get("/{id}/visualization", response_model=SuccessResponse[dict])
async def get_pyramid_visualization(
    id: UUID,
    viz_service: VisualizationService = Depends(get_visualization_service)
):
    result = await viz_service.get_react_flow_data(id)
    return SuccessResponse(data=result)

@router.post("/{id}/merge-nodes", response_model=SuccessResponse[PyramidNodeResponse])
async def merge_nodes(
    id: UUID,
    schema: NodeMergeRequest,
    service: PyramidService = Depends(get_service)
):
    result = await service.merge_nodes(id, schema)
    return SuccessResponse(data=result)

@router.post("/{id}/nodes", response_model=SuccessResponse[PyramidNodeResponse], status_code=status.HTTP_201_CREATED)
async def add_node(
    id: UUID,
    schema: PyramidNodeCreate,
    service: PyramidService = Depends(get_service)
):
    node = await service.add_node(id, schema)
    return SuccessResponse(data=node)
