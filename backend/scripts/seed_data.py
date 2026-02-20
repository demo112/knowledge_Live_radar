import asyncio
import sys
import os
import uuid
import logging
from sqlalchemy.future import select

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.pyramid import Pyramid, PyramidNode
from app.models.node_relation import NodeRelation  # Import this to register with SQLAlchemy
from app.data.seed_content_2026 import SEEDED_PYRAMIDS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_node_recursive(session, pyramid_id, parent_node, node_data, level=0):
    """
    Recursively create pyramid nodes.
    
    :param session: Database session
    :param pyramid_id: ID of the pyramid
    :param parent_node: Parent node object (None for root)
    :param node_data: Dictionary containing node data
    :param level: Current level (0 for root)
    """
    node_id = uuid.uuid4()
    
    # Calculate path
    if parent_node:
        path = f"{parent_node.path}{parent_node.id}/"
        parent_id = parent_node.id
    else:
        path = "/"
        parent_id = None
        
    node = PyramidNode(
        id=node_id,
        pyramid_id=pyramid_id,
        parent_id=parent_id,
        name=node_data["name"],
        description=node_data.get("description", ""),
        level=level,
        path=path,
        status="completed"  # Default status for seed data
    )
    session.add(node)
    logger.info(f"{'  ' * level}Created Node: {node.name} (Level {level})")
    
    # Recursively create children
    if "children" in node_data and node_data["children"]:
        for child_data in node_data["children"]:
            await create_node_recursive(session, pyramid_id, node, child_data, level + 1)

async def seed_data():
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Starting data seeding...")
            
            # Process each pyramid defined in SEEDED_PYRAMIDS
            for pyramid_data in SEEDED_PYRAMIDS:
                # Idempotency check: Skip if pyramid with same name exists
                existing_pyramid = await session.execute(
                    select(Pyramid).where(Pyramid.name == pyramid_data["name"])
                )
                if existing_pyramid.scalars().first():
                    logger.warning(f"Skipping existing pyramid: {pyramid_data['name']}")
                    continue
                
                # Create Pyramid
                pyramid_id = uuid.uuid4()
                pyramid = Pyramid(
                    id=pyramid_id,
                    name=pyramid_data["name"],
                    description=pyramid_data.get("description", "")
                )
                session.add(pyramid)
                logger.info(f"Created Pyramid: {pyramid.name}")
                
                # Create Nodes (Start from Level 0 children as root nodes)
                # Note: The data structure has children under pyramid, so these are Level 0 nodes (Roots)
                # However, usually a pyramid has ONE root or multiple roots. 
                # Our data structure implies multiple top-level categories.
                # Let's treat the top-level children as Level 0 nodes (multiple roots allowed).
                
                if "children" in pyramid_data:
                    for root_data in pyramid_data["children"]:
                        await create_node_recursive(session, pyramid_id, None, root_data, level=0)
            
            await session.commit()
            logger.info("Data seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_data())
