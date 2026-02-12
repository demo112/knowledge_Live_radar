import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base

class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False) # technology, tool, method, organization
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    synonyms: Mapped[List["ConceptSynonym"]] = relationship("ConceptSynonym", back_populates="concept", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Concept(id={self.id}, name={self.name}, type={self.type})>"

class ConceptSynonym(Base):
    __tablename__ = "concept_synonyms"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id"), nullable=False)
    synonym: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    concept: Mapped["Concept"] = relationship("Concept", back_populates="synonyms")

    def __repr__(self):
        return f"<ConceptSynonym(id={self.id}, synonym={self.synonym})>"
