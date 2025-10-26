"""User and Workspace Pydantic schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr


# Workspace Schemas
class WorkspaceBase(BaseModel):
    """Base workspace schema."""
    name: str
    settings: Optional[Dict[str, Any]] = {}


class WorkspaceCreate(WorkspaceBase):
    """Workspace creation schema."""
    pass


class WorkspaceUpdate(BaseModel):
    """Workspace update schema."""
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceResponse(WorkspaceBase):
    """Workspace response schema."""
    id: UUID
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: str
    last_name: str
    phone: str


class UserCreate(UserBase):
    """User creation schema."""
    workspace_name: Optional[str] = None
    password: str


class UserResponse(UserBase):
    """User response schema."""
    id: int
    workspace_id: Optional[UUID]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    """API key creation payload."""
    name: Optional[str] = None


class APIKeyMetadata(BaseModel):
    """API key metadata (no secret)."""
    id: UUID
    name: str
    created_at: datetime
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIKeyWithSecretResponse(BaseModel):
    """Response when a new API key secret is issued."""
    api_key: str
    key: APIKeyMetadata


class RegistrationResponse(APIKeyWithSecretResponse):
    """Registration response with associated resources."""
    user: UserResponse
    workspace: WorkspaceResponse
