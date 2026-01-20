"""Session management API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
import json

from app.api.schemas import (
    SessionConfig,
    SessionStartResponse,
    SessionStopResponse,
    SessionResponse,
    SessionListResponse,
    EventListResponse,
    ErrorResponse
)
from app.core.session_manager import SessionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


@router.post("/start", response_model=SessionStartResponse, responses={500: {"model": ErrorResponse}})
async def start_session(config: SessionConfig):
    """
    Start a new recording session.
    
    This endpoint:
    1. Creates a new session folder
    2. Launches the browser with specified configuration
    3. Navigates to the starting URL (if provided)
    4. Begins capturing events
    
    Args:
        config: Session configuration (url, browser, incognito, user_data_dir)
    
    Returns:
        SessionStartResponse with run_id and status
    
    Raises:
        HTTPException: If session creation or browser launch fails
    """
    try:
        logger.info(f"Starting session with config: {config.dict()}")
        
        session_manager = get_session_manager()
        
        # Create session
        session_data = await session_manager.create_session(
            url=config.url,
            browser_type=config.browser,
            incognito=config.incognito,
            user_data_dir=config.user_data_dir,
            window_width=config.window_width,
            window_height=config.window_height
        )
        
        # Start recording
        await session_manager.start_recording(session_data['run_id'])
        
        return SessionStartResponse(
            session_id=session_data['run_id'],  # Use run_id as session_id
            run_id=session_data['run_id'],
            status="started"
        )
        
    except FileNotFoundError as e:
        logger.error(f"File not found error starting session: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"配置文件缺失: {str(e)}"
        )
    except PermissionError as e:
        logger.error(f"Permission error starting session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"权限错误: {str(e)}。请检查浏览器路径和文件权限。"
        )
    except Exception as e:
        logger.error(f"Error starting session: {e}", exc_info=True)
        error_msg = str(e)
        
        # Provide more helpful error messages for common issues
        if "browser" in error_msg.lower() or "executable" in error_msg.lower():
            error_msg = f"浏览器启动失败: {error_msg}。请检查 config/browser.yaml 中的浏览器路径配置。"
        elif "playwright" in error_msg.lower():
            error_msg = f"Playwright 错误: {error_msg}。请确保已运行 'playwright install' 安装浏览器。"
        elif "timeout" in error_msg.lower():
            error_msg = f"超时错误: {error_msg}。浏览器启动超时，请重试。"
        
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/{session_id}/stop", response_model=SessionStopResponse, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def stop_session(session_id: str):
    """
    Stop a recording session.
    
    This endpoint:
    1. Stops event capture
    2. Closes the browser
    3. Saves the session to file
    4. Closes WebSocket connections
    
    Args:
        session_id: Run ID of the session to stop
    
    Returns:
        SessionStopResponse with run_id, status, and event_count
    
    Raises:
        HTTPException: If session not found or stop fails
    """
    try:
        logger.info(f"Stopping session: {session_id}")
        
        session_manager = get_session_manager()
        
        # Check if session exists
        session_data = session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Stop recording
        updated_session = await session_manager.stop_recording(session_id)
        
        return SessionStopResponse(
            session_id=updated_session['run_id'],
            run_id=updated_session['run_id'],
            status=updated_session['status'],
            event_count=updated_session.get('event_count', 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of sessions per page"),
    status: Optional[str] = Query(None, description="Filter by status (started, stopped, error)"),
    browser_type: Optional[str] = Query(None, description="Filter by browser type (chrome, edge, firefox)"),
    url: Optional[str] = Query(None, description="Filter by URL (partial match)"),
    start_date: Optional[str] = Query(None, description="Filter by start date (ISO format: YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (ISO format: YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in session ID or URL"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)")
):
    """
    List all recording sessions with pagination and filters.

    Args:
        page: Page number (1-indexed)
        page_size: Number of sessions per page (max 100)
        status: Optional filter by status
        browser_type: Optional filter by browser type
        url: Optional filter by URL (partial match)
        start_date: Optional filter by start date
        end_date: Optional filter by end date
        search: Optional search in session ID or URL
        tags: Optional filter by tags (comma-separated)

    Returns:
        SessionListResponse with sessions list, total count, page, and page_size
    """
    try:
        session_manager = get_session_manager()

        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        if browser_type:
            filters['browser_type'] = browser_type
        if url:
            filters['url'] = url
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if search:
            filters['search'] = search
        if tags:
            filters['tags'] = [tag.strip() for tag in tags.split(',')]

        # Get sessions
        sessions, total = session_manager.list_sessions(
            page=page,
            page_size=page_size,
            filters=filters if filters else None
        )

        return SessionListResponse(
            sessions=[SessionResponse(**s) for s in sessions],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate", responses={500: {"model": ErrorResponse}})
async def validate_sessions():
    """
    Validate all sessions and return corrupted ones.

    Returns:
        List of corrupted session IDs
    """
    try:
        session_manager = get_session_manager()
        storage = session_manager.storage_manager
        session_ids = storage.list_sessions()

        corrupted = []
        for session_id in session_ids:
            session_json = storage.load_session_json(session_id)
            if session_json is None:
                corrupted.append(session_id)

        logger.info(f"Validation complete: {len(corrupted)} corrupted sessions found")
        return {"corrupted_sessions": corrupted, "total_checked": len(session_ids)}
    except Exception as e:
        logger.error(f"Error validating sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", responses={500: {"model": ErrorResponse}})
async def get_statistics():
    """
    Get statistics about all sessions.

    Returns:
        Statistics including total sessions, events, storage, browser types, tags, etc.
    """
    try:
        session_manager = get_session_manager()
        storage_manager = session_manager.storage_manager

        # Get all sessions
        all_sessions, total = session_manager.list_sessions(page=1, page_size=10000)

        # Calculate statistics
        stats = {
            "total_sessions": total,
            "total_events": sum(s.get('event_count', 0) for s in all_sessions),
            "browser_types": {},
            "status_counts": {},
            "tags": {},
            "total_storage_bytes": 0,
            "sessions_by_date": {}
        }

        # Analyze each session
        for session in all_sessions:
            # Browser types
            browser = session.get('browser_type', 'unknown')
            stats["browser_types"][browser] = stats["browser_types"].get(browser, 0) + 1

            # Status counts
            status = session.get('status', 'unknown')
            stats["status_counts"][status] = stats["status_counts"].get(status, 0) + 1

            # Tags
            for tag in session.get('tags', []):
                stats["tags"][tag] = stats["tags"].get(tag, 0) + 1

            # Storage size
            try:
                size = storage_manager.get_session_size(session['run_id'])
                stats["total_storage_bytes"] += size
            except:
                pass

            # Sessions by date
            start_time = session.get('start_time', '')
            if start_time:
                date = start_time.split('T')[0]
                stats["sessions_by_date"][date] = stats["sessions_by_date"].get(date, 0) + 1

        # Convert bytes to MB
        stats["total_storage_mb"] = round(stats["total_storage_bytes"] / (1024 * 1024), 2)

        return stats

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse, responses={404: {"model": ErrorResponse}})
async def get_session(session_id: str):
    """
    Get details of a specific session.
    
    Args:
        session_id: Run ID of the session
    
    Returns:
        SessionResponse with complete session details
    
    Raises:
        HTTPException: If session not found
    """
    try:
        session_manager = get_session_manager()
        session_data = session_manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return SessionResponse(**session_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/events", response_model=EventListResponse, responses={404: {"model": ErrorResponse}})
async def get_session_events(
    session_id: str,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(100, ge=1, le=1000, description="Number of events per page")
):
    """
    Get all events for a specific session with pagination.
    
    Args:
        session_id: Run ID of the session
        page: Page number (1-indexed)
        page_size: Number of events per page (max 1000)
    
    Returns:
        EventListResponse with events list, total count, page, and page_size
    
    Raises:
        HTTPException: If session not found
    """
    try:
        session_manager = get_session_manager()
        
        # Load session data
        session_json = session_manager.storage_manager.load_session_json(session_id)
        if not session_json:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        events = session_json.get('events', [])
        total = len(events)
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_events = events[start:end]
        
        from app.api.schemas import EventResponse
        return EventListResponse(
            events=[EventResponse(**e) for e in paginated_events],
            total=total,
            page=page,
            page_size=page_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/export", responses={404: {"model": ErrorResponse}})
async def export_session_json(session_id: str):
    """
    Export a session and all its events as JSON.
    
    Args:
        session_id: Run ID of the session to export
    
    Returns:
        JSON object with session details and all events
    
    Raises:
        HTTPException: If session not found
    """
    try:
        from fastapi.responses import JSONResponse
        
        session_manager = get_session_manager()
        
        # Load session data
        session_json = session_manager.storage_manager.load_session_json(session_id)
        if not session_json:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Return as downloadable JSON file
        filename = f"session_{session_id}.json"
        
        return JSONResponse(
            content=session_json,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}", responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def delete_session(session_id: str):
    """
    Delete a session and all its data.

    Args:
        session_id: Run ID of the session to delete

    Returns:
        Success message

    Raises:
        HTTPException: If session not found or deletion failed
    """
    try:
        session_manager = get_session_manager()

        # Check if session exists
        session_data = session_manager.storage_manager.load_session_json(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Delete the session
        success = session_manager.storage_manager.delete_session(session_id)

        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to delete session {session_id}")

        logger.info(f"Deleted session: {session_id}")
        return {"status": "success", "message": f"Session {session_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-delete", responses={500: {"model": ErrorResponse}})
async def batch_delete_sessions(session_ids: list[str]):
    """
    Delete multiple sessions at once.

    Args:
        session_ids: List of session IDs to delete

    Returns:
        Summary of deletion results

    Raises:
        HTTPException: If batch deletion fails
    """
    try:
        session_manager = get_session_manager()

        results = {
            "success": [],
            "failed": [],
            "not_found": []
        }

        for session_id in session_ids:
            # Try to delete the session directly
            # Even if session.json is corrupted, we should still delete the folder
            success = session_manager.storage_manager.delete_session(session_id)

            if success:
                results["success"].append(session_id)
                logger.info(f"Deleted session: {session_id}")
            else:
                results["not_found"].append(session_id)
                logger.error(f"Session not found or failed to delete: {session_id}")

        return {
            "status": "completed",
            "total": len(session_ids),
            "deleted": len(results["success"]),
            "failed": len(results["failed"]),
            "not_found": len(results["not_found"]),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error in batch delete: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{session_id}", responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def update_session(session_id: str, name: Optional[str] = None, notes: Optional[str] = None):
    """
    Update session metadata (name/notes).

    Args:
        session_id: Run ID of the session to update
        name: Optional custom name for the session
        notes: Optional notes/description for the session

    Returns:
        Success message with updated session data

    Raises:
        HTTPException: If session not found or update failed
    """
    try:
        session_manager = get_session_manager()

        # Load session data
        session_json = session_manager.storage_manager.load_session_json(session_id)
        if not session_json:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Update metadata
        session_data = session_json.get('session', {})
        if name is not None:
            session_data['custom_name'] = name
        if notes is not None:
            session_data['notes'] = notes

        # Save updated session
        session_manager.storage_manager.save_session_json(
            run_id=session_id,
            session_data=session_data,
            events=session_json.get('events', [])
        )

        logger.info(f"Updated session metadata: {session_id}")
        return {
            "status": "success",
            "message": f"Session {session_id} updated successfully",
            "session": session_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/tags", responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def add_tags(session_id: str, tags: list[str]):
    """
    Add tags to a session.

    Args:
        session_id: Run ID of the session
        tags: List of tags to add

    Returns:
        Success message with updated tags
    """
    try:
        session_manager = get_session_manager()
        session_json = session_manager.storage_manager.load_session_json(session_id)
        if not session_json:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        session_data = session_json.get('session', {})
        existing_tags = set(session_data.get('tags', []))
        existing_tags.update(tags)
        session_data['tags'] = list(existing_tags)

        session_manager.storage_manager.save_session_json(
            run_id=session_id,
            session_data=session_data,
            events=session_json.get('events', [])
        )

        logger.info(f"Added tags to session {session_id}: {tags}")
        return {"status": "success", "tags": session_data['tags']}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}/tags", responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def remove_tags(session_id: str, tags: list[str]):
    """
    Remove tags from a session.

    Args:
        session_id: Run ID of the session
        tags: List of tags to remove

    Returns:
        Success message with updated tags
    """
    try:
        session_manager = get_session_manager()
        session_json = session_manager.storage_manager.load_session_json(session_id)
        if not session_json:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        session_data = session_json.get('session', {})
        existing_tags = set(session_data.get('tags', []))
        existing_tags.difference_update(tags)
        session_data['tags'] = list(existing_tags)

        session_manager.storage_manager.save_session_json(
            run_id=session_id,
            session_data=session_data,
            events=session_json.get('events', [])
        )

        logger.info(f"Removed tags from session {session_id}: {tags}")
        return {"status": "success", "tags": session_data['tags']}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/generate-script", responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_test_script(session_id: str, framework: str = Query("playwright", description="Test framework (playwright or selenium)")):
    """
    Generate test script from recorded session.

    Args:
        session_id: Run ID of the session
        framework: Test framework (playwright or selenium)

    Returns:
        Generated test script as text
    """
    try:
        session_manager = get_session_manager()
        session_json = session_manager.storage_manager.load_session_json(session_id)
        if not session_json:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        session_data = session_json.get('session', {})
        events = session_json.get('events', [])

        if framework.lower() == "playwright":
            script = _generate_playwright_script(session_data, events)
        elif framework.lower() == "selenium":
            script = _generate_selenium_script(session_data, events)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported framework: {framework}")

        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=script, media_type="text/plain")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating test script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_playwright_script(session_data: dict, events: list) -> str:
    """Generate Playwright test script from session data."""
    start_url = session_data.get('start_url', 'about:blank')

    script = f"""import {{ test, expect }} from '@playwright/test';

