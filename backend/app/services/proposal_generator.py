import uuid
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.approval import Approval
from app.models.pyramid import PyramidNode
from app.models.content import ContentItem
from app.services.concept_matcher import MatchResult, MatchType

logger = logging.getLogger(__name__)

class ProposalGenerator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_proposals_from_matches(
        self, 
        matches: List[MatchResult], 
        content_item: ContentItem,
        pyramid_id: uuid.UUID
    ) -> List[Approval]:
        """
        Generate change proposals based on concept matches.
        """
        proposals = []
        
        for match in matches:
            proposal = await self.create_proposal_for_match(match, content_item, pyramid_id)
            if proposal:
                proposals.append(proposal)
                self.db.add(proposal)
        
        await self.db.commit()
        for p in proposals:
            await self.db.refresh(p)
            
        return proposals

    async def create_proposal_for_match(
        self, 
        match: MatchResult, 
        content_item: ContentItem,
        pyramid_id: uuid.UUID
    ) -> Optional[Approval]:
        
        # Calculate priority/confidence based on match confidence
        confidence = match.confidence
        
        if match.match_type == MatchType.NEW:
            # Propose creating a new node
            # For now, we don't have a parent, so it might be a root node or require manual placement
            return Approval(
                type="create_node",
                status="pending",
                source_content_id=content_item.id,
                generated_by="ai",
                confidence_score=confidence,
                reason=f"New concept extracted from content: {match.details}",
                data={
                    "name": match.details.split("'")[1] if "'" in match.details else "Unknown", # Hacky extraction from details string, improve later by passing Concept object
                    "pyramid_id": str(pyramid_id),
                    "description": "Extracted from content", # We should pass concept description here
                    "parent_id": None 
                }
            )
            
        elif match.match_type in [MatchType.EXACT, MatchType.SYNONYM]:
            # Propose linking content to existing node
            if not match.node_id:
                logger.warning(f"Match type {match.match_type} but no node_id provided")
                return None
                
            return Approval(
                type="link_content",
                status="pending",
                source_content_id=content_item.id,
                target_id=match.node_id,
                generated_by="ai",
                confidence_score=confidence,
                reason=f"Content matches existing node: {match.details}",
                data={
                    "node_id": str(match.node_id),
                    "content_id": str(content_item.id)
                }
            )
            
        return None
