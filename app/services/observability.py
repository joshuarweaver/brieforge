"""Observability and audit logging utilities."""
from typing import Any, Dict, Optional
from datetime import datetime
import uuid
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
        serialized_details = self._make_serializable(details or {})
        log = AuditLog(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type=event_type,
            source=source,
            details=serialized_details,
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

    def _make_serializable(self, value: Any) -> Any:
        """Convert nested structures into JSON-serializable equivalents."""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, uuid.UUID):
            return str(value)

        if isinstance(value, dict):
            return {k: self._make_serializable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._make_serializable(v) for v in value]

        return str(value)
