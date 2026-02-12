import uuid
import logging
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pyramid import PyramidNode
from app.models.content import ContentItem, ContentNodeRelation
from app.models.approval import Approval
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

class DriftDetector:
    """
    Detects semantic drift in knowledge concepts (nodes) by comparing historical and recent content.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def detect_drift(self, pyramid_id: uuid.UUID) -> List[Approval]:
        """
        Scan all nodes in a pyramid for concept drift.
        """
        logger.info(f"Starting drift detection for pyramid {pyramid_id}")
        proposals = []
        
        # 1. Get all nodes
        nodes = await self._fetch_nodes(pyramid_id)
        
        # For performance, maybe limit to nodes with recent updates?
        # For MVP, we scan all.
        
        for node in nodes:
            drift = await self._check_node_drift(node)
            if drift:
                proposals.append(drift)
        
        # Save proposals
        saved_proposals = []
        for p in proposals:
            # Check for existing pending drift proposal for this node to avoid spam
            exists = await self._drift_proposal_exists(p.target_id)
            if not exists:
                self.db.add(p)
                saved_proposals.append(p)
        
        if saved_proposals:
            await self.db.commit()
            for p in saved_proposals:
                await self.db.refresh(p)
            logger.info(f"Detected {len(saved_proposals)} concepts with drift")
            
        return saved_proposals

    async def _check_node_drift(self, node: PyramidNode) -> Optional[Approval]:
        # 2. Get old and new content
        # Define "Old": older than 30 days
        # Define "New": newer than 7 days
        # Note: In a fresh project, "Old" might be empty. We might need shorter windows for demo.
        # Let's use 14 days for Old and 3 days for New for faster testing/demo, 
        # or stick to prod values and accept no drift in early days.
        
        now = datetime.now(timezone.utc)
        threshold_old_end = now - timedelta(days=30)
        threshold_new_start = now - timedelta(days=7)
        
        # Fetch 5 samples of each
        old_content = await self._fetch_node_content(node.id, None, threshold_old_end, limit=5)
        new_content = await self._fetch_node_content(node.id, threshold_new_start, None, limit=5)
        
        if not old_content or not new_content:
            # Cannot compare if missing data on either side
            return None
            
        # 3. Compare using AI
        # Prepare summaries
        old_text = "\n".join([f"- {c.title}: {c.summary or 'No summary'}" for c in old_content])
        new_text = "\n".join([f"- {c.title}: {c.summary or 'No summary'}" for c in new_content])
        
        prompt = f"""
        Concept Name: {node.name}
        Description: {node.description or 'N/A'}
        
        Historical Content (Older than 30 days):
        {old_text}
        
        Recent Content (Last 7 days):
        {new_text}
        
        Task: Analyze if the meaning or focus of this concept has shifted (drifted) significantly.
        Does the recent content suggest the concept has evolved into something else or broadened/narrowed significantly compared to historical understanding?
        
        Return 'YES' if significant drift is detected, otherwise 'NO'.
        If YES, provide a brief reason (max 1 sentence).
        """
        
        try:
            response = await ai_service.chat_completion([
                {"role": "system", "content": "You are a knowledge graph consistency analyzer."},
                {"role": "user", "content": prompt}
            ])
            
            if response and "YES" in response.upper():
                # Extract reason (naive parsing)
                reason = "Detected semantic shift in recent content."
                if "YES" in response:
                    parts = response.split("YES", 1)
                    if len(parts) > 1:
                        reason = parts[1].strip().strip(":,- ")
                
                return Approval(
                    type="fix_drift",
                    status="pending",
                    target_id=node.id,
                    generated_by="ai",
                    confidence_score=0.7, # AI judgment
                    reason=f"Concept Drift Detected: {reason}",
                    data={
                        "node_id": str(node.id),
                        "node_name": node.name,
                        "drift_analysis": reason,
                        "old_sample_count": len(old_content),
                        "new_sample_count": len(new_content)
                    }
                )
        except Exception as e:
            logger.error(f"Error checking drift for node {node.id}: {e}")
            
        return None

    async def _fetch_nodes(self, pyramid_id: uuid.UUID) -> List[PyramidNode]:
        result = await self.db.execute(
            select(PyramidNode)
            .where(PyramidNode.pyramid_id == pyramid_id)
            .where(PyramidNode.is_deleted == False)
        )
        return result.scalars().all()

    async def _fetch_node_content(self, node_id: uuid.UUID, start_date: Optional[datetime], end_date: Optional[datetime], limit: int) -> List[ContentItem]:
        query = (
            select(ContentItem)
            .join(ContentNodeRelation, ContentNodeRelation.content_id == ContentItem.id)
            .where(ContentNodeRelation.node_id == node_id)
            .order_by(ContentItem.publish_time.desc())
            .limit(limit)
        )
        
        if start_date:
            query = query.where(ContentItem.publish_time >= start_date)
        if end_date:
            query = query.where(ContentItem.publish_time <= end_date)
            
        result = await self.db.execute(query)
        return result.scalars().all()
        
    async def _drift_proposal_exists(self, node_id: uuid.UUID) -> bool:
        result = await self.db.execute(
            select(Approval)
            .where(Approval.type == "fix_drift")
            .where(Approval.target_id == node_id)
            .where(Approval.status == "pending")
        )
        return result.scalars().first() is not None
