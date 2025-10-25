"""Signal Analysis database model."""
from datetime import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class SignalAnalysisType(str, enum.Enum):
    """Types of signal analysis that can be performed."""
    COMPREHENSIVE = "comprehensive"  # Full analysis across all signals
    COMPETITOR = "competitor"  # Competitor strategy analysis
    AUDIENCE = "audience"  # Audience insights
    MESSAGING = "messaging"  # Messaging patterns
    CREATIVE = "creative"  # Creative recommendations
    TRENDS = "trends"  # Market trends


class SignalAnalysisStatus(str, enum.Enum):
    """Signal analysis status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SignalAnalysis(Base):
    """
    Signal Analysis model for storing AI-generated insights from raw signals.

    This is an intermediate analysis step that processes raw signals before
    the final comprehensive Analysis (Insight Lattice) is generated.
    """

    __tablename__ = "signal_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)

    # Analysis metadata
    analysis_type = Column(SQLEnum(SignalAnalysisType), nullable=False, default=SignalAnalysisType.COMPREHENSIVE)
    status = Column(SQLEnum(SignalAnalysisStatus), nullable=False, default=SignalAnalysisStatus.PENDING)

    # LLM metadata
    llm_provider = Column(String, nullable=True)  # claude, openai
    llm_model = Column(String, nullable=True)  # claude-3-5-sonnet-20241022, gpt-4, etc.
    tokens_used = Column(Integer, nullable=True)

    # Analysis results stored as JSON
    # Structure depends on analysis_type but generally includes:
    # {
    #   "summary": str,
    #   "key_insights": List[str],
    #   "competitor_strategies": Dict[str, Any],  # if relevant
    #   "audience_insights": Dict[str, Any],  # if relevant
    #   "messaging_patterns": Dict[str, Any],  # if relevant
    #   "creative_recommendations": List[Dict],  # if relevant
    #   "market_trends": List[Dict],  # if relevant
    #   "signal_count": int,  # number of signals analyzed
    #   "confidence_score": float,  # 0-1 confidence in insights
    # }
    insights = Column(JSON, nullable=True)

    # Raw LLM response for debugging/auditing
    raw_response = Column(Text, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="signal_analyses")
