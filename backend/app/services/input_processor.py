import logging
import uuid
import asyncio
from typing import List, Optional, Union
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.content import ContentItem
from app.services.input_parser import InputParser
from app.services.contribution.contribution_tracker import ContributionTracker
from app.services.fetchers import get_fetcher

logger = logging.getLogger(__name__)

class InputProcessor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.contribution_tracker = ContributionTracker(db)

    async def _refetch_with_relations(self, content_id: uuid.UUID) -> ContentItem:
        stmt = select(ContentItem).where(ContentItem.id == content_id).options(
            selectinload(ContentItem.validation_result)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def process_file_input(self, file: UploadFile, submitter_id: Optional[str] = None) -> ContentItem:
        content_text = ""
        input_type = "unknown"
        
        filename = file.filename.lower() if file.filename else ""
        
        try:
            if filename.endswith(".pdf"):
                input_type = "pdf"
                content_text = await InputParser.parse_pdf(file)
            elif filename.endswith(".docx"):
                input_type = "word"
                content_text = await InputParser.parse_docx(file)
            elif filename.endswith(".md"):
                input_type = "markdown"
                content_text = await InputParser.parse_markdown(file)
            elif filename.endswith((".png", ".jpg", ".jpeg")):
                input_type = "image"
                content_text = await InputParser.parse_image(file)
            elif filename.endswith(".txt"):
                input_type = "text"
                content_text = await InputParser.parse_text(file)
            else:
                # Default to text if unknown but try parsing as text
                input_type = "text"
                content_text = await InputParser.parse_text(file)
                
            content_item = ContentItem(
                title=file.filename or "Untitled File",
                url=f"file://{file.filename}", # Virtual URL
                content_text=content_text,
                submitter_id=submitter_id,
                input_type=input_type,
                status="PENDING"
            )
            self.db.add(content_item)
            await self.db.commit()
            content_item = await self._refetch_with_relations(content_item.id)

            await self.contribution_tracker.create_contribution(
                user_id=submitter_id,
                input_type=input_type,
                original_input=f"file://{file.filename}" if file.filename else "file://unknown",
                content_id=content_item.id
            )

            return content_item
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            raise

    async def process_url_input(self, url: str, submitter_id: Optional[str] = None) -> ContentItem:
        try:
            # Use web fetcher for generic URL
            fetcher = get_fetcher("web") 
            items = await fetcher.fetch(url)
            
            if not items:
                raise ValueError(f"No content found at {url}")
                
            # Take the first item (assuming URL points to a single article/page)
            item_data = items[0]
            
            content_item = ContentItem(
                title=item_data.get("title", "Untitled URL"),
                url=url,
                summary=item_data.get("summary"),
                content_text=item_data.get("content"),
                publish_time=item_data.get("publish_time"),
                submitter_id=submitter_id,
                input_type="url",
                status="PENDING"
            )
            self.db.add(content_item)
            await self.db.commit()
            content_item = await self._refetch_with_relations(content_item.id)

            await self.contribution_tracker.create_contribution(
                user_id=submitter_id,
                input_type="url",
                original_input=url,
                content_id=content_item.id
            )

            return content_item
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            raise

    async def process_text_input(self, text: str, title: str = "Untitled Note", submitter_id: Optional[str] = None) -> ContentItem:
        try:
            content_item = ContentItem(
                title=title,
                url="text://manual-input",
                content_text=text,
                submitter_id=submitter_id,
                input_type="text",
                status="PENDING"
            )
            self.db.add(content_item)
            await self.db.commit()
            content_item = await self._refetch_with_relations(content_item.id)

            await self.contribution_tracker.create_contribution(
                user_id=submitter_id,
                input_type="text",
                original_input=text,
                content_id=content_item.id
            )

            return content_item
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            raise

    async def process_batch_files(self, files: List[UploadFile], submitter_id: Optional[str] = None) -> List[ContentItem]:
        tasks = [self.process_file_input(file, submitter_id) for file in files]
        return await asyncio.gather(*tasks)

    async def process_batch_urls(self, urls: List[str], submitter_id: Optional[str] = None) -> List[ContentItem]:
        tasks = [self.process_url_input(url, submitter_id) for url in urls]
        return await asyncio.gather(*tasks)
