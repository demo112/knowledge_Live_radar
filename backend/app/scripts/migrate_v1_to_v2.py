import asyncio
import logging
import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.pyramid import Pyramid, PyramidNode
from app.models.knowledge import KnowledgeCluster, KnowledgeNode, ClusterNodeMembership, KnowledgeNodeRelation
from app.models.content import ContentNodeRelation, ContentKnowledgeRelation
from app.models.source import SourceNodeRelation, SourceKnowledgeRelation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_pyramids(db: AsyncSession):
    logger.info("Starting migration from Pyramid to Knowledge Graph...")
    
    # Mappings to track old IDs to new IDs
    pyramid_to_cluster = {}
    node_to_knowledge = {}

    # 1. Migrate Pyramids to KnowledgeClusters
    result = await db.execute(select(Pyramid))
    pyramids = result.scalars().all()
    
    logger.info(f"Found {len(pyramids)} pyramids to migrate.")
    
    for pyramid in pyramids:
        logger.info(f"Migrating Pyramid: {pyramid.name}")
        cluster = KnowledgeCluster(
            id=uuid.uuid4(),
            name=pyramid.name,
            description=pyramid.description,
            cluster_type="manual",
            status="active",
            created_at=pyramid.created_at,
            updated_at=pyramid.updated_at
        )
        db.add(cluster)
        pyramid_to_cluster[pyramid.id] = cluster.id
        
        # 2. Migrate PyramidNodes to KnowledgeNodes
        node_result = await db.execute(select(PyramidNode).where(PyramidNode.pyramid_id == pyramid.id))
        nodes = node_result.scalars().all()
        
        logger.info(f"  - Found {len(nodes)} nodes in pyramid.")
        
        for node in nodes:
            k_node = KnowledgeNode(
                id=uuid.uuid4(),
                name=node.name,
                description=node.description,
                node_type="concept",
                status="active",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(k_node)
            node_to_knowledge[node.id] = k_node.id
            
            # Create Cluster Membership
            membership = ClusterNodeMembership(
                cluster_id=cluster.id,
                node_id=k_node.id,
                role="member",
                weight=1.0
            )
            db.add(membership)
    
    await db.flush() # Flush to get IDs if needed, though we generated UUIDs manually
    
    # 3. Create Relations (Structure)
    logger.info("Migrating node relations (structure)...")
    count_relations = 0
    
    # Fetch all nodes again to process relationships
    # We can use the previously fetched nodes if we kept them, but let's query broadly or just iterate if we had a big list.
    # To save memory, let's query all nodes that have a parent_id
    
    node_result = await db.execute(select(PyramidNode).where(PyramidNode.parent_id.isnot(None)))
    child_nodes = node_result.scalars().all()
    
    for node in child_nodes:
        if node.id in node_to_knowledge and node.parent_id in node_to_knowledge:
            # Parent -> Child relationship (is_part_of or contains)
            # In knowledge graph, usually we might want directed edges.
            # Let's say Parent -> Child is "contains" or Child -> Parent is "is_part_of".
            # Let's create Parent -> Child relation for hierarchy.
            
            relation = KnowledgeNodeRelation(
                id=uuid.uuid4(),
                source_node_id=node_to_knowledge[node.parent_id],
                target_node_id=node_to_knowledge[node.id],
                relation_type="contains", # Hierarchical containment
                weight=1.0,
                discovered_by="migration"
            )
            db.add(relation)
            count_relations += 1

    logger.info(f"Created {count_relations} structural relations.")
    
    # 4. Migrate Content Relations
    logger.info("Migrating content relations...")
    content_rels_result = await db.execute(select(ContentNodeRelation))
    content_rels = content_rels_result.scalars().all()
    
    count_content_rels = 0
    for rel in content_rels:
        if rel.node_id in node_to_knowledge:
            # Check if exists to avoid duplicates if run multiple times (though we assume fresh run)
            # For simplicity, we just add.
            k_rel = ContentKnowledgeRelation(
                content_id=rel.content_id,
                node_id=node_to_knowledge[rel.node_id],
                confidence=rel.confidence,
                source=rel.source
            )
            db.add(k_rel)
            count_content_rels += 1
            
    logger.info(f"Migrated {count_content_rels} content relations.")
    
    # 5. Migrate Source Relations
    logger.info("Migrating source relations...")
    source_rels_result = await db.execute(select(SourceNodeRelation))
    source_rels = source_rels_result.scalars().all()
    
    count_source_rels = 0
    for rel in source_rels:
        if rel.node_id in node_to_knowledge:
            k_rel = SourceKnowledgeRelation(
                source_id=rel.source_id,
                node_id=node_to_knowledge[rel.node_id],
                weight=rel.weight
            )
            db.add(k_rel)
            count_source_rels += 1
            
    logger.info(f"Migrated {count_source_rels} source relations.")
    
    await db.commit()
    logger.info("Migration completed successfully!")

async def main():
    async with AsyncSessionLocal() as db:
        await migrate_pyramids(db)

if __name__ == "__main__":
    asyncio.run(main())