test('recorded session - {session_data.get('run_id', 'unknown')}', async ({{ page }}) => {{
    // Navigate to starting URL
    await page.goto('{start_url}');

"""

    for event in events:
        event_type = event.get('event_type')
        locators = event.get('locators', [])

        if event_type == 'click' and locators:
            best_locator = locators[0]
            playwright_code = best_locator.get('playwright', '')
            if playwright_code:
                script += f"    // Click event\n"
                script += f"    await {playwright_code}.click();\n"
                script += f"    await page.waitForTimeout(500);\n\n"

        elif event_type == 'input' and locators:
            best_locator = locators[0]
            playwright_code = best_locator.get('playwright', '')
            value = event.get('target_data', {}).get('value', '')
            if playwright_code and value:
                script += f"    // Input event\n"
                script += f"    await {playwright_code}.fill('{value}');\n\n"

        elif event_type == 'navigation':
            url = event.get('page_url', '')
            if url and url != start_url:
                script += f"    // Navigation\n"
                script += f"    await page.goto('{url}');\n\n"

    script += """    // Add assertions as needed
    // await expect(page).toHaveTitle(/expected title/);
}});
"""

    return script


def _generate_selenium_script(session_data: dict, events: list) -> str:
    """Generate Selenium test script from session data."""
    start_url = session_data.get('start_url', 'about:blank')

    script = f"""from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_recorded_session():
    # Setup
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        # Navigate to starting URL
        driver.get('{start_url}')
        time.sleep(1)

