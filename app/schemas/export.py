"""Export schemas."""
from typing import Any, Dict
from pydantic import BaseModel


class ExportPreviewResponse(BaseModel):
    """Response representing an export payload preview."""
    platform: str
    dry_run: bool
    payload: Dict[str, Any]
    blueprint: Dict[str, Any]
