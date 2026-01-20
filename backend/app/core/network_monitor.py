"""Network monitor for capturing HTTP requests and responses."""

from playwright.async_api import Page, Request, Response
from typing import Dict, Any, Optional, Callable, List
import logging
import re
import os
import hashlib
from datetime import datetime
from pathlib import Path

from app.core.config import config

logger = logging.getLogger(__name__)


class NetworkMonitor:
    """Monitor and capture network requests and responses."""
    
    def __init__(self, recorder_config: Optional[Dict[str, Any]] = None):
        """Initialize Network Monitor."""
        self.network_callback: Optional[Callable] = None
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        self._recorder_config = recorder_config or {}
        self.privacy_mode = self._cfg_get('recorder.privacy_mode', 'none')
        self.capture_enabled = self._cfg_get('recorder.network.enabled', True)
        self.capture_request = self._cfg_get('recorder.network.capture_request', True)
        self.capture_response = self._cfg_get('recorder.network.capture_response', True)
        self.capture_body = self._cfg_get('recorder.network.capture_body', True)
        self.max_body_size = self._cfg_get('recorder.network.max_body_size', 1048576)
        self.max_body_text_len = int(self._cfg_get('recorder.network.max_body_text_len', 0) or 0)
        self.capture_mode = str(self._cfg_get('recorder.network.capture_mode', 'all') or 'all')
        self.include_url_patterns = self._cfg_get('recorder.network.include_url_patterns', []) or []
        self.ignore_resource_types = self._cfg_get(
            'recorder.network.ignore_resource_types',
            ['image', 'stylesheet', 'font', 'media']
        )
        self.ignore_url_patterns = self._cfg_get('recorder.network.ignore_url_patterns', [])
        
        # Network body storage configuration
        self.store_bodies = self._cfg_get('recorder.network.store_bodies', False)
        self.store_bodies_threshold = self._cfg_get('recorder.network.store_bodies_threshold', 102400)
        self.storage_directory = self._cfg_get('recorder.network.storage_directory', 'network')
        self._body_file_prefix: Optional[str] = None
        
        # Current session ID for file naming
        self.current_session_id: Optional[str] = None
        self.request_counter = 0
        self.enabled = True
        
        # Ensure storage directory exists if body storage is enabled
        if self.store_bodies:
            self._ensure_storage_directory()

    def _cfg_get(self, key_path: str, default: Any = None) -> Any:
        """Read from per-session recorder_config with fallback to global config."""
        try:
            parts = key_path.split('.')
            value: Any = self._recorder_config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    raise KeyError(part)
            return value
        except Exception:
            return config.get('recorder', key_path, default)

    def _cut_text(self, text: Optional[str]) -> Optional[str]:
        if text is None or not isinstance(text, str):
            return text
        limit = int(self.max_body_text_len or 0)
        if limit <= 0 or len(text) <= limit:
            return text
        return text[:limit] + f"\n…(truncated: {len(text)})"

    def _should_include_url(self, url: str) -> bool:
        if self.capture_mode != 'minimal':
            return True
        if not self.include_url_patterns:
            return False
        for pattern in self.include_url_patterns:
            try:
                if re.search(pattern, url):
                    return True
            except re.error as e:
                logger.warning(f"Invalid include regex pattern '{pattern}': {e}")
        return False

    def set_session_folder(self, run_id: str, network_folder: Path) -> None:
        """Store network bodies under the session folder (runs/<run_id>/network)."""
        self.set_session_id(run_id)
        self.storage_directory = str(network_folder)
        self._body_file_prefix = "network"
        if self.store_bodies:
            self._ensure_storage_directory()

    def disable(self) -> None:
        """Disable monitoring (used when user stops recording but keeps the browser open)."""
        self.enabled = False
        self.capture_enabled = False
        self.network_callback = None
        self.pending_requests.clear()
        logger.info("Network monitoring disabled")
    
    def set_network_callback(self, callback: Callable) -> None:
        """
        Set callback function for captured network data.
        
        Args:
            callback: Async function to call with network data
        """
        self.network_callback = callback
    
    def set_session_id(self, session_id: str) -> None:
        """
        Set the current session ID for file naming.
        
        Args:
            session_id: Session ID to use for naming stored files
        """
        self.current_session_id = session_id
        self.request_counter = 0
        logger.info(f"Set session ID for network monitor: {session_id}")
    
    def _ensure_storage_directory(self) -> None:
        """Ensure the network storage directory exists."""
        try:
            storage_path = Path(self.storage_directory)
            storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Network storage directory ready: {storage_path.absolute()}")
        except Exception as e:
            logger.error(f"Failed to create storage directory: {e}")
            raise
    
    def _generate_body_filename(self, url: str, content_type: str = None) -> str:
        """
        Generate a unique filename for storing a response body.
        
        Args:
            url: Request URL
            content_type: Content type of the response
        
        Returns:
            Filename for storing the body
        """
        self.request_counter += 1
        
        # Create a hash of the URL for uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Determine file extension from content type
        extension = '.bin'
        if content_type:
            content_type_lower = content_type.lower()
            if 'json' in content_type_lower:
                extension = '.json'
            elif 'html' in content_type_lower:
                extension = '.html'
            elif 'xml' in content_type_lower:
                extension = '.xml'
            elif 'text' in content_type_lower:
                extension = '.txt'
        
        # Format: session_<session_id>_req_<counter>_<url_hash><extension>
        filename = f"session_{self.current_session_id}_req_{self.request_counter:04d}_{url_hash}{extension}"
        return filename
    
    def _save_body_to_file(self, body: bytes, url: str, content_type: str = None) -> Optional[str]:
        """
        Save response body to a file.
        
        Args:
            body: Response body as bytes
            url: Request URL
            content_type: Content type of the response
        
        Returns:
            Relative path to the saved file, or None if save failed
        """
        try:
            filename = self._generate_body_filename(url, content_type)
            filepath = Path(self.storage_directory) / filename
            
            # Write body to file
            with open(filepath, 'wb') as f:
                f.write(body)
            
            logger.info(f"Saved network body to: {filepath}")
            
            # Return session-relative path (so API can expose via /runs/<run_id>/...)
            if self._body_file_prefix:
                return f"{self._body_file_prefix}/{filename}"
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save network body: {e}")
            return None
    
    def _should_store_body(self, body: bytes) -> bool:
        """
        Determine if a response body should be stored to disk.
        
        Args:
            body: Response body as bytes
        
        Returns:
            True if body should be stored, False otherwise
        """
        if not self.store_bodies:
            return False
        
        if not body:
            return False
        
        # Check if body size exceeds threshold
        body_size = len(body)
        return body_size >= self.store_bodies_threshold
    
    async def setup_monitoring(self, page: Page) -> None:
        """
        Set up network monitoring for a page.
        
        Args:
            page: Playwright Page to monitor
        """
        if not self.capture_enabled:
            logger.info("Network monitoring is disabled")
            return
        
        try:
            # Listen to request events
            page.on("request", lambda request: self._on_request(request))
            
            # Listen to response events
            page.on("response", lambda response: self._on_response(response))
            
            # Listen to request failed events
            page.on("requestfailed", lambda request: self._on_request_failed(request))
            
            logger.info(f"Set up network monitoring for page: {page.url}")
            
        except Exception as e:
            logger.error(f"Error setting up network monitoring: {e}")
            raise
    
    def _on_request(self, request: Request) -> None:
        """
        Handle request event (synchronous wrapper).
        
        Args:
            request: Playwright Request object
        """
        try:
            if not self.enabled:
                return

            # Check if we should capture this request
            if not self.should_capture_request(request):
                return
            
            # Capture request data
            request_data = self._capture_request_sync(request)
            
            # Store in pending requests
            self.pending_requests[request.url] = {
                'request': request_data,
                'response': None,
                'timestamp': request_data.get('timestamp')
            }
            
            logger.debug(f"Captured request: {request.method} {request.url}")
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
    
    def _on_response(self, response: Response) -> None:
        """
        Handle response event (synchronous wrapper).
        
        Args:
            response: Playwright Response object
        """
        try:
            if not self.enabled:
                return

            # Check if we should capture this response
            if not self.should_capture_request(response.request):
                return
            
            # Capture response data
            response_data = self._capture_response_sync(response)
            
            # Update pending request with response
            url = response.url
            if url in self.pending_requests:
                self.pending_requests[url]['response'] = response_data
                
                # Trigger callback with complete network data
                if self.network_callback:
                    network_data = self.pending_requests[url]
                    # Apply privacy filter
                    network_data = self.apply_privacy_filter(network_data, self.privacy_mode)
                    # Call callback - schedule it as a task
                    import asyncio
                    asyncio.ensure_future(self.network_callback(network_data))
                
                # Clean up pending request
                del self.pending_requests[url]
            
            logger.debug(f"Captured response: {response.status} {response.url}")
            
        except Exception as e:
            logger.error(f"Error handling response: {e}")
    
    def _on_request_failed(self, request: Request) -> None:
        """
        Handle request failed event.
        
        Args:
            request: Playwright Request object
        """
        try:
            if not self.enabled:
                return

            url = request.url
            if url in self.pending_requests:
                # Mark as failed
                self.pending_requests[url]['failed'] = True
                self.pending_requests[url]['failure'] = request.failure
                
                # Clean up
                del self.pending_requests[url]
            
            logger.debug(f"Request failed: {request.url}")
            
        except Exception as e:
            logger.error(f"Error handling request failure: {e}")
    
    def _capture_request_sync(self, request: Request) -> Dict[str, Any]:
        """
        Capture request details (synchronous).
        
        Args:
            request: Playwright Request object
        
        Returns:
            Dictionary with request details
        """
        try:
            request_data = {
                'method': request.method,
                'url': request.url,
                'headers': dict(request.headers),
                'resource_type': request.resource_type,
                'timestamp': None  # Will be set by caller
            }
            
            # Capture request body if enabled
            if self.capture_request and self.capture_body:
                try:
                    post_data = request.post_data
                    if post_data:
                        # Check size limit
                        if len(post_data) <= self.max_body_size:
                            request_data['body'] = self._cut_text(post_data) if isinstance(post_data, str) else post_data
                        else:
                            request_data['body'] = f"[Body too large: {len(post_data)} bytes]"
                except Exception as e:
                    logger.warning(f"Failed to capture request body: {e}")
                    request_data['body'] = None
            
            return request_data
            
        except Exception as e:
            logger.error(f"Error capturing request: {e}")
            return {}
    
    def _capture_response_sync(self, response: Response) -> Dict[str, Any]:
        """
        Capture response details (synchronous).
        
        Args:
            response: Playwright Response object
        
        Returns:
            Dictionary with response details
        """
        try:
            response_data = {
                'status': response.status,
                'status_text': response.status_text,
                'headers': dict(response.headers),
                'url': response.url,
                'timestamp': None  # Will be set by caller
            }
            
            # Note: response.body() is async, so we can't capture it here
            # This will need to be handled differently if body capture is needed
            # For now, we'll mark it as not captured in sync context
            if self.capture_response and self.capture_body:
                response_data['body'] = '[Body capture requires async context]'
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error capturing response: {e}")
            return {}
    
    async def handle_request(self, request: Request) -> Dict[str, Any]:
        """
        Handle and capture request details (async version).
        
        Args:
            request: Playwright Request object
        
        Returns:
            Dictionary with request details
        """
        try:
            request_data = {
                'method': request.method,
                'url': request.url,
                'headers': dict(request.headers),
                'resource_type': request.resource_type,
                'timestamp': None  # Will be set by caller
            }
            
            # Capture request body if enabled
            if self.capture_request and self.capture_body:
                try:
                    post_data = request.post_data
                    if post_data:
                        body_bytes = post_data.encode('utf-8') if isinstance(post_data, str) else post_data
                        body_size = len(body_bytes)
                        content_type = request.headers.get('content-type', '')
                        
                        # Check if body should be stored to disk
                        if self._should_store_body(body_bytes):
                            # Store body to file
                            stored_path = self._save_body_to_file(body_bytes, request.url, content_type)
                            if stored_path:
                                request_data['body'] = f"[Stored to file: {stored_path}]"
                                request_data['body_file'] = stored_path
                                request_data['body_size'] = body_size
                                logger.info(f"Stored large request body ({body_size} bytes) to: {stored_path}")
                            else:
                                request_data['body'] = f"[Failed to store body: {body_size} bytes]"
                                request_data['body_size'] = body_size
                        else:
                            # Body is small enough to store inline
                            if body_size <= self.max_body_size:
                                request_data['body'] = self._cut_text(post_data) if isinstance(post_data, str) else post_data
                            else:
                                request_data['body'] = f"[Body too large: {body_size} bytes]"
                            request_data['body_size'] = body_size
                except Exception as e:
                    logger.warning(f"Failed to capture request body: {e}")
                    request_data['body'] = None
            
            return request_data
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {}
    
    async def handle_response(self, response: Response) -> Dict[str, Any]:
        """
        Handle and capture response details (async version).
        
        Args:
            response: Playwright Response object
        
        Returns:
            Dictionary with response details
        """
        try:
            response_data = {
                'status': response.status,
                'status_text': response.status_text,
                'headers': dict(response.headers),
                'url': response.url,
                'timestamp': None  # Will be set by caller
            }
            
            # Capture response body if enabled
            if self.capture_response and self.capture_body:
                try:
                    body = await response.body()
                    if body:
                        body_size = len(body)
                        content_type = response.headers.get('content-type', '')
                        
                        # Check if body should be stored to disk
                        if self._should_store_body(body):
                            # Store body to file
                            stored_path = self._save_body_to_file(body, response.url, content_type)
                            if stored_path:
                                response_data['body'] = f"[Stored to file: {stored_path}]"
                                response_data['body_file'] = stored_path
                                response_data['body_size'] = body_size
                                logger.info(f"Stored large response body ({body_size} bytes) to: {stored_path}")
                            else:
                                response_data['body'] = f"[Failed to store body: {body_size} bytes]"
                                response_data['body_size'] = body_size
                        else:
                            # Body is small enough to store inline
                            if body_size <= self.max_body_size:
                                # Try to decode as text
                                try:
                                    response_data['body'] = self._cut_text(body.decode('utf-8'))
                                except UnicodeDecodeError:
                                    # Binary data, store as base64 or size info
                                    response_data['body'] = f"[Binary data: {body_size} bytes]"
                            else:
                                response_data['body'] = f"[Body too large: {body_size} bytes]"
                            response_data['body_size'] = body_size
                except Exception as e:
                    logger.warning(f"Failed to capture response body: {e}")
                    response_data['body'] = None
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error handling response: {e}")
            return {}
    
    def apply_privacy_filter(self, data: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """
        Apply privacy filtering to network data.
        
        Args:
            data: Network data dictionary
            mode: Privacy mode ('none', 'partial', 'strict')
        
        Returns:
            Filtered network data dictionary
        """
        if mode == 'none':
            return data
        
        # Create a copy to avoid modifying original
        filtered_data = data.copy()
        
        if mode == 'strict':
            # Remove all potentially sensitive data
            if 'request' in filtered_data and filtered_data['request']:
                request = filtered_data['request']
                # Remove sensitive headers
                if 'headers' in request:
                    request['headers'] = self._filter_headers(request['headers'], strict=True)
                # Remove body
                if 'body' in request:
                    request['body'] = '[Removed for privacy]'
            
            if 'response' in filtered_data and filtered_data['response']:
                response = filtered_data['response']
                # Remove sensitive headers
                if 'headers' in response:
                    response['headers'] = self._filter_headers(response['headers'], strict=True)
                # Remove body
                if 'body' in response:
                    response['body'] = '[Removed for privacy]'
        
        elif mode == 'partial':
            # Mask sensitive fields but preserve structure
            if 'request' in filtered_data and filtered_data['request']:
                request = filtered_data['request']
                # Filter sensitive headers
                if 'headers' in request:
                    request['headers'] = self._filter_headers(request['headers'], strict=False)
                # Mask sensitive body content
                if 'body' in request and request['body']:
                    request['body'] = self._mask_sensitive_body(request['body'])
            
            if 'response' in filtered_data and filtered_data['response']:
                response = filtered_data['response']
                # Filter sensitive headers
                if 'headers' in response:
                    response['headers'] = self._filter_headers(response['headers'], strict=False)
                # Mask sensitive body content
                if 'body' in response and response['body']:
                    response['body'] = self._mask_sensitive_body(response['body'])
        
        return filtered_data
    
    def _filter_headers(self, headers: Dict[str, str], strict: bool = False) -> Dict[str, str]:
        """
        Filter sensitive headers.
        
        Args:
            headers: Headers dictionary
            strict: If True, remove all auth headers; if False, mask them
        
        Returns:
            Filtered headers dictionary
        """
        sensitive_headers = [
            'authorization',
            'cookie',
            'set-cookie',
            'x-api-key',
            'x-auth-token',
            'x-csrf-token'
        ]
        
        filtered = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if key_lower in sensitive_headers:
                if strict:
                    # Skip sensitive headers entirely
                    continue
                else:
                    # Mask the value
                    filtered[key] = '[MASKED]'
            else:
                filtered[key] = value
        
        return filtered
    
    def _mask_sensitive_body(self, body: str) -> str:
        """
        Mask sensitive content in request/response body.
        
        Args:
            body: Body content as string
        
        Returns:
            Masked body content
        """
        # List of sensitive field patterns
        sensitive_patterns = [
            r'"password"\s*:\s*"[^"]*"',
            r'"token"\s*:\s*"[^"]*"',
            r'"api_key"\s*:\s*"[^"]*"',
            r'"secret"\s*:\s*"[^"]*"',
            r'"credit_card"\s*:\s*"[^"]*"',
            r'"cvv"\s*:\s*"[^"]*"'
        ]
        
        masked_body = body
        for pattern in sensitive_patterns:
            # Replace sensitive values with masked placeholder
            masked_body = re.sub(
                pattern,
                lambda m: m.group(0).rsplit('"', 2)[0] + '"[MASKED]"',
                masked_body,
                flags=re.IGNORECASE
            )
        
        return masked_body
    
    def should_capture_request(self, request: Request) -> bool:
        """
        Determine if a request should be captured.
        
        Args:
            request: Playwright Request object
        
        Returns:
            True if request should be captured, False otherwise
        """
        # Check if network monitoring is enabled
        if not self.capture_enabled:
            return False

        # Minimal mode: only capture whitelisted URLs
        if not self._should_include_url(request.url):
            return False
        
        # Check resource type
        resource_type = request.resource_type
        if resource_type in self.ignore_resource_types:
            logger.debug(f"Ignoring request due to resource type: {resource_type}")
            return False
        
        # Check URL patterns
        url = request.url
        for pattern in self.ignore_url_patterns:
            try:
                if re.search(pattern, url):
                    logger.debug(f"Ignoring request due to URL pattern: {pattern}")
                    return False
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        
        return True
    
    def get_pending_requests(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all pending requests (requests without responses yet).
        
        Returns:
            Dictionary of pending requests
        """
        return self.pending_requests.copy()
    
    def clear_pending_requests(self) -> None:
        """Clear all pending requests."""
        self.pending_requests.clear()
        logger.debug("Cleared pending requests")
    
    def cleanup_session_files(self, session_id: str) -> int:
        """
        Clean up stored network body files for a specific session.
        
        Args:
            session_id: Session ID to clean up files for
        
        Returns:
            Number of files deleted
        """
        try:
            storage_path = Path(self.storage_directory)
            if not storage_path.exists():
                return 0
            
            # Find all files for this session
            pattern = f"session_{session_id}_*"
            files_deleted = 0
            
            for filepath in storage_path.glob(pattern):
                try:
                    filepath.unlink()
                    files_deleted += 1
                    logger.debug(f"Deleted network body file: {filepath}")
                except Exception as e:
                    logger.warning(f"Failed to delete file {filepath}: {e}")
            
            logger.info(f"Cleaned up {files_deleted} network body files for session {session_id}")
            return files_deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up session files: {e}")
            return 0