"""

    for event in events:
        event_type = event.get('event_type')
        locators = event.get('locators', [])

        if event_type == 'click' and locators:
            # Find CSS or XPath locator
            css_locator = next((l for l in locators if l.get('strategy') == 'css'), None)
            xpath_locator = next((l for l in locators if l.get('strategy') == 'xpath'), None)

            if css_locator:
                selector = css_locator.get('selector', '')
                script += f"        # Click event\n"
                script += f"        element = WebDriverWait(driver, 10).until(\n"
                script += f"            EC.element_to_be_clickable((By.CSS_SELECTOR, '{selector}'))\n"
                script += f"        )\n"
                script += f"        element.click()\n"
                script += f"        time.sleep(0.5)\n\n"
            elif xpath_locator:
                selector = xpath_locator.get('selector', '')
                script += f"        # Click event\n"
                script += f"        element = WebDriverWait(driver, 10).until(\n"
                script += f"            EC.element_to_be_clickable((By.XPATH, '{selector}'))\n"
                script += f"        )\n"
                script += f"        element.click()\n"
                script += f"        time.sleep(0.5)\n\n"

        elif event_type == 'input' and locators:
            css_locator = next((l for l in locators if l.get('strategy') == 'css'), None)
            value = event.get('target_data', {}).get('value', '')

            if css_locator and value:
                selector = css_locator.get('selector', '')
                script += f"        # Input event\n"
                script += f"        element = driver.find_element(By.CSS_SELECTOR, '{selector}')\n"
                script += f"        element.clear()\n"
                script += f"        element.send_keys('{value}')\n\n"

        elif event_type == 'navigation':
            url = event.get('page_url', '')
            if url and url != start_url:
                script += f"        # Navigation\n"
                script += f"        driver.get('{url}')\n"
                script += f"        time.sleep(1)\n\n"

    script += """        # Add assertions as needed
        # assert "Expected Title" in driver.title

    finally:
        driver.quit()

if __name__ == "__main__":
    test_recorded_session()
"""

    return script
