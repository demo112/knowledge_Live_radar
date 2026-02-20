import asyncio
import sys
import os
from uuid import uuid4

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.models.content import ContentItem

async def seed():
    print("Starting content seed process...")
    async with AsyncSessionLocal() as session:
        # Create some content items
        contents = [
            ContentItem(
                title="Understanding AI Model Evaluation",
                url="https://example.com/ai-eval",
                summary="A deep dive into how large language models are evaluated using benchmarks like MMLU and GSM8K.",
                content_text="Full text content here...",
                concepts=["Model Evaluation", "Benchmarks", "LLM"],
                status="PROCESSED",
                ai_processed=True
            ),
            ContentItem(
                title="Red Teaming for Safety",
                url="https://example.com/red-teaming",
                summary="Exploring the importance of red teaming in ensuring AI safety and alignment.",
                content_text="Full text content here...",
                concepts=["Red Teaming", "Safety", "Alignment"],
                status="PROCESSED",
                ai_processed=True
            ),
            ContentItem(
                title="Integration Testing in ML Systems",
                url="https://example.com/integration-testing",
                summary="Best practices for integration testing in machine learning pipelines.",
                content_text="Full text content here...",
                concepts=["Integration Tests", "System Testing", "MLOps"],
                status="PROCESSED",
                ai_processed=True
            )
        ]
        
        for content in contents:
            session.add(content)
        
        await session.commit()
        print(f"Seeded {len(contents)} content items.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())
