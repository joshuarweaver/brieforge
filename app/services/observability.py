"""Observability and audit logging utilities."""
from typing import Any, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import AuditLog


class ObservabilityService:
    """Utility for recording audit/observability events."""

    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        *,
        workspace_id,
        user_id: int,
        event_type: str,
        source: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Persist an audit log entry."""
        log = AuditLog(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type=event_type,
            source=source,
            details=details or {},
            created_at=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_events(
        self,
        *,
        workspace_id,
        limit: int = 100,
        event_type: Optional[str] = None,
    ):
        """Fetch recent events for a workspace."""
        query = (
            self.db.query(AuditLog)
            .filter(AuditLog.workspace_id == workspace_id)
            .order_by(AuditLog.created_at.desc())
        )
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        return query.limit(limit).all()
