"""Campaign export endpoints."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models import Campaign, User
from app.schemas import ExportPreviewResponse
from app.services.export.service import AdExportService

router = APIRouter(prefix="/campaigns", tags=["exports"])


@router.post("/{campaign_id}/exports/{platform}", response_model=ExportPreviewResponse, status_code=status.HTTP_200_OK)
def generate_export_payload(
    campaign_id: UUID,
    platform: str,
    dry_run: bool = Query(True, description="If true, no API calls are made"),
    workspace_id = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Build export payloads for supported ad platforms."""
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == workspace_id
    ).first()

    if campaign is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    service = AdExportService(db)
    try:
        export_payload = service.export_campaign(
            campaign=campaign,
            workspace_id=workspace_id,
            user_id=current_user.id,
            platform=platform.lower(),
            dry_run=dry_run,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    return ExportPreviewResponse(**export_payload)
