import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # pyramid_structure, content_classification, etc.
    input_hash: Mapped[str] = mapped_column(String(64), index=True) # Used for caching/deduplication
    
    # AI Output
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)       # The actual suggestion content
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)    # AI's reasoning process
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True) # Suggestion validity period

    def __repr__(self):
        return f"<AISuggestion(id={self.id}, type={self.type}, confidence={self.confidence})>"
