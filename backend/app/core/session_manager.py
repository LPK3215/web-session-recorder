"""Session manager for coordinating recording sessions."""

from typing import Dict, Any, Optional, Set, List, Tuple
from datetime import datetime
import logging
import uuid
import asyncio

from playwright.async_api import Page

from app.core.browser import BrowserController
from app.core.event_capturer import EventCapturer
from app.core.network_monitor import NetworkMonitor
from app.core.locators import LocatorGenerator
from app.core.storage_manager import StorageManager

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages recording sessions and coordinates all components.
    
    Responsibilities:
    - Create and manage session lifecycle
    - Coordinate browser controller, event capturer, and network monitor
    - Handle event persistence to file system
    - Stream events via WebSocket to connected clients
    """
    
    def __init__(self):
        """Initialize Session Manager."""
        self.storage_manager = StorageManager()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.websocket_connections: Dict[str, Set] = {}  # run_id -> set of websockets
    
    async def create_session(
        self,
        url: Optional[str] = None,
        browser_type: str = "chrome",
        incognito: bool = False,
        user_data_dir: Optional[str] = None,
        window_width: Optional[int] = None,
        window_height: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new recording session.
        
        Args:
            url: Starting URL (optional)
            browser_type: Browser type (chrome, edge, firefox)
            incognito: Whether to use incognito mode
            user_data_dir: Path to user data directory (optional)
            window_width: Browser window width (optional)
            window_height: Browser window height (optional)
        
        Returns:
            Session data dictionary
        """
        try:
            # Generate unique run_id
            run_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create session data
            session_data = {
                'run_id': run_id,
                'start_url': url,
                'start_time': datetime.now().isoformat(),
                'status': 'created',
                'browser_type': browser_type,
                'incognito': incognito,
                'user_data_dir': user_data_dir,
                'event_count': 0,
                'events': []
            }
            
            # Create session folder
            session_folder = self.storage_manager.create_session_folder(run_id)
            
            # Initialize session state
            self.active_sessions[run_id] = {
                'session_data': session_data,
                'browser_controller': None,
                'event_capturer': None,
                'network_monitor': None,
                'status': 'created',
                'window_width': window_width,
                'window_height': window_height,
                'session_folder': session_folder
            }
            
            logger.info(f"Created session: {run_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def start_recording(self, run_id: str) -> None:
        """
        Start recording for a session.
        
        This method:
        1. Launches the browser
        2. Sets up event capturer and network monitor
        3. Navigates to the starting URL (if provided)
        4. Begins capturing events
        
        Args:
            run_id: Run ID of the session to start
        """
        try:
            if run_id not in self.active_sessions:
                raise ValueError(f"Session {run_id} not found")
            
            session_state = self.active_sessions[run_id]
            session_data = session_state['session_data']
            
            # Initialize components
            browser_controller = BrowserController()
            locator_generator = LocatorGenerator()
            event_capturer = EventCapturer(locator_generator)
            network_monitor = NetworkMonitor()
            
            # Set up event callback
            event_capturer.set_event_callback(
                lambda event: self.handle_event(run_id, event)
            )
            
            # Set session folder for screenshots
            session_folder = session_state.get('session_folder')
            if session_folder:
                screenshot_folder = session_folder / 'screenshots'
                event_capturer.set_session_folder(run_id, screenshot_folder)
            
            # Launch browser
            await browser_controller.launch_browser(
                browser_type=session_data['browser_type'],
                headless=False,
                use_local=True,
                window_width=session_state.get('window_width'),
                window_height=session_state.get('window_height')
            )
            
            # Add browser close handler with immediate response
            async def on_browser_disconnected():
                await self._handle_browser_closed(run_id)
            
            browser_controller.browser.on('disconnected', lambda: asyncio.create_task(on_browser_disconnected()))
            
            # Create browser context
            await browser_controller.create_context(
                incognito=session_data['incognito'],
                user_data_dir=session_data['user_data_dir'],
                window_width=session_state.get('window_width'),
                window_height=session_state.get('window_height')
            )
            
            # Navigate to URL or blank page
            page = await browser_controller.navigate(session_data['start_url'])
            
            # Add page close handler with immediate response
            async def on_page_closed():
                await self._handle_browser_closed(run_id)
            
            page.on('close', lambda: asyncio.create_task(on_page_closed()))
            
            # Set up event capturer
            await event_capturer.inject_script(page)
            await event_capturer.setup_listeners(page)
            
            # Set up network monitor
            await network_monitor.setup_monitoring(page)

            # Set up network callback to store network data
            async def network_data_callback(network_data):
                """Store network data in session state"""
                if 'network_events' not in session_state:
                    session_state['network_events'] = []
                session_state['network_events'].append(network_data)
                logger.info(f"Network event captured: {network_data.get('url', 'unknown')}")

            network_monitor.set_network_callback(network_data_callback)
            
            # Update session state
            session_state['browser_controller'] = browser_controller
            session_state['event_capturer'] = event_capturer
            session_state['network_monitor'] = network_monitor
            session_state['page'] = page
            session_state['status'] = 'recording'
            
            # Update session data
            session_data['status'] = 'started'
            session_data['start_time'] = datetime.now().isoformat()
            
            logger.info(f"Started recording for session {run_id}")
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            # Update session status to error
            if run_id in self.active_sessions:
                self.active_sessions[run_id]['session_data']['status'] = 'error'
            raise
    
    async def stop_recording(self, run_id: str) -> Dict[str, Any]:
        """
        Stop recording for a session.
        
        This method:
        1. Stops event capture
        2. Closes the browser
        3. Saves the session to file
        4. Cleans up resources
        
        Args:
            run_id: Run ID of the session to stop
        
        Returns:
            Updated session data
        """
        try:
            # Check if session is in active sessions
            if run_id not in self.active_sessions:
                # Try to load from file (might have been stopped already by browser close)
                session_json = self.storage_manager.load_session_json(run_id)
                if session_json and session_json.get('session'):
                    session_data = session_json['session']
                    if session_data.get('status') == 'stopped':
                        logger.info(f"Session {run_id} already stopped")
                        return session_data
                
                # Session not found anywhere
                logger.warning(f"Session {run_id} not found in active sessions or files")
                raise ValueError(f"Session {run_id} not found")
            
            session_state = self.active_sessions[run_id]
            session_data = session_state['session_data']
            browser_controller = session_state.get('browser_controller')
            
            # 不再关闭浏览器，只停止录制
            # 浏览器关闭由用户手动操作
            logger.info(f"Recording stopped for session {run_id}, browser remains open")
            
            # Update session data
            session_data['status'] = 'stopped'
            session_data['end_time'] = datetime.now().isoformat()

            # Add network events to session data
            if 'network_events' in session_state:
                session_data['network_events'] = session_state['network_events']
                logger.info(f"Saving {len(session_state['network_events'])} network events to session")
            else:
                logger.warning("No network events found in session_state")

            # Convert all datetime objects in events to strings
            if 'events' in session_data:
                for event in session_data['events']:
                    if 'timestamp' in event and hasattr(event['timestamp'], 'isoformat'):
                        event['timestamp'] = event['timestamp'].isoformat()

            # Save session to file
            self.storage_manager.save_session_json(
                run_id=run_id,
                session_data=session_data,
                events=session_data.get('events', [])
            )
            
            # Clean up session state
            session_state['status'] = 'stopped'
            
            # Close WebSocket connections for this session
            if run_id in self.websocket_connections:
                for ws in self.websocket_connections[run_id]:
                    try:
                        await ws.close()
                    except Exception as e:
                        logger.warning(f"Error closing WebSocket: {e}")
                del self.websocket_connections[run_id]
            
            # Remove from active sessions
            del self.active_sessions[run_id]
            
            logger.info(f"Stopped recording for session {run_id}")
            return session_data
            
        except ValueError as e:
            # Re-raise ValueError with original message
            logger.error(f"Error stopping recording: {e}")
            raise
        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            raise
    
    async def _handle_browser_closed(self, run_id: str) -> None:
        """
        Handle browser being closed by user - optimized for immediate response.
        
        Args:
            run_id: Run ID of the session whose browser was closed
        """
        try:
            logger.info(f"Browser closed for session {run_id}, stopping immediately...")
            
            if run_id not in self.active_sessions:
                return
            
            session_state = self.active_sessions[run_id]
            session_data = session_state['session_data']
            
            # Update session data immediately
            session_data['status'] = 'stopped'
            session_data['end_time'] = datetime.now().isoformat()
            
            # Convert all datetime objects in events to strings
            if 'events' in session_data:
                for event in session_data['events']:
                    if 'timestamp' in event and hasattr(event['timestamp'], 'isoformat'):
                        event['timestamp'] = event['timestamp'].isoformat()
            
            # Save session data
            self.storage_manager.save_session_json(
                run_id=run_id,
                session_data=session_data,
                events=session_data.get('events', [])
            )
            
            # Close WebSocket connections immediately to notify frontend
            if run_id in self.websocket_connections:
                for ws in list(self.websocket_connections[run_id]):
                    try:
                        await ws.close()
                    except:
                        pass
                del self.websocket_connections[run_id]
            
            # Remove from active sessions
            del self.active_sessions[run_id]
            
            logger.info(f"Session {run_id} stopped immediately")
            
        except Exception as e:
            logger.error(f"Error handling browser close: {e}")
            # Force cleanup
            if run_id in self.active_sessions:
                try:
                    del self.active_sessions[run_id]
                except:
                    pass
    
    async def handle_event(self, run_id: str, event: Dict[str, Any]) -> None:
        """
        Handle a captured event.
        
        This method:
        1. Adds the event to session data
        2. Streams the event via WebSocket to connected clients
        
        Args:
            run_id: Run ID of the session
            event: Event data dictionary
        """
        try:
            if run_id not in self.active_sessions:
                logger.warning(f"Session {run_id} not found for event")
                return
            
            session_state = self.active_sessions[run_id]
            session_data = session_state['session_data']
            
            # Convert datetime to ISO format string if present
            if 'timestamp' in event and hasattr(event['timestamp'], 'isoformat'):
                event['timestamp'] = event['timestamp'].isoformat()
            
            # Add event to session data
            if 'events' not in session_data:
                session_data['events'] = []
            
            session_data['events'].append(event)
            session_data['event_count'] = len(session_data['events'])
            
            # Stream event via WebSocket
            await self.stream_event(run_id, event)
            
            logger.debug(f"Handled event {event.get('seq')} for session {run_id}")
            
        except Exception as e:
            logger.error(f"Error handling event: {e}")
            # Don't raise - we don't want to stop recording due to event handling errors
    
    async def stream_event(self, run_id: str, event: Dict[str, Any]) -> None:
        """
        Stream an event to connected WebSocket clients.
        
        Args:
            run_id: Run ID of the session
            event: Event data dictionary
        """
        try:
            if run_id not in self.websocket_connections:
                return
            
            # Convert event to JSON-serializable format
            event_data = {
                'run_id': run_id,
                'seq': event.get('seq'),
                'timestamp': event.get('timestamp'),
                'event_type': event.get('event_type'),
                'page_url': event.get('page_url'),
                'page_title': event.get('page_title'),
                'target_data': event.get('target_data'),
                'locators': event.get('locators'),
                'network_data': event.get('network_data')
            }
            
            # Send to all connected clients
            disconnected_clients = set()
            for ws in self.websocket_connections[run_id]:
                try:
                    await ws.send_json(event_data)
                except Exception as e:
                    logger.warning(f"Error sending event to WebSocket: {e}")
                    disconnected_clients.add(ws)
            
            # Remove disconnected clients
            for ws in disconnected_clients:
                self.websocket_connections[run_id].discard(ws)
            
        except Exception as e:
            logger.error(f"Error streaming event: {e}")
    
    def get_session(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a session by run_id.
        
        Args:
            run_id: Run ID of the session
        
        Returns:
            Session data or None if not found
        """
        # Check active sessions first
        if run_id in self.active_sessions:
            return self.active_sessions[run_id]['session_data']
        
        # Load from file
        session_json = self.storage_manager.load_session_json(run_id)
        if session_json and 'session' in session_json:
            return session_json['session']
        
        return None
    
    def list_sessions(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List sessions with pagination and filters.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of sessions per page
            filters: Optional filters (status, browser_type)
        
        Returns:
            Tuple of (sessions list, total count)
        """
        # Get all session run_ids
        all_run_ids = self.storage_manager.list_sessions()
        
        # Load session data
        sessions = []
        for run_id in all_run_ids:
            session_data = self.get_session(run_id)
            if session_data:
                # Apply filters
                if filters:
                    if 'status' in filters and session_data.get('status') != filters['status']:
                        continue
                    if 'browser_type' in filters and session_data.get('browser_type') != filters['browser_type']:
                        continue
                
                sessions.append(session_data)
        
        total = len(sessions)
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_sessions = sessions[start:end]
        
        return paginated_sessions, total
    
    def add_websocket_connection(self, run_id: str, websocket) -> None:
        """
        Add a WebSocket connection for a session.
        
        Args:
            run_id: Run ID of the session
            websocket: WebSocket connection object
        """
        if run_id not in self.websocket_connections:
            self.websocket_connections[run_id] = set()
        
        self.websocket_connections[run_id].add(websocket)
        logger.info(f"Added WebSocket connection for session {run_id}")
    
    def remove_websocket_connection(self, run_id: str, websocket) -> None:
        """
        Remove a WebSocket connection for a session.
        
        Args:
            run_id: Run ID of the session
            websocket: WebSocket connection object
        """
        if run_id in self.websocket_connections:
            self.websocket_connections[run_id].discard(websocket)
            logger.info(f"Removed WebSocket connection for session {run_id}")
    
    def is_session_active(self, run_id: str) -> bool:
        """
        Check if a session is currently active (recording).
        
        Args:
            run_id: Run ID of the session
        
        Returns:
            True if session is active, False otherwise
        """
        return (
            run_id in self.active_sessions and
            self.active_sessions[run_id]['status'] == 'recording'
        )
    
    def get_active_session_count(self) -> int:
        """
        Get the number of active recording sessions.
        
        Returns:
            Number of active sessions
        """
        return sum(
            1 for state in self.active_sessions.values()
            if state['status'] == 'recording'
        )
