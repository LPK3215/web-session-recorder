"""FastAPI application entry point."""

import sys
import asyncio

# Fix for Windows: Set ProactorEventLoop for subprocess support
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import config
from app.api import websocket, sessions, config as config_api, profiles
from app.api.middleware import setup_exception_handlers

# Create FastAPI app
app = FastAPI(
    title=config.get('app', 'app.name', 'Web Session Recorder'),
    version=config.get('app', 'app.version', '1.0.0'),
    debug=config.get('app', 'app.debug', True)
)

# Add CORS middleware
cors_origins = config.get('app', 'server.cors_origins', [])
if not cors_origins:
    # Default to allow all origins if not configured
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up error handling
setup_exception_handlers(app)

# Include routers
app.include_router(sessions.router)
app.include_router(websocket.router, tags=["websocket"])
app.include_router(config_api.router)
app.include_router(profiles.router)

# Serve recorded session artifacts (session.json, screenshots, network files)
backend_dir = Path(__file__).resolve().parent.parent
runs_dir_name = config.get('app', 'output.runs_dir', 'runs')
runs_dir = backend_dir / runs_dir_name
runs_dir.mkdir(parents=True, exist_ok=True)
app.mount("/runs", StaticFiles(directory=str(runs_dir)), name="runs")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": config.get('app', 'app.name'),
        "version": config.get('app', 'app.version'),
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
