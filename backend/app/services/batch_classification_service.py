import logging
import json
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.content import ContentItem
from app.core.ai.client import ai_client
from app.services.evolution_engine import EvolutionEngine
from app.database import AsyncSessionLocal

from app.core.ai.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)

class BatchClassificationService:
    def __init__(self):
        pass

    async def start_batch_classification(self, batch_size: int = 10, background_tasks = None):
        if background_tasks:
            background_tasks.add_task(self._execute_batch_classification, batch_size)
            return {"status": "started", "message": f"Batch classification started for {batch_size} items"}
        else:
            return await self._execute_batch_classification(batch_size)

    async def _execute_batch_classification(self, batch_size: int = 10):
        logger.info(f"Starting batch classification for {batch_size} items")
        
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
            
            for item in items:
                items_data.append({
                    "id": item.id,
                    "title": item.title,
                    "url": item.url,
                    "content_text": item.content_text or ""
                })
        
        tasks = [self._process_single_item_ai(data) for data in items_data]
        ai_results = await asyncio.gather(*tasks)
        
        success_count = 0
        
        async with AsyncSessionLocal() as db:
            evolution_engine = EvolutionEngine(db)
            
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
                            await db.commit()
                            await db.refresh(item)
                            
                            await evolution_engine.auto_classify_content(item)
                            
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to update/link item {res['id']}: {e}")
                        await db.rollback()
            
        logger.info(f"Batch classification completed. Success: {success_count}/{len(items_data)}")
        return {"processed_count": len(items_data), "success_count": success_count}

    async def _process_single_item_ai(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            content_preview = (item_data.get("content_text") or "")[:1000]
            variables = {
                "title": item_data.get("title"),
                "url": item_data.get("url"),
                "content_preview": content_preview
            }
            
            prompt_content, metadata = prompt_loader.render_prompt("content/batch_analysis", variables)
            
            if not prompt_content:
                logger.error(f"Failed to load prompt 'content_analysis_batch' for item {item_data['id']}")
                return {"id": item_data["id"], "success": False}
            
            system_prompt = metadata.get("system_prompt")
            if not system_prompt:
                logger.error(f"Missing system_prompt in metadata for 'content/batch_analysis'")
                return {"id": item_data["id"], "success": False}
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_content}
            ]
            
            response_text = await ai_client.chat_completion(messages)
            
            if not response_text:
                logger.warning(f"AI returned empty response for item {item_data['id']}")
                return {"id": item_data["id"], "success": False}
                
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            try:
                data = json.loads(clean_text)
            except json.JSONDecodeError:
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

    # Removed _construct_classification_prompt as it is replaced by prompt_loader

batch_classification_service = BatchClassificationService()
