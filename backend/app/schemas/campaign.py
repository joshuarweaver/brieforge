"""Campaign Pydantic schemas."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# Brief Schema
class Brief(BaseModel):
    """Campaign brief schema."""
    goal: str
    audiences: List[str]
    offer: str
    competitors: List[str]
    channels: List[str]  # linkedin, facebook, instagram, tiktok, youtube, pinterest, google_ads
    budget_band: str
    voice_constraints: Optional[str] = None


# Campaign Schemas
class CampaignBase(BaseModel):
    """Base campaign schema."""
    name: str
    brief: Brief


class CampaignCreate(CampaignBase):
    """Campaign creation schema."""
    pass


class CampaignUpdate(BaseModel):
    """Campaign update schema."""
    name: Optional[str] = None
    brief: Optional[Brief] = None
    status: Optional[str] = None


class CampaignResponse(CampaignBase):
    """Campaign response schema."""
    id: int
    workspace_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Signal Schemas
class SignalEvidence(BaseModel):
    """Signal evidence schema."""
    url: str
    timestamp: str
    snippet: str
    metadata: Dict[str, Any]


class SignalResponse(BaseModel):
    """Signal response schema."""
    id: int
    campaign_id: int
    source: str
    search_method: str
    query: str
    evidence: SignalEvidence
    relevance_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class SignalStats(BaseModel):
    """Signal statistics schema."""
    total_signals: int
    by_source: Dict[str, int]
    by_search_method: Dict[str, int]
    avg_relevance_score: float
