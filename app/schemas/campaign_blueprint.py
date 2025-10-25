"""Campaign blueprint schemas."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class AudienceHypothesis(BaseModel):
    """Hypothesis about a target audience cluster."""
    audience: str
    focus_entities: List[str]
    pain_points: List[str]
    language_notes: List[str]
    supporting_signals: List[str]


class ValueProposition(BaseModel):
    """Value proposition derived from signals."""
    statement: str
    supporting_entities: List[str]
    trend_score: Optional[float] = None
    proof_points: List[str]


class MessagingPillar(BaseModel):
    """Messaging pillar recommendation."""
    pillar: str
    key_messages: List[str]
    supporting_urls: List[str]
    relevance_score: Optional[float] = None


class CreativeVariation(BaseModel):
    """Alternative creative variant for an asset."""
    headline: str
    primary_text: str
    cta: Optional[str] = None


class DraftAsset(BaseModel):
    """Draft ad asset ready for export adapters."""
    id: UUID
    platform: str
    objective: str
    audience_focus: List[str]
    headline: str
    primary_text: str
    cta: str
    supporting_signals: List[str]
    creative_hooks: List[str]
    variations: List[CreativeVariation]


class InsightsSummary(BaseModel):
    """Aggregate blueprint insights."""
    top_entities: List[str]
    trending_topics: List[str]
    sentiment_distribution: Dict[str, float]


class CampaignBlueprint(BaseModel):
    """Campaign blueprint response schema."""
    artifact_id: Optional[UUID] = None
    campaign_id: UUID
    generated_at: datetime
    summary: str
    insights: InsightsSummary
    audience_hypotheses: List[AudienceHypothesis]
    value_propositions: List[ValueProposition]
    messaging_pillars: List[MessagingPillar]
    draft_assets: List[DraftAsset]
    next_actions: List[str]


class CampaignBlueprintListItem(BaseModel):
    """Lightweight record for blueprint history listing."""
    id: UUID
    campaign_id: UUID
    summary: str
    created_at: datetime
