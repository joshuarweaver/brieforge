"""Analysis and Asset database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Analysis(Base):
    """Analysis model for storing Insight Lattice results."""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)

    # 2-page strategy document (Markdown)
    strategy = Column(Text, nullable=False)

    # Structured analysis results (all JSONB)
    pillars = Column(JSON, nullable=False)  # [{name, message, supporting_signals[]}]
    hooks = Column(JSON, nullable=False)  # [{hook, channel, source_signals[]}]
    objections = Column(JSON, nullable=False)  # [{objection, response, evidence[]}]
    kpis = Column(JSON, nullable=False)  # [{metric, range, sources[], confidence}]

    # Attribution map
    receipts = Column(JSON, nullable=False)  # Full provenance: inputs -> signals -> decisions

    # Panel reviews
    panel_reviews = Column(JSON, nullable=True)  # [{agent, feedback, diffs, reasoning}]

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="analyses")


class GeneratedAsset(Base):
    """Generated asset model."""

    __tablename__ = "generated_assets"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)

    # Asset classification
    asset_type = Column(String, nullable=False)  # social, google_ads
    platform = Column(String, nullable=True)  # linkedin, facebook, instagram, etc.
    format = Column(String, nullable=True)  # feed_post, reel, story, carousel

    # Asset content (JSONB, structure varies by type)
    # Social: {copy, visual_guidance, hook_source, persona_target, journey_stage, cta, hashtags, reasoning, supporting_signals[], expected_kpis{}}
    # Google Ads: {headlines[], descriptions[], sitelinks[], callouts[], competitive_intel, hook_rationale, supporting_signals[], expected_kpis{}}
    content = Column(JSON, nullable=False)

    # Receipts (supporting evidence)
    receipts = Column(JSON, nullable=False)  # [SignalEvidence objects]

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="assets")
    ratings = relationship("AssetRating", back_populates="asset", cascade="all, delete-orphan")


class AssetRating(Base):
    """Asset rating model for learning system."""

    __tablename__ = "asset_ratings"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("generated_assets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    asset = relationship("GeneratedAsset", back_populates="ratings")


class SuccessPattern(Base):
    """Success pattern model for learning system."""

    __tablename__ = "success_patterns"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    pattern_type = Column(String, nullable=False)  # hook, objection_response, proof_angle
    content = Column(JSON, nullable=False)  # Pattern-specific structure
    usage_count = Column(Integer, default=1)
    avg_rating = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
