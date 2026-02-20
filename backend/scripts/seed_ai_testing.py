import asyncio
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.models.pyramid import Pyramid, PyramidNode
from app.models.source import InformationSource
from sqlalchemy import select

async def seed():
    print("Starting seed process...")
    async with AsyncSessionLocal() as session:
        # Check if exists
        stmt = select(Pyramid).where(Pyramid.name == "AI Testing")
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            print("Pyramid 'AI Testing' already exists.")
        else:
            print("Creating Pyramid...")
            pyramid = Pyramid(name="AI Testing", description="Knowledge pyramid for AI Testing methodologies.")
            session.add(pyramid)
            await session.flush() # Get ID

            print(f"Created Pyramid: {pyramid.id}")

            # Nodes
            nodes_data = [
                {"name": "Model Evaluation", "level": 1, "children": [
                    {"name": "Benchmarks", "level": 2},
                    {"name": "Human Eval", "level": 2},
                    {"name": "Auto Eval", "level": 2}
                ]},
                {"name": "System Testing", "level": 1, "children": [
                    {"name": "Integration Tests", "level": 2},
                    {"name": "End-to-End Tests", "level": 2},
                    {"name": "Robustness", "level": 2}
                ]},
                {"name": "Safety & Alignment", "level": 1, "children": [
                    {"name": "Red Teaming", "level": 2},
                    {"name": "Jailbreak Testing", "level": 2}
                ]}
            ]

            for i, node_data in enumerate(nodes_data):
                parent_path = f"/{node_data['name']}"
                parent = PyramidNode(
                    pyramid_id=pyramid.id,
                    name=node_data["name"],
                    level=node_data["level"],
                    sort_order=i,
                    path=parent_path,
                    health_score=85 # Dummy score
                )
                session.add(parent)
                await session.flush()
                
                if "children" in node_data:
                    for j, child_data in enumerate(node_data["children"]):
                        child_path = f"{parent_path}/{child_data['name']}"
                        child = PyramidNode(
                            pyramid_id=pyramid.id,
                            parent_id=parent.id,
                            name=child_data["name"],
                            level=child_data["level"],
                            sort_order=j,
                            path=child_path,
                            health_score=90 # Dummy score
                        )
                        session.add(child)
            
            print("Pyramid and Nodes created.")

        # Source
        stmt_source = select(InformationSource).where(InformationSource.name == "AI Testing arXiv")
        result_source = await session.execute(stmt_source)
        existing_source = result_source.scalar_one_or_none()

        if existing_source:
             print("Source 'AI Testing arXiv' already exists.")
        else:
            print("Creating Information Source...")
            source = InformationSource(
                name="AI Testing arXiv",
                type="RSS",
                url="http://export.arxiv.org/rss/cs.SE",
                status="ACTIVE",
                check_interval=3600
            )
            session.add(source)
            print("Information Source created.")

        await session.commit()
        print("Seeding completed successfully.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())
