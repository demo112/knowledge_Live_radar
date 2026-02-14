import logging
import json
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.content import ContentItem
from app.services.ai_service import ai_service
from app.services.evolution_engine import EvolutionEngine
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class BatchClassificationService:
    def __init__(self):
        pass

    async def start_batch_classification(self, batch_size: int = 10, background_tasks = None):
        """
        Start batch classification. If background_tasks is provided, run in background.
        Otherwise run immediately (blocking).
        """
        if background_tasks:
            background_tasks.add_task(self._execute_batch_classification, batch_size)
            return {"status": "started", "message": f"Batch classification started for {batch_size} items"}
        else:
            return await self._execute_batch_classification(batch_size)

    async def _execute_batch_classification(self, batch_size: int = 10):
        logger.info(f"Starting batch classification for {batch_size} items")
        
        # Phase 1: Fetch items that need processing
        # We target items that are NOT ai_processed yet
        items_data = []
        async with AsyncSessionLocal() as db:
            stmt = select(ContentItem).where(
                ContentItem.ai_processed == False
            ).limit(batch_size)
            result = await db.execute(stmt)
            items = result.scalars().all()
            
            if not items:
                logger.info("No unclassified items found.")
                return {"processed_count": 0, "success_count": 0}
            
            logger.info(f"Found {len(items)} items to process.")
            
            # Detach items or copy data needed for AI to avoid session issues
            for item in items:
                items_data.append({
                    "id": item.id,
                    "title": item.title,
                    "url": item.url,
                    "content_text": item.content_text or ""
                })
        
        # Phase 2: AI Processing (Enrichment) - Concurrent
        # Process in chunks to avoid hitting rate limits if batch_size is large
        # For now, we assume batch_size is small (e.g., 10)
        tasks = [self._process_single_item_ai(data) for data in items_data]
        ai_results = await asyncio.gather(*tasks)
        
        # Phase 3: Update DB & Link to Nodes
        success_count = 0
        
        # We process updates sequentially to ensure stability
        async with AsyncSessionLocal() as db:
            evolution_engine = EvolutionEngine(db)
            
            for res in ai_results:
                if res and res["success"]:
                    try:
                        # Fetch item again in current session
                        stmt = select(ContentItem).where(ContentItem.id == res["id"])
                        result = await db.execute(stmt)
                        item = result.scalar_one_or_none()
                        
                        if item:
                            # 1. Apply Enrichment
                            item.tags = res["tags"]
                            item.concepts = res["concepts"]
                            if res["summary"]:
                                item.summary = res["summary"]
                            item.ai_processed = True
                            
                            db.add(item)
                            # Commit enrichment first
                            await db.commit()
                            await db.refresh(item)
                            
                            # 2. Apply Linking (EvolutionEngine)
                            # This will use the newly added tags/concepts/summary
                            await evolution_engine.auto_classify_content(item)
                            
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to update/link item {res['id']}: {e}")
                        await db.rollback()
            
        logger.info(f"Batch classification completed. Success: {success_count}/{len(items_data)}")
        return {"processed_count": len(items_data), "success_count": success_count}

    async def _process_single_item_ai(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call LLM to generate summary, tags, and concepts.
        """
        try:
            prompt = self._construct_classification_prompt(item_data)
            messages = [
                {"role": "system", "content": "You are a helpful assistant that categorizes content."},
                {"role": "user", "content": prompt}
            ]
            
            response_text = await ai_service.chat_completion(messages)
            
            if not response_text:
                logger.warning(f"AI returned empty response for item {item_data['id']}")
                return {"id": item_data["id"], "success": False}
                
            # Basic cleanup
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            try:
                data = json.loads(clean_text)
            except json.JSONDecodeError:
                # Try to extract JSON if it's wrapped in text
                start = clean_text.find("{")
                end = clean_text.rfind("}")
                if start != -1 and end != -1:
                    try:
                        data = json.loads(clean_text[start:end+1])
                    except:
                        logger.error(f"Failed to parse AI response for item {item_data['id']}")
                        return {"id": item_data["id"], "success": False}
                else:
                    logger.error(f"Failed to parse AI response for item {item_data['id']}")
                    return {"id": item_data["id"], "success": False}
            
            return {
                "id": item_data["id"],
                "success": True,
                "tags": data.get("tags", []),
                "concepts": data.get("concepts", []),
                "summary": data.get("summary", "")
            }
        except Exception as e:
            logger.error(f"AI processing failed for item {item_data['id']}: {e}")
            return {"id": item_data["id"], "success": False}

    def _construct_classification_prompt(self, item_data: Dict[str, Any]) -> str:
        content_preview = (item_data.get("content_text") or "")[:1000]
        return f"""
        Analyze the following content and provide:
        1. A list of relevant tags (max 5).
        2. A list of key concepts (max 5).
        3. A brief summary (1-2 sentences).

        Return ONLY a JSON object with keys: "tags", "concepts", "summary".

        Title: {item_data.get("title")}
        URL: {item_data.get("url")}
        Content Preview:
        {content_preview}
        """

batch_classification_service = BatchClassificationService()
