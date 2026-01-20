"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SessionConfig(BaseModel):
    """Request schema for creating a session."""
    url: Optional[str] = Field(None, description="Starting URL (optional)")
    browser: str = Field("chrome", description="Browser type (chrome, edge, firefox)")
    incognito: bool = Field(False, description="Whether to use incognito mode")
    user_data_dir: Optional[str] = Field(None, description="Path to user data directory (optional)")
    window_width: Optional[int] = Field(None, description="Browser window width (optional, default: 1920)")
    window_height: Optional[int] = Field(None, description="Browser window height (optional, default: 1080)")
    profile: Optional[str] = Field("default", description="Recording profile name (from backend/config/profiles/*.yaml)")


class SessionStartResponse(BaseModel):
    """Response schema for starting a session."""
    session_id: str = Field(..., description="Run ID of the created session")
    run_id: str = Field(..., description="Unique run ID of the session")
    status: str = Field(..., description="Session status")


class SessionStopResponse(BaseModel):
    """Response schema for stopping a session."""
    session_id: str = Field(..., description="Run ID of the session")
    run_id: str = Field(..., description="Unique run ID of the session")
    status: str = Field(..., description="Session status")
    event_count: int = Field(..., description="Total number of events captured")


class SessionResponse(BaseModel):
    """Response schema for session details."""
    run_id: str
    start_url: Optional[str] = None
    start_time: str
    end_time: Optional[str] = None
    status: str
    browser_type: str
    incognito: bool
    event_count: int
    user_data_dir: Optional[str] = None


class SessionListResponse(BaseModel):
    """Response schema for session list."""
    sessions: List[SessionResponse]
    total: int = Field(..., description="Total number of sessions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of sessions per page")


class LocatorModel(BaseModel):
    """Schema for locator information."""
    strategy: str = Field(..., description="Locator strategy (role, label, css, xpath, etc.)")
    selector: str = Field(..., description="Locator selector string")
    stability: Optional[str] = Field(None, description="Stability rating (high, medium, low)")


class EventResponse(BaseModel):
    """Response schema for event details."""
    seq: int
    timestamp: str
    event_type: str
    page_url: str
    page_title: Optional[str] = None
    target_data: Optional[Dict[str, Any]] = None
    locators: Optional[List[Dict[str, Any]]] = None
    network_data: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None
    iframe_context: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None


class EventListResponse(BaseModel):
    """Response schema for event list."""
    events: List[EventResponse]
    total: int = Field(..., description="Total number of events")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of events per page")


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
