"""Recording profile management API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List

from app.core.profile_manager import profile_manager

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


class ProfileInfoResponse(BaseModel):
    name: str = Field(..., description="Profile name")
    description: str = Field(..., description="Human-readable description")
    source: str = Field(..., description="Source file path")


@router.get("", response_model=List[ProfileInfoResponse])
async def list_profiles():
    """List available recording profiles."""
    profiles = profile_manager.list_profiles()
    return [ProfileInfoResponse(name=p.name, description=p.description, source=p.source) for p in profiles]
