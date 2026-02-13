import asyncio
import sys
import os
import uuid
import logging

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.pyramid import Pyramid, PyramidNode
from app.models.node_relation import NodeRelation  # Import this to register with SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    async with AsyncSessionLocal() as session:
        try:
            logger.info("Starting data seeding...")
            
            # Check if demo pyramid already exists
            # (In a real scenario we might check by name, but here we just create a new one)
            
            # 1. Create Pyramid
            pyramid_id = uuid.uuid4()
            pyramid = Pyramid(
                id=pyramid_id,
                name="AI 知识体系 (Demo)",
                description="自动生成的演示金字塔，用于展示系统功能。"
            )
            session.add(pyramid)
            logger.info(f"Created Pyramid: {pyramid.name}")

            # 2. Create Root Node (Level 0)
            root_id = uuid.uuid4()
            root_node = PyramidNode(
                id=root_id,
                pyramid_id=pyramid_id,
                parent_id=None,
                name="人工智能",
                description="Artificial Intelligence",
                level=0,
                path="/",
                status="completed"
            )
            session.add(root_node)
            logger.info(f"Created Root Node: {root_node.name}")

            # 3. Create Level 1 Nodes
            l1_nodes_data = [
                ("机器学习", "Machine Learning"),
                ("深度学习", "Deep Learning"),
                ("自然语言处理", "Natural Language Processing")
            ]
            
            l1_nodes = []
            for name, desc in l1_nodes_data:
                node_id = uuid.uuid4()
                node = PyramidNode(
                    id=node_id,
                    pyramid_id=pyramid_id,
                    parent_id=root_id,
                    name=name,
                    description=desc,
                    level=1,
                    path=f"/{root_id}/",
                    status="completed"
                )
                session.add(node)
                l1_nodes.append(node)
                logger.info(f"Created L1 Node: {node.name}")

            # 4. Create Level 2 Nodes (Attached to specific L1 nodes)
            # Attach to 机器学习
            ml_node = l1_nodes[0]
            l2_ml_data = ["监督学习", "无监督学习", "强化学习"]
            for name in l2_ml_data:
                node_id = uuid.uuid4()
                node = PyramidNode(
                    id=node_id,
                    pyramid_id=pyramid_id,
                    parent_id=ml_node.id,
                    name=name,
                    description=f"{ml_node.name} sub-field",
                    level=2,
                    path=f"{ml_node.path}{ml_node.id}/",
                    status="completed"
                )
                session.add(node)

            # Attach to 深度学习
            dl_node = l1_nodes[1]
            l2_dl_data = ["卷积神经网络 (CNN)", "循环神经网络 (RNN)", "Transformer"]
            for name in l2_dl_data:
                node_id = uuid.uuid4()
                node = PyramidNode(
                    id=node_id,
                    pyramid_id=pyramid_id,
                    parent_id=dl_node.id,
                    name=name,
                    description=f"{dl_node.name} architecture",
                    level=2,
                    path=f"{dl_node.path}{dl_node.id}/",
                    status="completed"
                )
                session.add(node)
                
                # Add L3 for Transformer
                if name == "Transformer":
                    l3_data = ["BERT", "GPT", "T5"]
                    for l3_name in l3_data:
                        l3_id = uuid.uuid4()
                        l3_node = PyramidNode(
                            id=l3_id,
                            pyramid_id=pyramid_id,
                            parent_id=node_id,
                            name=l3_name,
                            description="Transformer model",
                            level=3,
                            path=f"{node.path}{node.id}/",
                            status="completed"
                        )
                        session.add(l3_node)

            # Attach to NLP
            nlp_node = l1_nodes[2]
            l2_nlp_data = ["大语言模型 (LLM)", "文本生成", "机器翻译"]
            for name in l2_nlp_data:
                node_id = uuid.uuid4()
                node = PyramidNode(
                    id=node_id,
                    pyramid_id=pyramid_id,
                    parent_id=nlp_node.id,
                    name=name,
                    description=f"{nlp_node.name} task",
                    level=2,
                    path=f"{nlp_node.path}{nlp_node.id}/",
                    status="completed"
                )
                session.add(node)

            await session.commit()
            logger.info("Data seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_data())
