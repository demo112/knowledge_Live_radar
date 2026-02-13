import uuid
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class NodeRelation(Base):
    __tablename__ = "node_relations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramid_nodes.id", ondelete="CASCADE"), nullable=False)
    target_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pyramid_nodes.id", ondelete="CASCADE"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(50), default="related", nullable=False)
    
    __table_args__ = (
        UniqueConstraint('source_node_id', 'target_node_id', 'relation_type', name='uq_node_relation'),
    )

    # Relationships
    source_node = relationship("PyramidNode", foreign_keys=[source_node_id], back_populates="outgoing_relations")
    target_node = relationship("PyramidNode", foreign_keys=[target_node_id], back_populates="incoming_relations")

    def __repr__(self):
        return f"<NodeRelation(source={self.source_node_id}, target={self.target_node_id}, type={self.relation_type})>"
