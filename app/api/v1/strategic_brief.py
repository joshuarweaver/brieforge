"""Strategic Brief API endpoints."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Campaign, StrategicBrief
from app.services.strategic_brief_generator import StrategicBriefGenerator, StrategicBriefError
from app.services.llm import LLMProvider

router = APIRouter()


# Request/Response models
class GenerateBriefRequest(BaseModel):
    """Request to generate a strategic brief."""
    llm_provider: LLMProvider = LLMProvider.CLAUDE
    include_analysis_ids: Optional[List[UUID]] = None
    custom_instructions: Optional[str] = None
    async_mode: bool = False  # Run in background


class StrategicBriefResponse(BaseModel):
    """Strategic brief response."""
    id: UUID
    campaign_id: UUID
    status: str
    version: int
    content: dict
    custom_instructions: Optional[str]
    llm_provider: Optional[str]
    llm_model: Optional[str]
    tokens_used: Optional[int]
    error_message: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, brief: StrategicBrief):
        """Convert ORM model to response."""
        return cls(
            id=brief.id,
            campaign_id=brief.campaign_id,
            status=brief.status,
            version=brief.version,
            content=brief.content,
            custom_instructions=brief.custom_instructions,
            llm_provider=brief.llm_provider,
            llm_model=brief.llm_model,
            tokens_used=brief.tokens_used,
            error_message=brief.error_message,
            created_at=brief.created_at.isoformat(),
            updated_at=brief.updated_at.isoformat()
        )


def run_brief_generation_task(
    campaign_id: UUID,
    llm_provider: LLMProvider,
    include_analysis_ids: Optional[List[UUID]],
    custom_instructions: Optional[str],
    db: Session
):
    """Background task to generate strategic brief."""
    try:
        generator = StrategicBriefGenerator(db=db, llm_provider=llm_provider)

        # Convert UUIDs to strings for the generator
        analysis_ids_str = [str(aid) for aid in include_analysis_ids] if include_analysis_ids else None

        result = generator.generate_brief(
            campaign_id=str(campaign_id),
            include_analysis_ids=analysis_ids_str,
            custom_instructions=custom_instructions
        )

        # Create brief record
        brief = StrategicBrief(
            campaign_id=campaign_id,
            status="completed",
            llm_provider=llm_provider.value,
            llm_model=result['metadata']['llm_model'],
            tokens_used=result['brief_content']['tokens_used'],
            content=result['brief_content'],
            custom_instructions=custom_instructions,
            version=1
        )

        db.add(brief)
        db.commit()

    except Exception as e:
        # Create failed brief record
        brief = StrategicBrief(
            campaign_id=campaign_id,
            status="failed",
            error_message=str(e),
            content={},
            custom_instructions=custom_instructions,
            version=1
        )
        db.add(brief)
        db.commit()
        print(f"Background brief generation failed: {str(e)}")


@router.post(
    "/campaigns/{campaign_id}/strategic-brief",
    response_model=StrategicBriefResponse,
    status_code=status.HTTP_200_OK
)
def generate_strategic_brief(
    campaign_id: UUID,
    request: GenerateBriefRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive 2-page strategic brief for a campaign.

    This endpoint uses AI to synthesize campaign data, signal intelligence,
    and analysis insights into a professional strategic marketing brief.

    **The brief includes:**
    - Executive Summary
    - Market Context & Competitive Landscape
    - Target Audience Deep Dive
    - Messaging Strategy
    - Channel Strategy & Tactics
    - Creative Direction
    - Success Metrics & KPIs

    **Parameters:**
    - `llm_provider`: LLM provider (claude or openai)
    - `include_analysis_ids`: Optional list of specific analysis IDs to include
    - `custom_instructions`: Optional custom instructions for the brief
    - `async_mode`: If true, runs in background and returns immediately

    **Prerequisites:**
    - Campaign must have completed signal analyses
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
            # Create pending brief and run in background
            brief = StrategicBrief(
                campaign_id=campaign_id,
                status="pending",
                llm_provider=request.llm_provider.value,
                content={},
                custom_instructions=request.custom_instructions,
                version=1
            )
            db.add(brief)
            db.commit()
            db.refresh(brief)

            # Schedule background task
            background_tasks.add_task(
                run_brief_generation_task,
                campaign_id=campaign_id,
                llm_provider=request.llm_provider,
                include_analysis_ids=request.include_analysis_ids,
                custom_instructions=request.custom_instructions,
                db=db
            )

            return StrategicBriefResponse.from_orm(brief)
        else:
            # Run synchronously
            generator = StrategicBriefGenerator(db=db, llm_provider=request.llm_provider)

            # Convert UUIDs to strings
            analysis_ids_str = [str(aid) for aid in request.include_analysis_ids] if request.include_analysis_ids else None

            result = generator.generate_brief(
                campaign_id=str(campaign_id),
                include_analysis_ids=analysis_ids_str,
                custom_instructions=request.custom_instructions
            )

            # Create brief record
            brief = StrategicBrief(
                campaign_id=campaign_id,
                status="completed",
                llm_provider=request.llm_provider.value,
                llm_model=result['metadata']['llm_model'],
                tokens_used=result['brief_content']['tokens_used'],
                content=result['brief_content'],
                custom_instructions=request.custom_instructions,
                version=1
            )

            db.add(brief)
            db.commit()
            db.refresh(brief)

            return StrategicBriefResponse.from_orm(brief)

    except StrategicBriefError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Brief generation failed: {str(e)}"
        )


@router.get(
    "/campaigns/{campaign_id}/strategic-briefs",
    response_model=List[StrategicBriefResponse]
)
def list_campaign_briefs(
    campaign_id: UUID,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all strategic briefs for a campaign.

    **Query Parameters:**
    - `limit`: Max briefs to return (default: 10)
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
    query = db.query(StrategicBrief).filter(
        StrategicBrief.campaign_id == campaign_id
    ).order_by(StrategicBrief.created_at.desc())

    if limit:
        query = query.limit(limit)

    briefs = query.all()
    return [StrategicBriefResponse.from_orm(b) for b in briefs]


@router.get(
    "/strategic-briefs/{brief_id}",
    response_model=StrategicBriefResponse
)
def get_strategic_brief(
    brief_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific strategic brief by ID."""
    brief = db.query(StrategicBrief).filter(
        StrategicBrief.id == brief_id
    ).first()

    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategic brief {brief_id} not found"
        )

    # Check campaign belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == brief.campaign_id,
        Campaign.workspace_id == current_user.workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategic brief not found"
        )

    return StrategicBriefResponse.from_orm(brief)


@router.delete(
    "/strategic-briefs/{brief_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_strategic_brief(
    brief_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a strategic brief."""
    brief = db.query(StrategicBrief).filter(
        StrategicBrief.id == brief_id
    ).first()

    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategic brief {brief_id} not found"
        )

    # Check campaign belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == brief.campaign_id,
        Campaign.workspace_id == current_user.workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategic brief not found"
        )

    db.delete(brief)
    db.commit()
