"""Strategic Brief database model."""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class StrategicBrief(Base):
    """
    Strategic Brief model for storing AI-generated marketing strategy documents.

    A strategic brief is a comprehensive 2-page document that synthesizes
    market intelligence, audience insights, and strategic recommendations.
    """

    __tablename__ = "strategic_briefs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)

    # Brief metadata
    status = Column(String, nullable=False, default="completed")  # completed, failed
    version = Column(Integer, default=1)  # For versioning briefs

    # LLM metadata
    llm_provider = Column(String, nullable=True)  # claude, openai
    llm_model = Column(String, nullable=True)  # claude-3-5-sonnet-20241022, gpt-4, etc.
    tokens_used = Column(Integer, nullable=True)

    # Brief content stored as JSON
    # Structure: {
    #   "full_text": str,  # Complete markdown brief
    #   "sections": {
    #       "Executive Summary": str,
    #       "Market Context": str,
    #       "Target Audience Deep Dive": str,
    #       "Messaging Strategy": str,
    #       "Channel Strategy & Tactics": str,
    #       "Creative Direction": str,
    #       "Success Metrics": str
    #   },
    #   "metadata": {
    #       "signal_count": int,
    #       "analyses_used": int,
    #       "custom_instructions": str  # if any
    #   }
    # }
    content = Column(JSON, nullable=False)

    # Custom instructions used for generation
    custom_instructions = Column(Text, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="strategic_briefs")
