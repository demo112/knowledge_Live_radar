import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.pyramid_service import PyramidService
from app.schemas.pyramid import PyramidCreate, PyramidNodeCreate

async def main():
    async with AsyncSessionLocal() as session:
        service = PyramidService(session)
        
        # 1. Create Pyramid
        print("Creating Pyramid...")
        pyramid_in = PyramidCreate(name="Test Pyramid", description="For verification")
        pyramid = await service.create_pyramid(pyramid_in)
        print(f"Pyramid Created: {pyramid.id} - {pyramid.name}")

        # 2. Add Root Node
        print("Adding Root Node...")
        root_node_in = PyramidNodeCreate(name="Root Node", description="Top level")
        root_node = await service.add_node(pyramid.id, root_node_in)
        print(f"Root Node Created: {root_node.id} - Path: {root_node.path}")

        # 3. Add Child Node
        print("Adding Child Node...")
        child_node_in = PyramidNodeCreate(name="Child Node", parent_id=root_node.id)
        child_node = await service.add_node(pyramid.id, child_node_in)
        print(f"Child Node Created: {child_node.id} - Path: {child_node.path} - Level: {child_node.level}")

        # 4. Verify Hierarchy
        print("Verifying Hierarchy...")
        details = await service.get_pyramid_details(pyramid.id)
        print(f"Pyramid has {len(details.nodes)} nodes.")
        for node in details.nodes:
            print(f" - {node.name} ({node.path})")

if __name__ == "__main__":
    asyncio.run(main())
