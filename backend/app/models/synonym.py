from typing import Optional
from sqlalchemy import String, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid

from app.database import Base

class SynonymMapping(Base):
    __tablename__ = "synonym_mappings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    canonical_term: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    synonym: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    source: Mapped[str] = mapped_column(String(50), default="manual")  # manual, ai_generated
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SynonymMapping {self.synonym} -> {self.canonical_term}>"
