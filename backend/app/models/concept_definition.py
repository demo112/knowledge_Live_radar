import uuid
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

class ConceptDefinition(Base):
    __tablename__ = "concept_definitions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    term: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    
    context_examples: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    drift_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    drift_evidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Evidence details
    
    previous_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("concept_definitions.id"), nullable=True)
    
    proposal_id: Mapped[Optional[uuid.UUID]] = mapped_column(String(36), nullable=True) # Link to ChangeProposal if applicable. Using String to avoid circular dependency if Proposal is in another module not yet ready or complex.
    
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    previous_version: Mapped[Optional["ConceptDefinition"]] = relationship("ConceptDefinition", remote_side=[id], backref="next_version")

    def __repr__(self):
        return f"<ConceptDefinition(id={self.id}, term={self.term}, version={self.version})>"
