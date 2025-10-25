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


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema."""
    id: int
    workspace_id: Optional[UUID]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
