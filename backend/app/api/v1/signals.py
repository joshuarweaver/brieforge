"""Signal collection API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models import User, Campaign, Signal
from app.services.signal_orchestrator import SignalOrchestrator

router = APIRouter()


class CollectSignalsRequest(BaseModel):
    """Request to collect signals for a campaign."""
    cartridge_names: Optional[List[str]] = None  # None = all cartridges
    max_queries_per_cartridge: int = 10


class CollectSignalsResponse(BaseModel):
    """Response from signal collection."""
    campaign_id: int
    cartridges_run: int
    total_signals: int
    errors: List[dict]
    timestamp: str


class SignalResponse(BaseModel):
    """Signal response schema."""
    id: int
    campaign_id: int
    source: str
    search_method: str
    query: str
    evidence: List[dict]
    relevance_score: float
    created_at: str

    class Config:
        from_attributes = True


@router.post("/{campaign_id}/signals/collect", response_model=CollectSignalsResponse)
async def collect_signals(
    campaign_id: int,
    request: CollectSignalsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace)
):
    """
    Collect signals for a campaign using signal cartridges.

    This endpoint runs signal collection cartridges to gather intelligence
    from various sources (Google, Meta Ads, LinkedIn Ads, YouTube, etc.).

    - **campaign_id**: Campaign ID to collect signals for
    - **cartridge_names**: Optional list of cartridge names (default: all)
    - **max_queries_per_cartridge**: Max queries per cartridge (default: 10)

    Returns summary of signal collection including errors.
    """
    # Verify campaign exists and belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Create orchestrator and collect signals
    orchestrator = SignalOrchestrator(db)

    try:
        result = await orchestrator.collect_signals(
            campaign_id=campaign_id,
            cartridge_names=request.cartridge_names,
            max_queries_per_cartridge=request.max_queries_per_cartridge
        )
        return CollectSignalsResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signal collection failed: {str(e)}"
        )


@router.get("/{campaign_id}/signals", response_model=List[SignalResponse])
def get_campaign_signals(
    campaign_id: int,
    min_relevance: float = 0.0,
    source: Optional[str] = None,
    limit: Optional[int] = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace_id: int = Depends(get_current_workspace)
):
    """
    Get signals for a campaign with optional filtering.

    - **campaign_id**: Campaign ID
    - **min_relevance**: Minimum relevance score (0-1)
    - **source**: Filter by source platform (google, meta, linkedin, etc.)
    - **limit**: Max number of signals to return

    Returns list of signals ordered by relevance score.
    """
    # Verify campaign exists and belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    orchestrator = SignalOrchestrator(db)
    signals = orchestrator.get_campaign_signals(
        campaign_id=campaign_id,
        min_relevance=min_relevance,
        source=source,
        limit=limit
    )

    # Convert to response format
    return [
        SignalResponse(
            id=signal.id,
            campaign_id=signal.campaign_id,
            source=signal.source,
            search_method=signal.search_method,
            query=signal.query,
            evidence=signal.evidence,
            relevance_score=signal.relevance_score,
            created_at=signal.created_at.isoformat()
        )
        for signal in signals
    ]


@router.get("/cartridges", response_model=List[str])
def list_available_cartridges():
    """
    List all available signal cartridges.

    Returns list of cartridge names that can be used for signal collection.
    """
    from app.services.signals.base import CartridgeRegistry
    return CartridgeRegistry.list_names()
