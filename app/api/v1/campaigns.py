"""Campaign endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models import User, Campaign
from app.schemas import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignBlueprint,
    CampaignBlueprintListItem,
)
from app.services.campaign_blueprint import CampaignBlueprintService

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
    campaign_id: UUID,
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
    campaign_id: UUID,
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
    campaign_id: UUID,
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


@router.post("/{campaign_id}/blueprint", response_model=CampaignBlueprint)
def generate_campaign_blueprint(
    campaign_id: UUID,
    workspace_id: int = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    persist: bool = Query(True, description="Persist the blueprint artifact"),
):
    """Generate a structured campaign blueprint from signals."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    service = CampaignBlueprintService(db)
    blueprint = service.generate_blueprint(
        campaign=campaign,
        workspace_id=workspace_id,
        user_id=current_user.id,
        persist=persist,
    )
    return CampaignBlueprint.model_validate(blueprint)


@router.get("/{campaign_id}/blueprints", response_model=List[CampaignBlueprintListItem])
def list_campaign_blueprints(
    campaign_id: UUID,
    workspace_id: int = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List stored blueprint artifacts for a campaign."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    service = CampaignBlueprintService(db)
    artifacts = service.list_blueprints(campaign_id)
    return [
        CampaignBlueprintListItem(
            id=artifact.id,
            campaign_id=artifact.campaign_id,
            summary=artifact.summary,
            created_at=artifact.created_at,
        )
        for artifact in artifacts
    ]


@router.get("/{campaign_id}/blueprints/{blueprint_id}", response_model=CampaignBlueprint)
def get_campaign_blueprint(
    campaign_id: UUID,
    blueprint_id: UUID,
    workspace_id: int = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a stored blueprint artifact."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    service = CampaignBlueprintService(db)
    artifact = service.get_blueprint(blueprint_id)

    if artifact is None or artifact.campaign_id != campaign_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blueprint not found",
        )

    blueprint = artifact.blueprint.copy()
    blueprint["artifact_id"] = str(artifact.id)
    return CampaignBlueprint.model_validate(blueprint)
