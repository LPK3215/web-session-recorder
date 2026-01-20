"""Configuration management API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging

from app.core.config import config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigUpdateRequest(BaseModel):
    """Request schema for updating configuration."""
    file: str = Field(..., description="Config file name (app, browser, recorder, database, locators)")
    content: str = Field(..., description="YAML content as string")


class ConfigResponse(BaseModel):
    """Response schema for configuration retrieval."""
    app: Dict[str, Any] = Field(..., description="Application configuration")
    browser: Dict[str, Any] = Field(..., description="Browser configuration")
    recorder: Dict[str, Any] = Field(..., description="Recorder configuration")
    database: Dict[str, Any] = Field(..., description="Database configuration")
    locators: Dict[str, Any] = Field(..., description="Locators configuration")


class ConfigUpdateResponse(BaseModel):
    """Response schema for configuration update."""
    status: str = Field(..., description="Status of the update (success or error)")
    message: str = Field(..., description="Detailed message")


class UrlPreset(BaseModel):
    """URL preset schema."""
    name: str = Field(..., description="Display name of the URL preset")
    url: str = Field(..., description="URL value")


class WindowSizePreset(BaseModel):
    """Window size preset schema."""
    name: str = Field(..., description="Display name of the window size preset")
    width: int = Field(..., description="Window width in pixels")
    height: int = Field(..., description="Window height in pixels")


class RecorderPresetsResponse(BaseModel):
    """Response schema for recorder presets."""
    default_urls: list[UrlPreset] = Field(..., description="List of default URL presets")
    window_sizes: list[WindowSizePreset] = Field(..., description="List of window size presets")


@router.get("", response_model=ConfigResponse)
async def get_config():
    """
    Get all configuration files.
    
    Returns all loaded YAML configuration as a single JSON object with keys:
    - app: Application and server settings
    - browser: Browser paths and launch options
    - recorder: Recording strategy and event capture settings
    - database: Database connection and retention policy
    - locators: Locator generation strategies and priorities
    
    Returns:
        ConfigResponse with all configuration data
    
    Raises:
        HTTPException: If configuration loading fails
    """
    try:
        all_configs = config.get_all()
        
        # Ensure all expected config files are present
        expected_configs = ['app', 'browser', 'recorder', 'database', 'locators']
        response_data = {}
        
        for config_name in expected_configs:
            response_data[config_name] = all_configs.get(config_name, {})
        
        return ConfigResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error retrieving configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve configuration: {str(e)}")


@router.get("/presets", response_model=RecorderPresetsResponse)
async def get_recorder_presets():
    """
    Get recorder presets (default URLs and window sizes).
    
    Returns:
        RecorderPresetsResponse with default_urls and window_sizes
    
    Raises:
        HTTPException: If configuration loading fails
    """
    try:
        # Get default URLs
        default_urls = config.get('recorder', 'recorder.default_urls', [])
        url_presets = [UrlPreset(**url) for url in default_urls]
        
        # Get window sizes
        window_sizes = config.get('recorder', 'recorder.window_sizes', [])
        size_presets = [WindowSizePreset(**size) for size in window_sizes]
        
        return RecorderPresetsResponse(
            default_urls=url_presets,
            window_sizes=size_presets
        )
        
    except Exception as e:
        logger.error(f"Error retrieving recorder presets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve recorder presets: {str(e)}")


@router.put("", response_model=ConfigUpdateResponse)
async def update_config(request: ConfigUpdateRequest):
    """
    Update a configuration file.
    
    This endpoint:
    1. Validates the YAML syntax
    2. Writes the content to the appropriate config file
    3. Reloads the configuration in memory
    
    Args:
        request: ConfigUpdateRequest with file name and YAML content
    
    Returns:
        ConfigUpdateResponse with status and message
    
    Raises:
        HTTPException: If validation fails or file write fails
    """
    try:
        # Validate file name
        valid_files = ['app', 'browser', 'recorder', 'database', 'locators']
        if request.file not in valid_files:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid config file name. Must be one of: {', '.join(valid_files)}"
            )
        
        logger.info(f"Updating configuration file: {request.file}.yaml")
        
        # Save configuration
        success = config.save_config(request.file, request.content)
        
        if not success:
            return ConfigUpdateResponse(
                status="error",
                message="Failed to save configuration. Check YAML syntax and file permissions."
            )
        
        return ConfigUpdateResponse(
            status="success",
            message=f"Configuration file '{request.file}.yaml' updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")
