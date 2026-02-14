import logging
import json
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.content import ContentItem
from app.services.ai_service import ai_service
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
        async with AsyncSessionLocal() as db:
            try:
                # 1. Fetch unclassified items
                stmt = select(ContentItem).where(
                    ContentItem.ai_processed == False
                ).limit(batch_size)
                
                result = await db.execute(stmt)
                items = result.scalars().all()
                
                if not items:
                    logger.info("No unclassified items found.")
                    return {"processed_count": 0, "success_count": 0}
                
                logger.info(f"Found {len(items)} unclassified items. Processing...")
                
                # 2. Process items
                # We process them concurrently but with a limit to avoid overwhelming the AI service or DB
                # For now, let's just use asyncio.gather for the whole batch since batch_size is small (default 10)
                tasks = [self._classify_item(db, item) for item in items]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                success_count = 0
                for res in results:
                    if isinstance(res, Exception):
                        logger.error(f"Error classifying item: {res}")
                    elif res:
                        success_count += 1
                
                logger.info(f"Batch classification completed. Success: {success_count}/{len(items)}")
                return {"processed_count": len(items), "success_count": success_count}
            except Exception as e:
                logger.error(f"Error in batch classification execution: {e}")
                return {"processed_count": 0, "success_count": 0, "error": str(e)}

    async def _classify_item(self, db: AsyncSession, item: ContentItem) -> bool:
        try:
            # Construct prompt
            prompt = self._construct_classification_prompt(item)
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant that categorizes content."},
                {"role": "user", "content": prompt}
            ]
            
            # Call AI
            response_text = await ai_service.chat_completion(messages)
            
            if not response_text:
                logger.warning(f"AI returned empty response for item {item.id}")
                # We don't mark as processed so it can be retried later, 
                # or we could mark it with error status if we had one.
                return False
                
            # Parse response (expecting JSON)
            try:
                # Basic cleanup of markdown code blocks if present
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)
                
                tags = data.get("tags", [])
                concepts = data.get("concepts", [])
                summary = data.get("summary", "")
                
                # Update item
                # Since we are using asyncio.gather, multiple tasks might be trying to commit.
                # It's better to update the object and then commit individually or collect results and commit once.
                # However, with AsyncSession, we need to be careful about concurrency on the same session.
                # AsyncSession is NOT thread-safe/concurrency-safe for concurrent operations.
                # We should probably process items sequentially or use separate sessions if we want true parallelism.
                # But here we passed `db` which is a single session.
                
                # CRITICAL FIX: To avoid "RuntimeError: Method 'commit' can't be called ..."
                # we should NOT share the session for concurrent DB writes if we can't ensure serialization.
                # Or, we just update the objects in memory here, and commit them all at once in _execute_batch_classification?
                # But _classify_item is async and calls AI service which takes time.
                # While one is waiting for AI, another might use the session.
                # SQLAlchemy AsyncSession usage in asyncio.gather is tricky.
                
                # Better approach for stability: Create a new session for each item, OR process sequentially.
                # Given batch_size is small, let's try processing sequentially within the batch to be safe with the session,
                # OR use a separate session for each item inside _classify_item.
                
                # Let's use separate session per item to allow concurrency.
                # BUT the item passed in `items` is attached to the main `db` session.
                # If we use a new session, we need to merge the item or fetch it again.
                
                # Let's change strategy: _execute_batch_classification manages the session for fetching,
                # then we extract IDs and data needed for AI.
                # Then we run AI tasks concurrently.
                # Then we collect results.
                # Then we update DB in a single transaction or batch update.
                
                return {
                    "id": item.id,
                    "tags": tags,
                    "concepts": concepts,
                    "summary": summary,
                    "success": True
                }
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response for item {item.id}: {response_text}")
                return {"id": item.id, "success": False}
                
        except Exception as e:
            logger.error(f"Error in _classify_item for {item.id}: {e}")
            return {"id": item.id, "success": False}

    def _construct_classification_prompt(self, item: ContentItem) -> str:
        content_preview = (item.content_text or "")[:1000]
        return f"""
        Analyze the following content and provide:
        1. A list of relevant tags (max 5).
        2. A list of key concepts (max 5).
        3. A brief summary (1-2 sentences).

        Return ONLY a JSON object with keys: "tags", "concepts", "summary".

        Title: {item.title}
        URL: {item.url}
        Content Preview:
        {content_preview}
        """

    # Redefine _execute to handle the concurrency issue
    async def _execute_batch_classification(self, batch_size: int = 10):
        logger.info(f"Starting batch classification for {batch_size} items")
        
        # Phase 1: Fetch items
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
            
            # Detach items or copy data needed for AI
            for item in items:
                items_data.append({
                    "id": item.id,
                    "title": item.title,
                    "url": item.url,
                    "content_text": item.content_text
                })
        
        # Phase 2: AI Processing (Concurrent)
        # We use a dummy object or just pass dict to a helper
        tasks = [self._process_single_item_ai(data) for data in items_data]
        ai_results = await asyncio.gather(*tasks)
        
        # Phase 3: Update DB
        success_count = 0
        async with AsyncSessionLocal() as db:
            for res in ai_results:
                if res and res["success"]:
                    try:
                        stmt = select(ContentItem).where(ContentItem.id == res["id"])
                        result = await db.execute(stmt)
                        item = result.scalar_one_or_none()
                        
                        if item:
                            item.tags = res["tags"]
                            item.concepts = res["concepts"]
                            if res["summary"]:
                                item.summary = res["summary"]
                            item.ai_processed = True
                            
                            db.add(item)
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to update item {res['id']}: {e}")
            
            await db.commit()
            
        logger.info(f"Batch classification completed. Success: {success_count}/{len(items_data)}")
        return {"processed_count": len(items_data), "success_count": success_count}

    async def _process_single_item_ai(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        # Helper to create a dummy object-like structure for the prompt method
        class DummyItem:
            def __init__(self, d): self.__dict__ = d
        
        item = DummyItem(item_data)
        
        try:
            prompt = self._construct_classification_prompt(item)
            messages = [
                {"role": "system", "content": "You are a helpful assistant that categorizes content."},
                {"role": "user", "content": prompt}
            ]
            
            response_text = await ai_service.chat_completion(messages)
            
            if not response_text:
                return {"id": item_data["id"], "success": False}
                
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            
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

batch_classification_service = BatchClassificationService()
