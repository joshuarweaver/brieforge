"""Observability and compliance log models."""
from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, JSON, String, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class AuditLog(Base):
    """Audit log entry for platform operations."""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    source = Column(String, nullable=False)
    details = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
