"""Analysis API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Campaign, SignalAnalysis, SignalAnalysisType, SignalAnalysisStatus
from app.services.signal_analyzer import SignalAnalyzer, SignalAnalyzerError
from app.services.llm import LLMProvider

router = APIRouter()


# Request/Response models
class AnalyzeRequest(BaseModel):
    """Request to analyze campaign signals."""
    analysis_type: SignalAnalysisType = SignalAnalysisType.COMPREHENSIVE
    llm_provider: LLMProvider = LLMProvider.CLAUDE
    max_signals: Optional[int] = None
    min_relevance: float = 0.0
    async_mode: bool = False  # Run in background


class SignalAnalysisResponse(BaseModel):
    """Signal analysis response."""
    id: int
    campaign_id: int
    analysis_type: str
    status: str
    llm_provider: Optional[str]
    llm_model: Optional[str]
    tokens_used: Optional[int]
    insights: Optional[dict]
    error_message: Optional[str]
    created_at: str
    completed_at: Optional[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, analysis: SignalAnalysis):
        """Convert ORM model to response."""
        return cls(
            id=analysis.id,
            campaign_id=analysis.campaign_id,
            analysis_type=analysis.analysis_type.value,
            status=analysis.status.value,
            llm_provider=analysis.llm_provider,
            llm_model=analysis.llm_model,
            tokens_used=analysis.tokens_used,
            insights=analysis.insights,
            error_message=analysis.error_message,
            created_at=analysis.created_at.isoformat(),
            completed_at=analysis.completed_at.isoformat() if analysis.completed_at else None
        )


def run_analysis_task(
    campaign_id: int,
    analysis_type: SignalAnalysisType,
    llm_provider: LLMProvider,
    max_signals: Optional[int],
    min_relevance: float,
    db: Session
):
    """Background task to run analysis."""
    try:
        analyzer = SignalAnalyzer(db=db, llm_provider=llm_provider)
        analyzer.analyze(
            campaign_id=campaign_id,
            analysis_type=analysis_type,
            max_signals=max_signals,
            min_relevance=min_relevance
        )
    except Exception as e:
        print(f"Background analysis failed: {str(e)}")


@router.post(
    "/campaigns/{campaign_id}/analyze",
    response_model=SignalAnalysisResponse,
    status_code=status.HTTP_200_OK
)
def analyze_campaign_signals(
    campaign_id: int,
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze collected signals for a campaign using AI.

    This endpoint triggers AI analysis of the signals collected for a campaign.
    The analysis can be run synchronously or asynchronously (background).

    **Analysis Types:**
    - `comprehensive`: Full analysis across all dimensions
    - `competitor`: Competitor strategy analysis
    - `audience`: Audience insights and pain points
    - `messaging`: Messaging patterns analysis
    - `creative`: Creative recommendations
    - `trends`: Market trends analysis

    **Parameters:**
    - `analysis_type`: Type of analysis to perform
    - `llm_provider`: LLM provider (claude or openai)
    - `max_signals`: Max signals to include (null = all)
    - `min_relevance`: Minimum relevance score filter
    - `async_mode`: If true, runs in background and returns immediately
    """
    # Check campaign exists and belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == current_user.workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    try:
        if request.async_mode:
            # Create pending analysis and run in background
            analysis = SignalAnalysis(
                campaign_id=campaign_id,
                analysis_type=request.analysis_type,
                status=SignalAnalysisStatus.PENDING,
                llm_provider=request.llm_provider.value
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)

            # Schedule background task
            background_tasks.add_task(
                run_analysis_task,
                campaign_id=campaign_id,
                analysis_type=request.analysis_type,
                llm_provider=request.llm_provider,
                max_signals=request.max_signals,
                min_relevance=request.min_relevance,
                db=db
            )

            return SignalAnalysisResponse.from_orm(analysis)
        else:
            # Run synchronously
            analyzer = SignalAnalyzer(db=db, llm_provider=request.llm_provider)
            analysis = analyzer.analyze(
                campaign_id=campaign_id,
                analysis_type=request.analysis_type,
                max_signals=request.max_signals,
                min_relevance=request.min_relevance
            )

            return SignalAnalysisResponse.from_orm(analysis)

    except SignalAnalyzerError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get(
    "/campaigns/{campaign_id}/signal-analyses",
    response_model=List[SignalAnalysisResponse]
)
def list_campaign_analyses(
    campaign_id: int,
    analysis_type: Optional[SignalAnalysisType] = None,
    status_filter: Optional[SignalAnalysisStatus] = None,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all signal analyses for a campaign.

    **Query Parameters:**
    - `analysis_type`: Filter by analysis type
    - `status_filter`: Filter by status (pending, in_progress, completed, failed)
    - `limit`: Max analyses to return
    """
    # Check campaign exists and belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == current_user.workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    # Build query
    query = db.query(SignalAnalysis).filter(
        SignalAnalysis.campaign_id == campaign_id
    )

    if analysis_type:
        query = query.filter(SignalAnalysis.analysis_type == analysis_type)

    if status_filter:
        query = query.filter(SignalAnalysis.status == status_filter)

    query = query.order_by(SignalAnalysis.created_at.desc())

    if limit:
        query = query.limit(limit)

    analyses = query.all()
    return [SignalAnalysisResponse.from_orm(a) for a in analyses]


@router.get(
    "/signal-analyses/{analysis_id}",
    response_model=SignalAnalysisResponse
)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific signal analysis by ID."""
    analysis = db.query(SignalAnalysis).filter(
        SignalAnalysis.id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {analysis_id} not found"
        )

    # Check campaign belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == analysis.campaign_id,
        Campaign.workspace_id == current_user.workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return SignalAnalysisResponse.from_orm(analysis)


@router.delete(
    "/signal-analyses/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a signal analysis."""
    analysis = db.query(SignalAnalysis).filter(
        SignalAnalysis.id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {analysis_id} not found"
        )

    # Check campaign belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == analysis.campaign_id,
        Campaign.workspace_id == current_user.workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    db.delete(analysis)
    db.commit()

    return None
