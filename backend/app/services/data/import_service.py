import logging
import json
import uuid
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.pyramid import Pyramid, PyramidNode
from app.models.source import InformationSource

logger = logging.getLogger(__name__)

@dataclass
class ImportConflict:
    type: str
    existing_name: str
    import_name: str
    resolution: Optional[str] = None # skip/overwrite/rename

@dataclass
class ImportResult:
    success: bool
    pyramid_count: int = 0
    source_count: int = 0
    errors: List[str] = None
    conflicts: List[ImportConflict] = None

class ImportService:
    async def validate_import_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        errors = []
        if "version" not in data:
            errors.append("Missing version")
        if "pyramids" not in data and "sources" not in data:
            errors.append("No data to import")
        return len(errors) == 0, errors

    async def detect_conflicts(self, data: Dict[str, Any]) -> List[ImportConflict]:
        conflicts = []
        async with AsyncSessionLocal() as session:
            # Check Pyramids
            if "pyramids" in data:
                for p in data["pyramids"]:
                    stmt = select(Pyramid).where(Pyramid.name == p["name"])
                    existing = await session.scalar(stmt)
                    if existing:
                        conflicts.append(ImportConflict("pyramid", existing.name, p["name"]))
            
            # Check Sources
            if "sources" in data:
                for s in data["sources"]:
                    stmt = select(InformationSource).where(InformationSource.name == s["name"])
                    existing = await session.scalar(stmt)
                    if existing:
                        conflicts.append(ImportConflict("source", existing.name, s["name"]))
        return conflicts

    async def import_data(self, data: Dict[str, Any], conflict_resolutions: Dict[str, str] = None) -> ImportResult:
        result = ImportResult(success=True, errors=[], conflicts=[])
        
        async with AsyncSessionLocal() as session:
            try:
                # Import Pyramids
                if "pyramids" in data:
                    for p in data["pyramids"]:
                        # Handle conflict
                        resolution = conflict_resolutions.get(f"pyramid:{p['name']}") if conflict_resolutions else None
                        
                        stmt = select(Pyramid).where(Pyramid.name == p["name"])
                        existing = await session.scalar(stmt)
                        
                        if existing:
                            if resolution == "skip":
                                continue
                            elif resolution == "overwrite":
                                # Delete existing? Or update? Overwrite usually implies replace.
                                await session.delete(existing)
                                await session.flush()
                            elif resolution == "rename":
                                p["name"] = f"{p['name']} (Imported)"
                            else:
                                # Default skip if conflict not resolved? Or fail?
                                # Let's skip for safety
                                result.conflicts.append(ImportConflict("pyramid", p["name"], p["name"]))
                                continue
                        
                        # Create Pyramid
                        new_pyramid = Pyramid(
                            id=uuid.uuid4(), # Generate new ID to avoid conflict
                            name=p["name"],
                            description=p.get("description")
                        )
                        session.add(new_pyramid)
                        await session.flush()
                        result.pyramid_count += 1
                        
                        # Create Nodes (and map IDs)
                        node_id_map = {} # old_id -> new_uuid
                        # Need to insert parents first. Sort by level?
                        # Assuming nodes are list.
                        # Simple approach: Create all, then set parents.
                        
                        nodes_to_create = []
                        for n in p["nodes"]:
                            new_id = uuid.uuid4()
                            node_id_map[n["id"]] = new_id # assuming n["id"] exists in export
                            
                            new_node = PyramidNode(
                                id=new_id,
                                pyramid_id=new_pyramid.id,
                                name=n["name"],
                                description=n.get("description"),
                                level=n.get("level", 0),
                                # parent_id set later
                            )
                            nodes_to_create.append((new_node, n.get("parent_id")))
                            session.add(new_node)
                        
                        await session.flush()
                        
                        # Set parents
                        for node, old_parent_id in nodes_to_create:
                            if old_parent_id and old_parent_id in node_id_map:
                                node.parent_id = node_id_map[old_parent_id]
                        
                        # Import Content? (Not implemented in basic version as per tasks, but design mentioned it)
                        # ...
                        
                # Import Sources
                if "sources" in data:
                    for s in data["sources"]:
                        # Conflict logic similar to pyramid...
                        stmt = select(InformationSource).where(InformationSource.name == s["name"])
                        existing = await session.scalar(stmt)
                        if existing:
                             # ... same logic
                             continue
                             
                        new_source = InformationSource(
                            name=s["name"],
                            type=s["type"],
                            url=s["url"],
                            config=s.get("config"),
                            check_interval=s.get("check_interval", 3600)
                        )
                        session.add(new_source)
                        result.source_count += 1
                
                await session.commit()
                
            except Exception as e:
                logger.error(f"Import failed: {e}")
                await session.rollback()
                result.success = False
                result.errors.append(str(e))
                
        return result

import_service = ImportService()
