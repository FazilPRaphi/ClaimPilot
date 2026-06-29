"""
Base service class providing common functionality for all services.
Helps enforce consistent patterns across the application.
"""

from supabase import Client


class BaseService:
    """
    Base class for all services.
    Provides common initialization and patterns.
    """

    def __init__(self, db_client: Client):
        """Initialize service with database client."""
        self.db_client = db_client
