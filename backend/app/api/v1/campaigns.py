"""Campaign endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models import User, Campaign
from app.schemas import CampaignCreate, CampaignUpdate, CampaignResponse

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=List[CampaignResponse])
def list_campaigns(
    workspace_id: int = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List campaigns in workspace."""
    campaigns = db.query(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).offset(skip).limit(limit).all()

    return campaigns


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign_data: CampaignCreate,
    workspace_id: int = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Create a new campaign."""
    campaign = Campaign(
        workspace_id=workspace_id,
        name=campaign_data.name,
        brief=campaign_data.brief.model_dump(),
        status="draft"
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    workspace_id: int = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Get campaign by ID."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    workspace_id: int = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Update campaign."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Update fields
    if campaign_data.name is not None:
        campaign.name = campaign_data.name
    if campaign_data.brief is not None:
        campaign.brief = campaign_data.brief.model_dump()
    if campaign_data.status is not None:
        campaign.status = campaign_data.status

    db.commit()
    db.refresh(campaign)

    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: int,
    workspace_id: int = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Delete campaign."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    db.delete(campaign)
    db.commit()
