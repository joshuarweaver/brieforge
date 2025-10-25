"""Signal enrichment schemas."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class SignalEnrichmentSummary(BaseModel):
    """Summary of enrichment run."""
    created: int
    skipped: int
    processed: int


class SignalEnrichmentResponse(BaseModel):
    """Detailed enrichment record."""
    id: UUID
    signal_id: UUID
    enrichment_type: str
    entities: List[str]
    sentiment: Optional[float]
    trend_score: Optional[float]
    features: Dict[str, float]
    created_at: datetime

    class Config:
        from_attributes = True
