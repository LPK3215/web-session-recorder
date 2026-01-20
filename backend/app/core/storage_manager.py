"""Storage manager for organizing session data into folders."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import shutil
import logging

from app.core.config import config

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Manages file-based storage for recording sessions.
    
    Each session gets its own folder containing:
    - session.json: Session metadata and all events
    - screenshots/: All screenshots for this session
    - network/: Network request/response bodies
    """
    
    def __init__(self):
        """Initialize Storage Manager."""
        # Get base directory from config (relative to backend/)
        backend_dir = Path(__file__).parent.parent.parent
        base_dir = config.get('app', 'output.runs_dir', 'runs')
        self.base_dir = backend_dir / base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage manager initialized: {self.base_dir}")
    
    def create_session_folder(self, run_id: str) -> Path:
        """
        Create a folder for a new session.
        
        Args:
            run_id: Unique run ID for the session
        
        Returns:
            Path to the created session folder
        """
        session_folder = self.base_dir / run_id
        session_folder.mkdir(parents=True, exist_ok=True)
        
        # Create subfolders
        (session_folder / 'screenshots').mkdir(exist_ok=True)
        (session_folder / 'network').mkdir(exist_ok=True)
        
        logger.info(f"Created session folder: {session_folder}")
        return session_folder
    
    def get_session_folder(self, run_id: str) -> Path:
        """
        Get the folder path for a session.
        
        Args:
            run_id: Unique run ID for the session
        
        Returns:
            Path to the session folder
        """
        return self.base_dir / run_id
    
    def get_screenshot_path(self, run_id: str, event_seq: int) -> Path:
        """
        Get the path for a screenshot file.
        
        Args:
            run_id: Unique run ID for the session
            event_seq: Event sequence number
        
        Returns:
            Path to the screenshot file
        """
        session_folder = self.get_session_folder(run_id)
        return session_folder / 'screenshots' / f'event_{event_seq}.png'
    
    def get_network_body_path(self, run_id: str, request_id: str) -> Path:
        """
        Get the path for a network request/response body file.
        
        Args:
            run_id: Unique run ID for the session
            request_id: Unique request ID
        
        Returns:
            Path to the network body file
        """
        session_folder = self.get_session_folder(run_id)
        return session_folder / 'network' / f'request_{request_id}_body.txt'
    
    def save_session_json(
        self,
        run_id: str,
        session_data: Dict[str, Any],
        events: List[Dict[str, Any]]
    ) -> Path:
        """
        Save session data and events to a JSON file.
        
        Args:
            run_id: Unique run ID for the session
            session_data: Session metadata
            events: List of event dictionaries
        
        Returns:
            Path to the saved JSON file
        """
        session_folder = self.get_session_folder(run_id)
        json_path = session_folder / 'session.json'
        
        # Build export data
        export_data = {
            "session": session_data,
            "events": events,
            "metadata": {
                "total_events": len(events),
                "saved_time": datetime.now().isoformat()
            }
        }
        
        # Save with pretty formatting
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved session JSON: {json_path}")
        return json_path
    
    def load_session_json(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data from JSON file.
        
        Args:
            run_id: Unique run ID for the session
        
        Returns:
            Session data dictionary or None if not found
        """
        session_folder = self.get_session_folder(run_id)
        json_path = session_folder / 'session.json'
        
        if not json_path.exists():
            logger.warning(f"Session JSON not found: {json_path}")
            return None
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load session JSON: {e}")
            return None
    
    def list_sessions(self) -> List[str]:
        """
        List all session run IDs.
        
        Returns:
            List of run IDs
        """
        if not self.base_dir.exists():
            return []
        
        sessions = []
        for item in self.base_dir.iterdir():
            if item.is_dir() and item.name.startswith('session_'):
                sessions.append(item.name)
        
        return sorted(sessions, reverse=True)  # Most recent first
    
    def delete_session(self, run_id: str) -> bool:
        """
        Delete a session folder and all its contents.
        
        Args:
            run_id: Unique run ID for the session
        
        Returns:
            True if deleted successfully, False otherwise
        """
        session_folder = self.get_session_folder(run_id)
        
        if not session_folder.exists():
            logger.warning(f"Session folder not found: {session_folder}")
            return False
        
        try:
            shutil.rmtree(session_folder)
            logger.info(f"Deleted session folder: {session_folder}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session folder: {e}")
            return False
    
    def get_session_size(self, run_id: str) -> int:
        """
        Get the total size of a session folder in bytes.
        
        Args:
            run_id: Unique run ID for the session
        
        Returns:
            Total size in bytes
        """
        session_folder = self.get_session_folder(run_id)
        
        if not session_folder.exists():
            return 0
        
        total_size = 0
        for file_path in session_folder.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
    
    def export_session(self, run_id: str, target_path: Path) -> bool:
        """
        Export a session folder to a target location.
        
        Args:
            run_id: Unique run ID for the session
            target_path: Target directory path
        
        Returns:
            True if exported successfully, False otherwise
        """
        session_folder = self.get_session_folder(run_id)
        
        if not session_folder.exists():
            logger.warning(f"Session folder not found: {session_folder}")
            return False
        
        try:
            target_folder = target_path / run_id
            shutil.copytree(session_folder, target_folder, dirs_exist_ok=True)
            logger.info(f"Exported session to: {target_folder}")
            return True
        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            return False
