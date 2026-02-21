from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.knowledge_service import KnowledgeService
from app.schemas.knowledge import (
    KnowledgeNodeCreate, KnowledgeNodeUpdate, KnowledgeNodeResponse,
    KnowledgeClusterCreate, KnowledgeClusterUpdate, KnowledgeClusterResponse,
    KnowledgeNodeRelationCreate, KnowledgeNodeRelationResponse,
    ClusterNodeMembershipCreate, ClusterNodeMembershipResponse,
    KnowledgeGraphResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

def get_service(db: AsyncSession = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)

# Node Endpoints
@router.post("/nodes", response_model=SuccessResponse[KnowledgeNodeResponse], status_code=status.HTTP_201_CREATED)
async def create_node(
    data: KnowledgeNodeCreate,
    service: KnowledgeService = Depends(get_service)
):
    node = await service.create_node(data)
    return SuccessResponse(data=node)

@router.get("/nodes", response_model=SuccessResponse[List[KnowledgeNodeResponse]])
async def list_nodes(
    skip: int = 0,
    limit: int = 100,
    service: KnowledgeService = Depends(get_service)
):
    nodes = await service.list_nodes(skip=skip, limit=limit)
    return SuccessResponse(data=nodes)

@router.get("/nodes/{id}", response_model=SuccessResponse[KnowledgeNodeResponse])
async def get_node(
    id: UUID,
    service: KnowledgeService = Depends(get_service)
):
    node = await service.get_node(id)
    return SuccessResponse(data=node)

@router.put("/nodes/{id}", response_model=SuccessResponse[KnowledgeNodeResponse])
async def update_node(
    id: UUID,
    data: KnowledgeNodeUpdate,
    service: KnowledgeService = Depends(get_service)
):
    node = await service.update_node(id, data)
    return SuccessResponse(data=node)

@router.post("/nodes/{id}/cognitive-model", response_model=SuccessResponse[KnowledgeNodeResponse])
async def generate_cognitive_model(
    id: UUID,
    service: KnowledgeService = Depends(get_service)
):
    """
    Generate a cognitive model for the node using AI.
    """
    node = await service.generate_cognitive_model_for_node(id)
    return SuccessResponse(data=node)

@router.post("/nodes/{id}/evolve-model", response_model=SuccessResponse[KnowledgeNodeResponse])
async def evolve_node_model(
    id: UUID,
    service: KnowledgeService = Depends(get_service)
):
    """
    Task 2.3: Evolve the cognitive model based on recently linked content.
    """
    node = await service.evolve_node_model(id)
    return SuccessResponse(data=node)

@router.delete("/nodes/{id}", response_model=SuccessResponse[bool])
async def delete_node(
    id: UUID,
    service: KnowledgeService = Depends(get_service)
):
    result = await service.delete_node(id)
    return SuccessResponse(data=result)

@router.get("/nodes/{id}/graph", response_model=SuccessResponse[KnowledgeGraphResponse])
async def get_knowledge_graph(
    id: UUID,
    depth: int = Query(2, ge=1, le=5),
    relation_type: Optional[str] = None,
    service: KnowledgeService = Depends(get_service)
):
    """
    Task 3.2: Get the knowledge graph structure (nodes and edges) starting from the given node up to the specified depth.
    """
    graph_data = await service.get_knowledge_graph(id, depth, relation_type)
    return SuccessResponse(data=graph_data)

# Cluster Endpoints
@router.post("/clusters", response_model=SuccessResponse[KnowledgeClusterResponse], status_code=status.HTTP_201_CREATED)
async def create_cluster(
    data: KnowledgeClusterCreate,
    service: KnowledgeService = Depends(get_service)
):
    cluster = await service.create_cluster(data)
    return SuccessResponse(data=cluster)

@router.get("/clusters", response_model=SuccessResponse[List[KnowledgeClusterResponse]])
async def list_clusters(
    skip: int = 0,
    limit: int = 100,
    service: KnowledgeService = Depends(get_service)
):
    clusters = await service.list_clusters(skip=skip, limit=limit)
    return SuccessResponse(data=clusters)

@router.get("/clusters/{id}", response_model=SuccessResponse[KnowledgeClusterResponse])
async def get_cluster(
    id: UUID,
    service: KnowledgeService = Depends(get_service)
):
    cluster = await service.get_cluster(id)
    return SuccessResponse(data=cluster)

@router.put("/clusters/{id}", response_model=SuccessResponse[KnowledgeClusterResponse])
async def update_cluster(
    id: UUID,
    data: KnowledgeClusterUpdate,
    service: KnowledgeService = Depends(get_service)
):
    cluster = await service.update_cluster(id, data)
    return SuccessResponse(data=cluster)

@router.delete("/clusters/{id}", response_model=SuccessResponse[bool])
async def delete_cluster(
    id: UUID,
    service: KnowledgeService = Depends(get_service)
):
    result = await service.delete_cluster(id)
    return SuccessResponse(data=result)

# Membership Endpoints
@router.post("/clusters/{cluster_id}/nodes", response_model=SuccessResponse[ClusterNodeMembershipResponse])
async def add_node_to_cluster(
    cluster_id: UUID,
    data: ClusterNodeMembershipCreate,
    service: KnowledgeService = Depends(get_service)
):
    membership = await service.add_node_to_cluster(cluster_id, data)
    return SuccessResponse(data=membership)

@router.delete("/clusters/{cluster_id}/nodes/{node_id}", response_model=SuccessResponse[bool])
async def remove_node_from_cluster(
    cluster_id: UUID,
    node_id: UUID,
    service: KnowledgeService = Depends(get_service)
):
    result = await service.remove_node_from_cluster(cluster_id, node_id)
    return SuccessResponse(data=result)

# Relation Endpoints
@router.post("/nodes/{source_id}/relations", response_model=SuccessResponse[KnowledgeNodeRelationResponse])
async def create_relation(
    source_id: UUID,
    data: KnowledgeNodeRelationCreate,
    service: KnowledgeService = Depends(get_service)
):
    relation = await service.create_relation(source_id, data)
    return SuccessResponse(data=relation)

@router.delete("/relations/{id}", response_model=SuccessResponse[bool])
async def delete_relation(
    id: UUID,
    service: KnowledgeService = Depends(get_service)
):
    result = await service.delete_relation(id)
    return SuccessResponse(data=result)
