"""Campaign database model."""
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Campaign(Base):
    """Campaign model."""

    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(
        String,
        default="draft"
    )  # draft, gathering_signals, analyzing, generating, completed, failed

    # Brief stored as JSONB
    # Structure: {
    #   goal: str,
    #   audiences: List[str],
    #   offer: str,
    #   competitors: List[str],
    #   channels: List[str],  # linkedin, facebook, instagram, tiktok, youtube, pinterest
    #   budget_band: str,
    #   voice_constraints: str
    # }
    brief = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="campaigns")
    signals = relationship("Signal", back_populates="campaign", cascade="all, delete-orphan")
    signal_analyses = relationship("SignalAnalysis", back_populates="campaign", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="campaign", cascade="all, delete-orphan")
    assets = relationship("GeneratedAsset", back_populates="campaign", cascade="all, delete-orphan")
