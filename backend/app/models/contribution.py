from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

from app.database import Base

class Contribution(Base):
    __tablename__ = "contributions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(50), nullable=True)  # Optional for anonymous/system
    
    # Input details
    input_type: Mapped[str] = mapped_column(String(20), nullable=False)  # url, pdf, docx, text, image
    original_input: Mapped[str] = mapped_column(Text, nullable=False)  # URL or file path or raw text
    
    # Processing results
    extracted_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_concepts: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True)
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending, processing, processed, failed
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Links
    content_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("content_items.id"), nullable=True)
    
    # Relationships
    # Note: approvals relationship will be defined in Approval model or via backref if needed
    # For now, we store proposal_ids as JSON list if needed, or rely on Approval.source_contribution_id
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Contribution id={self.id} type={self.input_type} status={self.status}>"
