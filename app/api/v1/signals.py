"""Signal collection API endpoints."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models import User, Campaign, Signal, SignalEnrichment
from app.services.signal_orchestrator import SignalOrchestrator
from app.services.signal_enrichment_service import SignalEnrichmentService
from app.schemas import SignalEnrichmentSummary, SignalEnrichmentResponse

router = APIRouter(prefix="/campaigns", tags=["signals"])


class CollectSignalsRequest(BaseModel):
    """Request to collect signals for a campaign."""
    cartridge_names: Optional[List[str]] = None  # None = all cartridges
    max_queries_per_cartridge: int = 10


class CollectSignalsResponse(BaseModel):
    """Response from signal collection."""
    campaign_id: UUID
    cartridges_run: int
    total_signals: int
    errors: List[dict]
    timestamp: str
    deduplicated_urls: int


class SignalResponse(BaseModel):
    """Signal response schema."""
    id: UUID
    campaign_id: UUID
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
    campaign_id: UUID,
    request: CollectSignalsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace_id: UUID = Depends(get_current_workspace)
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
            max_queries_per_cartridge=request.max_queries_per_cartridge,
            user_id=current_user.id,
            workspace_id=workspace_id,
        )
        return CollectSignalsResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signal collection failed: {str(e)}"
        )


@router.post("/{campaign_id}/signals/enrich", response_model=SignalEnrichmentSummary)
def enrich_signals(
    campaign_id: UUID,
    limit: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace_id: UUID = Depends(get_current_workspace)
):
    """
    Derive enriched metadata (entities, sentiment, trends) for campaign signals.

    - **campaign_id**: Campaign to enrich
    - **limit**: Optional limit of most recent signals to process
    """
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    service = SignalEnrichmentService(db)
    summary = service.enrich_campaign(
        campaign_id=campaign_id,
        workspace_id=workspace_id,
        user_id=current_user.id,
        limit=limit
    )
    return SignalEnrichmentSummary(**summary)


@router.get("/{campaign_id}/signals", response_model=List[SignalResponse])
def get_campaign_signals(
    campaign_id: UUID,
    min_relevance: float = 0.0,
    source: Optional[str] = None,
    limit: Optional[int] = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace_id: UUID = Depends(get_current_workspace)
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

    try:
        signals = orchestrator.get_campaign_signals(
            campaign_id=campaign_id,
            min_relevance=min_relevance,
            source=source,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
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


@router.get("/signals/{signal_id}/enrichments", response_model=List[SignalEnrichmentResponse])
def list_signal_enrichments(
    signal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace_id: UUID = Depends(get_current_workspace)
):
    """List enrichment records for a specific signal."""
    signal = (
        db.query(Signal)
        .join(Campaign, Signal.campaign_id == Campaign.id)
        .filter(
            Signal.id == signal_id,
            Campaign.workspace_id == workspace_id
        )
        .first()
    )

    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )

    enrichments = (
        db.query(SignalEnrichment)
        .filter(SignalEnrichment.signal_id == signal_id)
        .order_by(SignalEnrichment.created_at.desc())
        .all()
    )

    return [SignalEnrichmentResponse.model_validate(enrichment) for enrichment in enrichments]


@router.get("/cartridges", response_model=List[str])
def list_available_cartridges():
    """
    List all available signal cartridges.

    Returns list of cartridge names that can be used for signal collection.
    """
    from app.services.signals.base import CartridgeRegistry
    return CartridgeRegistry.list_names()
