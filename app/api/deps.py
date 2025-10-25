"""API dependencies."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import split_api_key, verify_secret
from app.models import User, APIKey


def get_current_user(
    api_key_header: Optional[str] = Header(default=None, alias=settings.API_KEY_HEADER_NAME),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    try:
        key_id, secret = split_api_key(api_key_header)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    api_key: Optional[APIKey] = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.revoked_at.is_(None))
        .first()
    )

    if api_key is None or not verify_secret(secret, api_key.hashed_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    user = api_key.user
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    api_key.last_used_at = datetime.utcnow()

    return user


def get_current_workspace(current_user: User = Depends(get_current_user)) -> UUID:
    """Get current user's workspace ID."""
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not assigned to a workspace",
        )
    return current_user.workspace_id
