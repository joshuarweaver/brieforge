"""Compliance checks and policy enforcement."""
from typing import Dict, Any
from sqlalchemy.orm import Session


class ComplianceError(Exception):
    """Raised when an action violates compliance rules."""


class ComplianceService:
    """Simple rule-based compliance guard."""

    def __init__(self, db: Session):
        self.db = db

    def ensure_allowed(self, *, workspace_id, event_type: str, context: Dict[str, Any] | None = None) -> None:
        """Placeholder for more advanced compliance logic."""
        # In a real system, this would check persisted workspace policies, budgets, etc.
        # Hook provided for future per-workspace rules.
        # Currently acts as an extension point, so it simply passes.
        return None
