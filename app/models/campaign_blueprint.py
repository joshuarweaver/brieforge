"""Campaign blueprint persistence models."""
from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CampaignBlueprintArtifact(Base):
    """Persisted blueprint artifact for a campaign."""

    __tablename__ = "campaign_blueprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False, index=True)
    summary = Column(String, nullable=False)
    blueprint = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="blueprint_artifacts")
