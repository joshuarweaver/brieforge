"""Signal enrichment models."""
from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, Enum, ForeignKey, JSON, String, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.core.database import Base


class SignalEnrichmentType(str, PyEnum):
    """Types of enrichment applied to signals."""
    SEMANTIC = "semantic"
    PERFORMANCE = "performance"
    TREND = "trend"


class SignalEnrichment(Base):
    """Enriched metadata derived from a signal."""

    __tablename__ = "signal_enrichments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    signal_id = Column(UUID(as_uuid=True), ForeignKey("signals.id"), nullable=False, index=True)
    enrichment_type = Column(Enum(SignalEnrichmentType, name="signal_enrichment_type"), nullable=False)
    entities = Column(JSON, nullable=False, default=list)
    sentiment = Column(Float, nullable=True)
    trend_score = Column(Float, nullable=True)
    features = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    signal = relationship("Signal", back_populates="enrichments")
