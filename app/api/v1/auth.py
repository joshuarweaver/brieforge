"""Authentication endpoints using API keys."""
import secrets
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import generate_api_key
from app.core.config import settings
from app.api.deps import get_current_user
from app.models import User, Workspace, APIKey
from app.schemas import (
    UserCreate,
    UserResponse,
    WorkspaceResponse,
    APIKeyCreate,
    APIKeyMetadata,
    APIKeyWithSecretResponse,
    RegistrationResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _require_admin_token(admin_token: Optional[str]) -> None:
    """Validate provided admin token when provisioning keys."""
    expected = settings.ADMIN_PROVISION_TOKEN
    if not expected:
        return

    if not admin_token or not secrets.compare_digest(admin_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin provisioning token",
        )


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")
):
    """Register a new user and issue their first API key."""
    _require_admin_token(admin_token)

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        email=user_data.email,
        hashed_password=None,
        role="admin",
    )
    db.add(new_user)
    db.flush()

    workspace_name = user_data.workspace_name or f"{user_data.email.split('@')[0]}'s Workspace"
    workspace = Workspace(
        name=workspace_name,
        owner_id=new_user.id,
        settings={}
    )
    db.add(workspace)
    db.flush()

    new_user.workspace_id = workspace.id

    key_id, plain_api_key, hashed_secret = generate_api_key()
    api_key_record = APIKey(
        id=key_id,
        name="Default key",
        hashed_key=hashed_secret,
        user_id=new_user.id,
    )
    db.add(api_key_record)

    db.commit()
    db.refresh(new_user)
    db.refresh(workspace)
    db.refresh(api_key_record)

    return RegistrationResponse(
        api_key=plain_api_key,
        key=APIKeyMetadata.model_validate(api_key_record),
        user=UserResponse.model_validate(new_user),
        workspace=WorkspaceResponse.model_validate(workspace),
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse.model_validate(current_user)


@router.get("/api-keys", response_model=List[APIKeyMetadata])
def list_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List active API keys for the current user."""
    keys = (
        db.query(APIKey)
        .filter(APIKey.user_id == current_user.id, APIKey.revoked_at.is_(None))
        .order_by(APIKey.created_at.asc())
        .all()
    )
    return [APIKeyMetadata.model_validate(key) for key in keys]


@router.post("/api-keys", response_model=APIKeyWithSecretResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")
):
    """Create an additional API key for the authenticated user."""
    _require_admin_token(admin_token)

    key_name = payload.name or f"Key created at {datetime.utcnow().isoformat(timespec='seconds')}Z"
    key_id, plain_api_key, hashed_secret = generate_api_key()
    api_key_record = APIKey(
        id=key_id,
        name=key_name,
        hashed_key=hashed_secret,
        user_id=current_user.id,
    )
    db.add(api_key_record)
    db.commit()
    db.refresh(api_key_record)

    return APIKeyWithSecretResponse(
        api_key=plain_api_key,
        key=APIKeyMetadata.model_validate(api_key_record),
    )


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke an API key."""
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == current_user.id)
        .first()
    )

    if api_key is None or api_key.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    api_key.revoked_at = datetime.utcnow()
    db.add(api_key)
    db.commit()
