import logging
import json
import uuid
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.pyramid import Pyramid, PyramidNode
from app.models.source import InformationSource
from app.models.content import ContentItem, ContentNodeRelation

logger = logging.getLogger(__name__)

@dataclass
class ExportOptions:
    include_content: bool = False
    include_sources: bool = False
    pyramid_ids: Optional[List[str]] = None

@dataclass
class ExportResult:
    file_path: str = "" # In memory for now, or temp file
    data: Dict[str, Any] = None

class ExportService:
    async def export_data(self, options: ExportOptions) -> Dict[str, Any]:
        async with AsyncSessionLocal() as session:
            data = {
                "version": "1.0",
                "exported_at": str(datetime.now()),
                "pyramids": [],
                "sources": []
            }
            
            # Pyramids
            stmt = select(Pyramid).options(selectinload(Pyramid.nodes))
            if options.pyramid_ids:
                stmt = stmt.where(Pyramid.id.in_(options.pyramid_ids))
            
            pyramids = (await session.execute(stmt)).scalars().all()
            
            for p in pyramids:
                p_data = {
                    "id": str(p.id),
                    "name": p.name,
                    "description": p.description,
                    "nodes": []
                }
                
                # Nodes
                # Re-fetch nodes to ensure we get them all or use relationship
                # Assuming p.nodes is loaded
                for n in p.nodes:
                    n_data = {
                        "id": str(n.id),
                        "name": n.name,
                        "description": n.description,
                        "level": n.level,
                        "parent_id": str(n.parent_id) if n.parent_id else None,
                        "content": []
                    }
                    
                    if options.include_content:
                        # Fetch content for this node
                        content_stmt = select(ContentItem).join(ContentNodeRelation).where(ContentNodeRelation.node_id == n.id)
                        contents = (await session.execute(content_stmt)).scalars().all()
                        for c in contents:
                            n_data["content"].append({
                                "title": c.title,
                                "url": c.url,
                                "summary": c.summary,
                                "created_at": str(c.created_at)
                            })
                    
                    p_data["nodes"].append(n_data)
                
                data["pyramids"].append(p_data)
            
            # Sources
            if options.include_sources:
                stmt = select(InformationSource)
                sources = (await session.execute(stmt)).scalars().all()
                for s in sources:
                    config = s.config.copy() if s.config else {}
                    # Mask sensitive keys
                    if "api_key" in config:
                        config["api_key"] = "***"
                    if "password" in config:
                        config["password"] = "***"
                        
                    data["sources"].append({
                        "name": s.name,
                        "type": s.type,
                        "url": s.url,
                        "config": config,
                        "check_interval": s.check_interval
                    })
            
            return data

export_service = ExportService()
