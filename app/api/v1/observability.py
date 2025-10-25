"""Observability endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models import User
from app.services.observability import ObservabilityService

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/events", response_model=List[dict])
def list_observability_events(
    limit: int = Query(50, ge=1, le=200),
    event_type: Optional[str] = None,
    workspace_id = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return recent audit/observability events for the workspace."""
    service = ObservabilityService(db)
    events = service.list_events(
        workspace_id=workspace_id,
        limit=limit,
        event_type=event_type,
    )
    return [
        {
            "id": str(event.id),
            "workspace_id": str(event.workspace_id),
            "user_id": event.user_id,
            "event_type": event.event_type,
            "source": event.source,
            "details": event.details,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]
