"""
Lifespan management for ClaimPilot FastAPI application.

Handles startup and shutdown events cleanly using async context managers.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifecycle.
    
    Startup: Initialize resources, connect to databases, etc.
    Shutdown: Cleanup resources, close connections.
    """
    
    logger.info("Starting ClaimPilot API...")
    
    # Place startup logic here (e.g., warming up caches, checking DB connections)
    
    yield
    
    # Place shutdown logic here
    logger.info("Shutting down ClaimPilot API...")
