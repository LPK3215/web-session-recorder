"""WebSocket routes for real-time event streaming."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json

from app.api.sessions import get_session_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time event streaming.
    
    This endpoint:
    1. Accepts WebSocket connections for a specific session
    2. Streams events in real-time as they are captured
    3. Handles client disconnections gracefully
    4. Supports automatic reconnection
    
    Args:
        websocket: WebSocket connection
        session_id: Run ID of the session to stream events from
    
    Protocol:
        - Client connects to /ws/sessions/{run_id}
        - Server sends events as JSON messages
        - Each message contains: run_id, seq, timestamp, event_type, page_url, etc.
        - Client can disconnect at any time
        - Server handles reconnection by allowing new connections
    
    Example message:
        {
            "run_id": "session_20240115_103000_abc123",
            "seq": 5,
            "timestamp": "2024-01-15T10:30:00",
            "event_type": "click",
            "page_url": "https://example.com",
            "page_title": "Example Page",
            "target_data": {...},
            "locators": [...],
            "network_data": {...}
        }
    """
    # Get session manager
    session_manager = get_session_manager()
    
    # Verify session exists
    session_data = session_manager.get_session(session_id)
    if not session_data:
        logger.warning(f"WebSocket connection attempted for non-existent session {session_id}")
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # Accept WebSocket connection
    await websocket.accept()
    logger.info(f"WebSocket connected for session {session_id}")
    
    # Add connection to session manager
    session_manager.add_websocket_connection(session_id, websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "run_id": session_id,
            "status": session_data.get('status'),
            "message": "Connected to event stream"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (e.g., ping/pong for keepalive)
                data = await websocket.receive_text()
                
                # Handle client messages
                try:
                    message = json.loads(data)
                    message_type = message.get('type')
                    
                    if message_type == 'ping':
                        # Respond to ping with pong
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": message.get('timestamp')
                        })
                    elif message_type == 'get_status':
                        # Send current session status
                        current_session = session_manager.get_session(session_id)
                        await websocket.send_json({
                            "type": "status",
                            "run_id": session_id,
                            "status": current_session.get('status') if current_session else "unknown",
                            "event_count": current_session.get('event_count', 0) if current_session else 0
                        })
                    else:
                        logger.debug(f"Unknown message type from client: {message_type}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from WebSocket client: {data}")
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for session {session_id}")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket receive loop: {e}")
                break
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
    
    finally:
        # Remove connection from session manager
        session_manager.remove_websocket_connection(session_id, websocket)
        logger.info(f"WebSocket connection closed for session {session_id}")
