import uuid
from uuid import UUID
from typing import List, Optional, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.pyramid import PyramidRepository, PyramidNodeRepository
from app.schemas.pyramid import PyramidCreate, PyramidUpdate, PyramidNodeCreate, PyramidNodeUpdate

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
        if not pyramid:
            raise HTTPException(status_code=404, detail="Pyramid not found")
        return pyramid

    async def get_pyramid_details(self, id: UUID) -> Any:
        pyramid = await self.pyramid_repo.get_with_nodes(id)
        if not pyramid:
            raise HTTPException(status_code=404, detail="Pyramid not found")
        return pyramid

    async def get_all_pyramids(self, skip: int = 0, limit: int = 100) -> List[Any]:
        return await self.pyramid_repo.get_all(skip, limit)

    async def update_pyramid(self, id: UUID, schema: PyramidUpdate) -> Any:
        pyramid = await self.get_pyramid(id)
        return await self.pyramid_repo.update(pyramid, schema.model_dump(exclude_unset=True))

    async def delete_pyramid(self, id: UUID) -> Any:
        pyramid = await self.get_pyramid(id)
        return await self.pyramid_repo.delete(id)

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
        if not node:
             raise HTTPException(status_code=404, detail="Node not found")
        return node

    async def update_node(self, node_id: UUID, schema: PyramidNodeUpdate) -> Any:
        node = await self.get_node(node_id)
        return await self.node_repo.update(node, schema.model_dump(exclude_unset=True))

    async def delete_node(self, node_id: UUID) -> Any:
        node = await self.get_node(node_id)
        return await self.node_repo.delete(node_id)

    async def move_node(self, node_id: UUID, new_parent_id: Optional[UUID], new_sort_order: Optional[int]) -> Any:
        """
        Move a node to a new parent and/or update its sort order.
        """
        node = await self.get_node(node_id)
        
        # 1. Update Sort Order if provided
        if new_sort_order is not None:
            node.sort_order = new_sort_order
            
        # 2. Handle Parent Change
        if new_parent_id is not None or (new_parent_id is None and node.parent_id is not None):
            # If new_parent_id is explicitly passed (even if same as current), we process it.
            # But usually we check if it's different.
            if new_parent_id != node.parent_id:
                old_path = node.path
                
                if new_parent_id is None:
                    # Move to root
                    node.parent_id = None
                    node.level = 0
                    node.path = "/"
                else:
                    # Move to new parent
                    new_parent = await self.get_node(new_parent_id)
                    if new_parent.pyramid_id != node.pyramid_id:
                        raise HTTPException(status_code=400, detail="Cannot move node to a different pyramid")
                    
                    # Circular dependency check: Is new_parent a descendant of node?
                    # Descendant path starts with node.path + node.id
                    node_path_prefix = f"{node.path}{node.id}/"
                    if new_parent.path.startswith(node_path_prefix) or new_parent.id == node.id:
                        raise HTTPException(status_code=400, detail="Cannot move node to its own descendant")
                        
                    node.parent_id = new_parent.id
                    node.level = new_parent.level + 1
                    node.path = f"{new_parent.path}{new_parent.id}/"
                
                # Update descendants
                # We need to find all nodes starting with old_path + node.id
                # and replace that prefix with new node.path + node.id
                # This requires repository support or direct SQL execution.
                # For simplicity here, assuming repository can handle or we do it here.
                # Actually, implementing recursive update in service is cleaner but slower for big trees.
                # Let's try to do it via repository method if possible, or direct logic here.
                
                # We need a method to update descendants paths.
                await self.node_repo.update_descendants_path(
                    pyramid_id=node.pyramid_id,
                    old_prefix=f"{old_path}{node.id}/",
                    new_prefix=f"{node.path}{node.id}/",
                    level_diff=node.level - (len(old_path.strip("/").split("/")) if old_path != "/" else 0) # Approximation, safer to calculate diff
                )

        await self.db.commit()
        await self.db.refresh(node)
        return node

