"""Signal database model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Signal(Base):
    """Signal model for storing gathered intelligence."""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)

    # Signal metadata
    source = Column(String, nullable=False)  # serp_organic, meta_ads, reddit_organic, etc.
    search_method = Column(String, nullable=False)  # Which search method was used
    query = Column(String, nullable=False)  # Original search query

    # Evidence stored as JSONB
    # Structure: {
    #   url: str,
    #   timestamp: str (ISO format),
    #   snippet: str,
    #   metadata: Dict  # Platform-specific data (upvotes, views, ad spend indicators, etc.)
    # }
    evidence = Column(JSON, nullable=False)

    # Scoring
    relevance_score = Column(Float, default=0.0)  # 0.0-1.0, calculated by Insight Lattice

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="signals")
