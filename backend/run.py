"""Entry point for running the FastAPI backend server."""

import uvicorn
import sys
import asyncio
from pathlib import Path

# Fix for Windows: Set ProactorEventLoop for subprocess support
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.config import config


def main():
    """Start the FastAPI server."""
    host = config.get('app', 'server.host', '127.0.0.1')
    port = config.get('app', 'server.port', 8000)
    reload = config.get('app', 'server.reload', True)
    
    print(f"Starting Web Session Recorder Backend")
    print(f"Server: http://{host}:{port}")
    print(f"Reload: {reload}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
