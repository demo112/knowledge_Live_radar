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

from app.core.ai.facade import ai_facade
from app.repositories.pyramid import PyramidNodeRepository

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
            
            concept_name = match.concept_name or "Unknown"
            
            # Use AI to find best parent node
            repo = PyramidNodeRepository(self.db)
            all_nodes = await repo.get_by_pyramid(pyramid_id)
            candidate_nodes = [
                {"id": str(n.id), "name": n.name, "description": n.description or ""}
                for n in all_nodes
            ]
            
            # Find best parent placement
            placement = await ai_facade.find_best_parent_node(
                new_node_name=concept_name,
                new_node_description="Extracted from content",
                source_context=content_item.title + "\n" + (content_item.summary or ""),
                candidate_nodes=candidate_nodes
            )
            
            parent_id = placement.best_parent_id
            placement_reason = placement.reasoning
            
            # Generate proposal reason
            base_reason = await ai_facade.generate_proposal_reason(
                match_type="NEW",
                concept_name=concept_name,
                content_title=content_item.title
            )
            
            final_reason = f"{base_reason}\n\nPlacement: {placement_reason}"

            # Use summary as description, truncate if too long
            description = content_item.summary or "Extracted from content"
            if len(description) > 500:
                description = description[:497] + "..."

            return Approval(
                type="create_node",
                status="pending",
                source_content_id=content_item.id,
                generated_by="ai",
                confidence_score=confidence,
                reason=final_reason,
                data={
                    "name": concept_name,
                    "pyramid_id": str(pyramid_id),
                    "description": description,
                    "parent_id": str(parent_id) if parent_id else None
                }
            )
            
        elif match.match_type in [MatchType.EXACT, MatchType.SYNONYM]:
            # Propose linking content to existing node
            if not match.node_id:
                logger.warning(f"Match type {match.match_type} but no node_id provided")
                return None
            
            node_name = match.node_name or "Unknown"

            reason = await ai_facade.generate_proposal_reason(
                match_type=match.match_type.value,
                concept_name=content_item.title, 
                content_title=content_item.title,
                node_name=node_name
            )

            return Approval(
                type="link_content",
                status="pending",
                source_content_id=content_item.id,
                target_id=match.node_id,
                generated_by="ai",
                confidence_score=confidence,
                reason=reason,
                data={
                    "node_id": str(match.node_id),
                    "content_id": str(content_item.id)
                }
            )
            
        return None
