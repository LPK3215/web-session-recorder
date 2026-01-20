"""Event capturer for recording browser interactions."""

from playwright.async_api import Page, Dialog, Download
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import logging
import json
import asyncio

from app.core.locators import LocatorGenerator
from app.core.config import config

logger = logging.getLogger(__name__)


class EventCapturer:
    """Capture browser events and generate locators."""
    
    def __init__(self, locator_generator: Optional[LocatorGenerator] = None):
        """
        Initialize Event Capturer.
        
        Args:
            locator_generator: LocatorGenerator instance (creates new if None)
        """
        self.locator_generator = locator_generator or LocatorGenerator()
        self.event_callback: Optional[Callable] = None
        self.seq_counter = 0
        self.injector_script = self._load_injector_script()
        self.session_id: Optional[int] = None
        self.run_id: Optional[str] = None
        self.screenshot_folder: Optional[Path] = None
        
        # Load screenshot configuration
        self.screenshot_enabled = config.get('recorder', 'recorder.screenshots.enabled', True)  # Enable by default
        self.screenshot_on_events = config.get('recorder', 'recorder.screenshots.on_events', ['navigation', 'click'])
        self.screenshot_quality = config.get('recorder', 'recorder.screenshots.quality', 80)
    
    def set_session_id(self, session_id: int) -> None:
        """
        Set the session ID for screenshot file naming.
        
        Args:
            session_id: ID of the current session
        """
        self.session_id = session_id
        logger.debug(f"Set session ID for event capturer: {session_id}")
    
    def set_session_folder(self, run_id: str, screenshot_folder: Path) -> None:
        """
        Set the session folder for storing screenshots.
        
        Args:
            run_id: Unique run ID for the session
            screenshot_folder: Path to the screenshots folder
        """
        self.run_id = run_id
        self.screenshot_folder = screenshot_folder
        self.screenshot_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Screenshot folder set: {screenshot_folder}")
    
    def _load_injector_script(self) -> str:
        """Load the JavaScript injector script."""
        try:
            # Get the backend directory (parent of app/)
            from pathlib import Path
            backend_dir = Path(__file__).parent.parent.parent
            script_path = backend_dir / 'scripts' / 'injector.js'
            
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load injector script from {script_path}: {e}")
            raise FileNotFoundError(f"无法加载 JavaScript 注入脚本: {script_path}。请确保 backend/scripts/injector.js 文件存在。")
    
    def set_event_callback(self, callback: Callable) -> None:
        """
        Set callback function for captured events.
        
        Args:
            callback: Async function to call with captured events
        """
        self.event_callback = callback
    
    async def inject_script(self, page: Page) -> None:
        """
        Inject JavaScript capturer script into a page and all frames.
        
        This method injects the event capture script into:
        - The main page (via add_init_script for future navigations)
        - All existing frames including iframes
        - Handles cross-origin iframe restrictions gracefully
        
        Args:
            page: Playwright Page to inject script into
        """
        try:
            # Add init script to run on every page load (main frame and future iframes)
            await page.add_init_script(self.injector_script)
            logger.debug(f"Injected capturer script into page: {page.url}")
            
            # Also inject into all existing frames (including iframes)
            injected_count = 0
            failed_count = 0
            
            for frame in page.frames:
                try:
                    # Inject script into frame
                    await frame.evaluate(self.injector_script)
                    injected_count += 1
                    
                    # Check if this is an iframe
                    is_iframe = frame != page.main_frame
                    frame_type = "iframe" if is_iframe else "main frame"
                    logger.debug(f"Injected script into {frame_type}: {frame.url}")
                    
                except Exception as e:
                    failed_count += 1
                    # This is expected for cross-origin iframes
                    is_iframe = frame != page.main_frame
                    frame_type = "iframe" if is_iframe else "frame"
                    
                    # Check if it's a cross-origin error
                    error_msg = str(e).lower()
                    if 'cross-origin' in error_msg or 'blocked' in error_msg or 'access' in error_msg:
                        logger.info(f"Cross-origin {frame_type} blocked script injection: {frame.url}")
                    else:
                        logger.warning(f"Failed to inject into {frame_type} {frame.url}: {e}")
            
            logger.info(f"Script injection complete: {injected_count} successful, {failed_count} failed/restricted")
            
        except Exception as e:
            logger.error(f"Error injecting script: {e}")
            raise
    
    async def setup_listeners(self, page: Page) -> None:
        """
        Set up Playwright event listeners for a page.
        
        This includes listeners for:
        - Navigation events (including iframe navigations)
        - Dialog events
        - Download events
        - Custom DOM events from injected JavaScript
        - New frame attachments (for dynamic iframes)
        
        Args:
            page: Playwright Page to attach listeners to
        """
        try:
            # Listen to navigation events (fires for main frame and iframes)
            page.on("framenavigated", lambda frame: asyncio.create_task(
                self.handle_navigation(page, frame.url)
            ))
            
            # Listen to new frames being attached (for dynamic iframes)
            page.on("frameattached", lambda frame: asyncio.create_task(
                self._handle_frame_attached(page, frame)
            ))
            
            # Listen to dialog events (alert, confirm, prompt)
            page.on("dialog", lambda dialog: asyncio.create_task(
                self.handle_dialog(page, dialog)
            ))
            
            # Listen to download events
            page.on("download", lambda download: asyncio.create_task(
                self.handle_download(page, download)
            ))
            
            # Listen to custom events from injected JavaScript
            await page.expose_function(
                "__recorder_send_event__",
                lambda event_data: asyncio.create_task(
                    self.handle_dom_event(page, event_data)
                )
            )
            
            # Set up listener for custom events
            await page.evaluate("""
                window.addEventListener('__recorder_event__', (e) => {
                    if (window.__recorder_send_event__) {
                        window.__recorder_send_event__(e.detail);
                    }
                });
            """)
            
            logger.info(f"Set up event listeners for page: {page.url}")
            
        except Exception as e:
            logger.error(f"Error setting up listeners: {e}")
            raise
    
    async def _handle_frame_attached(self, page: Page, frame) -> None:
        """
        Handle new frame attachment (for dynamic iframes).
        
        Args:
            page: Playwright Page
            frame: The newly attached frame
        """
        try:
            # Wait a bit for the frame to load
            await asyncio.sleep(0.1)
            
            # Inject script into the new frame
            try:
                await frame.evaluate(self.injector_script)
                logger.debug(f"Injected script into newly attached frame: {frame.url}")
            except Exception as e:
                # Expected for cross-origin frames
                error_msg = str(e).lower()
                if 'cross-origin' in error_msg or 'blocked' in error_msg:
                    logger.info(f"Cross-origin frame blocked script injection: {frame.url}")
                else:
                    logger.warning(f"Failed to inject into new frame {frame.url}: {e}")
        except Exception as e:
            logger.error(f"Error handling frame attachment: {e}")
    
    async def handle_dom_event(self, page: Page, event_data: Dict[str, Any]) -> None:
        """
        Handle DOM events captured by JavaScript.
        
        Args:
            page: Playwright Page where event occurred
            event_data: Event data from JavaScript including iframe context
        """
        try:
            # Increment sequence counter
            self.seq_counter += 1
            
            # Extract event information
            event_type = event_data.get('type')
            timestamp = datetime.fromtimestamp(event_data.get('timestamp', 0) / 1000)
            page_context = event_data.get('page', {})
            target_info = event_data.get('target')
            event_details = event_data.get('event_details', {})
            frame_info = page_context.get('frame', {})
            
            # Capture screenshot asynchronously to avoid blocking
            screenshot_path = None
            if self.screenshot_enabled and event_type in self.screenshot_on_events:
                screenshot_path = f"screenshots/event_{self.seq_counter}.png"
                # 异步截图，不等待完成，避免页面抖动
                asyncio.create_task(self.capture_screenshot(page, event_type, self.seq_counter))
            
            # Generate locators for target element
            locators = []
            if target_info:
                # Pass iframe context to locator generator
                locators = self.locator_generator.generate_locators(
                    target_info, 
                    iframe_context=frame_info
                )
            
            # Build event record with iframe context and screenshot
            event = {
                'seq': self.seq_counter,
                'timestamp': timestamp,
                'event_type': event_type,
                'page_url': page_context.get('url', page.url),
                'page_title': await page.title(),
                'target_data': target_info,
                'locators': locators,
                'network_data': None,  # Will be populated by network monitor
                'raw_data': event_data,
                'iframe_context': frame_info if frame_info.get('is_iframe') else None,
                'screenshot_path': screenshot_path
            }
            
            # Apply privacy filtering if needed
            privacy_mode = config.get('recorder', 'recorder.privacy_mode', 'none')
            if privacy_mode != 'none':
                event = self._apply_privacy_filter(event, privacy_mode)
            
            # Call event callback
            if self.event_callback:
                await self.event_callback(event)
            
            # Log with iframe context if applicable
            iframe_suffix = f" (in iframe: {frame_info.get('frame_url')})" if frame_info.get('is_iframe') else ""
            screenshot_suffix = f" [screenshot: {screenshot_path}]" if screenshot_path else ""
            logger.debug(f"Captured {event_type} event (seq={self.seq_counter}){iframe_suffix}{screenshot_suffix}")
            
        except Exception as e:
            logger.error(f"Error handling DOM event: {e}")
    
    async def handle_navigation(self, page: Page, url: str) -> None:
        """
        Handle page navigation events.
        
        Args:
            page: Playwright Page
            url: New URL after navigation
        """
        try:
            # Increment sequence counter
            self.seq_counter += 1
            
            # Capture screenshot if enabled for navigation events
            screenshot_path = await self.capture_screenshot(page, 'navigation', self.seq_counter)
            
            # Build navigation event
            event = {
                'seq': self.seq_counter,
                'timestamp': datetime.now(),
                'event_type': 'navigation',
                'page_url': url,
                'page_title': await page.title(),
                'target_data': None,
                'locators': None,
                'network_data': None,
                'raw_data': {
                    'type': 'navigation',
                    'url': url,
                    'timestamp': datetime.now().timestamp() * 1000
                },
                'screenshot_path': screenshot_path
            }
            
            # Call event callback
            if self.event_callback:
                await self.event_callback(event)
            
            screenshot_suffix = f" [screenshot: {screenshot_path}]" if screenshot_path else ""
            logger.debug(f"Captured navigation event to {url} (seq={self.seq_counter}){screenshot_suffix}")
            
            # Re-inject script after navigation
            await self.inject_script(page)
            
        except Exception as e:
            logger.error(f"Error handling navigation: {e}")
    
    async def handle_dialog(self, page: Page, dialog: Dialog) -> None:
        """
        Handle dialog events (alert, confirm, prompt).
        
        Args:
            page: Playwright Page
            dialog: Dialog object
        """
        try:
            # Increment sequence counter
            self.seq_counter += 1
            
            # Capture dialog information
            dialog_type = dialog.type
            dialog_message = dialog.message
            dialog_default_value = dialog.default_value
            
            # Build dialog event
            event = {
                'seq': self.seq_counter,
                'timestamp': datetime.now(),
                'event_type': 'dialog',
                'page_url': page.url,
                'page_title': await page.title(),
                'target_data': None,
                'locators': None,
                'network_data': None,
                'raw_data': {
                    'type': 'dialog',
                    'dialog_type': dialog_type,
                    'message': dialog_message,
                    'default_value': dialog_default_value,
                    'timestamp': datetime.now().timestamp() * 1000
                }
            }
            
            # Call event callback
            if self.event_callback:
                await self.event_callback(event)
            
            logger.debug(f"Captured {dialog_type} dialog event (seq={self.seq_counter})")
            
            # Auto-dismiss dialog
            await dialog.dismiss()
            
        except Exception as e:
            logger.error(f"Error handling dialog: {e}")
    
    async def handle_download(self, page: Page, download: Download) -> None:
        """
        Handle file download events.
        
        Args:
            page: Playwright Page
            download: Download object
        """
        try:
            # Increment sequence counter
            self.seq_counter += 1
            
            # Capture download information
            suggested_filename = download.suggested_filename
            download_url = download.url
            
            # Build download event
            event = {
                'seq': self.seq_counter,
                'timestamp': datetime.now(),
                'event_type': 'download',
                'page_url': page.url,
                'page_title': await page.title(),
                'target_data': None,
                'locators': None,
                'network_data': None,
                'raw_data': {
                    'type': 'download',
                    'filename': suggested_filename,
                    'url': download_url,
                    'timestamp': datetime.now().timestamp() * 1000
                }
            }
            
            # Call event callback
            if self.event_callback:
                await self.event_callback(event)
            
            logger.debug(f"Captured download event: {suggested_filename} (seq={self.seq_counter})")
            
        except Exception as e:
            logger.error(f"Error handling download: {e}")
    
    def _apply_privacy_filter(self, event: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Apply privacy filtering to event data.
        
        Args:
            event: Event dictionary
            mode: Privacy mode ('partial' or 'strict')
        
        Returns:
            Filtered event dictionary
        """
        if mode == 'strict':
            # Remove all potentially sensitive data
            if event.get('target_data'):
                target = event['target_data']
                if target.get('value'):
                    target['value'] = None
                if target.get('text'):
                    target['text'] = None
            
            # Remove sensitive raw data
            if event.get('raw_data', {}).get('input_data'):
                event['raw_data']['input_data']['value_length'] = 0
        
        elif mode == 'partial':
            # Mask sensitive fields but preserve structure
            if event.get('target_data'):
                target = event['target_data']
                
                # Check if field is sensitive
                raw_input_data = event.get('raw_data', {}).get('input_data', {})
                is_sensitive = raw_input_data.get('is_sensitive', False)
                
                if is_sensitive and target.get('value'):
                    # Mask value but preserve length
                    value_length = len(target['value'])
                    target['value'] = '*' * value_length
        
        return event
    
    def reset_sequence(self) -> None:
        """Reset the sequence counter (for new sessions)."""
        self.seq_counter = 0
        logger.debug("Reset event sequence counter")
    
    async def capture_screenshot(self, page: Page, event_type: str, seq: int) -> Optional[str]:
        """
        Capture a screenshot for an event.
        
        Args:
            page: Playwright Page to capture
            event_type: Type of event that triggered the screenshot
            seq: Sequence number of the event
        
        Returns:
            Relative path to the saved screenshot file, or None if screenshot capture is disabled or failed
        """
        if not self.screenshot_enabled:
            return None
        
        # Check if we should capture screenshot for this event type
        if event_type not in self.screenshot_on_events:
            return None
        
        if self.screenshot_folder is None:
            logger.warning("Cannot capture screenshot: screenshot_folder not set")
            return None
        
        try:
            # Generate filename: event_{seq}.png
            filename = f"event_{seq}.png"
            filepath = self.screenshot_folder / filename
            
            # Capture screenshot (PNG doesn't support quality parameter)
            await page.screenshot(
                path=str(filepath),
                type='png'
            )
            
            logger.debug(f"Captured screenshot: {filename}")
            # Return relative path: screenshots/event_{seq}.png
            return f"screenshots/{filename}"
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None
