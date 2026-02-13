import uuid
from uuid import UUID
from typing import List, Optional, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.pyramid import PyramidRepository, PyramidNodeRepository
from app.schemas.pyramid import PyramidCreate, PyramidUpdate, PyramidNodeCreate, PyramidNodeUpdate, NodeSplitRequest, NodeMergeRequest

class PyramidService:
    def __init__(self, db: AsyncSession):
        self.pyramid_repo = PyramidRepository(db)
        self.node_repo = PyramidNodeRepository(db)
        self.db = db

    # Pyramid Operations
    async def create_pyramid(self, schema: PyramidCreate) -> Any:
        return await self.pyramid_repo.create(schema.model_dump())

    async def get_pyramid(self, id: UUID) -> Any:
        pyramid = await self.pyramid_repo.get(id)
        if not pyramid or pyramid.is_deleted:
            raise HTTPException(status_code=404, detail="Pyramid not found")
        return pyramid

    async def get_pyramid_details(self, id: UUID) -> Any:
        pyramid = await self.pyramid_repo.get_with_nodes(id)
        if not pyramid or pyramid.is_deleted:
            raise HTTPException(status_code=404, detail="Pyramid not found")
        return pyramid

    async def get_all_pyramids(self, skip: int = 0, limit: int = 100) -> List[Any]:
        return await self.pyramid_repo.get_all(skip, limit)

    async def update_pyramid(self, id: UUID, schema: PyramidUpdate) -> Any:
        pyramid = await self.get_pyramid(id)
        return await self.pyramid_repo.update(pyramid, schema.model_dump(exclude_unset=True))

    async def calculate_health_score(self, pyramid_id: UUID) -> int:
        """
        Calculate health score for a pyramid.
        Score = (Completed Nodes / Total Nodes) * 100
        """
        pyramid = await self.get_pyramid_details(pyramid_id)
        if not pyramid or not pyramid.nodes:
            return 100
            
        total_nodes = len(pyramid.nodes)
        if total_nodes == 0:
            return 100
            
        completed_nodes = sum(1 for node in pyramid.nodes if node.status == "completed")
        
        return int((completed_nodes / total_nodes) * 100)

    async def delete_pyramid(self, id: UUID) -> Any:
        pyramid = await self.get_pyramid(id)
        # Soft delete nodes first
        await self.node_repo.soft_delete_by_pyramid(id)
        # Soft delete pyramid
        return await self.pyramid_repo.soft_delete(id)


    # Node Operations (Task 6)
    async def add_node(self, pyramid_id: UUID, schema: PyramidNodeCreate) -> Any:
        # Check pyramid exists
        await self.get_pyramid(pyramid_id)
        
        data = schema.model_dump()
        data["pyramid_id"] = pyramid_id
        
        # Generate ID explicitly to construct path
        new_id = uuid.uuid4()
        data["id"] = new_id
        
        if schema.parent_id:
            parent = await self.node_repo.get(schema.parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="Parent node not found")
            if parent.pyramid_id != pyramid_id:
                raise HTTPException(status_code=400, detail="Parent node belongs to different pyramid")
            
            data["level"] = parent.level + 1
            # Path format: /parent_path/parent_id/
            # Assuming root path is "/"
            if parent.path == "/":
                 data["path"] = f"/{parent.id}/"
            else:
                 data["path"] = f"{parent.path}{parent.id}/"
        else:
            data["level"] = 0
            data["path"] = "/" # Root node path convention

        return await self.node_repo.create(data)

    async def get_node(self, node_id: UUID) -> Any:
        node = await self.node_repo.get(node_id)
        if not node or node.is_deleted:
             raise HTTPException(status_code=404, detail="Node not found")
        return node

    async def delete_node(self, node_id: UUID) -> Any:
        node = await self.get_node(node_id)
        # Soft delete descendants
        await self.node_repo.soft_delete_descendants(node.pyramid_id, node.path)
        # Soft delete node
        return await self.node_repo.update(node, {"is_deleted": True})

    async def split_node(self, node_id: UUID, schema: NodeSplitRequest) -> List[Any]:
        node = await self.get_node(node_id)
        created_nodes = []
        for child_schema in schema.children:
            child_schema.parent_id = node.id
            new_node = await self.add_node(node.pyramid_id, child_schema)
            created_nodes.append(new_node)
        return created_nodes

    async def merge_nodes(self, pyramid_id: UUID, schema: NodeMergeRequest) -> Any:
        nodes = []
        for nid in schema.source_node_ids:
            node = await self.node_repo.get(nid)
            if not node or node.pyramid_id != pyramid_id or node.is_deleted:
                raise HTTPException(status_code=400, detail=f"Node {nid} invalid")
            nodes.append(node)
        
        if not nodes:
             raise HTTPException(status_code=400, detail="No nodes provided")

        first_node = nodes[0]
        new_node_data = PyramidNodeCreate(
            name=schema.new_node_name,
            description=schema.new_node_description,
            parent_id=first_node.parent_id
        )
        new_node = await self.add_node(pyramid_id, new_node_data)
        
        for node in nodes:
            children = await self.node_repo.get_children(node.id)
            for child in children:
                old_child_path = child.path
                new_child_path_prefix = f"{new_node.path}{child.id}/"
                level_diff = (new_node.level + 1) - child.level
                
                # Update child
                await self.node_repo.update(child, {
                    "parent_id": new_node.id,
                    "path": new_child_path_prefix,
                    "level": new_node.level + 1
                })
                
                # Update descendants
                await self.node_repo.update_descendants_path(
                    pyramid_id,
                    old_child_path,
                    new_child_path_prefix,
                    level_diff
                )
        
        for node in nodes:
             await self.node_repo.update(node, {"is_deleted": True})
             
        return new_node

    async def update_node(self, node_id: UUID, schema: PyramidNodeUpdate) -> Any:
        node = await self.get_node(node_id)
        return await self.node_repo.update(node, schema.model_dump(exclude_unset=True))

    async def delete_node(self, node_id: UUID) -> Any:
        node = await self.get_node(node_id)
        
        # Soft delete descendants
        # Path format for children: {node.path}{node.id}/
        if node.path == "/":
             child_path_prefix = f"/{node.id}/"
        else:
             child_path_prefix = f"{node.path}{node.id}/"
             
        await self.node_repo.soft_delete_descendants(node.pyramid_id, child_path_prefix)
        
        # Soft delete the node itself
        return await self.node_repo.soft_delete(node_id)

    async def move_node(self, node_id: UUID, new_parent_id: Optional[UUID] = None, new_sort_order: Optional[int] = None) -> Any:
        """
        Move a node to a new parent and/or update its sort order.
        """
        node = await self.get_node(node_id)
        
        # 1. Update Sort Order if provided
        if new_sort_order is not None:
            node.sort_order = new_sort_order
            
        # 2. Handle Parent Change
        if new_parent_id is not None and new_parent_id != node.parent_id:
            old_path = node.path
            old_level = node.level
            old_prefix = f"{old_path}{node.id}/" if old_path != "/" else f"/{node.id}/"

            if new_parent_id == node.id:
                 raise HTTPException(status_code=400, detail="Cannot move node to itself")

            new_parent = await self.get_node(new_parent_id)
            if new_parent.pyramid_id != node.pyramid_id:
                raise HTTPException(status_code=400, detail="Cannot move node to a different pyramid")
            
            # Circular dependency check: Is new_parent a descendant of node?
            # Descendant path starts with node.path + node.id
            if new_parent.path.startswith(old_prefix) or new_parent.id == node.id:
                raise HTTPException(status_code=400, detail="Cannot move node to its own descendant")
                
            # Update node
            node.parent_id = new_parent.id
            node.level = new_parent.level + 1
            node.path = f"{new_parent.path}{new_parent.id}/" if new_parent.path != "/" else f"/{new_parent.id}/"
            
            new_prefix = f"{node.path}{node.id}/"
            level_diff = node.level - old_level
            
            # Update descendants
            await self.node_repo.update_descendants_path(
                pyramid_id=node.pyramid_id,
                old_prefix=old_prefix,
                new_prefix=new_prefix,
                level_diff=level_diff
            )
        elif new_parent_id is None and node.parent_id is not None:
             # Move to root
             old_path = node.path
             old_level = node.level
             old_prefix = f"{old_path}{node.id}/" if old_path != "/" else f"/{node.id}/"

             node.parent_id = None
             node.level = 0
             node.path = "/"
             
             new_prefix = f"/{node.id}/"
             level_diff = node.level - old_level
             
             await self.node_repo.update_descendants_path(
                pyramid_id=node.pyramid_id,
                old_prefix=old_prefix,
                new_prefix=new_prefix,
                level_diff=level_diff
             )

        await self.db.commit()
        await self.db.refresh(node)
        return node

