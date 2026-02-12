import logging
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.content import ContentItem
from app.models.approval import Approval
from app.services.concept_extractor import ConceptExtractor
from app.services.concept_matcher import ConceptMatcher
from app.services.proposal_generator import ProposalGenerator

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.extractor = ConceptExtractor(db)
        self.matcher = ConceptMatcher(db)
        self.proposal_generator = ProposalGenerator(db)

    async def analyze_content(self, content_id: uuid.UUID, pyramid_id: uuid.UUID) -> List[Approval]:
        """
        Full pipeline: Extract Concepts -> Match Nodes -> Generate Proposals
        """
        logger.info(f"Starting analysis for content {content_id} on pyramid {pyramid_id}")
        
        # 1. Load Content
        stmt = select(ContentItem).where(ContentItem.id == content_id)
        result = await self.db.execute(stmt)
        content_item = result.scalar_one_or_none()
        
        if not content_item:
            logger.error(f"Content item {content_id} not found")
            return []
            
        if not content_item.content_text:
            logger.warning(f"Content item {content_id} has no text to analyze")
            return []

        # 2. Extract Concepts
        logger.info("Extracting concepts...")
        concepts_data = await self.extractor.extract_concepts(content_item.content_text)
        if not concepts_data:
            logger.info("No concepts extracted")
            return []
            
        # Save concepts to DB (get Concept objects)
        concepts = await self.extractor.save_concepts(concepts_data)
        logger.info(f"Saved {len(concepts)} concepts")

        # 3. Match Concepts
        logger.info("Matching concepts to pyramid nodes...")
        matches = await self.matcher.batch_match(concepts, pyramid_id)
        
        # 4. Generate Proposals
        logger.info("Generating proposals...")
        proposals = await self.proposal_generator.generate_proposals_from_matches(matches, content_item, pyramid_id)
        
        logger.info(f"Generated {len(proposals)} proposals")
        return proposals
