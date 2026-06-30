"""
CORS configuration for ClaimPilot.

Attaches the CORSMiddleware to the FastAPI application.
Call configure_cors(app) from the application factory or main.py.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings


def configure_cors(app: FastAPI) -> None:
    """Attach CORSMiddleware with environment-appropriate origins."""

    if settings.APP_ENV == "production":
        # Restrict to known origins in production.
        origins = [
            "https://claimpilot.app",
        ]
    else:
        # Allow all origins in development.
        origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
